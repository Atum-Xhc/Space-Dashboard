"""
tests/test_clients.py
Testy jednostkowe dla modułów dashboard/.

Uruchomienie:
    pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock

from dashboard.nasa_client import NASAClient
from dashboard.iss_client import ISSClient
from dashboard.charts import neo_scatter_chart, neo_bar_chart, iss_map


# ---------------------------------------------------------------------------
# DANE TESTOWE (mocki – nie potrzebują klucza API)
# ---------------------------------------------------------------------------

MOCK_APOD = {
    "title": "Andromeda Galaxy",
    "explanation": "The Andromeda Galaxy is a spiral galaxy.",
    "url": "https://example.com/andromeda.jpg",
    "hdurl": "https://example.com/andromeda_hd.jpg",
    "media_type": "image",
    "date": "2024-01-01",
}

MOCK_NEO_RESPONSE = {
    "element_count": 2,
    "near_earth_objects": {
        "2024-01-01": [
            {
                "name": "(2024 AA1)",
                "is_potentially_hazardous_asteroid": False,
                "estimated_diameter": {
                    "meters": {
                        "estimated_diameter_min": 10.5,
                        "estimated_diameter_max": 23.5,
                    }
                },
                "close_approach_data": [{
                    "relative_velocity": {"kilometers_per_hour": "45000"},
                    "miss_distance": {"kilometers": "500000"},
                    "close_approach_date": "2024-01-01",
                }],
            },
            {
                "name": "(2024 BB2)",
                "is_potentially_hazardous_asteroid": True,
                "estimated_diameter": {
                    "meters": {
                        "estimated_diameter_min": 100.0,
                        "estimated_diameter_max": 250.0,
                    }
                },
                "close_approach_data": [{
                    "relative_velocity": {"kilometers_per_hour": "80000"},
                    "miss_distance": {"kilometers": "1200000"},
                    "close_approach_date": "2024-01-01",
                }],
            },
        ]
    },
}

MOCK_ISS_POSITION = {
    "iss_position": {"latitude": "51.5074", "longitude": "-0.1278"},
    "timestamp": 1700000000,
}

MOCK_ASTRONAUTS = {
    "people": [
        {"name": "Oleg Kononenko", "craft": "ISS"},
        {"name": "Nikolai Chub", "craft": "ISS"},
    ]
}

MOCK_MARS_PHOTOS = {
    "photos": [
        {
            "id": 1,
            "img_src": "https://example.com/mars1.jpg",
            "camera": {"full_name": "Front Hazard Avoidance Camera"},
            "earth_date": "2015-06-03",
            "rover": {"name": "Curiosity"},
        }
    ]
}


# ---------------------------------------------------------------------------
# TESTY NASA CLIENT
# ---------------------------------------------------------------------------

class TestNASAClient:
    def setup_method(self):
        self.client = NASAClient(api_key="TEST_KEY")

    @patch("dashboard.nasa_client.httpx.Client.get")
    def test_get_apod_returns_title(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_APOD
        mock_get.return_value = mock_resp

        result = self.client.get_apod()
        assert result["title"] == "Andromeda Galaxy"
        assert result["media_type"] == "image"

    @patch("dashboard.nasa_client.httpx.Client.get")
    def test_get_neo_flattens_asteroids(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NEO_RESPONSE
        mock_get.return_value = mock_resp

        result = self.client.get_neo(days=1)
        assert result["element_count"] == 2
        assert len(result["asteroids"]) == 2

    @patch("dashboard.nasa_client.httpx.Client.get")
    def test_get_neo_sorts_by_distance(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NEO_RESPONSE
        mock_get.return_value = mock_resp

        result = self.client.get_neo()
        asteroids = result["asteroids"]
        # Powinny być posortowane rosnąco po odległości
        distances = [a["miss_distance_km"] for a in asteroids]
        assert distances == sorted(distances)

    @patch("dashboard.nasa_client.httpx.Client.get")
    def test_get_neo_hazardous_flag(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NEO_RESPONSE
        mock_get.return_value = mock_resp

        result = self.client.get_neo()
        hazardous = [a for a in result["asteroids"] if a["hazardous"]]
        assert len(hazardous) == 1
        assert "BB2" in hazardous[0]["name"]

    @patch("dashboard.nasa_client.httpx.Client.get")
    def test_get_mars_photos_limit_20(self, mock_get):
        mock_resp = MagicMock()
        # Generuj 25 zdjęć
        many_photos = {"photos": MOCK_MARS_PHOTOS["photos"] * 25}
        mock_resp.json.return_value = many_photos
        mock_get.return_value = mock_resp

        result = self.client.get_mars_photos()
        assert len(result) <= 20


# ---------------------------------------------------------------------------
# TESTY ISS CLIENT
# ---------------------------------------------------------------------------

class TestISSClient:
    def setup_method(self):
        self.client = ISSClient()

    @patch("dashboard.iss_client.httpx.Client.get")
    def test_get_position_returns_floats(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_ISS_POSITION
        mock_get.return_value = mock_resp

        pos = self.client.get_position()
        assert isinstance(pos["latitude"], float)
        assert isinstance(pos["longitude"], float)

    @patch("dashboard.iss_client.httpx.Client.get")
    def test_get_astronauts_returns_list(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_ASTRONAUTS
        mock_get.return_value = mock_resp

        people = self.client.get_astronauts()
        assert isinstance(people, list)
        assert len(people) == 2
        assert people[0]["name"] == "Oleg Kononenko"


# ---------------------------------------------------------------------------
# TESTY WYKRESÓW
# ---------------------------------------------------------------------------

class TestCharts:
    SAMPLE_ASTEROIDS = [
        {
            "name": "Test Asteroid",
            "diameter_min_m": 10.0,
            "diameter_max_m": 20.0,
            "hazardous": False,
            "velocity_kmh": 50000,
            "miss_distance_km": 500000,
            "close_approach_date": "2024-01-01",
        }
    ]

    def test_neo_scatter_returns_figure(self):
        fig = neo_scatter_chart(self.SAMPLE_ASTEROIDS)
        assert fig is not None

    def test_neo_bar_returns_figure(self):
        fig = neo_bar_chart(self.SAMPLE_ASTEROIDS)
        assert fig is not None

    def test_iss_map_returns_figure(self):
        fig = iss_map(51.5, -0.12)
        assert fig is not None

    def test_empty_asteroids_returns_empty_figure(self):
        fig = neo_scatter_chart([])
        assert fig is not None  # Nie rzuca wyjątku
