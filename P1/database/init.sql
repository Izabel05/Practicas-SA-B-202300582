CREATE TABLE solicitudes (
    id INTEGER GENERATED ALWAYS AS IDENTITY,

    titulo VARCHAR(150) NOT NULL,

    area_solicitante VARCHAR(100) NOT NULL,

    prioridad SMALLINT NOT NULL,

    costo_estimado NUMERIC(12, 2) NOT NULL DEFAULT 0.00,

    estado VARCHAR(20) NOT NULL DEFAULT 'registrada',

    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_solicitudes
        PRIMARY KEY (id),

    CONSTRAINT chk_solicitudes_titulo
        CHECK (LENGTH(TRIM(titulo)) >= 3),

    CONSTRAINT chk_solicitudes_area
        CHECK (LENGTH(TRIM(area_solicitante)) >= 2),

    CONSTRAINT chk_solicitudes_prioridad
        CHECK (prioridad BETWEEN 1 AND 5),

    CONSTRAINT chk_solicitudes_costo
        CHECK (costo_estimado >= 0),

    CONSTRAINT chk_solicitudes_estado
        CHECK (
            estado IN (
                'registrada',
                'en_proceso',
                'finalizada',
                'cancelada'
            )
        )
);