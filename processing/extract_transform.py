import logging
import re

logger = logging.getLogger(__name__)

HEADER = re.compile(
    r"(?P<month>\w{3})\s+(?P<day>\d{1,2})\s(?P<time>\d{2}:\d{2}:\d{2})\s"
    r"(?P<host>\S+)\s(?P<process>[\w\-]+)(?:\[(?P<pid>\d+)\])?:\s(?P<message>.*)"
)
FAILED = re.compile(
    r"Failed password for (?P<invalid>invalid user )?\s*(?P<user>\S*?)\s+from\s+(?P<ip>[\d.]+)"
)
ACCEPTED = re.compile(
    r"Accepted \w+ for (?P<user>\S+) from (?P<ip>[\d.]+)"
)


def extract(row: str):
    """in: une ligne de log / out: dict de l'événement, ou None si ligne ignorée"""
    try:
        header = HEADER.search(row.strip())
        if not header:
            logger.warning("Ligne mal formatée : %r", row[:80])
            return None

        data = header.groupdict()
        message = data["message"]

        m = FAILED.search(message)
        if m:
            data.update(event="failed", user=m["user"], ip=m["ip"],
                        invalid_user=bool(m["invalid"]))
            return data

        m = ACCEPTED.search(message)
        if m:
            data.update(event="accepted", user=m["user"], ip=m["ip"],
                        invalid_user=False)
            return data

        return None  # ligne valide mais sans intérêt (CRON, Connection closed...)
    except Exception as e:
        logger.error("Erreur inattendue sur %r : %s", row[:80], e)
        return None

if __name__ == "__main__":
    import logging
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ingestion import read

    logging.basicConfig(level=logging.WARNING)
    rows = read.ingest("./data")
    events = [e for e in map(extract, rows) if e]
    print(f"Lignes lues : {len(rows)}")
    print(f"Événements retenus : {len(events)}")
    print(f"  failed   : {sum(e['event'] == 'failed' for e in events)}")
    print(f"  accepted : {sum(e['event'] == 'accepted' for e in events)}")
    for e in events[:3]:
        print(e["event"], e["user"], e["ip"], e["invalid_user"])