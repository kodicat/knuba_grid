import azure.cosmos.documents as doc
import azure.cosmos.exceptions as exceptions
import urllib3
import config
import json

from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobPrefix

# Initialize the Cosmos client
connection_policy = doc.ConnectionPolicy()
# Disable in production
connection_policy.DisableSSLVerification = "true"
# disable ssl certificate warnings
urllib3.disable_warnings()

HOST = config.settings.get('host')
KEY = config.settings.get('key')
DATABASE_ID = config.settings.get('database_id')
AZURE_BLOB_STORAGE_CONNECTION_STRING = config.settings.get('blob_storage_connection_string')
AZURE_BLOB_STORAGE_NAME = config.settings.get('blob_storage_name')
AZURE_BLOB_STORAGE_FILE_NAME = config.settings.get('blob_storage_file_name')

def getOrCreateDatabase(client):
    try:
        database = client.create_database(id=DATABASE_ID, offer_throughput=20000)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))
    except exceptions.CosmosResourceExistsError:
        database = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))
    return database

def getOrCreateContainer(database, container_name, partition_key, unique_key_policy=None):
    container = None
    try:
        if (unique_key_policy == None):
            container = database.create_container(
                id=container_name,
                partition_key=partition_key,
                offer_throughput=5000,
            )
        else:
            container = database.create_container(
                id=container_name,
                partition_key=partition_key,
                offer_throughput=5000,
                unique_key_policy=unique_key_policy
            )
        print('Container with id \'{0}\' created'.format(container_name))
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(container_name)
        print('Container with id \'{0}\' was found'.format(container_name))
    return container

def insert_items(container, items):
    for x in items:
        container.upsert_item(body=x)
    printLastRequestStatistics(container, 'Create item with ' + str(len(items)) + ' items')

def read_item(container, name, model):
    items = container.query_items(
        query='SELECT * FROM c WHERE c.productName = @name AND c.productModel = @model',
        parameters=[{'name': '@name', 'value': name}, {'name': '@model', 'value': model}],
        enable_cross_partition_query=True
    )
    dummy = [item for item in items]
    printLastRequestStatistics(container, 'Query item by model: ' + model + ' and name: ' + name)

def read_all_items(container):
    item_list = list(container.read_all_items(max_item_count=1000))
    printLastRequestStatistics(container, 'Read all items with: ' + str(len(item_list)) + ' items')

def printLastRequestStatistics(container, text):
    headers = container.client_connection.last_response_headers
    print('  Operation: ' + text)
    print('    Duration ms: ', headers['x-ms-request-duration-ms'])
    print('    Rate Units (RU): ', headers['x-ms-request-charge'])
    print()

def cleanUpDatabase(client, database):
    try:
        client.delete_database(database)
    except exceptions.CosmosResourceNotFoundError:
        pass

def create_items(count):
    ids = range(1, count + 1)
    return list(map(lambda i: create_item(i), ids))

def create_item(i):
    id = str(i)
    return {
        'id': id,
        'productName': 'Widget' + id,
        'productModel': 'Model' + id
    }

def run_container(container, items):
    print_container_statistics(container)
    insert_items(container, items)
    read_item(container, 'Widget99', 'Model99')
    read_all_items(container)
    download_blob_and_save(container)
    print('----')

def print_container_statistics(container):
    container_props = container.read()
    print('Container id: ', container_props.get('id'), ', partitionKey: ', container_props.get('partitionKey'), ', uniqueKeyPolicy: ', container_props.get('uniqueKeyPolicy'))

def download_blob_from_storage(blob_storage_name, file_name):
    blob_client = BlobServiceClient.from_connection_string(AZURE_BLOB_STORAGE_CONNECTION_STRING)
    blob_container = next(filter(lambda x: x.name == blob_storage_name, blob_client.list_containers()))
    blob_container_client = blob_client.get_container_client(container=blob_container.name)
    blob_file_descriptor = next(filter(lambda x: x.name == file_name, blob_container_client.list_blobs()))
    blob_file_client = blob_container_client.get_blob_client(blob=blob_file_descriptor.name)
    return blob_file_client.download_blob().readall().decode('utf-8')

def download_blob_and_save(container):
    blob = download_blob_from_storage(blob_storage_name=AZURE_BLOB_STORAGE_NAME, file_name=AZURE_BLOB_STORAGE_FILE_NAME)
    blob_json = json.loads(blob)
    container.upsert_item(body=blob_json)
    printLastRequestStatistics(container, 'Save blob file')

def run():
    try:
        client = CosmosClient(url=HOST, credential=KEY, connection_verify=False, connection_policy=connection_policy)
        database = getOrCreateDatabase(client)

        partition_key1 = PartitionKey(path='/id')
        container_1_100 = getOrCreateContainer(database, container_name="container_1_100", partition_key=partition_key1)
        container_1_1000 = getOrCreateContainer(database, container_name="container_1_1000", partition_key=partition_key1)

        partition_key2 = PartitionKey(path=['/productName', '/productModel'], kind='MultiHash')
        uniqueKeyPolicy = {'uniqueKeys': [{'paths': ['/productName', '/productModel']}]}
        container_2_100 = getOrCreateContainer(database, container_name="container_2_100", partition_key=partition_key2, unique_key_policy=uniqueKeyPolicy)
        container_2_1000 = getOrCreateContainer(database, container_name="container_2_1000", partition_key=partition_key2, unique_key_policy=uniqueKeyPolicy)

        items_100 = create_items(count=100)
        items_1000 = create_items(count=1000)

        run_container(container_1_100, items_100)
        run_container(container_1_1000, items_1000)
        run_container(container_2_100, items_100)
        run_container(container_2_1000, items_1000)

    except exceptions.CosmosHttpResponseError as e:
        print('\n----Error. {0}'.format(e.message))

    finally:
        print("\n run() is done")

    # cleanUpDatabase(client, database)

if __name__ == '__main__':
    run()
