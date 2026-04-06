from models.pokemon import *
from models.move import Move
import loading.data_loader as data_loader
from random import randint
from math import floor
from .stat_modifiers import apply_stage, STAGE_MULTIPLIERS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState, Trainer

def calculate_damage(battle: "BattleState", attacker : Pokemon, defender : Pokemon, move : Move) -> dict:
    stab = 1.5 if move.type in attacker.types else 1.0
    rand_factor = randint(217,255) / 255
    type_bonus = get_type_effectiveness(move.type, defender.types)
    reflect = 1.0
    reflect_side = battle.player if defender in battle.player.team else battle.enemy

    # Adjust for physical/special & apply stage multipliers
    if move.category == "physical":
        atk_stat = apply_stage(attacker.stats[Stats.ATTACK.value], attacker.stages[Stages.ATTACK.value])
        
        # Burn halves attack stat
        if attacker.status == "burn":
            atk_stat = floor(atk_stat * 0.5)

        def_stat = apply_stage(defender.stats[Stats.DEFENSE.value], defender.stages[Stages.DEFENSE.value])
        reflect = 2.0 if reflect_side.reflect_active else 1.0
    elif move.category == "special":
        atk_stat = apply_stage(attacker.stats[Stats.SPECIAL.value], attacker.stages[Stages.SPECIAL.value])
        def_stat = apply_stage(defender.stats[Stats.SPECIAL.value], defender.stages[Stages.SPECIAL.value])
        reflect = 2.0 if reflect_side.light_screen_active else 1.0


    # Is crit?
    crit_mod = 1.0
    crit_threshold = attacker.base_stats[Stats.SPEED.value] / 2
    crit_threshold = floor(crit_threshold)   # Round down after every operation

    if attacker.focusing:
        crit_threshold /= 4
        crit_threshold = floor(crit_threshold)

    crit_ratio = 4 if move.high_crit else 1
    crit_threshold *= crit_ratio
    crit_threshold = floor(crit_threshold)

    crit_comparison = randint(0,255)

    if crit_comparison < min(255, crit_threshold):
        # Yes, critical hit
        crit_mod = 2.0
        reflect = 1.0   # Ignore reflect on crit
    
    damage = (((((2*attacker.level*crit_mod)/5)+2)*move.power*atk_stat/(def_stat * reflect))/50+2) * stab * type_bonus * rand_factor

    return {
        "damage": floor(damage),
        "crit": crit_mod,
        "type_bonus": type_bonus
    }


def get_type_effectiveness(move_type: str, defender_types : list[str]) -> float:
    result = 1.0
    for type in defender_types:
        if move_type in data_loader.TYPE_DATA[type]["weaknesses"]:
            result *= 2
        elif move_type in data_loader.TYPE_DATA[type]["resistances"]:
            result *= 0.5
        elif move_type in data_loader.TYPE_DATA[type]["immunities"]:
            result *= 0
    return result


def hits_target(move : Move, attacker : Pokemon, defender : Pokemon) -> bool:
    if move.accuracy == None:
        # Interpret moves.json accuracy:null to mean the move never misses
        return True
    
    if defender.semi_invulnerable_state == "flying" and move.name.lower() != "swift" and move.name.lower() != "bide" and move.name.lower() != "transform":
        return False
    
    if defender.semi_invulnerable_state == "underground" and move.name.lower() != "fissure" and move.name.lower() != "earthquake" and move.name.lower() != "swift" and move.name.lower() != "bide" and move.name.lower() != "transform":
        return False
    
    acc_move = move.accuracy / 100
    acc_move = floor(acc_move * 255)

    acc_user = STAGE_MULTIPLIERS[attacker.stages[Stages.ACCURACY.value]]
    evasion_target = STAGE_MULTIPLIERS[defender.stages[Stages.EVASION.value]]

    acc_modified = min(255, acc_move * acc_user / evasion_target)
    r = randint(0, 255)

    return r < acc_modified


def calculate_confusion_damage(battle : "BattleState", pokemon : Pokemon):
    level = pokemon.level
    atk_stat = apply_stage(pokemon.stats[Stats.ATTACK.value], pokemon.stages[Stages.ATTACK.value])
    def_stat = apply_stage(pokemon.stats[Stats.DEFENSE.value], pokemon.stages[Stages.DEFENSE.value])

    reflect_side = battle.enemy if battle.enemy.reflect_active else battle.player

    power = 40
    rand_factor = randint(217,255) / 255
    opponent_reflect = 0.5 if reflect_side.reflect_active else 1   # Gen 1 bug

    damage = floor(
        ((((2 * level / 5 + 2) * power * atk_stat / def_stat) / 50) + 2) * rand_factor * opponent_reflect
    )

    return damage