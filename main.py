from station import Station, Observation
import time

API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"

station = Station("IGODAL20", API_KEY)

try:
    while True:
        if station.stale:
            print("Fetching new data...")
            station.update()
            print("Done.\n")

            obs = station.observations[0]
            print(f"{station.name}, {obs.UTCTime} ({obs.age:.2f}s ago):")
            for stat in obs.data:
                print(stat)
            print(f"https://www.wunderground.com/dashboard/pws/{station.name}\n")

        time.sleep(5)

except ConnectionError as e:
    print(f"Error: {e}")