from utils.count import count_students
from ddb_utils import put_dynamodb_item, dynamodb_scan


def add_counts_to_ddb(path):
    counts_data = count_students(path)
    table_name = 'c2'
    # if counts_data.get('in', 0) or counts_data.get('out', 0):
    put_dynamodb_item(table_name, counts_data)

def fetch_counts():
    return dynamodb_scan('in_out')