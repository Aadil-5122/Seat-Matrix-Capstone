import numpy as np
import pandas as pd
import boto3
import time


def generate_sample_data(num_samples=10000):
    np.random.seed(42)
    # Generate timestamps starting from 3pm 19th Dec 2024, decreasing by 1 minute for each sample
    start_timestamp = int(time.mktime(time.strptime("2024-12-19 15:00:00", "%Y-%m-%d %H:%M:%S")))
    timestamps = [start_timestamp - i * 60 for i in range(num_samples)]

    # Generate random total occupancy values between 0 and 240
    total_occupancy = np.random.randint(0, 241, num_samples)

    # Generate random floor data for 5 floors with values between 0 and 64
    floor_data = {str(i): np.random.randint(0, 65, num_samples) for i in range(5)}

    # Create DataFrame
    data = pd.DataFrame({
        "timestamp": [f"{ts}.000000" for ts in timestamps],
        "total_occupancy": total_occupancy,
        "floor_data": [dict(zip(floor_data.keys(), [floor_data[str(i % 5)][j] for i in range(5)])) for j in range(num_samples)]
    })
    return data


def dump_data_to_dynamodb(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Specify your AWS region
    table = dynamodb.Table('occupy_floor')  # Updated table name
    for index, row in data.iterrows():
        item = {
            'timestamp': str(row['timestamp']),
            'total_occupancy': str(row['total_occupancy']),
            'floor_data': str(row['floor_data']),
        }
        table.put_item(Item=item)


def generate_in_out_data(num_samples=10000):
    np.random.seed(42)
    # Generate random timestamps within a recent range
    start_timestamp = int(time.time()) - 10 ** 6  # 1 million seconds ago
    end_timestamp = int(time.time())
    timestamps = np.random.randint(start_timestamp, end_timestamp, num_samples)

    # Generate random 'in' and 'out' values between 0 and 400
    in_values = np.random.randint(0, 401, num_samples)
    out_values = np.random.randint(0, 401, num_samples)

    # Create DataFrame
    data = pd.DataFrame({
        "timestamp": timestamps,
        "in": in_values,
        "out": out_values
    })
    return data


occupy_data = generate_sample_data()
in_out_data = generate_in_out_data()


# dump_data_to_dynamodb(data)


import numpy as np
import pandas as pd
import boto3
import time
from datetime import datetime, timedelta


def generate_sample_data(num_samples=100):
    # Start timestamp at 3 PM on 19th Dec 2024
    start_timestamp = int(datetime(2024, 12, 19, 15, 0).timestamp())
    timestamps = [start_timestamp - i * 25 * 60 for i in range(num_samples)]  # 25 minutes apart

    # Generate random total occupancy values between 0 and 240
    total_occupancy = np.random.randint(0, 241, num_samples)

    # Generate random floor data with values between 0 and 64
    floor_data = [{str(i): np.random.randint(0, 65) for i in range(5)} for _ in range(num_samples)]

    # Create DataFrame
    data = pd.DataFrame({
        "timestamp": [str(ts) for ts in timestamps],
        "total_occupancy": [str(occupancy) for occupancy in total_occupancy],
        "floor_data": [str(floor) for floor in floor_data]  # Convert dict to string for storage
    })
    return data


def dump_data_to_dynamodb1(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Specify your AWS region
    table = dynamodb.Table('occupy_floor1')
    for index, row in data.iterrows():
        item = {
            'timestamp': row['timestamp'],
            'total_occupancy': row['total_occupancy'],
            'floor_data': eval(row['floor_data']),  # Convert string back to dict
        }
        table.put_item(Item=item)


# Generate and dump sample data
# data = generate_sample_data()
# print(data.head(5))
# dump_data_to_dynamodb1(data)


import numpy as np
import pandas as pd
import boto3
from datetime import datetime, timedelta


def generate_in_out_data(num_samples=100):
    # Start timestamp at 3 PM on 19th Dec 2024
    start_timestamp = int(datetime(2024, 12, 19, 15, 0).timestamp())
    timestamps = [start_timestamp - i * 25 * 60 for i in range(num_samples)]  # 25 minutes apart

    # Generate random 'in' values between 0 and 430
    in_values = np.random.randint(0, 431, num_samples)

    # Generate 'out' values that are always less than 'in'
    out_values = [np.random.randint(0, in_value) if in_value > 0 else 0 for in_value in in_values]

    # Create DataFrame
    data = pd.DataFrame({
        "timestamp": [str(ts) for ts in timestamps],
        "in": in_values,
        "out": out_values
    })
    return data


def dump_in_out_data_to_dynamodb(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Specify your AWS region
    table = dynamodb.Table('in_out1')
    for index, row in data.iterrows():
        item = {
            'timestamp': str(row['timestamp']),
            'in': row['in'],
            'out': row['out'],
        }
        table.put_item(Item=item)


# Generate and dump in/out sample data
in_out_data = generate_in_out_data()
dump_in_out_data_to_dynamodb(in_out_data)
