import logging
import os

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

logger = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "log_analysis"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def init_db() -> None:
    """Crée la table events si elle n'existe pas."""
    conn = None
    try:
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    month TEXT, day INTEGER, time TEXT,
                    host TEXT, process TEXT,
                    event TEXT, "user" TEXT, ip TEXT,
                    invalid_user BOOLEAN
                )"""
            )
        logger.info("Table events prête dans PostgreSQL")
    except psycopg2.Error as e:
        logger.error("Erreur d'initialisation PostgreSQL : %s", e)
        raise
    finally:
        if conn:
            conn.close()


def save_events(events: list[dict]) -> int:
    """Remplace le contenu de la table par les événements donnés."""
    rows = [
        (e["month"], int(e["day"]), e["time"], e["host"], e["process"],
         e["event"], e["user"], e["ip"], bool(e["invalid_user"]))
        for e in events
    ]
    conn = None
    try:
        conn = get_conn()
        with conn, conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE events RESTART IDENTITY")
            execute_values(
                cur,
                """INSERT INTO events
                   (month, day, time, host, process, event, "user", ip, invalid_user)
                   VALUES %s""",
                rows,
            )
        logger.info("%d événements enregistrés dans PostgreSQL", len(rows))
        return len(rows)
    except (psycopg2.Error, KeyError, ValueError) as e:
        logger.error("Erreur d'écriture PostgreSQL : %s", e)
        return 0
    finally:
        if conn:
            conn.close()


def load_events() -> list[dict]:
    """Relit les événements depuis la base."""
    conn = None
    try:
        conn = get_conn()
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM events")
            events = [dict(r) for r in cur.fetchall()]
        logger.info("%d événements lus depuis PostgreSQL", len(events))
        return events
    except psycopg2.Error as e:
        logger.error("Erreur de lecture PostgreSQL : %s", e)
        return []
    finally:
        if conn:
            conn.close()