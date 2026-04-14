"""
Finnish train schedules using the VR Digitraffic open API.

Digitraffic is operated by Fintraffic and is free with no API key required.
API docs: https://www.digitraffic.fi/rautatieliikenne/
"""

import requests
from datetime import datetime
from knowledge_base.campus_data import (
    CAMPUSES, TRAIN_STATIONS, STATION_DISPLAY, find_cities,
)

DIGITRAFFIC_URL = "https://rata.digitraffic.fi/api/v1/live-trains/station"


def get_trains(origin: str, destination: str, max_results: int = 4) -> str:
    """
    Fetch the next train departures between two Finnish cities.

    Args:
        origin:      Origin city name (e.g. 'helsinki').
        destination: Destination city name (e.g. 'hämeenlinna').
        max_results: Maximum number of departures to return.

    Returns:
        Formatted schedule string, or '' if unavailable / no route found.
    """
    orig_code = TRAIN_STATIONS.get(origin.lower())
    dest_code = TRAIN_STATIONS.get(destination.lower())
    if not orig_code or not dest_code or orig_code == dest_code:
        return ""

    try:
        resp = requests.get(
            f"{DIGITRAFFIC_URL}/{orig_code}",
            params={
                "departing_trains": 30,
                "arrived_trains": 0,
                "arriving_trains": 0,
                "departed_trains": 0,
            },
            timeout=10,
        )
        resp.raise_for_status()
        trains = resp.json()
    except Exception:
        return ""

    results = []
    for train in trains:
        rows = train.get("timeTableRows", [])
        dep_time = arr_time = None
        found_origin = False

        for row in rows:
            code = row.get("stationShortCode")
            stopping = row.get("trainStopping", True)
            if code == orig_code and row["type"] == "DEPARTURE" and stopping:
                dep_time = row.get("scheduledTime")
                found_origin = True
            elif found_origin and code == dest_code and row["type"] == "ARRIVAL" and stopping:
                arr_time = row.get("scheduledTime")
                break

        if not dep_time or not arr_time:
            continue

        dep = datetime.fromisoformat(dep_time.replace("Z", "+00:00")).astimezone()
        arr = datetime.fromisoformat(arr_time.replace("Z", "+00:00")).astimezone()
        mins = int((arr - dep).total_seconds() / 60)
        label = f"{train.get('trainType', '')}{train.get('trainNumber', '')}"
        results.append(
            f"{label}: departs {dep.strftime('%H:%M')} → arrives {arr.strftime('%H:%M')} ({mins} min)"
        )
        if len(results) >= max_results:
            break

    if not results:
        return (
            f"No trains found right now from "
            f"{STATION_DISPLAY.get(orig_code, origin.title())} to "
            f"{STATION_DISPLAY.get(dest_code, destination.title())}. "
            "Check vr.fi for the full timetable."
        )

    orig_name = STATION_DISPLAY.get(orig_code, origin.title())
    dest_name = STATION_DISPLAY.get(dest_code, destination.title())
    return f"Next trains from {orig_name} to {dest_name}:\n" + "\n".join(results)


def get_transport_for_query(query: str) -> str:
    """
    Parse a user query for campus/city names and return transport advice.

    Handles:
    - Campuses with no direct train (returns bus/taxi note)
    - Two recognised cities (returns live train schedule)
    - One recognised city (defaults origin to Helsinki for arriving students)

    Returns:
        Formatted transport string, or '' if nothing useful can be determined.
    """
    q = query.lower()

    # Campuses with no direct train → return bus note
    for name, campus in CAMPUSES.items():
        if name in q and campus["station"] is None and campus.get("bus_note"):
            return f"Getting to {campus['display']}:\n{campus['bus_note']}"

    cities = find_cities(query)

    if len(cities) >= 2:
        return get_trains(cities[0], cities[1])

    if len(cities) == 1 and cities[0] != "helsinki":
        # Most arriving students travel from Helsinki — use as default origin
        return get_trains("helsinki", cities[0])

    return ""
