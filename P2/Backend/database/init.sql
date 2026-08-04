-- ============================================================
-- BASE DE DATOS: LOGIN Y REGISTRO
-- MOTOR: PostgreSQL / Neon DB
-- ROLES:
--   ADMIN   -> Ruta 1 y Ruta 2
--   CLIENTE -> Solo Ruta 2
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- 1. Extensiones
-- ------------------------------------------------------------

-- Permite generar UUID seguros mediante gen_random_uuid().
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Permite comparar correos sin diferenciar mayúsculas y minúsculas.
-- Ejemplo: correo@gmail.com = CORREO@gmail.com
CREATE EXTENSION IF NOT EXISTS citext;


-- ------------------------------------------------------------
-- 2. Tabla de roles
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS roles (
    id SMALLINT GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_roles
        PRIMARY KEY (id),

    CONSTRAINT uq_roles_nombre
        UNIQUE (nombre),

    CONSTRAINT ck_roles_nombre
        CHECK (nombre IN ('ADMIN', 'CLIENTE'))
);


-- ------------------------------------------------------------
-- 3. Tabla de usuarios
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID NOT NULL DEFAULT gen_random_uuid(),

    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,

    correo CITEXT NOT NULL,

    -- Aquí se almacena únicamente el hash generado por el backend.
    -- Nunca debe almacenarse la contraseña en texto plano.
    password_hash VARCHAR(255) NOT NULL,

    rol_id SMALLINT NOT NULL,

    activo BOOLEAN NOT NULL DEFAULT TRUE,
    correo_verificado BOOLEAN NOT NULL DEFAULT FALSE,

    ultimo_acceso TIMESTAMPTZ,

    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuarios
        PRIMARY KEY (id),

    CONSTRAINT uq_usuarios_correo
        UNIQUE (correo),

    CONSTRAINT fk_usuarios_roles
        FOREIGN KEY (rol_id)
        REFERENCES roles (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_usuarios_nombre
        CHECK (char_length(trim(nombre)) >= 2),

    CONSTRAINT ck_usuarios_apellido
        CHECK (char_length(trim(apellido)) >= 2),

    CONSTRAINT ck_usuarios_correo
        CHECK (
            correo::TEXT ~*
            '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
        ),

    CONSTRAINT ck_usuarios_password_hash
        CHECK (char_length(password_hash) >= 20)
);


-- ------------------------------------------------------------
-- 4. Índices
-- ------------------------------------------------------------

-- La restricción UNIQUE del correo ya crea su propio índice.
-- Este índice ayuda en consultas y filtros por rol.
CREATE INDEX IF NOT EXISTS idx_usuarios_rol_id
    ON usuarios (rol_id);

-- Ayuda a consultar usuarios activos.
CREATE INDEX IF NOT EXISTS idx_usuarios_activos
    ON usuarios (activo)
    WHERE activo = TRUE;


-- ------------------------------------------------------------
-- 5. Función para actualizar actualizado_en
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.actualizado_en := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


-- ------------------------------------------------------------
-- 6. Trigger de actualización
-- ------------------------------------------------------------

DROP TRIGGER IF EXISTS trg_usuarios_actualizado_en
ON usuarios;

CREATE TRIGGER trg_usuarios_actualizado_en
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION actualizar_fecha_modificacion();


-- ------------------------------------------------------------
-- 7. Insertar roles iniciales
-- ------------------------------------------------------------

INSERT INTO roles (nombre, descripcion)
VALUES
    (
        'ADMIN',
        'Administrador con acceso a todas las rutas del sistema'
    ),
    (
        'CLIENTE',
        'Cliente con acceso únicamente a las rutas autorizadas'
    )
ON CONFLICT (nombre) DO UPDATE
SET descripcion = EXCLUDED.descripcion;


COMMIT;