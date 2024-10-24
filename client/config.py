import os

# the key is the a well-known cosmos db emulator key, no need to remove it from repository
settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://cosmos:8081'),
    'key': os.environ.get('ACCOUNT_KEY', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'grid_labs_cosmos'),
}
