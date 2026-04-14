"""
Shared DuckDuckGo web search utilities.

Used by both the Flask fallback pipeline (via knowledge_base/query.py)
and the MCP server (mcp_server/search_server.py). No API key required.

Both functions return an empty string on any failure so callers can treat
a falsy return as "no results" and gracefully fall back to RAG-only answers.
"""

from ddgs import DDGS


def web_search(query: str, max_results: int = 3) -> str:
    """
    Perform a general DuckDuckGo web search.

    Args:
        query:       The search query string.
        max_results: Maximum number of results to return (default 3).

    Returns:
        Formatted string of results (title, URL, snippet per result)
        separated by '---', or an empty string if the search fails
        or returns no results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return ""
        return "\n---\n".join(
            f"[{r['title']}]({r['href']})\n{r['body'][:200]}"
            for r in results
        )
    except Exception:
        return ""


def search_finnish_housing(location: str, max_results: int = 3) -> str:
    """
    Search Finnish housing rental platforms for listings in a given location.

    Targets vuokraovi.com, oikotie.fi, and hops.fi using DuckDuckGo site:
    operators. The Finnish words 'vuokra asunto' (rental apartment) sharpen
    results toward actual listings rather than general pages.

    Args:
        location:    Finnish city or area name (e.g. 'Hämeenlinna', 'Riihimäki').
                     Accepts full sentences — DuckDuckGo handles natural language.
        max_results: Maximum number of results to return (default 3).

    Returns:
        Formatted string of rental listing results separated by '---',
        or an empty string if the search fails or returns no results.
    """
    query = (
        f"site:vuokraovi.com OR site:oikotie.fi OR site:hops.fi "
        f"{location} vuokra asunto"
    )
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return ""
        return "\n---\n".join(
            f"[{r['title']}]({r['href']})\n{r['body'][:200]}"
            for r in results
        )
    except Exception:
        return ""
