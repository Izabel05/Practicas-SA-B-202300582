"""Valida la distribucion minima de pruebas requerida para la Practica 7."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNIT_MINIMUM = 70.0
INTEGRATION_MINIMUM = 20.0

UNIT_PATTERNS = (
    "P4/Backend/*/internal/service/*_test.go",
    "P4/Backend/*/tests/test_*_service.py",
)
INTEGRATION_PATTERNS = (
    "P4/Backend/*/internal/controller/*_test.go",
    "P4/Backend/*/tests/test_api.py",
    "P4/Backend/*/tests/test_graphql.py",
)


def python_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def go_tests(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    return len(re.findall(r"(?m)^func\s+Test[A-Za-z0-9_]*\s*\(", source))


def count(patterns: tuple[str, ...]) -> tuple[int, list[Path]]:
    files = sorted({path for pattern in patterns for path in ROOT.glob(pattern)})
    total = sum(python_tests(path) if path.suffix == ".py" else go_tests(path) for path in files)
    return total, files


def main() -> int:
    unit, unit_files = count(UNIT_PATTERNS)
    integration, integration_files = count(INTEGRATION_PATTERNS)
    total = unit + integration
    if total == 0:
        print("No se encontraron pruebas clasificadas.", file=sys.stderr)
        return 1

    unit_percentage = unit * 100 / total
    integration_percentage = integration * 100 / total

    print(f"Pruebas unitarias: {unit}/{total} ({unit_percentage:.1f}%)")
    print(f"Pruebas de integracion: {integration}/{total} ({integration_percentage:.1f}%)")
    print(f"Archivos unitarios: {len(unit_files)}; archivos de integracion: {len(integration_files)}")

    errors: list[str] = []
    if unit_percentage < UNIT_MINIMUM:
        errors.append(f"unitarias {unit_percentage:.1f}% < {UNIT_MINIMUM:.0f}%")
    if integration_percentage < INTEGRATION_MINIMUM:
        errors.append(f"integracion {integration_percentage:.1f}% < {INTEGRATION_MINIMUM:.0f}%")

    if errors:
        print("Distribucion invalida: " + ", ".join(errors), file=sys.stderr)
        return 1

    print("Distribucion 70/20 validada correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
