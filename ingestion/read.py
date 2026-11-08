import gzip
import logging
import os

logger = logging.getLogger(__name__)


def ingest(path: str) -> list[str]:
    """in: dossier de logs / out: liste de toutes les lignes de tous les fichiers"""
    rows = []

    try:
        files = sorted(os.listdir(path))
    except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
        logger.error("Dossier illisible %s : %s", path, e)
        return rows

    for file in files:
        file_path = os.path.join(path, file)
        if not os.path.isfile(file_path):
            continue
        try:
            if file.endswith(".gz"):
                f = gzip.open(file_path, mode="rt", encoding="utf-8")
            else:
                f = open(file_path, mode="r", encoding="utf-8")
            with f:
                lines = f.readlines()
            if not lines:
                logger.warning("Fichier vide : %s", file_path)
            rows.extend(lines)
            logger.info("%s : %d lignes lues", file_path, len(lines))
        except (OSError, UnicodeDecodeError) as e:
            logger.error("Erreur de lecture sur %s : %s", file_path, e)

    return rows

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)  # affiche les logs dans le terminal

    rows = ingest("./data")
    print(f"Nombre total de lignes : {len(rows)}")
    print("Premières lignes :")
    for r in rows[:3]:
        print(r.strip())
    print("Dernière ligne :")
    print(rows[-1].strip() if rows else "aucune")