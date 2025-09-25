# Snapshots GEDCOM Normalisés

Ce dossier contient les snapshots GEDCOM de référence générés depuis OCaml pour les tests de parité.

## Structure

```
snapshots/
├── small/          # Snapshots pour fixtures petites
├── medium/         # Snapshots pour fixtures moyennes
├── edge/           # Snapshots pour cas particuliers
└── README.md       # Ce fichier
```

## Correspondance avec les fixtures GWB

- `small/demo_min.ged` ← `gwb/small/demo_min/base`
- `medium/demo_copy.ged` ← `gwb/medium/demo_copy/base`
- `edge/encodage_min.ged` ← `gwb/edge/encodage_min/base`

## Normalisation

Les snapshots sont normalisés pour permettre des comparaisons stables :
- Espaces en fin de ligne supprimés
- Lignes vides ignorées
- Ordre des champs HEAD normalisé
- Encodage UTF-8 uniforme

## Génération

Les snapshots sont générés automatiquement par le script `tools/generate_snapshots.py` en utilisant le bridge OCaml.

## Utilisation

Ces snapshots servent de référence pour les tests de parité Python vs OCaml dans `tests/test_snapshot_parity.py`.
