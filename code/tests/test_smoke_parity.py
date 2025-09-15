from __future__ import annotations

import os
from pathlib import Path

import pytest
from geneweb.adapters.ocaml_bridge.bridge import run_gwb2ged


@pytest.mark.smoke
def test_gwb2ged_smoke_demo(tmp_path: Path) -> None:
    if os.getenv("RUN_OCAML_TESTS", "0") != "1":
        pytest.skip("RUN_OCAML_TESTS!=1 : tests smoke OCaml désactivés")
    # Arrange: local OCaml repo path
    ocaml_root = Path(
        os.getenv(
            "GENEWEB_OCAML_ROOT",
            "/Users/valentin/Desktop/tek5/piscine/legacy/geneweb_python/geneweb",
        )
    )
    demo_dir = ocaml_root / "distribution" / "demo.gwb"
    if not demo_dir.exists():
        pytest.skip(
            f"Répertoire demo introuvable: {demo_dir}. Exportez GENEWEB_OCAML_ROOT si besoin."
        )

    out_file = tmp_path / "demo.ged"

    # Act
    run_gwb2ged(["-i", str(demo_dir), "-o", str(out_file)])

    # Assert
    assert out_file.exists()
    # Basic sanity: GEDCOM starts with HEAD
    head = out_file.read_text(encoding="utf-8", errors="ignore").splitlines()[:5]
    assert any("0 HEAD" in line for line in head)
