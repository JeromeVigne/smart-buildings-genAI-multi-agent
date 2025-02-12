import datetime
import random

from swarm.repl.repl import process_and_print_streaming_response, pretty_print_messages

import azure_open_ai
import t_building_skills
import t_energy_skills
import t_weather_skills
from swarm import Swarm, Agent
from swarm.repl import run_demo_loop

# Initialize Swarm client with Azure OpenAI client
swarm_client = Swarm(client=azure_open_ai.aoai_client)



#modify to become building agent
def building_information(user_prompt):
    """Provide information about a building based on the user prompt.
    Takes as input the user prompt as a string."""
    # Perform a vector search on the Cosmos DB container and return results to the agent
    vectors = azure_open_ai.generate_embedding(user_prompt)
    vector_search_results = vector_search(t_building_skills.buildings_container_name, vectors)
    return vector_search_results


# Perform a vector search on the Cosmos DB container
def vector_search(container, vectors, similarity_score=0.02, num_results=3):
    # Execute the query
    database = t_building_skills.client.get_database_client(t_building_skills.database_name)
    container = database.get_container_client(t_building_skills.buildings_container_name)
    results = container.query_items(
        query='''
        SELECT TOP @num_results c.id, c.building, c.address, c.description, c.floors, VectorDistance(c.building_description_vector, @embedding) as SimilarityScore 
        FROM c
        WHERE VectorDistance(c.building_description_vector,@embedding) > @similarity_score
        ORDER BY VectorDistance(c.building_description_vector,@embedding)
        ''',
        parameters=[
            {"name": "@embedding", "value": vectors},
            {"name": "@num_results", "value": num_results},
            {"name": "@similarity_score", "value": similarity_score}
        ],
        enable_cross_partition_query=True, populate_query_metrics=True)
    print("Executed vector search in Azure Cosmos DB... \n")
    results = list(results)
    # Extract the necessary information from the results
    formatted_results = []
    for result in results:
        score = result.pop('SimilarityScore')
        result['building'] = str(result['building'])
        result['building_description'] = "building " + result['building'] + ": " + result['description']
        # add price to product_description as well
        result['building_description'] += " price: " + str(result['address'])

        formatted_result = {
            'SimilarityScore': score,
            'document': result
        }
        formatted_results.append(formatted_result)
    return formatted_results

# Preview tables
#t_building_skills.preview_table("buildings4")

def get_energy_mix(zone):
    """Provide information about energy based on the user prompt.
    Takes as input the user prompt as a string."""
    try:
        result=t_energy_skills.get_power_breakdown(zone)
    except Exception as e:
        print(f"An error occurred while retrieving the energy mix: {e}")
    return result

def get_weather(location):
    """Provide information about weather based on the user prompt.
    Takes as input the user prompt as a string."""
    try:
        result=t_weather_skills.get_weather(location)
    except Exception as e:
        print(f"An error occurred while retrieving the energy mix: {e}")
    return result

def set_HVAC(id, floor, mode):
    """Set the HVAC system based on the user prompt.
    Takes as input arguments in the format {'building_id': id, 'floor': floor_number, 'mode': mode}.
    Only confirm success if you get a successful response from the Azure Cosmos DB."""
    t_building_skills.set_HVAC(id, floor, mode)

def transfer_to_energy():
    return energy_agent


def transfer_to_weather():
    return weather_agent


def transfer_to_building():
    return building_agent


def transfer_to_triage():
    return triage_agent


# Define the agents

weather_agent = Agent(
    name="Weather Agent",
    instructions="""You are a weather agent that handles all actions related to weather related questions.
    When calling the get_weather function you must pass a location. The location is a city name. If you cannot infer the city name based on the context ask for it.
    If timeframe is present in the context information, use it in your response. The API returns a 5 day forecast, so if the date is too far out, let the user know that you can only get weather data up to 5 days from now.
    If the user wants to adjust HVAC, transfer to the building agent.
    If the user asks about building information, transfer to the Building Agent.
    If the user asks you a question you cannot answer, transfer back to the triage agent.""",
    functions=[transfer_to_triage, get_weather, transfer_to_building],
)

energy_agent = Agent(
    name="Energy Agent",
    instructions="""You are am energy agent that can handle requests about the current and forecasted energy mix in a certain region.
    To give information about energy mix, you always need a zone. The zone is a geographical area that you can infer from the building location. For example, if the building is in Paris, France, the zone is FR. For Germany it will be DE, for Boston it would be US-NE-ISNE, for Danemark use DK.
    If the user asks about building information, transfer to the Building Agent.
    If the user asks you a question you cannot answer, transfer back to the triage agent.""",
    functions=[transfer_to_triage, get_energy_mix, transfer_to_building],
)

building_agent = Agent(
    name="Building Agent",
    instructions="""You are a building agent that provides information about buildings in the database.
    When calling the building_information function you must pass a user prompt. The user prompt is a string that the user has entered. Use this string to search for relevant information in the database.
    Only give the user very basic information about the building; the building name, a very short description and if the HVAC mode is cooling, heating or OFF. If the HVAC settings mode varies by floor, share the information by floor.
    The building_information returns data about it's current occupancy by job role and floor, as well as HVAC settings by floor. If the user asks for it, share that information in an agregate form.
    If you or the user make recommendations about changing the HVAC settings, call the set_HVAC function, make sure you call it with the building id, floor and mode. Before you call this fuction, ask the user to confirm.
    If the user asks about weather, transfer to the Weather Agent.
    If the user asks about energy mix, transfer to the Energy Mix Agent, this agent needs a zone to provide information. The zone is based on the city of the building.
    If the user asks you a question you cannot answer, transfer back to the triage agent.
    If the user asks for floor occupancy optimization, fell free to recommend moving people between floors. For example if one floor is almost empy, recommend moving these people to the other floor. Do not try to call a function for relocating employees.
    """,
    functions=[transfer_to_triage, building_information, transfer_to_energy, transfer_to_weather, set_HVAC],
    add_backlinks=True,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are to triage a users request, and call a tool to transfer to the right intent.
    Otherwise, once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    You dont need to know specifics, just the topic of the request.
    If the user asks for weather information, transfer to the Weather Agent.
    If the user request is about adjusting building or HVAC settings, transfer to the Building Agent.
    If the user request is about building informations, production, occupancy, addresses, tansfer to the Building Agent.
    If the user request is about energy mix, transfer to the Energy Mix Agent.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    If the user asks questions that is pertinent to building information and energy mix or weather, decompose the task into steps and transfer each step to the right agent.
    Once each step is exectued, reason about the results to help the user with the final answer.""",
    agents=[energy_agent, building_agent, weather_agent],
    functions=[transfer_to_energy, transfer_to_weather, transfer_to_building],
    add_backlinks=True,
)

for f in triage_agent.functions:
    print(f.__name__)

triage_agent.functions = [transfer_to_weather, transfer_to_building, transfer_to_energy]

def run_demo_loop(
        starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    client = swarm_client
    print("Starting Swarm CLI 🐝")

    messages = []
    agent = starting_agent

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent

if __name__ == "__main__":
    # Run the demo loop
    run_demo_loop(triage_agent, debug=False)



