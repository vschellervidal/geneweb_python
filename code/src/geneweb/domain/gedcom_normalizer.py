"""Module de normalisation GEDCOM pour les tests de parité.

Ce module fournit des fonctions pour normaliser les fichiers GEDCOM afin de permettre
des comparaisons stables entre les sorties OCaml et Python.
"""

from __future__ import annotations

from pathlib import Path


def normalize_gedcom_content(content: str) -> str:
    """Normalise le contenu GEDCOM pour les comparaisons.

    Args:
        content: Contenu GEDCOM brut

    Returns:
        Contenu GEDCOM normalisé
    """
    lines = content.splitlines()
    normalized_lines = []

    for line in lines:
        # Supprimer les espaces en fin de ligne
        line = line.rstrip()

        # Ignorer les lignes vides
        if not line.strip():
            continue

        normalized_lines.append(line)

    # Normaliser l'ordre des champs HEAD
    normalized_lines = _normalize_head_order(normalized_lines)

    return "\n".join(normalized_lines) + "\n"


def normalize_gedcom_file(input_path: Path, output_path: Path) -> None:
    """Normalise un fichier GEDCOM et le sauvegarde.

    Args:
        input_path: Chemin vers le fichier GEDCOM d'entrée
        output_path: Chemin vers le fichier GEDCOM normalisé de sortie
    """
    content = input_path.read_text(encoding="utf-8", errors="ignore")
    normalized_content = normalize_gedcom_content(content)

    # Créer le répertoire parent si nécessaire
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sauvegarder le contenu normalisé
    output_path.write_text(normalized_content, encoding="utf-8")


def _normalize_head_order(lines: list[str]) -> list[str]:
    """Normalise l'ordre des champs dans la section HEAD.

    Args:
        lines: Lignes GEDCOM

    Returns:
        Lignes avec ordre HEAD normalisé
    """
    if not lines or not lines[0].startswith("0 HEAD"):
        return lines

    # Trouver la section HEAD
    head_start = 0
    head_end = len(lines)

    for i, line in enumerate(lines[1:], 1):
        if line.startswith("0 "):
            head_end = i
            break

    # Extraire et réorganiser les champs HEAD
    head_lines = lines[head_start:head_end]
    head_line = head_lines[0]  # "0 HEAD"
    head_fields = head_lines[1:]  # Champs 1 CHAR, 1 SOUR, etc.

    # Ordre préféré pour les champs HEAD
    preferred_order = [
        "1 CHAR",
        "1 SOUR",
        "1 SUBM",
        "1 DEST",
        "1 DATE",
        "1 FILE",
        "1 GEDC",
        "1 LANG",
        "1 PLAC",
        "1 NOTE",
    ]

    # Réorganiser selon l'ordre préféré
    ordered_fields = []
    remaining_fields = head_fields.copy()

    for pattern in preferred_order:
        for field in remaining_fields[:]:
            if field.startswith(pattern):
                ordered_fields.append(field)
                remaining_fields.remove(field)

    # Ajouter les champs restants non reconnus
    ordered_fields.extend(remaining_fields)

    # Reconstruire les lignes
    result = lines[:head_start]
    result.append(head_line)
    result.extend(ordered_fields)
    result.extend(lines[head_end:])

    return result


def compare_gedcom_files(file1: Path, file2: Path) -> tuple[bool, str]:
    """Compare deux fichiers GEDCOM normalisés.

    Args:
        file1: Premier fichier GEDCOM
        file2: Deuxième fichier GEDCOM

    Returns:
        Tuple (sont_identiques, message_diff)
    """
    try:
        content1 = normalize_gedcom_content(file1.read_text(encoding="utf-8", errors="ignore"))
        content2 = normalize_gedcom_content(file2.read_text(encoding="utf-8", errors="ignore"))

        if content1 == content2:
            return True, "Les fichiers GEDCOM sont identiques"
        else:
            # Générer un diff simple
            lines1 = content1.splitlines()
            lines2 = content2.splitlines()

            diff_lines = []
            max_lines = max(len(lines1), len(lines2))

            for i in range(max_lines):
                line1 = lines1[i] if i < len(lines1) else "<MANQUANT>"
                line2 = lines2[i] if i < len(lines2) else "<MANQUANT>"

                if line1 != line2:
                    diff_lines.append(f"Ligne {i+1}:")
                    diff_lines.append(f"  - {line1}")
                    diff_lines.append(f"  + {line2}")

            return False, "\n".join(diff_lines)

    except Exception as e:
        return False, f"Erreur lors de la comparaison: {e}"
