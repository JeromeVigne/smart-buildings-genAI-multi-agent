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

def add_building(building_id, building_name, building_description, address, floors):
    database = client.get_database_client(database_name)
    container = database.get_container_client(buildings_container_name)
    building_description_vector = azure_open_ai.generate_embedding(building_description)
    building = {
        "id": str(building_id),
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
        ("hq01", "HQ", "Headquarters of the company. Located in Paris France, this is a three floor corporate building with sales, fincance and engineering.", "27 avenue de Tourville, Paris, France", [
        {
          "floor_number": 1,
          "occupancy": 50,
          "roles": [
            {
              "role": "Finance",
              "count": 10
            },
            {
              "role": "Engineering",
              "count": 40
            }
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
          "roles": [
            {
              "role": "Sales",
              "count": 10
            },
            {
              "role": "Finance",
              "count": 10
            },
            {
              "role": "Engineering",
              "count": 20
            }
          ],
          "hvac_settings": {
            "temperature": 21,
            "humidity": 50,
            "mode": "cooling"
          }
        },
        {
          "floor_number": 3,
          "occupancy": 30,
          "roles": [
            {
              "role": "Sales",
              "count": 25
            },
            {
              "role": "Finance",
              "count": 5
            }
          ],
          "hvac_settings": {
            "temperature": 23,
            "humidity": 40,
            "mode": "cooling"
          }
        }
      ]),
      ("prod01", "Production", "Production facility located in Hamburg, Germany. This is a two floor building with production, logistics and finance. The production floor contains a lot of specialized machinery. This site has likely the highest energy consumption impact out of all our global sites.", "Hochallee 27, Hamburg, Germany", 
       [
           {
          "floor_number": 1,
          "occupancy": 300,
          "roles": [
            {
              "role": "Production",
              "count": 260
            },
            {
              "role": "Engineering",
              "count": 40
            }
          ],
          "hvac_settings": {
            "temperature": 22,
            "humidity": 45,
            "mode": "heating"
          }
        },
        {
          "floor_number": 2,
          "occupancy": 120,
          "roles": [
            {
              "role": "Production",
              "count": 20
            },
            {
              "role": "Logicstics",
              "count": 80
            },
            {
              "role": "Finance",
              "count": 20
            }
          ],
          "hvac_settings": {
            "temperature": 21,
            "humidity": 50,
            "mode": "heating"
          }
        }
    ]
      ),("res003", "Research", "Research facility located in Boston, MA, USA. This is a two floor building with research, engineering and sales. The research floor contains expensive lab machinery.", "73 Fulton Street, Boston, MA, USA", [
          {
          "floor_number": 1,
          "occupancy": 120,
          "roles": [
            {
              "role": "Engineering",
              "count": 120
            }
          ],
          "hvac_settings": {
            "temperature": 22,
            "humidity": 45,
            "mode": "heating"
          }
        },
        {
          "floor_number": 2,
          "occupancy": 17,
          "roles": [
            {
              "role": "Logicstics",
              "count": 5
            },
            {
              "role": "Sales",
              "count": 12
            }
          ],
          "hvac_settings": {
            "temperature": 21,
            "humidity": 50,
            "mode": "heating"
          }
        }
      ]
      )
      ]

    for building in initial_buildings:
        print(f"Adding building {building[1]}")
        add_building(*building)

create_buildings()