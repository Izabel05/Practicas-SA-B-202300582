CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS multas (
    id_multa UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_prestamo UUID NOT NULL UNIQUE,
    id_usuario UUID NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
    fecha_generacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_pago TIMESTAMP WITH TIME ZONE,
    actualizado_en TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_multas_monto CHECK (monto > 0),
    CONSTRAINT ck_multas_estado CHECK (estado IN ('PENDIENTE', 'PAGADA', 'ANULADA')),
    CONSTRAINT ck_multas_pago CHECK (
        (estado = 'PAGADA' AND fecha_pago IS NOT NULL)
        OR (estado <> 'PAGADA' AND fecha_pago IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_multas_usuario ON multas(id_usuario);
CREATE INDEX IF NOT EXISTS idx_multas_estado ON multas(estado);
