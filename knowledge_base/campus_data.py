"""
Static data about HAMK campuses and Finnish train stations.

Used by weather.py and transport.py to resolve location names
from user queries into coordinates and station codes.
"""

# Campus name (lowercase, both with/without ä) → coordinates + transport info
CAMPUSES = {
    "hämeenlinna": {
        "lat": 61.00, "lon": 24.47,
        "display": "Hämeenlinna (Visamäki campus)",
        "station": "HL",
        "bus_note": None,
    },
    "hameenlinna": {
        "lat": 61.00, "lon": 24.47,
        "display": "Hämeenlinna (Visamäki campus)",
        "station": "HL",
        "bus_note": None,
    },
    "riihimäki": {
        "lat": 60.74, "lon": 24.77,
        "display": "Riihimäki campus",
        "station": "RI",
        "bus_note": None,
    },
    "riihimaki": {
        "lat": 60.74, "lon": 24.77,
        "display": "Riihimäki campus",
        "station": "RI",
        "bus_note": None,
    },
    "mustiala": {
        "lat": 60.83, "lon": 23.80,
        "display": "Mustiala campus",
        "station": None,
        "bus_note": (
            "No direct train to Mustiala. Take a train to Hämeenlinna (HL), "
            "then bus or taxi ~45 min to Mustiala campus."
        ),
    },
    "evo": {
        "lat": 61.20, "lon": 25.11,
        "display": "Evo campus",
        "station": None,
        "bus_note": (
            "No direct train to Evo. Take a train to Hämeenlinna (HL), "
            "then bus ~1 hour to Evo campus."
        ),
    },
    "valkeakoski": {
        "lat": 61.27, "lon": 24.03,
        "display": "Valkeakoski campus",
        "station": None,
        "bus_note": (
            "No direct train to Valkeakoski. Take a train to Toijala (TL) "
            "then bus ~20 min, or to Tampere then bus ~40 min."
        ),
    },
    "forssa": {
        "lat": 60.82, "lon": 23.62,
        "display": "Forssa campus",
        "station": None,
        "bus_note": (
            "No direct train to Forssa. Bus from Hämeenlinna takes ~1 hour."
        ),
    },
}

# City/campus names that map to VR train station codes
TRAIN_STATIONS = {
    "helsinki": "HKI",
    "tampere": "TPE",
    "turku": "TKU",
    "lahti": "LH",
    "hämeenlinna": "HL",
    "hameenlinna": "HL",
    "riihimäki": "RI",
    "riihimaki": "RI",
    "toijala": "TL",
    "pasila": "PSL",
    "tikkurila": "TKL",
}

STATION_DISPLAY = {
    "HKI": "Helsinki", "TPE": "Tampere", "TKU": "Turku",
    "LH": "Lahti", "HL": "Hämeenlinna", "RI": "Riihimäki",
    "TL": "Toijala", "PSL": "Pasila", "TKL": "Tikkurila",
}


def find_campus(query: str) -> str | None:
    """Return the first HAMK campus name found in the query, or None."""
    q = query.lower()
    return next((name for name in CAMPUSES if name in q), None)


def find_cities(query: str) -> list[str]:
    """Return all known train-station city names found in the query."""
    q = query.lower()
    return [city for city in TRAIN_STATIONS if city in q]
