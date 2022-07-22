from tkinter import N
from typing import List, Tuple
import requests
import time

class Observation:
    STAT_NAMES = ["winddir", "humidity", "temp", "windspeed", "windgust", "windchill", "dewpt", "heatindex", "pressure"]

    def __init__(self, json: str) -> None:
        self.parse(json)
    
    @property
    def age(self) -> float:
        return time.time() - self.epoch

    def parse(self, json: dict):
        self.station_name: str = json["stationID"]
        self.pos: Tuple[float, float] = (json["lat"], json["lon"])
        self.epoch: int = json["epoch"]
        self.UTCTime: str = json["obsTimeUtc"]
        self.timezone: str = json["tz"]

        self.data: List[Stat] = []

        for name in self.STAT_NAMES:
            stat: Stat = Stat(name, None, None, None)
            for post in ["High", "Low", "Avg", "Max", "Min"]:

                if name + post in json.keys():
                    value = json[name + post]
                elif name + post in json["metric"].keys():
                    value = json["metric"][name + post]
                else:
                    value = "-"

                match post:
                    case "High":
                        stat.hi = value
                    case "Avg":
                        stat.av = value
                    case "Low":
                        stat.lo = value
                    case "Max":
                        stat.hi = value if value != "-" else stat.hi
                    case "Min":
                        stat.lo = value if value != "-" else stat.lo 

            self.data.append(stat)

class Station:

    PARAMS = {
        "numericPrecision": "decimal",
        "format": "json",
        "units": "m",
    }

    def __init__(self, station_id: str, api_key: str) -> None:
        self.name = station_id
        self.apiKey = api_key

        self._observations: List[Observation] = []
        self.fetch()

    def fetch(self) -> requests.Response:
        print(f"Fetching data for {self.name}...")
        try:
            p = self.PARAMS | {
                "stationId": self.name,
                "apiKey": self.apiKey,
            }

            response = requests.get("https://api.weather.com/v2/pws/observations/all/1day", params=p)
            print(f"GET URL: {response.request.url}")

            self._observations = []
            for observation in response.json()["observations"]:
                self._observations.append(Observation(observation))

            print(f"Fetched {self.name}.\n")
            return response
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Could not fetch data for {self.stationId}: {e}")
    
    def get_observation(self, obs_id: int = -1) -> Observation:
        if time.time() - self._observations[-1].epoch > 300:
            self.fetch()
        
        return self._observations[obs_id]

class Stat:
    def __init__(self, name: str, hi: float, av: float, lo: float) -> None:
        self.name = name
        
        self.hi: float = hi
        self.av: float = av
        self.lo: float = lo
    
    @staticmethod
    def _form(n: float) -> str:
        width = 7

        if n == "-":
            return "-".rjust(width) 

        return f"{n:.2f}".rjust(width)
    
    def __repr__(self) -> str:
        return f"{self.name.ljust(13)} Max. {self._form(self.hi)}    Avg. {self._form(self.av)}    Min. {self._form(self.lo)}"