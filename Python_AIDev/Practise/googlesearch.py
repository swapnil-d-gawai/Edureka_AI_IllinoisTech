#!/usr/bin/env python3
"""Command-line utility to fetch top Bing search-result links."""

import argparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

def search(query: str, limit: int = 10):
    """Return extracted links from a Bing search."""
    url = "https://www.bing.com/search"
    params = {"q": query, "count": limit}
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for anchor in soup.select("li.b_algo h2 a[href]"):
        href = anchor.get("href", "")
        title = anchor.get_text(strip=True)

        # Skip duplicate or empty results.
        if (
            not href
            or not title
            or any(href == r["link"] for r in results)
        ):
            continue

        results.append({"title": title, "link": href})
        if len(results) >= limit:
            break

    return results

def main():
    parser = argparse.ArgumentParser(description="Get top Bing search links.")
    parser.add_argument("query", help="Search term")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of Bing results")
    args = parser.parse_args()

    try:
        results = search(args.query, args.num)
    except requests.RequestException as error:
        raise SystemExit(f"Search failed: {error}")

    if not results:
        print(
            "No results were extracted from Bing. The query may have no matches, "
            "its result markup may have changed, or Bing may have blocked the request."
        )
        return

    for index, result in enumerate(results, start=1):
        print(f"{index}. {result['title']}")
        print(f"   {result['link']}\n")

if __name__ == "__main__":
    main()