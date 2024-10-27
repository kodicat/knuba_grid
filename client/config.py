import os

# the key is the a well-known cosmos db emulator key, no need to remove it from repository
settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://cosmos:8081'),
    'key': os.environ.get('ACCOUNT_KEY', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'grid_labs_cosmos'),
    'blob_storage_connection_string': os.environ.get('AZURE_BLOB_STORAGE_CONNECTION_STRING', 'your_connection_string'),
    'blob_storage_name': os.environ.get('AZURE_BLOB_STORAGE_NAME', 'yukhymchuk-blob-storage'),
    'blob_storage_file_name': os.environ.get('AZURE_BLOB_STORAGE_FILE_NAME', 'blob.json'),
}
