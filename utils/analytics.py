from utils.count import count_students
from ddb_utils import put_dynamodb_item, dynamodb_scan


def add_counts_to_ddb(path):
    counts_data = count_students(path)
    table_name = 'in_out'
    # if counts_data.get('in', 0) or counts_data.get('out', 0):
    put_dynamodb_item(table_name, counts_data)


def fetch_stats(stats_type: str):
    if stats_type == 'occupancy':
        stats = dynamodb_scan('data_occupancy')
    elif stats_type == 'count':
        stats = dynamodb_scan('in_out')

    return stats