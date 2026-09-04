$ErrorActionPreference = "Stop"
$required = @("AUTH_DATABASE_URL", "CATALOG_DATABASE_URL", "LOANS_DATABASE_URL", "FINES_DATABASE_URL", "CRONJOBS_DATABASE_URL")
foreach ($name in $required) {
  if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
    throw "Falta la variable temporal $name. No use un archivo .env versionado."
  }
}

$backend = Resolve-Path (Join-Path $PSScriptRoot "..\..\P4\Backend")
$cronjobsMigration = Resolve-Path (Join-Path $PSScriptRoot "..\database\cronjobs_init.sql")
$migrations = @(
  @{Url=$env:AUTH_DATABASE_URL; File=(Join-Path $backend "autenticacion-ms\migrations\001_init.sql")},
  @{Url=$env:CATALOG_DATABASE_URL; File=(Join-Path $backend "catalogo-ms\migrations\001_init.sql")},
  @{Url=$env:LOANS_DATABASE_URL; File=(Join-Path $backend "prestamos-ms\migrations\001_init.sql")},
  @{Url=$env:FINES_DATABASE_URL; File=(Join-Path $backend "multas-ms\migrations\001_init.sql")},
  @{Url=$env:CRONJOBS_DATABASE_URL; File=$cronjobsMigration}
)
foreach ($migration in $migrations) {
  psql $migration.Url -v ON_ERROR_STOP=1 -f $migration.File
}
