import numpy as np
import pandas as pd
import boto3
import time


def generate_sample_data(num_samples=1000):
    np.random.seed(42)
    # Generate random timestamps within a recent range
    start_timestamp = int(time.time()) - 10 ** 6  # 1 million seconds ago
    end_timestamp = int(time.time())
    timestamps = np.random.randint(start_timestamp, end_timestamp, num_samples)

    # Generate random occupancy values between 0 and 112
    occupancy = np.random.randint(0, 113, num_samples)

    # Create DataFrame
    data = pd.DataFrame({"timestamp": timestamps, "occupancy": occupancy})
    return data


data = generate_sample_data()
data.to_csv('sample_data.csv')
print(data.head())


# import numpy as np
# import pandas as pd
# import time


def generate_in_out_data(num_samples=1000):
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


# Example usage
# data = generate_in_out_data()
# data.to_csv('sample_data_in_out.csv')
# print(data.head())


def dump_data_to_dynamodb(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Specify your AWS region
    table = dynamodb.Table('data_occupancy')
    for index, row in data.iterrows():
        item = {
            'timestamp': str(row['timestamp']),
            'in': str(row['in']),
            'out': str(row['out']),
        }
        table.put_item(Item=item)


dump_data_to_dynamodb(data)
