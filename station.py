from typing import List, Tuple
import requests
import time

class Observation:
    STAT_NAMES = ["winddir", "humidity", "temp", "windspeed", "windgust", "windchill", "dewpt", "heatindex", "pressure"]

    def __init__(self, json: str) -> None:
        self.parse(json)
    
    @property
    def isotime(self) -> str:
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(self.epoch))

    def parse(self, json: dict):
        self.ID: str = json["stationID"]
        self.pos: Tuple[float, float] = (json["lat"], json["lon"])
        self.epoch: int = json["epoch"]
        self.timezone: str = json["tz"]

        self.data: List[Stat] = []

        for name in self.STAT_NAMES:
            stat: Stat = Stat(name, None, None, None)
            for post in ["High", "Low", "Avg", "Max", "Min"]:
                value = None
                if name + post in json.keys():
                    value = json[name + post]
                elif name + post in json["metric"].keys():
                    value = json["metric"][name + post]
                
                match post:
                    case "High":
                        stat.hi = value
                    case "Avg":
                        stat.av = value
                    case "Low":
                        stat.lo = value
                    case "Max":
                        if value != None: stat.hi = value
                    case "Min":
                        if value != None: stat.lo = value 

            self.data.append(stat)

class Station:

    PARAMS = {
        "numericPrecision": "decimal",
        "format": "json",
        "units": "m",
    }

    def __init__(self, station_id: str, api_key: str) -> None:
        self.stationId = station_id
        self.apiKey = api_key
        self._cachedResponse: dict | None = None

    def fetch(self, ignore_error = False) -> requests.Response:
        try:
            response = requests.get("https://api.weather.com/v2/pws/observations/all/1day", params=self.PARAMS | {"stationId": self.stationId, "apiKey": self.apiKey})

            self._cachedResponse = response.json()
            return response
        except requests.exceptions.ConnectionError as e:
            if not ignore_error:
                raise ConnectionError(f"Could not fetch data for {self.stationId}: {e}")
    
    def get(self, obs_id: int = 127) -> Observation:
        # Fetch if cached response is null or stale (more than 300 seconds old)
        if self._cachedResponse == None or self._cachedResponse["observations"][127]["epoch"] < time.time() - 300:
            self.fetch(ignore_error=self._cachedResponse != None)
        
        return Observation(self._cachedResponse["observations"][obs_id])

class Stat:
    def __init__(self, name: str, hi: float | None, av: float | None, lo: float | None) -> None:
        self.name = name
        
        self.hi = hi
        self.av = av
        self.lo = lo
    
    def __repr__(self) -> str:
        return f"{self.name.ljust(25)}High: {self.hi}\tAverage: {self.av}\tLow: {self.lo}"