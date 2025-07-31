import json
import pandas as pd
import ast
import os

# Load JSON
with open("traininfo.json", "r", encoding="utf-8") as f:
    traininfo = json.load(f)

train_rows = []
station_rows = []
schedule_rows = []

for train in traininfo:
    train_no = train.get("trainNumber", "UNKNOWN")
    train_name = train.get("trainName", "Unnamed Train")
    train_rows.append({"train_no": train_no, "train_name": train_name})

    try:
        station_list = ast.literal_eval(train["stationList"])  # Convert string to list
    except Exception as e:
        print(f"⚠️ Error parsing stationList for train {train_no}: {e}")
        continue

    for stn in station_list:
        stn_code = stn.get("stationCode", "UNKNOWN")
        stn_name = stn.get("stationName", "Unknown Station")
        station_rows.append({"station_code": stn_code, "station_name": stn_name})
        schedule_rows.append({
            "train_no": train_no,
            "station_code": stn_code,
            "station_name": stn_name,
            "arrival_time": stn.get("arrivalTime", "--"),
            "departure_time": stn.get("departureTime", "--"),
            "day": stn.get("dayCount", "-"),
            "distance": stn.get("distance", "0"),
            "stop_number": stn.get("stnSerialNumber", "-")
        })

# Remove duplicates
stations_df = pd.DataFrame(station_rows).drop_duplicates()
trains_df = pd.DataFrame(train_rows).drop_duplicates()
schedules_df = pd.DataFrame(schedule_rows)

# Create data/ folder if not exists
os.makedirs("data", exist_ok=True)

# Save CSVs
stations_df.to_csv("data/stations.csv", index=False)
trains_df.to_csv("data/trains.csv", index=False)
schedules_df.to_csv("data/schedules.csv", index=False)

print("✅ Done! Files saved to /data folder:")
print("- stations.csv")
print("- trains.csv")
print("- schedules.csv")
