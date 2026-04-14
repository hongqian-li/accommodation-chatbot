"""
MCP server exposing search, weather, and transport tools for the HAMK chatbot.

Wraps shared logic from knowledge_base/ as MCP tools so Claude Code (or any
MCP client) can call them directly.

Run standalone:
    python mcp_server/search_server.py

Register in Claude Code via .mcp.json at the project root.

Tools exposed:
  - web_search(query)               General DuckDuckGo web search.
  - search_finnish_housing(location) Targeted search on Finnish rental platforms.
  - get_campus_weather(campus_name)  Current weather + 3-day forecast (Open-Meteo).
  - get_train_schedule(origin, dest) Live train departures (VR Digitraffic).
"""

import sys
import os

# Allow imports from the project root when run as a standalone script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from knowledge_base.web_search import (
    web_search as _web_search,
    search_finnish_housing as _search_finnish_housing,
)
from knowledge_base.weather import get_campus_weather as _get_weather
from knowledge_base.transport import get_trains as _get_trains

mcp = FastMCP("hamk-search")


@mcp.tool()
def web_search(query: str) -> str:
    """
    Perform a general web search using DuckDuckGo.

    Args:
        query: The search query string.

    Returns:
        Formatted search results (title, URL, snippet) separated by '---',
        or an empty string if no results are found.
    """
    return _web_search(query)


@mcp.tool()
def search_finnish_housing(location: str) -> str:
    """
    Search Finnish housing rental platforms for listings in a given location.

    Searches vuokraovi.com, oikotie.fi, and hops.fi via DuckDuckGo.
    Useful for finding current rental listings that the static knowledge
    base may not cover.

    Args:
        location: Finnish city or area name (e.g. 'Hämeenlinna', 'Riihimäki').

    Returns:
        Formatted rental listing results separated by '---',
        or an empty string if no results are found.
    """
    return _search_finnish_housing(location)


@mcp.tool()
def get_campus_weather(campus_name: str) -> str:
    """
    Get current weather and a 3-day forecast for a HAMK campus or Finnish city.

    Uses the Open-Meteo API (free, no key required).

    Args:
        campus_name: Campus or city name, e.g. 'hämeenlinna', 'mustiala',
                     'riihimäki', 'evo', 'valkeakoski', 'forssa'.

    Returns:
        Formatted weather report with current conditions and daily forecast,
        or an empty string if the location is not recognised.
    """
    return _get_weather(campus_name)


@mcp.tool()
def get_train_schedule(origin: str, destination: str) -> str:
    """
    Get the next train departures between two Finnish cities.

    Uses the VR Digitraffic open API (free, no key required).
    Covers long-distance and regional trains operated by VR.

    Args:
        origin:      Departure city (e.g. 'helsinki', 'tampere', 'turku').
        destination: Arrival city (e.g. 'hämeenlinna', 'riihimäki', 'lahti').

    Returns:
        Formatted schedule with train type, departure time, arrival time,
        and journey duration. Returns an empty string if the route is not
        found or the API is unavailable.
    """
    return _get_trains(origin, destination)


if __name__ == "__main__":
    mcp.run()
