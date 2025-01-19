import os
import azure_open_ai
from dotenv import load_dotenv

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential

#load variables
load_dotenv()

# Initialize the Cosmos client
# reference environment variables for the values of these variables
credential = DefaultAzureCredential()
endpoint = os.environ['AZURE_COSMOSDB_ENDPOINT']
key = os.environ['AZURE_COSMOSDB_KEY']
client = CosmosClient(endpoint, credential=credential)

# Database and container names
database_name = "smart-building"
buildings_container_name = "buildings2"

def preview_table(container_name):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    items = container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    )
    for item in items:
        if (container_name == buildings_container_name):
            # redact the product description vector
            item.pop("product_description_vector", None)
        print(item)