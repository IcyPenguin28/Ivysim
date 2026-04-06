from fastapi import FastAPI, HTTPException, UploadFile, File, responses
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from engine.battle_state import BattleState, Trainer
from ai.enemy_ai import EnemyAI
from models.pokemon import Pokemon, DEFAULT_DVS, DEFAULT_EVS
from models.move import Move
import loading.data_loader as data_loader
import json
from contextlib import asynccontextmanager
from random import seed
from urllib.parse import unquote
from loading.save_parser import parse_full_save

simulating : bool = False
current_battle : int = 0
num_battles : int = 0


# Pydantic models
class PokemonSet(BaseModel):
    species: str
    level: int = Field(...,ge=1, le=100)
    moves: list[str]
    nickname: Optional[str] = ""
    dvs: Optional[list[int]] = None
    evs: Optional[list[int]] = None

class MoveSet(BaseModel):
    moves: list[str] = Field(...,max_length=4)

class TeamRequest(BaseModel):
    team: list[PokemonSet] = Field(...,max_length=6)

class SimulationRequest(BaseModel):
    player_team: list[PokemonSet]
    player_name: str
    rival_name: str
    enemy_trainer_id: str
    num_battles: int = 250

# Utility functions
def build_pokemon(data: PokemonSet) -> Pokemon:
    try:
        print("BUILDING:", data.species, data.moves)

        stats_keys = ["hp", "attack", "defense", "special", "speed"]
        evs = dict(zip(stats_keys, data.evs)) if data.evs else DEFAULT_EVS
        dvs = dict(zip(stats_keys, data.dvs)) if data.dvs else DEFAULT_DVS

        mon = Pokemon(
            data.species,
            data.level,
            data.moves,
            data.nickname,
            evs,
            dvs
        )
        return mon

    except Exception as e:
        print("FAILED POKEMON:", data.species)
        print("MOVES:", data.moves)
        print("ERROR:", e)
        raise HTTPException(status_code=400, detail=str(e))


def load_trainer(trainer_id : str, rival_name : str = "BLUE") -> Trainer:
    try:
        data = data_loader.TRAINER_DATA[trainer_id]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Handle custom rival name
    name = ""

    if data["name"] == "BLUE":
        final_name = rival_name if rival_name else data["name"]
    else:
        final_name = data["name"]

    name = final_name if not data["class"] else f"{data['class']} {final_name}"
    
    

    team = []
    for mon in data["team"]:
        team.append(
            Pokemon(
                mon["species"],
                mon["level"],
                mon["moves"]
            )
        )
    
    return Trainer(team, name, EnemyAI(data["categories"]))


def build_team(team_data : list[PokemonSet]) -> list[Pokemon]:
    return [build_pokemon(p) for p in team_data]


def load_entire_dex() -> list:
    try:
        data = data_loader.POKEMON_DATA
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return data


def load_dex_entry(pokemon : str):
    try:
        data = data_loader.POKEMON_DATA[pokemon]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return data


# Set up the app
@asynccontextmanager
async def lifespan(app : FastAPI):
    data_loader.load_data()
    seed()

    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174"
]

# CORS Middleware to allow SOP
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


# Define endpoints
@app.get("/")
def root():
    return {"message": "Ivysim API is running"}


@app.get("/trainers")
def get_trainers():
    return [
        {"id": tid, "name": (data["class"] + " " + data["name"] if data["class"] else data["name"]), "team": data["team"], "categories": data["categories"]} for tid, data in data_loader.TRAINER_DATA.items()
    ]


@app.get("/trainer/{trainer_id}")
def get_trainer(trainer_id : str):
    trainer = load_trainer(trainer_id)
    return {
        "name": trainer.trainer_name,
        "team": [
            {
                "species": mon.species,
                "level": mon.level,
                "moves": [m.name for m in mon.moves]
            }
            for mon in trainer.team
        ],
        "categories": data_loader.TRAINER_DATA[trainer_id]["categories"]
    }


@app.get("/pokemon")
def get_all_pokemon():
    return load_entire_dex()


@app.get("/pokemon/{name}")
def get_pokemon(name : str):
    return load_dex_entry(name)


@app.get("/moves")
def get_all_moves():
    try:
        data = data_loader.MOVE_DATA
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return data


@app.get("/moves/{name}")
def get_move(name : str):
    try:
        data = data_loader.MOVE_DATA[unquote(name)]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return data


@app.post("/simulate")
def simulate(request: SimulationRequest):
    # print(request.model_dump())
    player_team = build_team(request.player_team)

    enemy = load_trainer(request.enemy_trainer_id, request.rival_name)
    enemy_data = data_loader.TRAINER_DATA[request.enemy_trainer_id]
    cats = enemy_data["categories"]

    battle = BattleState(
        player_team,
        enemy.team,
        request.player_name,
        enemy.trainer_name,
        cats,
        True
    )

    global simulating, current_battle, num_battles

    simulating = True
    current_battle = 0
    num_battles = request.num_battles

    def progress_callback(i):
        global current_battle
        current_battle = i

    results = battle.start_simulation(request.num_battles, progress_callback=progress_callback)

    simulating = False

    return results


@app.get("/simulation-progress")
def get_progress():
    if not simulating or num_battles == 0:
        return {"progress": 0}

    return {
        "progress": current_battle / num_battles,
        "current": current_battle,
        "total": num_battles
    }


@app.get("/download-log")
def download_log(f : str):
    path = f"logs/{f}"
    return responses.FileResponse(path, media_type='text/plain', filename=f)

@app.post("/load-save")
async def load_save(file : UploadFile=File(...)):
    try:
        contents = await file.read()

        if len(contents) < 0x8000:
            raise HTTPException(status_code=400, detail="Invalid file size.")
        
        parsed_data = parse_full_save(contents)
        return parsed_data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")