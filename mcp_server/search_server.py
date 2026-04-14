"""
MCP server exposing web search tools for the HAMK accommodation chatbot.

Wraps the shared search logic in knowledge_base/web_search.py as MCP tools
so that Claude Code (or any MCP client) can call them directly.

Run standalone:
    python mcp_server/search_server.py

Register in Claude Code via .claude/settings.local.json:
    "mcpServers": {
      "hamk-search": {
        "command": "python",
        "args": ["<absolute_path>/mcp_server/search_server.py"]
      }
    }

Tools exposed:
  - web_search(query)               General DuckDuckGo web search.
  - search_finnish_housing(location) Targeted search on Finnish rental platforms.
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


if __name__ == "__main__":
    mcp.run()
