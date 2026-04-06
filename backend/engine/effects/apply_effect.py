from .effect_registry import EFFECT_HANDLERS
from . import battle_effects
from random import randint, random
from models.pokemon import Pokemon
from models.move import Move
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState, Trainer

def apply_effect(battle: "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    # Handle chance if present
    chance = int(effect.get("chance", 1.0) * 100)

    if randint(1, 100) > chance:
        return
    
    effect_class = effect["class"]
    handler = EFFECT_HANDLERS.get(effect_class)

    if handler is None:
        battle.log(f"Effect class '{effect_class}' has not yet been implemented.")
        return
    
    handler(battle, user, move, target, effect, is_player, damage_dealt)