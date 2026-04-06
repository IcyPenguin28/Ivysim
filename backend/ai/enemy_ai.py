from ai.base_ai import BattleAI
from models.pokemon import Pokemon
from models.move import Move
from loading import data_loader
from sys import exit
from random import randint, choice, choices
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState, Trainer

AI_CAT2_TABLE = [
    ["meditate", "sharpen"],
    ["defense curl", "harden", "withdraw"],
    ["growth"],
    ["double team", "minimize"],
    ["pay day"],
    ["swift"],
    ["growl"],
    ["leer, tail whip"],
    ["string shot"],
    ["flash", "kinesis", "sand attack", "smokescreen"],
    ["conversion"],
    ["haze"],
    ["swords dance"],
    ["acid armor", "barrier"],
    ["agility"],
    ["amnesia"],
    ["recover", "rest", "soft-boiled"],
    ["transform"],
    ["screech"],
    ["light screen"],
    ["reflect"]
]

AI_TYPE_TABLE = {
    "move_type" : [
        "water",
        "fire",
        "fire",
        "grass",
        "electric",
        "water",
        "ground",
        "water",
        "fire",
        "electric",
        "ice", "grass",
        "psychic",
        "fire",
        "grass",
        "water",
        "normal",
        "normal",
        "ghost",
        "fire",
        "fire",
        "water",
        "electric",
        "electric",
        "grass",
        "grass",
        "grass",
        "grass",
        "grass",
        "ice",
        "ice",
        "ice",
        "ice",
        "fighting",
        "fighting",
        "fighting",
        "fighting",
        "fighting",
        "fighting",
        "fighting",
        "fighting",
        "poison",
        "poison",
        "poison",
        "poison",
        "poison",
        "poison",
        "ground",
        "ground",
        "ground",
        "ground",
        "ground",
        "ground",
        "flying",
        "flying",
        "flying",
        "flying",
        "flying",
        "psychic",
        "psychic",
        "bug",
        "bug",
        "bug",
        "bug",
        "bug",
        "bug",
        "bug",
        "rock",
        "rock",
        "rock",
        "rock",
        "rock",
        "rock",
        "ghost",
        "ghost",
        "fire",
        "water",
        "electric",
        "grass",
        "ice",
        "dragon"
    ],
    "bonus": [
        2,
        2,
        2,
        2,
        2,
        2,
        0,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0,
        2,
        2,
        0.5,
        2,
        0,
        2,
        2,
        0.5,
        0.5,
        2,
        0.5,
        0.5,
        2,
        2,
        2,
        2,
        0.5,
        0.5,
        0.5,
        0.5,
        2,
        2,
        0,
        2,
        0.5,
        0.5,
        2,
        0.5,
        0.5,
        2,
        2,
        0.5,
        0.5,
        2,
        2,
        0.5,
        2,
        2,
        2,
        0.5,
        2,
        2,
        0.5,
        2,
        0.5,
        0.5,
        2,
        0.5,
        2,
        2,
        0.5,
        0.5,
        2,
        2,
        2,
        0,
        0,
        0.5,
        0.5,
        0.5,
        0.5,
        2,
        2
    ],
    "defender_type": [
        "fire",
        "grass",
        "ice",
        "water",
        "water",
        "rock",
        "flying",
        "water",
        "fire",
        "electric",
        "ice",
        "grass",
        "psychic",
        "water",
        "fire",
        "grass",
        "rock",
        "ghost",
        "ghost",
        "bug",
        "rock",
        "ground",
        "ground",
        "flying",
        "ground",
        "bug",
        "poison",
        "rock",
        "flying",
        "water",
        "grass",
        "ground",
        "flying",
        "normal",
        "poison",
        "flying",
        "psychic",
        "bug",
        "rock",
        "ice",
        "ghost",
        "grass",
        "poison",
        "ground",
        "bug",
        "rock",
        "ghost",
        "fire",
        "electric",
        "grass",
        "bug",
        "rock",
        "poison",
        "electric",
        "fighting",
        "bug",
        "grass",
        "rock",
        "fighting",
        "poison",
        "fire",
        "grass",
        "fighting",
        "flying",
        "psychic",
        "ghost",
        "poison",
        "fire",
        "fighting",
        "ground",
        "flying",
        "bug",
        "ice",
        "normal",
        "psychic",
        "dragon",
        "dragon",
        "dragon",
        "dragon",
        "dragon",
        "dragon"
    ]
}

SLOT_WEIGHTS = [63, 64, 63, 66]

class EnemyAI(BattleAI):
    categories : tuple[int]

    def __init__(self, categories : tuple[int]):
        self.categories = categories


    def choose_move(self, battle : "BattleState", user : Pokemon, target :Pokemon) -> Move:
        scores = [10] * len(user.moves)
        for i in range(len(user.moves)):
            scores[i] += self.apply_categories(battle, user.moves[i], user, target)
        
        # Choose lowest score out of every move
        lowest_score = min(scores)
        valid_moves = []
        valid_indices = []

        for i in range(len(scores)):
            if scores[i] == lowest_score:
                valid_moves.append(user.moves[i])
                valid_indices.append(i)
        
        if len(valid_moves) == 1:
            return valid_moves[0]

        # Apply proper gen 1 weights for selection between multiple moves
        weights = [SLOT_WEIGHTS[i] for i in valid_indices]
        return choices(valid_moves, weights=weights, k=1)[0]
            
    
    def apply_categories(self, battle : "BattleState", move : Move, user : Pokemon, target :Pokemon) -> int:
        offset = 0
        for cat in self.categories:
            if cat == 1:
                if not move.power and target.status != "":
                    offset += 5
            elif cat == 2:
                if battle.turn == 2:
                    for encouragement_list in AI_CAT2_TABLE:
                        if move.name.lower() in encouragement_list:
                            offset -= 1
                            break
            elif cat == 3:
                # Check if table is fully populated
                rows = 81
                if len(AI_TYPE_TABLE["move_type"]) == rows and len(AI_TYPE_TABLE["bonus"]) == rows and len(AI_TYPE_TABLE["defender_type"]) == rows:
                    bonus = 0
                    for r in range(rows):
                        if AI_TYPE_TABLE["defender_type"][r] in target.types and AI_TYPE_TABLE["move_type"][r] == move.type:
                            bonus = AI_TYPE_TABLE["bonus"][r]
                            break
                    if bonus == 2:
                        offset -= 1
                    else:
                        offset += 1
                else:
                    battle.log("ERROR: AI_TYPE_TABLE is imbalanced!")
                    battle.log(f"Move Types: {len(AI_TYPE_TABLE['move_type'])}")
                    battle.log(f"Bonuses: {len(AI_TYPE_TABLE['bonus'])}")
                    battle.log(f"Defender Types: {len(AI_TYPE_TABLE['defender_type'])}")
                    exit()
        return offset
    

    def choose_switch(self, battle : "BattleState"):
        # TODO: Remove bool flag when player's version of this func is implemented
        for mon in battle.enemy.team:
            if not mon.is_fainted() and mon != battle.enemy.active:
                return mon
        return None
    

    def choose_action(self, battle : "BattleState", user : Pokemon, target : Pokemon):
        move = self.choose_move(battle, user, target)
        return ("move", move)