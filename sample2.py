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


data = generate_sample_data()
dump_data_to_dynamodb(data)
