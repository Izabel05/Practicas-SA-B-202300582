"""Actualiza de forma atomica las etiquetas de imagen del repositorio GitOps."""

from __future__ import annotations

import re
import sys
from pathlib import Path


IMAGES = (
    "api-gateway",
    "autenticacion-ms",
    "catalogo-ms",
    "prestamos-ms",
    "multas-ms",
    "cronjobs-worker",
)


def main() -> int:
    if len(sys.argv) != 3:
        print("uso: update-gitops.py <images.yaml> <version>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    version = sys.argv[2]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
        raise ValueError(f"version semantica invalida: {version}")
    content = path.read_text(encoding="utf-8")
    for image in IMAGES:
        pattern = rf"(?ms)^({re.escape(image)}:\s*\n(?:(?!^[A-Za-z0-9_-]+:).)*?^\s+tag:\s*)[^\n]+$"
        content, count = re.subn(pattern, rf"\g<1>{version}", content)
        if count != 1:
            raise ValueError(f"no se encontro exactamente una entrada para {image}")
    path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
