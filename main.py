from station import Station, Observation

API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"

station = Station("IGODAL20", API_KEY)
try:
    obs: Observation = station.get_observation()
    print(f"Data for {station.stationId} at {obs.isotime}, last 300 seconds:")
    for stat in obs.data:
        print(stat)

except ConnectionError as e:
    print(f"Error: {e}")