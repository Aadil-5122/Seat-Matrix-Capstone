import boto3
import logging
from typing import List, Dict

AWS_REGION = 'us-east-1'
logger = logging.getLogger("app_logger")


def update_data_fetch_schedule(item):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('fetch_data_schedule')
    table.put_item(Item=item)


def get_latest_in_out_entry(table_name):
    """
    Fetch the latest entry from the 'in_out' DynamoDB table.
    :return: The latest entry as a dictionary.
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table_name)

    response = table.scan()
    items = response.get('Items', [])

    if not items:
        return None

    latest_entry = max(items, key=lambda x: x['timestamp'])
    return latest_entry


def disable_data_fetcher(uid, app_name=None):
    try:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=AWS_REGION
                                  )
        table = dynamodb.Table('fetch_data_schedule')
        update_expression = 'SET #new_st = :val_st'
        expression_attribute_names = {'#new_st': 'st'}
        expression_attribute_value = {':val_st': 'inactive'}
        table.update_item(
            Key={'uid': uid, 'app_name': app_name},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_value
        )

        logger.info(f"Updated ns for uid={uid}")
        return {'status': 'success'}
    except Exception as e:
        return {
            'status': 'failed',
            'message': e,
            'user_id': uid,
        }


def add_user_to_db(item):
    try:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=AWS_REGION
                                  )
        table = dynamodb.Table('user')
        table.put_item(Item=item)
        logger.info(f"Added user {item['uid']}")
        return {'status': 'success'}
    except Exception as e:
        return {
            'status': 'failed',
            'message': e,
            'user_id': item['uid'],
        }


def dynamodb_scan(table_name, filter_key=None, filter_value=None):
    """
    This function is used to scan the dynamodb table
    :param table_name:  name
    :param filter_key: filter key
    :param filter_value: filter value
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

    table = dynamodb.Table(table_name)
    if filter_key is None:
        response = table.scan()
        return response['Items']
    response = table.scan(
        FilterExpression=filter_key + ' = :val',
        ExpressionAttributeValues={
            ':val': filter_value
        }
    )
    return response['Items']


def put_dynamodb_item(table_name, item, region=AWS_REGION):
    """
    This function is used to update the dynamodb item
    :param table_name: table name
    :param item: item to be updated
    :param region: region
    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region
    )
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)


def delete_dynamodb_item(table_name: str, key_value_pairs: dict, region=AWS_REGION) -> None:
    """
    This function deletes an item from a DynamoDB table based on the primary key.

    Args:
      table_name: The name of the DynamoDB table.
      key_value_pairs: A dictionary containing the primary key attributes and their values.
      region: The AWS region where the DynamoDB table is located (defaults to AWS_REGION).
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    table.delete_item(Key=key_value_pairs)


def delete_dynamodb_item_batch(table_name: str, items: List[Dict[str, str]], region: str = AWS_REGION) -> None:
    """
    This function deletes a batch of items from a DynamoDB table.

    Args:
        table_name (str): The name of the DynamoDB table.
        items (List[Dict[str, str]]): A list of dictionaries, each containing the primary key attributes and their
                                      values for the items to be deleted.
        region (str, optional): The AWS region where the DynamoDB table is located. Defaults to AWS_REGION.

    Returns:
        None
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key=item)


def dynamodb_query(table_name, key_value_pairs, scan_index_forward=True, index_name=None, limit=None,
                   get_whole_content=False):
    """
    This function is used to query the DynamoDB table with multiple keys and values.
    :param table_name: Table name
    :param key_value_pairs: List of key-value pairs, e.g., [('key1', 'value1'), ('key2', 'value2')]
    :param scan_index_forward: Sort the results in ascending order by sort key
    :param index_name: Name of the index to be used for the query
    :param limit: Maximum number of items to be returned
    :param get_whole_content: When true, query all pages to get the whole content
    :return: List of items
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table_name)
    key_conditions = []
    expression_attribute_values = {}

    for key, value in key_value_pairs:
        key_conditions.append(f"{key} = :{key}")
        expression_attribute_values[f":{key}"] = value
    key_condition_expression = ' AND '.join(key_conditions)

    items = []
    last_evaluated_key = None
    fetched_count = 0

    while True:
        query_params = {
            'KeyConditionExpression': key_condition_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ScanIndexForward': scan_index_forward
        }
        if index_name is not None:
            query_params['IndexName'] = index_name
        if limit is not None:
            query_params['Limit'] = limit - fetched_count
        if last_evaluated_key is not None:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = table.query(**query_params)
        items.extend(response.get('Items', []))
        fetched_count += len(response.get('Items', []))
        last_evaluated_key = response.get('LastEvaluatedKey', None)

        if not get_whole_content or last_evaluated_key is None or (limit and fetched_count >= limit):
            break

    return items[:limit] if limit else items


def update_dynamodb_item(table_name, key_value_pairs, update_expression, expression_attribute_value,
                         expression_attribute_names=None, region=AWS_REGION):
    """
    This function is used to update the dynamodb item
    :param table_name: table name
    :param update_expression: dynamodb update expression
    :param expression_attribute_value: dynamodb expression attribute value
    :param expression_attribute_names: dynamodb expression attribute names
    :param key_value_pairs: key value pairs
    :param region: region
    """
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=region
    )

    table = dynamodb.Table(table_name)

    logger.info(f"Updating item in table {table_name} with key {key_value_pairs} using update expression: "
                f"{update_expression}")
    try:
        if expression_attribute_names is not None:
            response = table.update_item(Key=key_value_pairs, UpdateExpression=update_expression,
                                         ExpressionAttributeValues=expression_attribute_value,
                                         ExpressionAttributeNames=expression_attribute_names)
            logger.info(f"Update successful: {response}")
            return response
        response = table.update_item(Key=key_value_pairs, UpdateExpression=update_expression,
                                     ExpressionAttributeValues=expression_attribute_value)
        logger.info(f"Update successful: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to update item in table {table_name} with key {key_value_pairs}: {e}")
        return {
            'status': 'failed',
            'message': str(e),
            'key': key_value_pairs,
        }


def dynamodb_query_with_key_condition_filter(table_name, key_condition_expression, filter_expression, index_name=None,
                                             scan_index_forward: bool = False, get_whole_content: bool = False):
    """
    This function is used to query the DynamoDB table with multiple keys and values.
    :param table_name: Table name
    :param key_condition_expression: Key condition expression
    :param filter_expression: Filter expression
    :param index_name: Name of the index to be used for the query
    :param scan_index_forward: Sort the results in ascending order by sort key
    :param get_whole_content: Get all the content
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table_name)
    items = []
    last_evaluated_key = None

    while True:
        query_params = {
            'KeyConditionExpression': key_condition_expression,
            'FilterExpression': filter_expression,
            'ScanIndexForward': scan_index_forward
        }
        if index_name is not None:
            query_params['IndexName'] = index_name
        if last_evaluated_key is not None:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = table.query(**query_params)
        items.extend(response.get('Items', []))
        last_evaluated_key = response.get('LastEvaluatedKey', None)

        if not get_whole_content or last_evaluated_key is None:
            break

    return items


def dynamodb_scan_with_filter_expression(table_name, filter_expression):
    """
    This function is used to scan the DynamoDB table with multiple keys and values.
    :param table_name: Table name
    :param filter_expression: Filter expression
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression=filter_expression
    )
    return response['Items']


def update_conditional_item(table_name, key, update_expression, expression_values,
                            condition_expression, expression_attribute_names):
    """
    Update an item in the table using optimistic locking.
        :param table_name: The name of the DynamoDB table.
        :param key: The primary key of the item to update.
        :param update_expression: The update expression to apply to the item.
        :param expression_values: The values to substitute into the update expression.
        :param condition_expression: The condition expression to apply to the update operation.
        :param expression_attribute_names: The attribute names to substitute into the condition expression.
    """
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table_name)

    response = table.update_item(
        TableName=table_name,
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ConditionExpression=condition_expression,
        ExpressionAttributeNames=expression_attribute_names,
    )
    logger.info(f"Updated item in table {table_name} with key {key}")
    return response
