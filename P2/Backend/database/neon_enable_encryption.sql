-- Ejecutar en NeonDB si la tabla usuarios ya fue creada.
-- No elimina usuarios: se detiene si encuentra alguno porque las claves de
-- cifrado pertenecen al backend y no deben copiarse al editor SQL.

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM usuarios LIMIT 1) THEN
        RAISE EXCEPTION
            'La tabla usuarios contiene datos. Respaldelos o elimine solo las cuentas de prueba antes de migrar.';
    END IF;
END;
$$;

ALTER TABLE usuarios
    DROP CONSTRAINT IF EXISTS uq_usuarios_correo,
    DROP CONSTRAINT IF EXISTS ck_usuarios_nombre,
    DROP CONSTRAINT IF EXISTS ck_usuarios_apellido,
    DROP CONSTRAINT IF EXISTS ck_usuarios_correo;

ALTER TABLE usuarios
    ALTER COLUMN nombre TYPE TEXT,
    ALTER COLUMN apellido TYPE TEXT,
    ALTER COLUMN correo TYPE TEXT,
    ADD COLUMN IF NOT EXISTS correo_hash CHAR(64);

ALTER TABLE usuarios
    ALTER COLUMN correo_hash SET NOT NULL;

ALTER TABLE usuarios
    ADD CONSTRAINT uq_usuarios_correo_hash UNIQUE (correo_hash),
    ADD CONSTRAINT ck_usuarios_correo_hash
        CHECK (correo_hash ~ '^[0-9a-f]{64}$');

COMMIT;
