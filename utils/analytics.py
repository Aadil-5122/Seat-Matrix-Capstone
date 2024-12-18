from ddb_utils import dynamodb_scan


def fetch_stats(stats_type: str):
    stats = []
    if stats_type == 'occupancy':
        stats = dynamodb_scan('data_occupancy')
    elif stats_type == 'count':
        stats = dynamodb_scan('in_out')

    return stats