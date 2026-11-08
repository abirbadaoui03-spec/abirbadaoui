import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent / "log_analysis.db"


def init_db(path=DB_PATH) -> None:
    """Crée la table events si elle n'existe pas."""
    try:
        with sqlite3.connect(path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month TEXT, day INTEGER, time TEXT,
                    host TEXT, process TEXT,
                    event TEXT, user TEXT, ip TEXT,
                    invalid_user INTEGER
                )"""
            )
        logger.info("Base initialisée : %s", path)
    except sqlite3.Error as e:
        logger.error("Erreur d'initialisation de la base : %s", e)
        raise


def save_events(events: list[dict], path=DB_PATH) -> int:
    """Remplace le contenu de la table par les événements donnés."""
    rows = [
        (e["month"], int(e["day"]), e["time"], e["host"], e["process"],
         e["event"], e["user"], e["ip"], int(e["invalid_user"]))
        for e in events
    ]
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("DELETE FROM events")  # évite les doublons à chaque lancement
            conn.executemany(
                """INSERT INTO events
                   (month, day, time, host, process, event, user, ip, invalid_user)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
        logger.info("%d événements enregistrés dans %s", len(rows), path)
        return len(rows)
    except (sqlite3.Error, KeyError, ValueError) as e:
        logger.error("Erreur d'écriture dans la base : %s", e)
        return 0


def load_events(path=DB_PATH) -> list[dict]:
    """Relit les événements depuis la base."""
    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM events")
            events = [dict(r) for r in cur.fetchall()]
        for e in events:
            e["invalid_user"] = bool(e["invalid_user"])
        logger.info("%d événements lus depuis %s", len(events), path)
        return events
    except sqlite3.Error as e:
        logger.error("Erreur de lecture de la base : %s", e)
        return []