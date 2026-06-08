"""Seed realistic demo signals for dashboard development and demos."""
from datetime import datetime, timedelta
from meridian import db
from meridian.models import Signal, SignalType

def seed_demo_signals():
    db.init_db()
    clients = {c.name: c for c in db.get_clients()}

    def dt(days_ago: int) -> datetime:
        return datetime.utcnow() - timedelta(days=days_ago)

    demo_signals = [
        # GC Changes — highest priority
        Signal(None, clients["Microsoft"].id, "Microsoft", SignalType.GC_CHANGE,
               "Microsoft names new General Counsel — Dev Stahlkopf departs",
               "Microsoft Corporation announced that Dev Stahlkopf will step down as General Counsel and EVP effective Q3. Search for successor underway. New GC appointment typically triggers outside counsel review.",
               "https://www.wsj.com", "Wall Street Journal", dt(1), dt(1)),
        Signal(None, clients["Boeing"].id, "Boeing", SignalType.GC_CHANGE,
               "Boeing appoints new Chief Legal Officer amid DOJ negotiations",
               "Boeing's board announced appointment of new CLO as part of leadership overhaul following ongoing Department of Justice negotiations. Incoming CLO historically reviews and rotates outside counsel relationships.",
               "https://www.reuters.com", "Reuters", dt(2), dt(2)),

        # M&A — highest priority
        Signal(None, clients["Salesforce"].id, "Salesforce", SignalType.MA_ACTIVITY,
               "Salesforce acquires Informatica for $11.4B in all-cash deal",
               "Salesforce announced definitive agreement to acquire Informatica Inc. for approximately $11.4 billion. Deal expected to close Q4 2026 pending regulatory approval. Transaction requires extensive M&A, antitrust, and integration counsel.",
               "https://www.sec.gov", "SEC EDGAR (8-K)", dt(0), dt(0)),
        Signal(None, clients["Amazon"].id, "Amazon", SignalType.MA_ACTIVITY,
               "Amazon files SC TO-T tender offer for iRobot at revised $1.7B valuation",
               "Amazon.com Inc. filed amended tender offer for iRobot Corporation following FTC regulatory review. Revised deal structure requires continued M&A and regulatory counsel engagement.",
               "https://www.sec.gov", "SEC EDGAR (SC TO-T)", dt(3), dt(3)),
        Signal(None, clients["JPMorgan Chase"].id, "JPMorgan Chase", SignalType.MA_ACTIVITY,
               "JPMorgan Chase acquires Washington D.C. regional bank assets",
               "JPMorgan Chase & Co. announced acquisition of select deposit and loan assets from regional bank in FDIC-assisted transaction. Bank M&A and regulatory counsel required.",
               "https://www.bloomberg.com", "Bloomberg", dt(4), dt(4)),

        # IPO Filings
        Signal(None, clients["Stripe"].id, "Stripe", SignalType.IPO_FILING,
               "Stripe confidentially files S-1 with SEC ahead of anticipated 2026 IPO",
               "Stripe Inc. has confidentially submitted a draft S-1 registration statement to the SEC. The payments company, last valued at $65B, is targeting a 2026 public market debut. IPO counsel engagement imminent.",
               "https://www.ft.com", "Financial Times", dt(1), dt(1)),

        # Funding Rounds
        Signal(None, clients["OpenAI"].id, "OpenAI", SignalType.FUNDING_ROUND,
               "OpenAI raises $40B Series F at $340B valuation led by SoftBank",
               "OpenAI closed a $40 billion Series F round led by SoftBank Vision Fund 2, at a post-money valuation of $340 billion. Round includes secondary component. Venture counsel and complex financing structures involved.",
               "https://www.wsj.com", "Wall Street Journal", dt(0), dt(0)),
        Signal(None, clients["SpaceX"].id, "SpaceX", SignalType.FUNDING_ROUND,
               "SpaceX raises $1B in new funding round at $350B valuation",
               "Space Exploration Technologies Corp. (SpaceX) closed a $1 billion tender offer round at a $350 billion valuation. Transaction involved secondary sales by early employees and investors. Complex securities and tender offer counsel needed.",
               "https://www.reuters.com", "Reuters", dt(5), dt(5)),

        # Regulatory
        Signal(None, clients["Alphabet"].id, "Alphabet", SignalType.REGULATORY,
               "DOJ files landmark antitrust remedy brief against Google Search monopoly",
               "The Department of Justice filed its proposed remedies brief in the Google Search antitrust case, including potential forced divestiture of Chrome browser and Android licensing restrictions. Extensive antitrust, regulatory, and appellate counsel required.",
               "https://www.doj.gov", "DOJ", dt(2), dt(2)),
        Signal(None, clients["Amazon"].id, "Amazon", SignalType.REGULATORY,
               "FTC issues second request in Amazon-iRobot merger review",
               "The Federal Trade Commission issued a second request for documents in its review of Amazon's proposed acquisition of iRobot, signaling a deeper antitrust investigation. Antitrust merger clearance counsel critical.",
               "https://www.ftc.gov", "FTC", dt(6), dt(6)),

        # Litigation
        Signal(None, clients["Nike"].id, "Nike", SignalType.LITIGATION,
               "Nike faces class action over alleged PFAS contamination in athletic wear",
               "A putative class action was filed in the Northern District of California alleging Nike knowingly used PFAS 'forever chemicals' in performance athletic wear. Plaintiff class estimated at 5 million consumers.",
               "https://www.courtlistener.org", "CourtListener", dt(3), dt(3)),
        Signal(None, clients["Goldman Sachs"].id, "Goldman Sachs", SignalType.LITIGATION,
               "Goldman Sachs named in 1MDB-related civil suit by Malaysian government",
               "The Malaysian government refiled civil claims against Goldman Sachs International arising from the 1MDB bond underwriting scandal. Claims seek $2.4 billion in additional disgorgement beyond prior settlement.",
               "https://www.reuters.com", "Reuters", dt(7), dt(7)),

        # Leadership
        Signal(None, clients["Starbucks"].id, "Starbucks", SignalType.LEADERSHIP,
               "Starbucks CEO Brian Niccol departs; board names interim successor",
               "Starbucks Corporation announced that CEO Brian Niccol has resigned, effective immediately. The board named COO Sara Trilling as interim CEO while conducting a search. CEO transitions frequently precede GC reviews and outside counsel changes.",
               "https://www.wsj.com", "Wall Street Journal", dt(1), dt(1)),
        Signal(None, clients["Pfizer"].id, "Pfizer", SignalType.LEADERSHIP,
               "Pfizer CFO David Denton to retire; successor search underway",
               "Pfizer Inc. announced CFO David Denton will retire after a planned transition period. CFO and legal leadership changes often signal broader outside counsel rotation discussions.",
               "https://www.bloomberg.com", "Bloomberg", dt(4), dt(4)),
    ]

    inserted = 0
    for s in demo_signals:
        result = db.insert_signal(s)
        if result:
            inserted += 1
            print(f"  [{s.signal_type.value}] {s.client_name}: {s.headline[:60]}…")
    print(f"\nInserted {inserted} demo signals.")


if __name__ == "__main__":
    seed_demo_signals()
