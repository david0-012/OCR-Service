from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


def extraer_texto(ruta_archivo: str) -> str:
    logger.info(f"Iniciando OCR Azure | archivo={ruta_archivo}")
    return _extraer_texto_azure(ruta_archivo)


def _extraer_texto_azure(ruta_archivo: str) -> str:
    if not settings.AZURE_ENDPOINT or not settings.AZURE_API_KEY:
        raise ValueError(
            "Falta configurar AZURE_ENDPOINT y/o AZURE_API_KEY para usar OCR de Azure"
        )

    endpoint = settings.AZURE_ENDPOINT.rstrip("/")

    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
        from azure.core.credentials import AzureKeyCredential
        from azure.core.exceptions import HttpResponseError
    except ImportError as e:
        logger.error("SDK de Azure no instalado. Instala azure-ai-documentintelligence y azure-core")
        raise RuntimeError(
            "Dependencias de Azure no instaladas. Ejecuta: uv sync"
        ) from e

    try:
        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(settings.AZURE_API_KEY),
        )

        with open(ruta_archivo, "rb") as f:
            document_bytes = f.read()

        poller = client.begin_analyze_document(
            "prebuilt-read",
            body=AnalyzeDocumentRequest(bytes_source=document_bytes),
        )
        result = poller.result()

        texto = " ".join(
            line.content
            for page in result.pages
            for line in (page.lines or [])
        )

        logger.info(f"Azure OCR exitoso | caracteres={len(texto)}")
        return texto

    except HttpResponseError as e:
        status = getattr(e, "status_code", "desconocido")
        logger.error(f"Azure OCR falló | status={status} | error={e}")
        if status == 401:
            raise RuntimeError(
                "Azure rechazó la autenticación (401). Revisa que AZURE_API_KEY y AZURE_ENDPOINT pertenezcan al mismo recurso y que el endpoint no tenga errores."
            ) from e
        raise

    except Exception as e:
        logger.error(f"Error en Azure OCR: {e}")
        raise