from loading.data_loader import load_data
import loading.data_loader as data_loader
from loading.save_parser import *
from models.pokemon import Pokemon
from engine.battle_state import BattleState
from random import seed

load_data()
seed()

save_file = load_save("backend/loading/test.sav")
party_count = get_party_count(save_file)
species = get_party_species(save_file, party_count)
data = parse_party_pokemon(save_file, party_count)
team : list[Pokemon] = build_party(species, data)
trainer_name : str = parse_trainer_name(save_file)
rival_name : str = parse_rival_name(save_file)

def print_team():
    print(f"\n{trainer_name}'s TEAM:")
    for team_member in team:
        print(f"{team_member.nickname} the {team_member.species.upper()}: Lv. {team_member.level}")
        print(f"\t[{team_member.moves[0].name}]\t[{team_member.moves[1].name}]")
        print(f"\t[{team_member.moves[2].name}]\t[{team_member.moves[3].name}]")
        print(f"EVs: {list(team_member.evs.values())}")
        print(f"DVs: {list(team_member.dvs.values())}\n")



battle = BattleState(
    [
        Pokemon("venusaur", 64, ["solar beam", "sleep powder", "growth", "mega drain"]),
        Pokemon("ninetales", 59, ["flamethrower", "quick attack", "hyper beam", "swift"]),
        Pokemon("lapras", 61, ["surf", "dragon rage", "confuse ray", "ice beam"]),
        Pokemon("jolteon", 61, ["thunder wave", "thunderbolt", "pin missile", "double kick"]),
        Pokemon("hypno", 62, ["psywave", "psychic", "hypnosis", "toxic"]),
        Pokemon("marowak", 60, ["bonemerang", "thrash", "earthquake", "leer"])
    ],# team,
    [
        Pokemon("pidgeot", 61, ["wing attack", "mirror move", "sky attack", "whirlwind"]),
        Pokemon("alakazam", 59, ["psybeam", "psychic", "reflect", "recover"]),
        Pokemon("rhydon", 61, ["leer", "tail whip", "fury attack", "horn drill"]),
        # Pokemon("arcanine", 61, ["roar", "leer", "ember", "take down"]),
        Pokemon("gyarados", 63, ["dragon rage", "hydro pump", "hyper beam", "leer"]),
        Pokemon("exeggutor", 61, ["hypnosis", "barrage", "stomp"]),
        # Pokemon("blastoise", 65, ["hydro pump", "blizzard", "bite", "withdraw"])
        Pokemon("charizard", 65, ["fire blast", "rage", "slash", "fire spin"])
    ], 
        trainer_name,
        rival_name,
        (1,3),
        True
)

battle.start_simulation(500)