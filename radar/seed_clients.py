"""
Seed the database with a sample client list.
Replace with your actual client data or import from a CSV.
"""
from radar import db
from radar.models import Client

SAMPLE_CLIENTS = [
    Client(0, "Microsoft", ticker="MSFT", domain="microsoft.com", industry="Technology", relationship_partner="Partner A"),
    Client(0, "Amazon", ticker="AMZN", domain="amazon.com", industry="Technology / Retail", relationship_partner="Partner B"),
    Client(0, "Boeing", ticker="BA", domain="boeing.com", industry="Aerospace & Defense", relationship_partner="Partner C"),
    Client(0, "JPMorgan Chase", ticker="JPM", domain="jpmorganchase.com", industry="Financial Services", relationship_partner="Partner D"),
    Client(0, "Pfizer", ticker="PFE", domain="pfizer.com", industry="Life Sciences", relationship_partner="Partner E"),
    Client(0, "Salesforce", ticker="CRM", domain="salesforce.com", industry="Technology", relationship_partner="Partner A"),
    Client(0, "Nike", ticker="NKE", domain="nike.com", industry="Consumer / Retail", relationship_partner="Partner F"),
    Client(0, "Starbucks", ticker="SBUX", domain="starbucks.com", industry="Consumer / Hospitality", relationship_partner="Partner G"),
    Client(0, "Goldman Sachs", ticker="GS", domain="goldmansachs.com", industry="Financial Services", relationship_partner="Partner D"),
    Client(0, "Alphabet", ticker="GOOGL", domain="google.com", industry="Technology", relationship_partner="Partner B"),
    # Private companies (no ticker — news-only monitoring)
    Client(0, "SpaceX", domain="spacex.com", industry="Aerospace", relationship_partner="Partner C"),
    Client(0, "Stripe", domain="stripe.com", industry="Fintech", relationship_partner="Partner D"),
    Client(0, "OpenAI", domain="openai.com", industry="Technology / AI", relationship_partner="Partner A"),
]


def seed():
    db.init_db()
    for client in SAMPLE_CLIENTS:
        cid = db.upsert_client(client)
        print(f"  Seeded: {client.name} (id={cid})")
    print(f"\nSeeded {len(SAMPLE_CLIENTS)} clients.")


if __name__ == "__main__":
    seed()
