from ddb_utils import dynamodb_scan, put_dynamodb_item
import json
import time

def add_seat_occupancy_to_ddb():
    response_ddb = {
        "timestamp": time.time(),
    }
    for floor_id in range(0,5):
        occupied_seats = 0
        file_path = f"seat_occupancy/seats{floor_id}.json"
        with open(file_path, 'r') as file:
            seats_json = json.load(file)
        for seat in seats_json:
            if seat.get('status') == 'occupied':
                occupied_seats +=1
        response_ddb['floor_data'][floor_id] = occupied_seats

    with open('seat_occupancy/total_occupancy.json', 'r') as file:
        total_occupancy = json.load(file)

    response_ddb['total_occupancy'] = total_occupancy

    put_dynamodb_item('occupy_floor1', response_ddb)

def fetch_stats(stats_type: str):
    stats = []
    if stats_type == 'occupancy':
        stats = dynamodb_scan('data_occupancy')
    elif stats_type == 'count':
        stats = dynamodb_scan('in_out')

    return stats