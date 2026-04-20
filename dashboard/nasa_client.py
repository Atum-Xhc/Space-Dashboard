"""
dashboard/nasa_client.py
Klient NASA Open APIs.

Używa:
- APOD: Astronomy Picture of the Day
- NeoWs: Near Earth Object Web Service (asteroidy)
- Mars Rover Photos: zdjęcia z łazika

Klucz API: darmowy na https://api.nasa.gov
Bez rejestracji: użyj DEMO_KEY (30 req/h, 50 req/dzień)
"""

import os
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.nasa.gov"


class NASAClient:
    """
    Klient do NASA Open APIs.

    Przykład użycia:
        client = NASAClient()
        apod = client.get_apod()
        print(apod["title"], apod["url"])
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("NASA_API_KEY", "DEMO_KEY")
        self._http = httpx.Client(timeout=15)

    def get_apod(self, apod_date: str | None = None) -> dict:
        """
        Pobierz Astronomiczne Zdjęcie Dnia (APOD).

        Args:
            apod_date: Data w formacie YYYY-MM-DD (domyślnie: dzisiaj)

        Returns:
            dict z kluczami: title, explanation, url, media_type, date
        """
        params = {"api_key": self.api_key}
        if apod_date:
            params["date"] = apod_date

        resp = self._http.get(f"{BASE_URL}/planetary/apod", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_neo(self, days: int = 7) -> dict:
        """
        Pobierz listę asteroid bliskich Ziemi (Near Earth Objects).

        Args:
            days: Liczba dni do przodu (max 7 dla DEMO_KEY)

        Returns:
            dict z kluczami: element_count, near_earth_objects (pogrupowane po dacie)
        """
        start = date.today().isoformat()
        end = (date.today() + timedelta(days=min(days, 7))).isoformat()

        params = {
            "api_key": self.api_key,
            "start_date": start,
            "end_date": end,
        }

        resp = self._http.get(f"{BASE_URL}/neo/rest/v1/feed", params=params)
        resp.raise_for_status()
        data = resp.json()

        # Spłaszcz strukturę – zbierz wszystkie asteroidy do jednej listy
        all_neo = []
        for day_data in data.get("near_earth_objects", {}).values():
            for neo in day_data:
                diameter = neo["estimated_diameter"]["meters"]
                close_approach = neo["close_approach_data"][0] if neo["close_approach_data"] else {}
                all_neo.append({
                    "name": neo["name"].strip("()"),
                    "diameter_min_m": round(diameter["estimated_diameter_min"], 1),
                    "diameter_max_m": round(diameter["estimated_diameter_max"], 1),
                    "hazardous": neo["is_potentially_hazardous_asteroid"],
                    "velocity_kmh": round(
                        float(close_approach.get("relative_velocity", {}).get("kilometers_per_hour", 0))
                    ),
                    "miss_distance_km": round(
                        float(close_approach.get("miss_distance", {}).get("kilometers", 0))
                    ),
                    "close_approach_date": close_approach.get("close_approach_date", ""),
                })

        return {
            "element_count": data.get("element_count", 0),
            "asteroids": sorted(all_neo, key=lambda x: x["miss_distance_km"]),
        }

    def get_mars_photos(self, rover: str = "curiosity", sol: int = 1000) -> list[dict]:
        """
        Pobierz zdjęcia z łazika marsjańskiego.

        Args:
            rover: "curiosity", "perseverance" lub "opportunity"
            sol: Dzień marsjański (sol) od lądowania

        Returns:
            Lista dict z kluczami: id, img_src, camera, earth_date
        """
        params = {
            "api_key": self.api_key,
            "sol": sol,
            "page": 1,
        }

        resp = self._http.get(
            f"{BASE_URL}/mars-photos/api/v1/rovers/{rover}/photos",
            params=params,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])

        return [
            {
                "id": p["id"],
                "img_src": p["img_src"],
                "camera": p["camera"]["full_name"],
                "earth_date": p["earth_date"],
                "rover": p["rover"]["name"],
            }
            for p in photos[:20]  # Maksymalnie 20 zdjęć
        ]

    def __del__(self):
        self._http.close()
