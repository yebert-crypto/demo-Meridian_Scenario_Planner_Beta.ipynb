"""
Import clients from a CSV file.

CSV format (columns, any order):
    name, ticker, domain, industry, relationship_partner, notes

Usage:
    python import_clients.py clients.csv
"""
import csv
import sys
from radar import db
from radar.models import Client


def import_csv(path: str):
    db.init_db()
    imported = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            client = Client(
                id=0,
                name=row["name"].strip(),
                ticker=row.get("ticker", "").strip() or None,
                domain=row.get("domain", "").strip() or None,
                industry=row.get("industry", "").strip() or None,
                relationship_partner=row.get("relationship_partner", "").strip() or None,
                notes=row.get("notes", "").strip() or None,
            )
            db.upsert_client(client)
            imported += 1
            print(f"  Imported: {client.name}")
    print(f"\nImported {imported} clients from {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_clients.py <clients.csv>")
        sys.exit(1)
    import_csv(sys.argv[1])
