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

def add_building(building_id, type, building_name, building_description, address, floors):
    database = client.get_database_client(database_name)
    container = database.get_container_client(buildings_container_name)
    building_description_vector = azure_open_ai.generate_embedding(building_description)
    building = {
        "id": str(building_id),
        "type": type,
        "building": building_name,
        "address": address,
        "description": building_description,
        "floors": floors,
        "building_description_vector": building_description_vector
    }
    try:
        container.create_item(body=building)
    except exceptions.CosmosHttpResponseError as e:
        print(f"An error occurred: {e.message}")

def create_buildings():
    initial_buildings = [
        ("hq01", "building","Headquarters", "Headquarters of the company. Located in Paris France, this is a three floor corporate building with sales, finance and engineering.", "27 avenue de Tourville, Paris, France", [
            {
                "floor_number": 1,
                "occupancy": 50,
                "capacity": 90,
                "roles": [
                    {"role": "Sales", "count": 20},
                    {"role": "Finance", "count": 15},
                    {"role": "Engineering", "count": 15}
                ],
                "hvac_settings": {
                    "temperature": 22,
                    "humidity": 45,
                    "mode": "cooling"
                }
            },
            {
                "floor_number": 2,
                "occupancy": 40,
                "capacity": 90,
                "roles": [
                    {"role": "Sales", "count": 10},
                    {"role": "Finance", "count": 10},
                    {"role": "Engineering", "count": 20}
                ],
                "hvac_settings": {
                    "temperature": 21,
                    "humidity": 50,
                    "mode": "heating"
                }
            },
            {
                "floor_number": 3,
                "occupancy": 30,
                "capacity": 90,
                "roles": [
                    {"role": "Sales", "count": 5},
                    {"role": "Finance", "count": 10},
                    {"role": "Engineering", "count": 15}
                ],
                "hvac_settings": {
                    "temperature": 23,
                    "humidity": 40,
                    "mode": "cooling"
                }
            }
        ]),
        ("prod01", "building", "Production Site", "Production site located in Hamburg, Germany. This site houses a lot of specilized machinery. This site focuses on manufacturing and assembly.", "Industriestrasse 12, Hamburg, Germany", [
            {
                "floor_number": 1,
                "occupancy": 100,
                "capacity": 120,
                "roles": [
                    {"role": "Engineering", "count": 20},
                    {"role": "Finance", "count": 10},
                    {"role": "Production", "count": 70}
                ],
                "hvac_settings": {
                    "temperature": 20,
                    "humidity": 55,
                    "mode": "cooling"
                }
            }
        ]),
        ("prod02", "building", "Production Site", "Production site located in Aalborg, Denmark. This site focuses on manufacturing and shipping.", "Fabriksvej 1, Aalborg, Denmark", [
            {
                "floor_number": 1,
                "occupancy": 80,
                "capacity": 100,
                "roles": [
                    {"role": "Engineering", "count": 10},
                    {"role": "Logistics", "count": 5},
                    {"role": "Production", "count": 65}
                ],
                "hvac_settings": {
                    "temperature": 19,
                    "humidity": 50,
                    "mode": "heating"
                }
            }
        ]),
        ("res01", "building", "Research Building", "Research building located in Boston, USA. This site focuses on research and development.", "123 Research Parkway, Boston, USA", [
            {
                "floor_number": 1,
                "occupancy": 60,
                "capacity": 80,
                "roles": [
                    {"role": "Engineering", "count": 40},
                    {"role": "Finance", "count": 10},
                    {"role": "Sales", "count": 10}
                ],
                "hvac_settings": {
                    "temperature": 20,
                    "humidity": 50,
                    "mode": "cooling"
                }
            },
            {
                "floor_number": 2,
                "occupancy": 40,
                "capacity": 60,
                "roles": [
                    {"role": "Engineering", "count": 30},
                    {"role": "Finance", "count": 5},
                    {"role": "Sales", "count": 5}
                ],
                "hvac_settings": {
                    "temperature": 21,
                    "humidity": 45,
                    "mode": "heating"
                }
            }
        ])
    ]

    for building in initial_buildings:
        print(f"Adding building {building[1]}")
        add_building(*building)

        for building in initial_buildings:
            print(f"Adding building {building[1]}")
            add_building(*building)

create_buildings()