import boto3
import datetime
from decimal import Decimal
from collections import defaultdict

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def query_nearest_entries(table, timestamp):
    """
    Query DynamoDB table for the nearest entry to the given timestamp.
    """
    response = table.scan()
    items = response['Items']
    # Find the nearest timestamp
    nearest_item = min(
        items,
        key=lambda item: abs(float(item['timestamp']) - float(timestamp))
    )
    return nearest_item


def aggregate_data(hourly_data, period):
    """
    Aggregate data based on the specified period (daily, weekly, etc.).
    """
    aggregated = defaultdict(int)
    for entry in hourly_data:
        timestamp = datetime.datetime.fromtimestamp(float(entry['timestamp']))
        if period == 'daily':
            key = timestamp.strftime('%Y-%m-%d')
        elif period == 'weekly':
            key = f"Week {timestamp.isocalendar()[1]}"
        elif period == 'monthly':
            key = timestamp.strftime('%b')
        elif period == 'yearly':
            key = timestamp.year
        aggregated[key] += int(entry['value'])

    # Format data for frontend
    return [{'label': k, 'visitors': v} for k, v in aggregated.items()]


def generate_graph_data():
    # Define your DynamoDB table names
    occupancy_table = dynamodb.Table('occupy_floor1')
    movement_table = dynamodb.Table('in_out1')

    # Define start and end times for your data range
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=365)  # Past year data

    # Generate hourly timestamps within the range
    hourly_timestamps = [
        start_time + datetime.timedelta(hours=i)
        for i in range(int((now - start_time).total_seconds() // 3600))
    ]

    # Fetch hourly data
    hourly_data = []
    for timestamp in hourly_timestamps:
        epoch_time = timestamp.timestamp()
        occupancy_entry = query_nearest_entries(occupancy_table, epoch_time)
        movement_entry = query_nearest_entries(movement_table, epoch_time)

        # Add to hourly data
        hourly_data.append({
            'timestamp': epoch_time,
            'total_occupied': int(occupancy_entry['total_occupancy']),
            'in': int(movement_entry['in']),
            'out': int(movement_entry['out']),
            'floor_data': str(eval(str(occupancy_entry['floor_data'])))  # Convert string to dict
        })

    # Aggregate data
    daily_data = aggregate_data(hourly_data, 'daily')
    weekly_data = aggregate_data(hourly_data, 'weekly')
    monthly_data = aggregate_data(hourly_data, 'monthly')
    yearly_data = aggregate_data(hourly_data, 'yearly')

    # Return data in the required format
    return {
        'hourly': hourly_data,
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data,
        'yearly': yearly_data,
    }


# Example usage
if __name__ == "__main__":
    data = generate_graph_data()
    print(data)
