import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load data
stations = pd.read_csv("data/stations.csv")
trains = pd.read_csv("data/trains.csv")
schedules = pd.read_csv("data/schedules.csv")

# Prepare station list
station_list = sorted(stations["station_name"].dropna().unique())

# Title
st.set_page_config(page_title="Railway Travel Assistant", layout="centered")
st.title("🚆 Railway Travel Assistant")
st.write("Plan your journey with the **nearest** direct or connecting train.")

# User input
col1, col2 = st.columns(2)
with col1:
    source = st.selectbox("📍 From Station", station_list)
with col2:
    destination = st.selectbox("🏁 To Station", station_list)

default_time = datetime.strptime("08:00", "%H:%M").time()
departure_time_input = st.time_input("⏰ Desired Departure Time", value=default_time, key="departure_time")

# Helper functions
def trains_from_station(station_name):
    return schedules[schedules["station_name"] == station_name]["train_no"].unique()

def get_route(train_no):
    return schedules[schedules["train_no"] == train_no].sort_values(by=["day", "stop_number"])

def time_difference(t1, t2):
    """Returns the absolute difference in minutes between two time objects."""
    dt1 = datetime.combine(datetime.today(), t1)
    dt2 = datetime.combine(datetime.today(), t2)
    return abs((dt1 - dt2).total_seconds() / 60)

# Search logic
if st.button("🔍 Find Trains"):
    if source == destination:
        st.warning("Source and destination must be different.")
    else:
        nearest_train = None
        nearest_diff = float('inf')

        for train_no in trains_from_station(source):
            route = get_route(train_no)
            station_names = route["station_name"].tolist()

            if destination in station_names:
                try:
                    src_info = route[route["station_name"] == source].iloc[0]
                    dest_info = route[route["station_name"] == destination].iloc[0]
                    dep_time_str = src_info['departure_time']
                    dep_time = datetime.strptime(dep_time_str, "%H:%M").time()

                    diff = time_difference(dep_time, departure_time_input)

                    if diff < nearest_diff:
                        nearest_diff = diff
                        nearest_train = {
                            "train_no": train_no,
                            "train_name": trains[trains['train_no'] == train_no]["train_name"].values[0],
                            "departure": dep_time_str,
                            "arrival": dest_info["arrival_time"]
                        }
                except:
                    continue

        if nearest_train:
            st.success(f"✅ Nearest Direct Train Found: {nearest_train['train_no']} - {nearest_train['train_name']}")
            st.write(f"📤 From {source} at {nearest_train['departure']}")
            st.write(f"📥 To {destination} at {nearest_train['arrival']}")
        else:
            st.warning("❌ No direct train found. Searching for alternate routes...")

            suggestions = []

            for mid_station in station_list:
                if mid_station in [source, destination]:
                    continue

                first_legs = []
                second_legs = []

                # Find trains from source to mid
                for train_no in trains_from_station(source):
                    route = get_route(train_no)
                    if mid_station in route["station_name"].values:
                        first_legs.append((train_no, route))

                # Find trains from mid to destination
                for train_no in trains_from_station(mid_station):
                    route = get_route(train_no)
                    if destination in route["station_name"].values:
                        second_legs.append((train_no, route))

                # Match each valid pair
                for t1, r1 in first_legs:
                    try:
                        t1_departure = r1[r1["station_name"] == source].iloc[0]["departure_time"]
                        t1_arrival = r1[r1["station_name"] == mid_station].iloc[0]["arrival_time"]
                        t1_name = trains[trains["train_no"] == t1]["train_name"].values[0]
                    except:
                        continue

                    for t2, r2 in second_legs:
                        try:
                            t2_departure = r2[r2["station_name"] == mid_station].iloc[0]["departure_time"]
                            t2_arrival = r2[r2["station_name"] == destination].iloc[0]["arrival_time"]
                            t2_name = trains[trains["train_no"] == t2]["train_name"].values[0]
                        except:
                            continue

                        # Add every valid connection regardless of time gap
                        suggestions.append({
                            "mid_station": mid_station,
                            "first_train": {
                                "no": t1,
                                "name": t1_name,
                                "from": source,
                                "to": mid_station,
                                "departure": t1_departure,
                                "arrival": t1_arrival
                            },
                            "second_train": {
                                "no": t2,
                                "name": t2_name,
                                "from": mid_station,
                                "to": destination,
                                "departure": t2_departure,
                                "arrival": t2_arrival
                            }
                        })

            if suggestions:
                st.info("🔁 Suggested alternate routes (via 1 intermediate station):")
                for s in suggestions:
                    st.write(f"🔹 Via **{s['mid_station']}**")
                    st.write(f"1️⃣ {s['first_train']['no']} ({s['first_train']['name']}): {s['first_train']['from']} → {s['first_train']['to']} | 🕗 {s['first_train']['departure']} → {s['first_train']['arrival']}")
                    st.write(f"2️⃣ {s['second_train']['no']} ({s['second_train']['name']}): {s['second_train']['from']} → {s['second_train']['to']} | 🕗 {s['second_train']['departure']} → {s['second_train']['arrival']}")
                    st.markdown("---")
            else:
                st.error("❌ No alternate connections found.")
