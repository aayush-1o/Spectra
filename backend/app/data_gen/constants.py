"""
Spectra — Data Generation Constants
Fictional "New Meridian City" geography and event configuration.
⚠️ All data is 100% synthetic. No real-world locations or people.
"""

# ── City Centre (fictional "New Meridian City") ───────────────────────────────
CITY_CENTRE_LAT = 51.5074
CITY_CENTRE_LON = -0.1278

# Bounding box offset (±degrees from city centre)
BBOX_DELTA = 0.3

LAT_MIN = CITY_CENTRE_LAT - BBOX_DELTA
LAT_MAX = CITY_CENTRE_LAT + BBOX_DELTA
LON_MIN = CITY_CENTRE_LON - BBOX_DELTA
LON_MAX = CITY_CENTRE_LON + BBOX_DELTA

# ── Event Type Weights ────────────────────────────────────────────────────────
# Must sum to 1.0; order matches EventType enum values.
EVENT_TYPES = ["call", "message", "meeting", "transfer"]
EVENT_WEIGHTS = [0.40, 0.35, 0.15, 0.10]

# ── Occupations (fictional) ───────────────────────────────────────────────────
OCCUPATIONS = [
    "Systems Analyst",
    "Data Courier",
    "Network Liaison",
    "Signal Technician",
    "Logistics Coordinator",
    "Field Operative",
    "Intelligence Archivist",
    "Urban Planner",
    "Communications Officer",
    "Forensic Accountant",
    "Trade Broker",
    "Infrastructure Auditor",
    "Cartographic Engineer",
    "Regulatory Specialist",
    "Surveillance Technician",
    "Compliance Consultant",
    "Route Strategist",
    "Asset Manager",
    "Document Control Officer",
    "Transfer Supervisor",
]

# ── Building Name Generators ──────────────────────────────────────────────────
BUILDING_PREFIXES = [
    "Synthetic", "Meridian", "Central", "North", "South", "East", "West",
    "Apex", "Nexus", "Delta", "Alpha", "Sigma", "Prime", "Vector", "Cipher",
]

BUILDING_SUFFIXES = [
    "Tower", "Block", "House", "Court", "Plaza", "Centre", "Hub",
    "Exchange", "Point", "Gate", "Square", "Terrace", "Quarter",
]
