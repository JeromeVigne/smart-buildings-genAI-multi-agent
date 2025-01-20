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
buildings_container_name = "buildings4"

def preview_table(container_name):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    items = container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    )
    for item in items:
        if (container_name == buildings_container_name):
            # redact the building description vector
            item.pop("building_description_vector", None)
        print(item)


def set_HVAC(id, floor, mode):
    """Set the HVAC system based on the user prompt.
     Takes as input arguments in the format {'building_id': id, 'floor': floor_number, 'mode': mode}.
     Only confirm success if you get a successful response from the Azure Cosmos DB."""
    database = client.get_database_client(database_name)
    container = database.get_container_client(buildings_container_name)
    try:
        building = container.read_item(item=id, partition_key='building')
        for fl in building['floors']:
            if fl['floor_number'] == int(floor):
                fl['hvac_settings']['mode'] = mode
        container.replace_item(item=building, body=building)
    except exceptions.CosmosHttpResponseError as e:
        print(f"An error occurred: {e.message}")
