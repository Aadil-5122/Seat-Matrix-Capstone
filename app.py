import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import json

from utils.analytics import fetch_stats, add_seat_occupancy_to_ddb
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Dict

from utils.analytics import add_counts_to_ddb, fetch_stats
from ddb_utils import get_latest_in_out_entry
from constants import floors, seats
from models import Seat, Floor, Statistic

from utils.count import count_students

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demonstration
in_out_records = []


def convert_timestamp_to_readable(timestamp: str) -> str:
    timestamp_float = float(timestamp)
    dt_object = datetime.fromtimestamp(timestamp_float)
    readable_format = dt_object.strftime("%A, %B %d, %Y, %I:%M %p")
    return readable_format


# Endpoints
@app.get("/floors/", response_model=List[Floor])
def read_floors():
    return floors


@app.get("/seats/", response_model=List[Seat])
def read_seats(floor_id: int):
    seats_list = []
    file_path = f"seat_occupancy/seats{floor_id}.json"
    with open(file_path, 'r') as file:
        seats_json = json.load(file)
    for seat_number in range(len(seats_json)):
        seat = seats_json[seat_number]
        seats_list.append(Seat(id = seat.get("id"), number=seat_number, floor_id = floor_id,
                          is_occupied= True if seat.get("status") is 'occupied' else False))

    add_seat_occupancy_to_ddb()

    return seats_list


@app.get("/in-out-status/", response_model=Dict)
def realtime_in_out_status():
    readable_timestamp = ''
    latest_entry = get_latest_in_out_entry('in_out')
    timestamp = latest_entry.get('timestamp', '')
    if timestamp:
        readable_timestamp = convert_timestamp_to_readable(timestamp)
    latest_entry['timestamp'] = readable_timestamp
    return latest_entry if latest_entry else {"message": "No entries found."}


@app.get("/total-occupancy-status/", response_model=Dict)
def realtime_total_occupancy_status():
    """This function will return total_occupancy, timestamp, and occupancy of each floor"""
    readable_timestamp = ''
    latest_entry = get_latest_in_out_entry('occupy_floor')
    timestamp = latest_entry.get('timestamp', '')
    if timestamp:
        readable_timestamp = convert_timestamp_to_readable(timestamp)
    latest_entry['timestamp'] = readable_timestamp
    return latest_entry if latest_entry else {"message": "No entries found."}


@app.get("/in-out/", response_model=List[Dict[str, int]])
def read_in_out():
    # Aggregate data by hour
    hourly_data = {}
    for record in in_out_records:
        hour = record.timestamp.strftime('%H:00 - %H:59')
        if hour not in hourly_data:
            hourly_data[hour] = {"hour": hour, "entries": 0, "exits": 0}
        if record.is_entry:
            hourly_data[hour]["entries"] += 1
        else:
            hourly_data[hour]["exits"] += 1

    # Return sorted hourly data
    return sorted(hourly_data.values(), key=lambda x: x["hour"])


@app.get("/statistics/", response_model=Statistic)
def read_statistics():
    total_capacity = len(seats)
    occupied_seats = sum(1 for seat in seats if seat.is_occupied)
    current_occupancy_rate = (occupied_seats / total_capacity) * 100 if total_capacity > 0 else 0
    return Statistic(
        total_capacity=total_capacity,
        average_occupancy_time=2.5,  # Placeholder value
        current_occupancy_rate=current_occupancy_rate
    )


@app.get("/seat-occupancy/")
def get_seat_occupancy():
    total_seats = len(seats)
    occupied_seats = sum(1 for seat in seats if seat.is_occupied)
    occupancy_rate = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
    return {
        "total_seats": total_seats,
        "occupied_seats": occupied_seats,
        "occupancy_rate": occupancy_rate
    }


@app.get("/get-stats")
def get_stats(stats_type: str):
    return fetch_stats(stats_type)


@app.get("/analytics/")
def get_analytics():
    total_entries = sum(1 for record in in_out_records if record.is_entry)
    total_exits = sum(1 for record in in_out_records if not record.is_entry)
    current_occupancy = total_entries - total_exits
    occupancy_rate = get_seat_occupancy()["occupancy_rate"]

    return {
        "total_entries": total_entries,
        "total_exits": total_exits,
        "current_occupancy": current_occupancy,
        "occupancy_rate": occupancy_rate
    }


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
