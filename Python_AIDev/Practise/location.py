#!/usr/bin/env python3
"""Return latitude, longitude, country and related location parameters."""

import argparse
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def get_location(name: str, count: int = 5, language: str = "en"):
    params = {
        "name": name,
        "count": count,
        "language": language,
        "format": "json",
    }
    response = requests.get(GEOCODE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])

def main():
    parser = argparse.ArgumentParser(description="Look up location parameters.")
    parser.add_argument("location", help="City or place name, e.g. Dublin")
    parser.add_argument("-n", "--count", type=int, default=5)
    args = parser.parse_args()

    try:
        results = get_location(args.location, args.count)
    except requests.RequestException as error:
        raise SystemExit(f"Location lookup failed: {error}")

    if not results:
        print("No matching location found.")
        return

    for index, place in enumerate(results, start=1):
        print(f"{index}. {place.get('name')}, {place.get('country', 'Unknown')}")
        print(f"   Latitude:  {place.get('latitude')}")
        print(f"   Longitude: {place.get('longitude')}")
        print(f"   Timezone:  {place.get('timezone')}")
        print(f"   Population: {place.get('population', 'N/A')}")
        print(f"   Elevation: {place.get('elevation', 'N/A')} m\n")

if __name__ == "__main__":
    main()