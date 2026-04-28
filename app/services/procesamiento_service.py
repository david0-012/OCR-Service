import re
import unicodedata
from app.core.logging import get_logger

logger = get_logger(__name__)


def procesar_texto(texto: str) -> dict:
    """
    Realiza transformaciones sobre el texto extraído:
    - Limpieza avanzada (normalización, eliminación de ruido)
    - Estructuración básica (extracción de campos)
    - Clasificación de tipo de documento
    
    Retorna:
        - num_palabras: cantidad de palabras
        - tipo_detectado: tipo de documento detectado
        - campos_extraidos: diccionario con campos estructurados
    """
    logger.info("Iniciando procesamiento de texto")
    
    # Paso 1: Limpieza avanzada
    texto_limpio = _limpiar_texto(texto)
    
    # Paso 2: Conteo de palabras
    palabras = texto_limpio.split()
    num_palabras = len(palabras)
    
    # Paso 3: Estructuración (extracción de campos)
    campos_extraidos = _extraer_campos(texto_limpio)
    
    # Paso 4: Clasificación
    tipo_detectado = _clasificar_documento(texto_limpio.lower())
    
    resultado = {
        "num_palabras": num_palabras,
        "tipo_detectado": tipo_detectado,
        "campos_extraidos": campos_extraidos,
    }
    
    logger.info(f"Procesamiento completado | palabras={num_palabras} | tipo={tipo_detectado} | campos={len(campos_extraidos)}")
    return resultado


def _limpiar_texto(texto: str) -> str:
    """
    Limpieza avanzada del texto:
    - Normaliza espacios múltiples
    - Elimina caracteres de control
    - Elimina espacios en blanco al inicio/final
    - Normaliza saltos de línea
    """
    # Eliminar caracteres de control (excepto saltos de línea)
    texto = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Normalizar saltos de línea y espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # Eliminar espacios en blanco al inicio/final
    texto = texto.strip()
    
    return texto


def _extraer_campos(texto: str) -> dict:
    """
    Extrae campos estructurados del texto usando regex:
    - Números de documento (factura, recibo, etc.)
    - Fechas
    - Montos/Totales
    - Nombres/Entidades
    """
    campos = {}
    texto_lower = texto.lower()
    
    # Extraer números de documento
    # Patrón: "número", "factura", "n°", etc.
    numero_match = re.search(r'(?:factura|recibo|n°|número|nº)\s*[:#]?\s*([\d\-]+)', texto_lower)
    if numero_match:
        campos['numero_documento'] = numero_match.group(1).strip()
    
    # Extraer fechas (formato DD/MM/YYYY o DD-MM-YYYY)
    fecha_match = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', texto)
    if fecha_match:
        campos['fecha'] = f"{fecha_match.group(1)}/{fecha_match.group(2)}/{fecha_match.group(3)}"
    
    # Extraer montos (precedidos por $, USD, etc.)
    monto_pattern = r'(?:total|subtotal|neto|monto|precio|costo)[:\s]*[$]?\s*([\d.,]+)'
    montos = re.findall(monto_pattern, texto_lower)
    if montos:
        campos['montos'] = montos
    
    # Extraer cliente/empresa (palabras después de "cliente", "empresa", etc.)
    cliente_match = re.search(r'(?:cliente|empresa|razón|a nombre de)[:\s]*([^\n]{1,60})', texto_lower)
    if cliente_match:
        campos['cliente'] = cliente_match.group(1).strip().title()
    
    return campos


def _clasificar_documento(texto_lower: str) -> str:
    """
    Clasifica el tipo de documento basado en palabras clave ponderadas.

    Nota:
    - Se normalizan acentos y caracteres especiales para tolerar variaciones del OCR.
    - Se elige la categoría con mayor puntaje, en lugar de exigir dos coincidencias exactas.
    - Prioriza documentos más específicos (CV, contrato, factura) antes que genéricos.
    """

    texto_normalizado = _normalizar_texto(texto_lower)

    palabras_clave = {
        # Documentos de identidad/CV
        "cv_hoja_vida": [
            "curriculum", "cv", "hoja de vida", "experiencia laboral",
            "formacion academica", "educacion", "competencias", "referencias",
            "perfil profesional", "objetivo laboral", "perfil de competencias",
            "historial laboral", "idiomas", "habilidades"
        ],

        # Facturas / comprobantes de pago / transacciones
        "factura": [
            "factura", "numero de factura", "n° factura", "rfc", "razon social",
            "iva", "importe", "subtotal neto", "emisor", "adquirente", "fecha de emision",
            "nit", "total compra", "total pagado", "medio de pago", "numero de orden",
            "transaccion", "aprobada", "referencia", "payu", "pagosonline", "tecnipagos",
            "comprobante", "pago seguro", "tarjeta", "visa"
        ],

        # Recibos y comprobantes
        "recibo": [
            "recibo", "recibido", "pagado por", "la cantidad de", "concepto",
            "constancia de pago", "comprobante de pago", "folio"
        ],
        
        # Contratos
        "contrato": [
            "contrato", "clausula", "acuerdo", "partes", "vigencia", "termino",
            "obligaciones", "condiciones", "firma y sello", "celebran"
        ],
    }

    mejor_tipo = "generico"
    mejor_puntaje = 0

    # Dar mayor peso a palabras clave que identifican documentos específicos
    for tipo, keywords in palabras_clave.items():
        puntaje = sum(1 for kw in keywords if kw in texto_normalizado)

        # Reglas fuertes: si aparece el nombre del tipo, sube la confianza significativamente
        if tipo.replace("_", " ") in texto_normalizado:
            puntaje += 3

        if puntaje > mejor_puntaje:
            mejor_tipo = tipo
            mejor_puntaje = puntaje

    # Penalizar señales de CV cuando aparecen patrones más propios de pagos/facturación.
    if mejor_tipo == "cv_hoja_vida":
        señales_pago = [
            "transaccion", "factura", "total pagado", "medio de pago", "numero de orden",
            "iva", "nit", "payu", "pagosonline", "tecnipagos", "tarjeta", "visa",
        ]
        if sum(1 for señal in señales_pago if señal in texto_normalizado) >= 2:
            mejor_tipo = "factura"
            mejor_puntaje += 2

    logger.info(f"Clasificación | tipo={mejor_tipo} | puntaje={mejor_puntaje}")

    # Si no hay señales suficientes, mantener genérico.
    if mejor_puntaje == 0:
        return "generico"

    return mejor_tipo
    

def _normalizar_texto(texto: str) -> str:
    """Convierte el texto a una forma simple y comparable para OCR ruidoso."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto