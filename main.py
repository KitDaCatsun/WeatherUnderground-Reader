from station import Station
import time

API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"

station = Station("IGODAL20", API_KEY)
print(station, end="\n\n")

try:
    while True:
        if station.stale:
            station.update()

        time.sleep(5 - (station.current.age % 5))
        print(station.current)

except ConnectionError as e:
    print(f"Error: {e}")