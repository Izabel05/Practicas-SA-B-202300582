"""Valida la seleccion de nueve pruebas ejecutada por el pipeline de P7."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNIT_MINIMUM = 70.0
INTEGRATION_MINIMUM = 20.0

# Siete pruebas unitarias: dos de autenticacion, dos de catalogo, dos de
# prestamos y una de multas.
UNIT_TESTS = (
    ("P4/Backend/autenticacion-ms/internal/service/auth_service_test.go", "TestRegisterCreatesReaderAndReturnsToken"),
    ("P4/Backend/autenticacion-ms/internal/service/auth_service_test.go", "TestLoginRejectsInactiveUser"),
    ("P4/Backend/catalogo-ms/internal/service/catalog_service_test.go", "TestCreateCategoryTrimsInput"),
    ("P4/Backend/catalogo-ms/internal/service/catalog_service_test.go", "TestUpdateCopyStatusNormalizesValue"),
    ("P4/Backend/prestamos-ms/tests/test_loan_service.py", "test_create_loan_reserves_copy"),
    ("P4/Backend/prestamos-ms/tests/test_loan_service.py", "test_return_copy_releases_catalog_copy"),
    ("P4/Backend/multas-ms/tests/test_fine_service.py", "test_calculates_amount_by_overdue_days"),
)

# Dos pruebas de integracion: endpoint HTTP de autenticacion y endpoint
# GraphQL de prestamos.
INTEGRATION_TESTS = (
    ("P4/Backend/autenticacion-ms/internal/controller/auth_controller_test.go", "TestRegisterEndpoint"),
    ("P4/Backend/prestamos-ms/tests/test_graphql.py", "test_query_loan"),
)


def validate_test(path_text: str, test_name: str) -> str | None:
    path = ROOT / path_text
    if not path.is_file():
        return f"No existe {path_text}"
    if test_name not in path.read_text(encoding="utf-8"):
        return f"No existe {test_name} en {path_text}"
    return None


def main() -> int:
    errors = [
        error
        for path, test_name in UNIT_TESTS + INTEGRATION_TESTS
        if (error := validate_test(path, test_name)) is not None
    ]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    unit = len(UNIT_TESTS)
    integration = len(INTEGRATION_TESTS)
    total = unit + integration
    unit_percentage = unit * 100 / total
    integration_percentage = integration * 100 / total

    print(f"Pruebas seleccionadas: {total}")
    print(f"Pruebas unitarias: {unit}/{total} ({unit_percentage:.1f}%)")
    print(f"Pruebas de integracion: {integration}/{total} ({integration_percentage:.1f}%)")

    if unit_percentage < UNIT_MINIMUM or integration_percentage < INTEGRATION_MINIMUM:
        print("La seleccion no cumple los minimos 70/20.", file=sys.stderr)
        return 1

    print("Seleccion de 7 pruebas unitarias y 2 de integracion validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
