import logging
from collections import Counter

logger = logging.getLogger(__name__)


def is_private(ip: str) -> bool:
    """Vrai pour les adresses du réseau interne (10.x, 192.168.x, 172.16-31.x, 127.x)."""
    try:
        a, b = (int(x) for x in ip.split(".")[:2])
    except ValueError:
        return False
    return a in (10, 127) or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31)


def get_country(ip: str) -> str:
    # À compléter selon la source de pays donnée par ton prof
    if is_private(ip):
        return "Réseau local"
    return "Inconnu"


def build_dashboard(events: list[dict]) -> dict:
    failed_by_country = Counter()
    success_by_user = Counter()
    invalid_user_failed = Counter()

    for e in events:
        if e["event"] == "failed":
            failed_by_country[get_country(e["ip"])] += 1
            if e["invalid_user"]:
                invalid_user_failed[e["user"] or "(vide)"] += 1
        elif e["event"] == "accepted":
            success_by_user[e["user"]] += 1

    logger.info("Dashboard construit à partir de %d événements", len(events))
    return {
        "failed_by_country": failed_by_country,
        "success_by_user": success_by_user,
        "invalid_user_failed": invalid_user_failed,
    }


def show(dashboard: dict) -> None:
    titles = {
        "failed_by_country": "Tentatives échouées par pays",
        "success_by_user": "Tentatives réussies par utilisateur",
        "invalid_user_failed": "Tentatives échouées avec invalid user",
    }
    for key, title in titles.items():
        print(f"\n=== {title} ===")
        for name, count in dashboard[key].most_common(10):
            print(f"{name:<25} {count}")

def show_graphs(dashboard: dict) -> None:
    """Affiche les 3 graphes du dashboard et les sauvegarde en PNG."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        logger.error("matplotlib indisponible : %s", e)
        return

    charts = [
        ("failed_by_country", "Tentatives échouées par pays"),
        ("success_by_user", "Tentatives réussies par utilisateur"),
        ("invalid_user_failed", "Tentatives échouées avec invalid user (top 10)"),
    ]

    fig, axes = plt.subplots(len(charts), 1, figsize=(10, 12))
    for ax, (key, title) in zip(axes, charts):
        items = dashboard[key].most_common(10)
        if not items:
            ax.set_title(f"{title} : aucune donnée")
            continue
        names = [name for name, _ in items]
        counts = [count for _, count in items]
        ax.barh(names, counts)
        ax.invert_yaxis()  # le plus grand en haut
        ax.set_title(title)
        ax.set_xlabel("Nombre de tentatives")

    fig.tight_layout()
    try:
        fig.savefig("dashboard.png")
        logger.info("Graphes sauvegardés dans dashboard.png")
    except OSError as e:
        logger.error("Impossible de sauvegarder le graphe : %s", e)
    plt.show()