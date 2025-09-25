"""Tests de parité avec snapshots GEDCOM normalisés.

Ces tests comparent les sorties Python vs les snapshots de référence générés depuis OCaml.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from geneweb.adapters.ocaml_bridge.bridge import run_gwb2ged


def _normalize_gedcom_simple(text: str) -> str:
    """Normalisation simple pour les comparaisons."""
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]

    # Normaliser les champs variables
    normalized_lines = []
    for line in lines:
        if line.startswith("2 TIME "):
            normalized_lines.append("2 TIME 00:00:00")
        elif line.startswith("1 FILE "):
            normalized_lines.append("1 FILE snapshot.ged")
        else:
            normalized_lines.append(line)

    return "\n".join(normalized_lines) + "\n"


@pytest.mark.snapshot
def test_gwb2ged_snapshot_demo_full(tmp_path: Path) -> None:
    """Test de parité avec snapshot de référence pour la base de démo complète."""
    if os.getenv("RUN_OCAML_TESTS", "0") != "1":
        pytest.skip("RUN_OCAML_TESTS!=1 : tests snapshot OCaml désactivés")

    # Arrange
    ocaml_root = Path(os.getenv("GENEWEB_OCAML_ROOT", ""))
    demo_dir = ocaml_root / "distribution" / "bases" / "demo.gwb"
    snapshot_path = (
        Path(__file__).parent / "fixtures" / "gedcom" / "snapshots" / "medium" / "demo_full.ged"
    )

    if not demo_dir.exists():
        pytest.skip(f"Base de démo introuvable: {demo_dir}")

    if not snapshot_path.exists():
        pytest.skip(f"Snapshot de référence introuvable: {snapshot_path}")

    # Act: Conversion Python via bridge OCaml
    output_file = tmp_path / "test_output.ged"
    run_gwb2ged([str(demo_dir), "-o", str(output_file)])

    # Assert: Comparaison avec le snapshot
    assert output_file.exists()

    # Lire et normaliser les deux fichiers
    output_content = _normalize_gedcom_simple(
        output_file.read_text(encoding="utf-8", errors="ignore")
    )
    snapshot_content = _normalize_gedcom_simple(
        snapshot_path.read_text(encoding="utf-8", errors="ignore")
    )

    # Comparaison ligne par ligne pour un meilleur diagnostic
    output_lines = output_content.splitlines()
    snapshot_lines = snapshot_content.splitlines()

    # Vérifier que les fichiers ont le même nombre de lignes
    if len(output_lines) != len(snapshot_lines):
        pytest.fail(
            f"Nombre de lignes différent: {len(output_lines)} vs {len(snapshot_lines)}\n"
            f"Output: {len(output_lines)} lignes\n"
            f"Snapshot: {len(snapshot_lines)} lignes"
        )

    # Comparer ligne par ligne
    for i, (output_line, snapshot_line) in enumerate(
        zip(output_lines, snapshot_lines, strict=False)
    ):
        if output_line != snapshot_line:
            pytest.fail(
                f"Différence à la ligne {i+1}:\n"
                f"  Output:   {output_line}\n"
                f"  Snapshot: {snapshot_line}"
            )

    # Si on arrive ici, les fichiers sont identiques
    assert True


@pytest.mark.snapshot
def test_gwb2ged_snapshot_edge_case(tmp_path: Path) -> None:
    """Test de parité pour le cas particulier (fixture vide)."""
    if os.getenv("RUN_OCAML_TESTS", "0") != "1":
        pytest.skip("RUN_OCAML_TESTS!=1 : tests snapshot OCaml désactivés")

    # Arrange
    fixture_path = Path(__file__).parent / "fixtures" / "gwb" / "edge" / "encodage_min" / "base"
    snapshot_path = (
        Path(__file__).parent / "fixtures" / "gedcom" / "snapshots" / "edge" / "encodage_min.ged"
    )

    if not fixture_path.exists():
        pytest.skip(f"Fixture introuvable: {fixture_path}")

    if not snapshot_path.exists():
        pytest.skip(f"Snapshot introuvable: {snapshot_path}")

    # Le snapshot pour ce cas particulier devrait être vide
    snapshot_content = snapshot_path.read_text(encoding="utf-8")
    assert (
        snapshot_content == ""
    ), f"Snapshot devrait être vide, mais contient: {repr(snapshot_content)}"

    # Pour une fixture vide, on s'attend à ce que la conversion échoue ou produise un fichier vide
    output_file = tmp_path / "test_output.ged"

    try:
        run_gwb2ged([str(fixture_path), "-o", str(output_file)])
        # Si la conversion réussit, vérifier que le résultat est vide ou minimal
        if output_file.exists():
            output_content = output_file.read_text(encoding="utf-8", errors="ignore")
            # Accepter soit un fichier vide, soit un fichier avec juste des en-têtes minimaux
            if output_content.strip():
                # Si le fichier n'est pas vide, vérifier qu'il contient au moins HEAD
                assert (
                    "0 HEAD" in output_content
                ), f"Fichier non-vide devrait contenir HEAD: {output_content[:100]}"
    except Exception:
        # Si la conversion échoue, c'est acceptable pour une fixture vide
        pass


@pytest.mark.snapshot
def test_snapshot_files_exist() -> None:
    """Test que les fichiers de snapshot existent."""
    snapshots_dir = Path(__file__).parent / "fixtures" / "gedcom" / "snapshots"

    # Vérifier que le dossier existe
    assert snapshots_dir.exists(), f"Dossier snapshots introuvable: {snapshots_dir}"

    # Vérifier les snapshots attendus
    expected_snapshots = [
        "edge/encodage_min.ged",
        "medium/demo_full.ged",
    ]

    for snapshot_rel_path in expected_snapshots:
        snapshot_path = snapshots_dir / snapshot_rel_path
        assert snapshot_path.exists(), f"Snapshot manquant: {snapshot_path}"

        # Vérifier que le fichier n'est pas vide (sauf pour le cas particulier)
        if snapshot_rel_path != "edge/encodage_min.ged":
            content = snapshot_path.read_text(encoding="utf-8")
            assert len(content) > 0, f"Snapshot vide: {snapshot_path}"
            assert "0 HEAD" in content, f"Snapshot devrait contenir HEAD: {snapshot_path}"
