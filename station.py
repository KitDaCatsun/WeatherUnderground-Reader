from typing import Any, Dict, List, Tuple
import requests
import time

class Observation:
    def __init__(self, json: str) -> None:
        self.stats: Dict[str: float] = {}
        self.parse(json)
    
    @property
    def age(self) -> float:
        return time.time() - self.epoch

    def parse(self, json: dict):
        self.station_name: str = json["stationID"]
        self.epoch: int = json["epoch"]
        self.localtime: str = json["obsTimeLocal"]

        self.stats = json["metric"]
        for key in ["humidity", "winddir"]:
            self.stats[key] = json[key]
    
    def __repr__(self) -> str:
        out = f"Readings from {time.strftime('%H:%M:%S', time.gmtime(self.epoch))} ({self.age:.1f}s ago)\n"

        for name, value in self.stats.items():
            out += f"{(name + ':').ljust(15)} {value:7.2f}\n"

        return out

class Station:

    PARAMS = {
        "numericPrecision": "decimal",
        "format": "json",
        "units": "m",
    }

    def __init__(self, station_id: str, api_key: str) -> None:
        self.name = station_id

        self.lat: float = None
        self.lon: float = None
        self.elev: float = None

        self.current = None

        self._apiKey = api_key
        self._cache = (-time.time(), None)

        self.update()

    def fetch(self) -> Any:
        if time.time() - self._cache[0] < 1:
            return self._cache[1]

        try:
            p = self.PARAMS | {
                "stationId": self.name,
                "apiKey": self._apiKey,
            }

            response = requests.get("https://api.weather.com/v2/pws/observations/current", params=p)
            data = response.json()["observations"][0]

            self._cache = (time.time(), data)

            return data
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Could not fetch data for {self.name}: {e}")
    
    def update(self) -> None:
        if not self.stale: return

        self.current = Observation(self.fetch())

        self.lat = self.fetch()["lat"]
        self.lon = self.fetch()["lon"]
        self.elev = self.fetch()["metric"]["elev"]

    @property
    def stale(self) -> bool:
        if not self.current: return True

        if time.time() - self.current.epoch < 30:
            return False
        else:
            return self.fetch()["epoch"] != self.current.epoch

    def __repr__(self) -> str:
        return f"{self.name}\nLatitude: {str(self.lat).ljust(4)}\nLongitude: {str(self.lon).ljust(4)}\nElevation: {str(self.elev).ljust(4)}m"