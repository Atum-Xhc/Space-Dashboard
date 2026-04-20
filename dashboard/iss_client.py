"""
dashboard/iss_client.py
Klient Open Notify API – pozycja ISS i astronauci na orbicie.

Nie wymaga klucza API – całkowicie darmowe.
Dokumentacja: http://open-notify.org/
"""

import httpx


class ISSClient:
    """
    Klient do Open Notify API (ISS).

    Przykład użycia:
        client = ISSClient()
        pos = client.get_position()
        print(pos["latitude"], pos["longitude"])
    """

    BASE_URL = "http://api.open-notify.org"

    def __init__(self):
        self._http = httpx.Client(timeout=10)

    def get_position(self) -> dict:
        """
        Pobierz aktualną pozycję ISS.

        Returns:
            dict z kluczami: latitude, longitude, timestamp
        """
        resp = self._http.get(f"{self.BASE_URL}/iss-now.json")
        resp.raise_for_status()
        data = resp.json()

        return {
            "latitude": float(data["iss_position"]["latitude"]),
            "longitude": float(data["iss_position"]["longitude"]),
            "timestamp": data["timestamp"],
        }

    def get_astronauts(self) -> list[dict]:
        """
        Pobierz listę astronautów aktualnie w kosmosie.

        Returns:
            Lista dict z kluczami: name, craft
        """
        resp = self._http.get(f"{self.BASE_URL}/astros.json")
        resp.raise_for_status()
        data = resp.json()

        return data.get("people", [])

    def get_iss_passes(self, lat: float, lon: float, n: int = 5) -> list[dict]:
        """
        Pobierz przewidywane przeloty ISS nad podaną lokalizacją.

        Args:
            lat: Szerokość geograficzna
            lon: Długość geograficzna
            n: Liczba przelotów do zwrócenia

        Returns:
            Lista dict z kluczami: duration, risetime
        """
        # Uwaga: /iss-pass.json jest często niedostępne w darmowym planie
        # Zostawiam jako przykład rozszerzenia
        try:
            resp = self._http.get(
                f"{self.BASE_URL}/iss-pass.json",
                params={"lat": lat, "lon": lon, "n": n},
            )
            resp.raise_for_status()
            return resp.json().get("response", [])
        except Exception:
            return []

    def __del__(self):
        self._http.close()
