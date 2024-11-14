## Running
docker compose up -d cosmos

### Wait some time :)
docker compose up --build client

### Cosmos DB Emulator link
https://localhost:8081/_explorer/index.html

### Make sure that 'blob_storage_connection_string'
Change blob_storage_connection_string in [config](./client/config.py) file