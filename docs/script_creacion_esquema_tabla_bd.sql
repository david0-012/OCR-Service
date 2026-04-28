-- Crear schema si no existe
CREATE SCHEMA IF NOT EXISTS public;

-- Tabla
CREATE TABLE IF NOT EXISTS public.documentos (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    estado VARCHAR(20),
    texto_extraido TEXT,
    datos_procesados JSON,
    fecha_creacion TIMESTAMP
);

-- Índice
CREATE INDEX IF NOT EXISTS ix_documentos_id 
ON public.documentos (id);