from enum import Enum
from .move import Move
from math import floor, sqrt
import loading.data_loader as data_loader

class Stats(Enum):
    HP=0
    ATTACK=1
    DEFENSE=2
    SPECIAL=3
    SPEED=4

class Stages(Enum):
    ATTACK=0
    DEFENSE=1
    SPECIAL=2
    SPEED=3
    ACCURACY=4
    EVASION=5

DEFAULT_DVS = {
    "hp": 7,
    "attack": 7,
    "defense": 7,
    "special": 7,
    "speed": 7
}

DEFAULT_EVS = {
    "hp": 32768,
    "attack": 32768,
    "defense": 32768,
    "special": 32768,
    "speed": 32768
}


class Pokemon:
    species : str
    nickname : str
    level : int
    types : list[str]
    base_stats: list[int]
    stats : list[int]
    evs: dict
    dvs: dict
    current_hp : int
    status : str
    stages: list[int]
    moves : list[Move]

    flinching : bool
    seeded : bool
    mist_active : bool
    toxic_counter : int
    afflicted_turns : int

    mimic_slot : int
    mimic_move : Move

    charge_turns : int
    charging_move : Move

    locked_turns : int
    locked_move : Move

    focusing : bool

    semi_invulnerable_state : str

    trapped_turns : int
    trap_damage : int

    recharge_turns : int

    bide_damage : int
    bide_turns : int

    counter_damage : int

    substitute_hp : int
    substitute_broken : bool

    # Transform vars
    original_species : str
    original_types : list[str]
    original_stats : list[int]
    original_moves : list[Move]


    def __init__(self, species : str, level : int, moves : list[str], nickname="", evs =DEFAULT_EVS, dvs=DEFAULT_DVS):
        self.species = species.lower()
        self.nickname = nickname if nickname else species.upper()
        self.level = level
        self.types = self.load_types()

        self.base_stats = self.load_base_stats()
        self.evs = evs
        self.dvs = dvs
        
        # Get true stats
        _hp = self.calculate_hp(self.base_stats[Stats.HP.value], level, self.dvs["hp"], self.evs["hp"])
        _atk = self.calculate_stat(self.base_stats[Stats.ATTACK.value], level, self.dvs["attack"], self.evs["attack"])
        _def = self.calculate_stat(self.base_stats[Stats.DEFENSE.value], level, self.dvs["defense"], self.evs["defense"])
        _spc = self.calculate_stat(self.base_stats[Stats.SPECIAL.value], level, self.dvs["special"], self.evs["special"])
        _spd = self.calculate_stat(self.base_stats[Stats.SPEED.value], level, self.dvs["speed"], self.evs["speed"])
        
        self.stats = [
            _hp,
            _atk,
            _def,
            _spc,
            _spd
        ]

        self.moves = []
        for move in moves:
            self.moves.append(self.load_move(move))

        # Prepare for any Transform shenanigans
        self.original_species = self.species
        self.original_types = self.types
        self.original_stats = self.stats
        self.original_moves = self.moves

        # Prepare Mimic
        self.mimic_move = None
        self.mimic_slot = None
    
        self.restore()


    def load_types(self) -> list[str]:
        return data_loader.POKEMON_DATA[self.species]["types"]


    def load_base_stats(self):
        data = data_loader.POKEMON_DATA[self.species]
        return [
            data["hp"],
            data["attack"],
            data["defense"],
            data["special"],
            data["speed"]
        ]
            

    def calculate_hp(self, base : Stats, level : int, dv:int=15, ev:int=65536):
        return floor(((base + dv) * 2 + floor(sqrt(ev) / 4) * level) / 100) + level + 10


    def calculate_stat(self, base : int, level : int, dv:int=15, ev:int=65536) -> int:
        return floor(((base + dv) * 2 + floor(sqrt(ev) / 4) * level) / 100) + 5


    def load_move(self, move_name):
        data = data_loader.MOVE_DATA[move_name]
        return Move(move_name, data)


    def is_fainted(self) -> bool:
        return self.current_hp <= 0
    

    def restore(self):
        self.current_hp = self.stats[Stats.HP.value]
        self.flinching = False
        self.afflicted_turns = 0
        
        self.trapped_turns = 0
        self.trap_damage = 0
        
        self.toxic_counter = 0
        self.seeded = False
        
        self.mist_active = False
        
        # Clear Mimic
        if self.mimic_move != None:
            self.moves[self.mimic_slot] = self.mimic_move
            self.mimic_move = None
            self.mimic_slot = None
        
        self.charge_turns = 0
        self.charging_move = None
        
        self.semi_invulnerable_state = ""
        
        self.recharge_turns = 0
        
        self.locked_move = None
        self.locked_turns = 0

        self.focusing = False

        self.status = ""
        self.stages = [0, 0, 0, 0, 0, 0]

        self.bide_damage = 0
        self.bide_turns = 0

        self.counter_damage = 0

        self.substitute_hp = 0
        self.substitute_broken = False

        for move in self.moves:
            move.current_pp
        
        # Clear Transform
        self.species = self.original_species
        self.types = self.original_types
        self.moves = self.original_moves
        self.stats = self.original_stats


    def on_switch_out(self):
        self.stages = [0, 0, 0, 0, 0, 0]

        # Volatile conditions
        self.seeded = False
        self.flinching = False
        self.trapped_turns = 0
        self.trap_damage = 0
        self.semi_invulnerable_state = ""
        self.charging_move = None
        self.charge_turns = 0
        self.focusing = False
        self.bide_turns = 0
        self.bide_damage = 0
        self.counter_damage = 0
        self.substitute_hp = 0

        # Clear Mimic
        if self.mimic_move != None:
            self.moves[self.mimic_slot] = self.mimic_move
            self.mimic_move = None
            self.mimic_slot = None
        
        # Clear Transform
        self.species = self.original_species
        self.types = self.original_types
        self.moves = self.original_moves
        self.stats = self.original_stats


        if self.status == "confusion":
            self.status = ""

        for move in self.moves:
            if move.disabled_turns > 0:
                move.disabled_turns = 0

        self.types = self.load_types()  # Reset conversion