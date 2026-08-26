CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS prestamos (
    id_prestamo UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario UUID NOT NULL,
    fecha_prestamo TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_limite TIMESTAMP WITH TIME ZONE NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_prestamos_estado CHECK (estado IN ('ACTIVO', 'COMPLETADO', 'VENCIDO')),
    CONSTRAINT ck_prestamos_fechas CHECK (fecha_limite > fecha_prestamo)
);

CREATE TABLE IF NOT EXISTS detalle_prestamo (
    id_detalle UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_prestamo UUID NOT NULL REFERENCES prestamos(id_prestamo) ON DELETE CASCADE,
    id_ejemplar UUID NOT NULL,
    fecha_devolucion TIMESTAMP WITH TIME ZONE,
    estado VARCHAR(50) NOT NULL DEFAULT 'PRESTADO',
    CONSTRAINT ck_detalle_estado CHECK (estado IN ('PRESTADO', 'DEVUELTO', 'VENCIDO'))
);

CREATE INDEX IF NOT EXISTS idx_prestamos_usuario ON prestamos(id_usuario);
CREATE INDEX IF NOT EXISTS idx_detalle_prestamo ON detalle_prestamo(id_prestamo);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ejemplar_prestamo_activo
    ON detalle_prestamo(id_ejemplar)
    WHERE estado IN ('PRESTADO', 'VENCIDO');
