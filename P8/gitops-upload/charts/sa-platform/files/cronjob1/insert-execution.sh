#!/bin/sh
set -eu

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -v student_id="$STUDENT_ID" <<'SQL'
INSERT INTO ejecuciones_cronjob (fecha_ejecucion, carne)
VALUES (CURRENT_TIMESTAMP AT TIME ZONE 'America/Guatemala', :'student_id');
SQL
