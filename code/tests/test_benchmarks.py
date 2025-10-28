"""Tests de benchmark pour mesurer les performances de gwb2ged.

Ces tests mesurent le temps d'exécution et la mémoire consommée
pour la conversion GWB → GEDCOM sur différentes fixtures.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from geneweb.adapters.ocaml_bridge.bridge import run_gwb2ged


@pytest.mark.benchmark
def test_benchmark_gwb2ged_demo_full(benchmark) -> None:
    """Benchmark de conversion pour la base de démo complète."""
    if os.getenv("RUN_OCAML_TESTS", "0") != "1":
        pytest.skip("RUN_OCAML_TESTS!=1 : benchmarks OCaml désactivés")

    # Arrange
    ocaml_root = Path(os.getenv("GENEWEB_OCAML_ROOT", ""))
    demo_dir = ocaml_root / "distribution" / "bases" / "demo.gwb"

    if not demo_dir.exists():
        pytest.skip(f"Base de démo introuvable: {demo_dir}")

    # Act & Assert: Benchmark de la conversion
    def convert_demo() -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            run_gwb2ged([str(demo_dir), "-o", tmp_path])
            result = Path(tmp_path).read_bytes()
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    result = benchmark(convert_demo)

    # Vérifier que la conversion produit un résultat valide
    MIN_GEDCOM_SIZE = 100  # Minimum 100 bytes pour un GEDCOM valide
    assert result
    assert b"0 HEAD" in result
    assert len(result) > MIN_GEDCOM_SIZE


@pytest.mark.benchmark
def test_benchmark_gwb2ged_multiple_runs(benchmark) -> None:
    """Benchmark avec plusieurs exécutions pour mesurer la stabilité."""
    if os.getenv("RUN_OCAML_TESTS", "0") != "1":
        pytest.skip("RUN_OCAML_TESTS!=1 : benchmarks OCaml désactivés")

    # Arrange
    ocaml_root = Path(os.getenv("GENEWEB_OCAML_ROOT", ""))
    demo_dir = ocaml_root / "distribution" / "bases" / "demo.gwb"

    if not demo_dir.exists():
        pytest.skip(f"Base de démo introuvable: {demo_dir}")

    # Act & Assert: Benchmark avec plusieurs exécutions
    def convert_demo() -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            run_gwb2ged([str(demo_dir), "-o", tmp_path])
            result = Path(tmp_path).read_bytes()
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    result = benchmark.pedantic(convert_demo, iterations=5, rounds=3)

    # Vérifier que la conversion produit un résultat valide
    assert result
    assert b"0 HEAD" in result


@pytest.mark.benchmark
class TestBenchmarkSeuils:
    """Tests de seuils de performance pour détecter les régressions."""

    def test_gwb2ged_should_complete_in_under_5_seconds(self, benchmark) -> None:
        """Test que la conversion de la démo complète se termine en moins de 5 secondes."""
        if os.getenv("RUN_OCAML_TESTS", "0") != "1":
            pytest.skip("RUN_OCAML_TESTS!=1 : benchmarks OCaml désactivés")

        # Arrange
        ocaml_root = Path(os.getenv("GENEWEB_OCAML_ROOT", ""))
        demo_dir = ocaml_root / "distribution" / "bases" / "demo.gwb"

        if not demo_dir.exists():
            pytest.skip(f" failure démo introuvable: {demo_dir}")

        # Act & Assert: Seuil de performance
        def convert_demo() -> bytes:
            with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                run_gwb2ged([str(demo_dir), "-o", tmp_path])
                result = Path(tmp_path).read_bytes()
                return result
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        benchmark(convert_demo)

        # Assert: Le temps moyen doit être sous le seuil
        MAX_CONVERSION_TIME = 5.0  # 5 secondes maximum
        assert (
            benchmark.stats["mean"] < MAX_CONVERSION_TIME
        ), f"Conversion trop lente: {benchmark.stats['mean']:.2f}s > {MAX_CONVERSION_TIME}s"
