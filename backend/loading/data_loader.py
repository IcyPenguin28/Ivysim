import json

POKEMON_DATA : dict = {}
MOVE_DATA : dict = {}
TYPE_DATA : dict = {}
TRAINER_DATA : dict = {}

def load_data():

    global POKEMON_DATA, MOVE_DATA, TYPE_DATA, TRAINER_DATA

    with open("data/pkmn.json") as f:
        try:
            POKEMON_DATA = json.load(f)
            # print("Successfully loaded Pokemon data")
        except Exception as e:
            print(f"Could not load Pokemon data: {e}")

    with open("data/moves.json") as f:
        try:
            MOVE_DATA = json.load(f)
            # print("Successfully loaded move data")
        except Exception as e:
            print(f"Could not load move data: {e}")

    with open("data/types.json") as f:
        try:
            TYPE_DATA = json.load(f)
            # print("Successfully loaded type data")
        except Exception as e:
            print(f"Could not load type data: {e}")
    
    with open("data/trainers.json") as f:
        try:
            TRAINER_DATA = json.load(f)
            # print("Successfully loaded trainer data")
        except Exception as e:
            print(f"Could not load type data: {e}")