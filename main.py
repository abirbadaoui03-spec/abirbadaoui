import logging

from ingestion import read
from processing import extract_transform
from storage import database
from serving import dashboard

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s : %(message)s",
)

if __name__ == "__main__":
    rows = read.ingest("./data")
    events = [e for e in map(extract_transform.extract, rows) if e]

    database.init_db()
    database.save_events(events)
    stored = database.load_events()

    result = dashboard.build_dashboard(stored)
    dashboard.show(result)
    dashboard.show_graphs(result)