import json
import logging
from collections import Counter
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

CACHE_PATH = Path(__file__).resolve().parent.parent / "storage" / "countries.json"
API_URL = "https://ipinfo.io/{address}/json"
MAX_ERRORS = 5          # on arrête si l'API échoue plusieurs fois de suite
MAX_NEW_PER_RUN = 300   # nombre maximum de nouvelles IP interrogées par lancement


def is_private(ip: str) -> bool:
    """Vrai pour les adresses du réseau interne (10.x, 127.x, 192.168.x, 172.16-31.x)."""
    try:
        a, b = (int(x) for x in ip.split(".")[:2])
    except ValueError:
        return False
    return a in (10, 127) or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31)


def _load_cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Cache illisible : %s", e)
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        logger.error("Impossible d'écrire le cache : %s", e)


def get_country(ip: str) -> str:
    """Interroge ipinfo.io pour une IP. Renvoie le code pays ou 'Inconnu'."""
    resp = requests.get(API_URL.format(address=ip), timeout=10)
    resp.raise_for_status()
    return resp.json().get("country", "Inconnu")


def resolve_countries(ips) -> dict:
    """in: IP (avec répétitions) / out: dict {ip: pays}."""
    cache = _load_cache()
    freq = Counter(ips)

    for ip in freq:
        if is_private(ip):
            cache[ip] = "Réseau local"

    # IP pas encore en cache, les plus fréquentes d'abord, limitées à MAX_NEW_PER_RUN
    todo = [ip for ip, _ in freq.most_common() if ip not in cache][:MAX_NEW_PER_RUN]
    logger.info("%d IP au total, %d à interroger ce coup-ci", len(freq), len(todo))

    errors = 0
    for n, ip in enumerate(todo, start=1):
        try:
            cache[ip] = get_country(ip)
            errors = 0
        except (requests.RequestException, ValueError) as e:
            errors += 1
            logger.error("Erreur API pour %s : %s", ip, e)
            if errors >= MAX_ERRORS:
                logger.error("Trop d'erreurs, arrêt des requêtes")
                break
        if n % 10 == 0:
            print(f"Pays : {n}/{len(todo)} IP traitées", flush=True)
        if n % 50 == 0:
            _save_cache(cache)

    _save_cache(cache)
    return {ip: cache.get(ip, "Non résolu") for ip in freq}