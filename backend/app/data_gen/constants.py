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

# ── Phase 8: Synthetic Organisations (12 fake company names) ─────────────────
SYNTHETIC_ORGS = [
    "Nexus Dynamics Ltd",
    "Meridian Analytics Corp",
    "Cipher Solutions Group",
    "Vector Capital Partners",
    "Alpha Signal Systems",
    "Delta Logistics Network",
    "Apex Data Consortium",
    "Sigma Trade Alliance",
    "Orbital Futures Inc",
    "Crux Intelligence Agency",
    "Vortex Communications LLC",
    "Prism Asset Holdings",
]

# ── Phase 8: Nationalities (30 country names) ─────────────────────────────────
NATIONALITIES = [
    "Meridian",
    "Valtoran",
    "Nexian",
    "Cipherian",
    "Deltese",
    "Alphan",
    "Sigmarite",
    "Orbitian",
    "Cruxian",
    "Vortexian",
    "Prismatic",
    "Syntherian",
    "Crestlandian",
    "Ironvale",
    "Stormhaven",
    "Deepwater",
    "Highridge",
    "Coldmere",
    "Ashford",
    "Blackstone",
    "Whitecliff",
    "Greenvale",
    "Redmont",
    "Bluehaven",
    "Goldshire",
    "Silverport",
    "Bronzefeld",
    "Coppergate",
    "Ironbell",
    "Steelmark",
]

# ── Phase 8: Risk Categories with weights ─────────────────────────────────────
RISK_CATEGORIES = ["low", "medium", "high", "critical"]
RISK_CATEGORY_WEIGHTS = [0.50, 0.30, 0.15, 0.05]

# ── Phase 8: Fake Platforms ───────────────────────────────────────────────────
FAKE_PLATFORMS = ["NexusMail", "VectorChat", "SecureLink", "GridComm"]

# ── Phase 8: Call Channels ────────────────────────────────────────────────────
CALL_CHANNELS = ["voice", "encrypted", "unknown"]

# ── Phase 8: Transfer Currencies ─────────────────────────────────────────────
TRANSFER_CURRENCIES = ["USD", "EUR", "MeridianCoin"]

# ── Phase 8: Synthetic Districts (8 names) ────────────────────────────────────
DISTRICTS = [
    "Central Nexus",
    "Eastern Grid",
    "Western Delta",
    "Northern Apex",
    "Southern Vector",
    "Cipher Quarter",
    "Meridian Heights",
    "Signal District",
]

# ── Phase 8: Threat Levels with weights ───────────────────────────────────────
THREAT_LEVELS = ["green", "amber", "red"]
THREAT_LEVEL_WEIGHTS = [0.60, 0.30, 0.10]

# ── Phase 8: Fake Alias Names ─────────────────────────────────────────────────
FAKE_ALIASES = [
    "Shadow", "Viper", "Ghost", "Phoenix", "Specter", "Wraith",
    "Cobra", "Falcon", "Raven", "Lynx", "Jaguar", "Panther",
    "Cyclone", "Tempest", "Blizzard", "Inferno", "Thunder", "Storm",
    "Cipher", "Nexus", "Vector", "Delta", "Alpha", "Sigma",
    "Oracle", "Phantom", "Eclipse", "Nova", "Zenith", "Apex",
]
