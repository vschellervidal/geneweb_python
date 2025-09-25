#!/usr/bin/env python3
"""Script pour générer les snapshots GEDCOM de référence depuis OCaml.

Ce script utilise le bridge OCaml pour convertir toutes les fixtures GWB
en fichiers GEDCOM normalisés qui serviront de référence pour les tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ajouter le src au path pour les imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from geneweb.adapters.ocaml_bridge.bridge import run_gwb2ged
from geneweb.domain.gedcom_normalizer import normalize_gedcom_file


def main() -> None:
    """Génère tous les snapshots GEDCOM de référence."""
    # Vérifier que GENEWEB_OCAML_ROOT est défini
    ocaml_root = os.getenv("GENEWEB_OCAML_ROOT")
    if not ocaml_root:
        print("❌ GENEWEB_OCAML_ROOT non défini")
        print("   Exportez cette variable vers votre installation OCaml compilée")
        sys.exit(1)

    ocaml_root_path = Path(ocaml_root)
    if not ocaml_root_path.exists():
        print(f"❌ GENEWEB_OCAML_ROOT pointe vers un chemin inexistant: {ocaml_root}")
        sys.exit(1)

    print(f"✅ Utilisation de GENEWEB_OCAML_ROOT: {ocaml_root}")

    # Chemins des fixtures et snapshots
    fixtures_root = project_root / "tests" / "fixtures" / "gwb"
    snapshots_root = project_root / "tests" / "fixtures" / "gedcom" / "snapshots"

    # Mapping des fixtures vers les snapshots
    fixtures_mapping = [
        ("small/demo_min", "small/demo_min.ged"),
        ("medium/demo_copy", "medium/demo_copy.ged"),
        ("edge/encodage_min", "edge/encodage_min.ged"),
    ]

    print(f"📁 Fixtures: {fixtures_root}")
    print(f"📁 Snapshots: {snapshots_root}")
    print()

    success_count = 0
    total_count = len(fixtures_mapping)

    for fixture_rel_path, snapshot_rel_path in fixtures_mapping:
        fixture_path = fixtures_root / fixture_rel_path / "base"
        snapshot_path = snapshots_root / snapshot_rel_path

        print(f"🔄 Traitement: {fixture_rel_path}")

        # Vérifier que la fixture existe
        if not fixture_path.exists():
            print(f"   ⚠️  Fixture introuvable: {fixture_path}")
            continue

        # Vérifier la taille de la fixture
        fixture_size = fixture_path.stat().st_size
        if fixture_size == 0:
            print(f"   ⚠️  Fixture vide (0 bytes): {fixture_path}")
            # Créer un snapshot vide pour les cas particuliers
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text("", encoding="utf-8")
            print(f"   ✅ Snapshot vide créé: {snapshot_path}")
            success_count += 1
            continue

        try:
            # Créer un fichier temporaire pour la conversion
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)

            # Convertir GWB → GEDCOM via OCaml
            print(f"   🔄 Conversion OCaml: {fixture_path} → {tmp_path}")
            run_gwb2ged([str(fixture_path), "-o", str(tmp_path)])

            # Vérifier que la conversion a réussi
            if not tmp_path.exists() or tmp_path.stat().st_size == 0:
                print("   ❌ Conversion échouée: fichier vide ou inexistant")
                continue

            # Normaliser et sauvegarder le snapshot
            print(f"   🔄 Normalisation: {tmp_path} → {snapshot_path}")
            normalize_gedcom_file(tmp_path, snapshot_path)

            # Nettoyer le fichier temporaire
            tmp_path.unlink()

            # Vérifier le résultat
            snapshot_size = snapshot_path.stat().st_size
            print(f"   ✅ Snapshot créé: {snapshot_path} ({snapshot_size} bytes)")
            success_count += 1

        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            continue

        print()

    # Résumé
    print("=" * 50)
    print(f"📊 Résumé: {success_count}/{total_count} snapshots générés")

    if success_count == total_count:
        print("🎉 Tous les snapshots ont été générés avec succès!")
        print()
        print("📝 Prochaines étapes:")
        print("   1. Vérifier les snapshots générés")
        print("   2. Créer les tests de comparaison")
        print("   3. Valider la parité Python vs OCaml")
    else:
        print(f"⚠️  {total_count - success_count} snapshots n'ont pas pu être générés")
        sys.exit(1)


if __name__ == "__main__":
    main()
