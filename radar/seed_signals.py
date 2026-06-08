"""Seed realistic demo signals for dashboard development and demos."""
from datetime import datetime, timedelta
from radar import db
from radar.models import Signal, SignalType

def _s(summary, insight):
    return f"{summary}\n\n💼 {insight}"

def seed_demo_signals():
    db.init_db()
    clients = {c.name: c for c in db.get_clients()}

    def dt(days_ago):
        return datetime.utcnow() - timedelta(days=days_ago)

    demo_signals = [
        Signal(None, clients["Microsoft"].id, "Microsoft", SignalType.GC_CHANGE,
               "Microsoft names new General Counsel — Dev Stahlkopf to depart",
               _s("Dev Stahlkopf will step down as Microsoft's General Counsel and EVP effective Q3. A successor search is underway.",
                  "New GCs typically conduct an outside counsel review within 90 days — high-priority outreach opportunity for relationship partners."),
               "https://www.wsj.com", "Wall Street Journal", dt(1), dt(1)),

        Signal(None, clients["Boeing"].id, "Boeing", SignalType.GC_CHANGE,
               "Boeing appoints new Chief Legal Officer amid DOJ negotiations",
               _s("Boeing's board named a new CLO as part of a broader leadership overhaul during ongoing DOJ deferred prosecution negotiations.",
                  "Incoming CLOs frequently rotate outside counsel relationships — priority engagement for Perkins' aviation and government contracts practice."),
               "https://www.reuters.com", "Reuters", dt(2), dt(2)),

        Signal(None, clients["Salesforce"].id, "Salesforce", SignalType.MA_ACTIVITY,
               "Salesforce acquires Informatica for $11.4B in all-cash deal",
               _s("Salesforce signed a definitive agreement to acquire data management company Informatica for $11.4B. Deal is pending regulatory approval, expected to close Q4 2026.",
                  "Transaction requires M&A, antitrust clearance, and integration counsel — reach out to relationship partner immediately."),
               "https://www.sec.gov", "SEC EDGAR (8-K)", dt(0), dt(0)),

        Signal(None, clients["Amazon"].id, "Amazon", SignalType.MA_ACTIVITY,
               "Amazon files tender offer for iRobot at revised $1.7B valuation",
               _s("Amazon filed an amended SC TO-T tender offer for iRobot following FTC scrutiny, revising the deal structure and valuation from the original $1.7B agreement.",
                  "Ongoing antitrust review creates continued need for merger clearance counsel — opportunity to engage on regulatory strategy."),
               "https://www.sec.gov", "SEC EDGAR (SC TO-T)", dt(3), dt(3)),

        Signal(None, clients["JPMorgan Chase"].id, "JPMorgan Chase", SignalType.MA_ACTIVITY,
               "JPMorgan acquires regional bank assets in FDIC-assisted transaction",
               _s("JPMorgan Chase acquired select deposit and loan assets from a regional bank in an FDIC-assisted transaction, expanding its mid-market presence.",
                  "Bank M&A and FDIC regulatory counsel required — contact financial institutions practice lead."),
               "https://www.bloomberg.com", "Bloomberg", dt(4), dt(4)),

        Signal(None, clients["Stripe"].id, "Stripe", SignalType.IPO_FILING,
               "Stripe confidentially files S-1 with SEC ahead of 2026 IPO",
               _s("Stripe submitted a confidential draft S-1 registration to the SEC, signaling a 2026 IPO target. The payments company was last valued at $65B in a secondary transaction.",
                  "IPO counsel engagement is imminent — S-1 to closing typically requires 6-9 months of intensive outside counsel work across securities, employment, and IP."),
               "https://www.ft.com", "Financial Times", dt(1), dt(1)),

        Signal(None, clients["OpenAI"].id, "OpenAI", SignalType.FUNDING_ROUND,
               "OpenAI closes $40B Series F at $340B valuation led by SoftBank",
               _s("OpenAI closed a $40 billion Series F financing led by SoftBank Vision Fund 2 at a $340B post-money valuation, making it the largest private fundraise in history.",
                  "Complex venture financing of this scale requires specialized securities and fund formation counsel — strong BD opportunity given Perkins' tech practice."),
               "https://www.wsj.com", "Wall Street Journal", dt(0), dt(0)),

        Signal(None, clients["SpaceX"].id, "SpaceX", SignalType.FUNDING_ROUND,
               "SpaceX raises $1B tender offer round at $350B valuation",
               _s("SpaceX closed a $1 billion tender offer allowing early employees and investors to sell shares at a $350B implied valuation.",
                  "Tender offer mechanics and secondary market transactions require specialized securities counsel — reach out to Perkins' venture/capital markets team."),
               "https://www.reuters.com", "Reuters", dt(5), dt(5)),

        Signal(None, clients["Alphabet"].id, "Alphabet", SignalType.REGULATORY,
               "DOJ files antitrust remedy brief seeking Google Search divestiture",
               _s("The Department of Justice filed its proposed remedies brief in the Google Search monopoly case, proposing forced divestiture of Chrome and Android licensing restrictions.",
                  "Landmark antitrust proceeding requiring appellate, regulatory, and constitutional counsel — Perkins' antitrust practice should engage relationship partner."),
               "https://www.doj.gov", "DOJ", dt(2), dt(2)),

        Signal(None, clients["Amazon"].id, "Amazon", SignalType.REGULATORY,
               "FTC issues second request in Amazon-iRobot merger review",
               _s("The FTC issued a second request for documents in its antitrust review of Amazon's iRobot acquisition, indicating the agency will conduct a deeper investigation.",
                  "Second requests significantly extend deal timelines and require intensive document review and regulatory counsel — escalate to antitrust practice."),
               "https://www.ftc.gov", "FTC", dt(6), dt(6)),

        Signal(None, clients["Nike"].id, "Nike", SignalType.LITIGATION,
               "Nike named in PFAS class action over performance athletic wear",
               _s("A class action was filed in the N.D. California alleging Nike knowingly used PFAS 'forever chemicals' in athletic wear sold to approximately 5 million consumers.",
                  "Consumer products litigation of this scale requires coordinated defense counsel — contact Perkins' product liability and class action defense team."),
               "https://www.courtlistener.org", "CourtListener", dt(3), dt(3)),

        Signal(None, clients["Goldman Sachs"].id, "Goldman Sachs", SignalType.LITIGATION,
               "Malaysia refiles $2.4B civil claims against Goldman Sachs over 1MDB",
               _s("The Malaysian government refiled civil claims against Goldman Sachs seeking $2.4B in additional disgorgement related to 1MDB bond underwriting, beyond the prior $3.9B settlement.",
                  "International arbitration and cross-border litigation requiring sophisticated financial institution defense counsel — flag to Perkins' financial services disputes team."),
               "https://www.reuters.com", "Reuters", dt(7), dt(7)),

        Signal(None, clients["Starbucks"].id, "Starbucks", SignalType.LEADERSHIP,
               "Starbucks CEO Brian Niccol resigns; COO named interim chief",
               _s("Brian Niccol resigned as Starbucks CEO effective immediately. The board named COO Sara Trilling as interim CEO while conducting an executive search.",
                  "CEO transitions frequently precede GC reviews and outside counsel rotation — monitor for CLO change signal and prepare relationship outreach."),
               "https://www.wsj.com", "Wall Street Journal", dt(1), dt(1)),

        Signal(None, clients["Pfizer"].id, "Pfizer", SignalType.LEADERSHIP,
               "Pfizer CFO David Denton to retire; successor search underway",
               _s("Pfizer announced CFO David Denton will retire after a transition period, with an executive search firm engaged to find a successor.",
                  "C-suite turnover at major pharma companies often signals broader legal team changes — a good moment to reconnect with the Pfizer relationship partner."),
               "https://www.bloomberg.com", "Bloomberg", dt(4), dt(4)),
    ]

    inserted = 0
    for s in demo_signals:
        result = db.insert_signal(s)
        if result:
            inserted += 1
    print(f"Inserted {inserted} demo signals.")


if __name__ == "__main__":
    seed_demo_signals()
