#!/usr/bin/env python3
"""Return environmental parameters for a location."""

import argparse
from datetime import datetime, timezone
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def resolve_location(location: str):
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    response = requests.get(GEOCODE_URL, params=params, timeout=10)
    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        raise SystemExit(f"Could not find location: {location}")

    return results[0]

def get_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 1,
    }
    response = requests.get(WEATHER_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def format_utc(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value

def main():
    parser = argparse.ArgumentParser(description="Get weather parameters for a location.")
    parser.add_argument("location", nargs="?", help="City name, e.g. Dublin")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None:
        latitude, longitude = args.lat, args.lon
        place_name = f"{latitude}, {longitude}"
    elif args.location:
        place = resolve_location(args.location)
        latitude = place["latitude"]
        longitude = place["longitude"]
        place_name = f"{place['name']}, {place.get('country', '')}"
    else:
        parser.error("Provide either a location name or both --lat and --lon.")

    try:
        weather = get_weather(latitude, longitude)
    except requests.RequestException as error:
        raise SystemExit(f"Weather lookup failed: {error}")

    current = weather["current"]
    daily = weather["daily"]

    print(f"Weather for {place_name}")
    print(f"Coordinates: {latitude}, {longitude}")
    print(f"Timezone: {weather.get('timezone')}\n")

    print("Current conditions")
    print(f"  Temperature:        {current['temperature_2m']} °C")
    print(f"  Feels like:         {current['apparent_temperature']} °C")
    print(f"  Humidity:           {current['relative_humidity_2m']}%")
    print(f"  Cloud cover:        {current['cloud_cover']}%")
    print(f"  Pressure (MSL):     {current['pressure_msl']} hPa")
    print(f"  Surface pressure:   {current['surface_pressure']} hPa")
    print(f"  Wind speed:         {current['wind_speed_10m']} km/h")
    print(f"  Wind direction:     {current['wind_direction_10m']}°")
    print(f"  Wind gusts:         {current['wind_gusts_10m']} km/h")
    print(f"  Precipitation:      {current['precipitation']} mm\n")

    print("Today")
    print(f"  Minimum temperature: {daily['temperature_2m_min'][0]} °C")
    print(f"  Maximum temperature: {daily['temperature_2m_max'][0]} °C")
    print(f"  Sunrise:             {daily['sunrise'][0]}")
    print(f"  Sunset:              {daily['sunset'][0]}")

if __name__ == "__main__":
    main()