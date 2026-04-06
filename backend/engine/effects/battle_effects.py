from .effect_registry import register_effect
from models.pokemon import Pokemon, Stats, Stages
from models.move import Move
from random import randint
from math import floor
import loading.data_loader as data_loader
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState, Trainer


STAT_MAP = {
        "attack": Stages.ATTACK.value,
        "defense": Stages.DEFENSE.value,
        "special": Stages.SPECIAL.value,
        "speed": Stages.SPEED.value,
        "accuracy": Stages.ACCURACY.value,
        "evasiveness": Stages.EVASION.value
    }

@register_effect("status_condition")
def apply_status(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    status = effect["status"]

    if target.status != "":
        battle.log("But it failed!")
        return

    # Substitute always protects against these statuses
    substitute_bans = ["poison", "bad_poison", "burn", "freeze"]

    if status in substitute_bans:
        if move.category == "status":
            battle.log("But it failed!")
        return

    # In gen 1, only indirect paralysis and direct confusion absorbed by the substitute
    if move.power and (status == "paralysis"):
        return
    if not move.power and (status == "confusion"):
        return
    
    # In gen 1, if a target's substitute is broken, secondary confusion does not work
    if target.substitute_broken:
        if move.name.lower() == "confusion" or move.name.lower() == "psybeam":
            return

    if target.status == "" and not target.is_fainted():
        # Target is healthy, they may be inflicted with a status
        target.status = status

        if status == "paralysis":
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} was paralyzed!")
        elif status == "poison":
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} was poisoned!")
        elif status == "bad_poison":
            target.toxic_counter = 1
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} was badly poisoned!")
        elif status == "burn":
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} was burned!")
        elif status == "confusion":
            target.afflicted_turns = randint(2, 5)
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} became confused!")
        elif status == "sleep":
            target.afflicted_turns = randint(1, 7)
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} fell asleep!")
        elif status == "freeze":
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} was frozen solid!")


@register_effect("drain")
def apply_drain(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if not target.substitute_broken:
        ratio = effect.get("ratio", 0)
        user.current_hp = min(user.stats[Stats.HP.value], user.current_hp + floor(damage_dealt * ratio))
        battle.log(f"Sucked health from {'Enemy ' if is_player else ''}{target.nickname}!")


@register_effect("stat_boost")
def apply_stat_boost(battle : "BattleState", user: Pokemon, move: Move, target: Pokemon, effect: dict, is_player: bool, damage_dealt: int):
    stages: int = effect.get("stages", 0)
    stat: str = effect["stat"]
    targ: str = effect.get("target", "enemy")

    # Determine which Pokémon is affected
    affected = target if targ == "enemy" else user

    # Consider mist
    if affected == target and target.mist_active and stages < 0:
        battle.log("But it failed!")
        return
    
    # Consider substitute
    if affected == target and target.substitute_hp > 0:
        if move.name.lower() == "growl" or move.name.lower() == "screech":
            battle.log("But it failed!")
            return

    stage_index = STAT_MAP[stat]
    current_stage = affected.stages[stage_index]

    enemy_prefix = "Enemy " if (
        (affected is target and is_player) or
        (affected is user and not is_player)
    ) else ""
    display_name = f"{enemy_prefix}{affected.nickname}"

    if stages < 0 and current_stage == -6:
        battle.log(f"{display_name}'s {stat.upper()} can't go any lower!")
        return

    if stages > 0 and current_stage == 6:
        battle.log(f"{display_name}'s {stat.upper()} can't go any higher!")
        return

    # Add or subtract stage
    affected.stages[stage_index] = max(-6, min(current_stage + stages, 6))

    # Text
    if stages == -2:
        battle.log(f"{display_name}'s {stat.upper()} greatly fell!")
    elif stages == -1:
        battle.log(f"{display_name}'s {stat.upper()} fell!")
    elif stages == 0:
        battle.log("No effect!")
    elif stages == 1:
        battle.log(f"{display_name}'s {stat.upper()} rose!")
    elif stages == 2:
        battle.log(f"{display_name}'s {stat.upper()} greatly rose!")


@register_effect("flinch")
def apply_flinch(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if target.substitute_hp <= 0:
        target.flinching = True


@register_effect("trap")
def apply_trap(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    turn_distribution = [2, 2, 2, 3, 3, 3, 4, 5]
    target.trapped_turns = turn_distribution[randint(0,len(turn_distribution) - 1)]
    target.trap_damage = damage_dealt


@register_effect("semi_invulnerable")
def apply_semi_invulnerable(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    state = effect.get("state", "underground")
    user.semi_invulnerable_state = state


@register_effect("lock")
def apply_lock(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.locked_turns > 0 and user.locked_move:
        # Decrement turns
        user.locked_turns = max(0, user.locked_turns - 1)
    elif user.locked_turns == 0 and user.locked_move:
        # Apply fatigue confusion
        user.afflicted_turns = randint(2, 5)
        user.status = "confusion"
        battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} became confused due to fatigue!")
        user.locked_move = None
    else:
        # Begin lockdown
        turns = effect.get("turns", 0)
        user.locked_move = move
        user.locked_turns = turns[randint(0, len(turns) - 1)] - 2   # This -2 is here to make sure the move actually lasts 3-4 turns bc I am stupid I think


@register_effect("self_faint")
def apply_self_faint(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if not target.substitute_broken:
        user.current_hp = 0
        battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} fainted!")


@register_effect("ohko")
def apply_ohko(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    target.current_hp = 0
    battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} fainted!")


@register_effect("special_damage")
def apply_special_damage(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    formula = effect.get("formula", "fixed")
    value = 0

    if formula == "fixed":
        value = effect.get("value", 0)
    elif formula == "level":
        value = user.level
    elif formula == "psywave":
        value = randint(1, floor(1.5*user.level)) if is_player else randint(0, floor(1.5*user.level))
    elif formula == "ratio":
        value = effect.get("ratio", 0) * target.stats[Stats.HP.value]
    
    if target.substitute_hp > 0:
        target.substitute_hp = max(0, target.substitute_hp - value)
        if target.substitute_hp <= 0:
            target.substitute_broken = True
            battle.log("The substitute was broken!")
    else:
        target.current_hp = max(0, target.current_hp - value)
        battle.log(f"{'Enemy ' if not is_player else ''}{target.nickname}{chr(39)+'s substitute' if target.substitute_hp > 0 else ''} took {value} damage!")
        if target.is_fainted():
            battle.log(f"{'Enemy ' if not is_player else ''}{target.nickname} fainted!")


@register_effect("heal")
def apply_heal(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.current_hp == user.stats[Stats.HP.value]:
        battle.log("But it failed!")
        return
    
    ratio = effect.get("ratio", 0)
    amount = floor(user.stats[Stats.HP.value] * ratio)
    user.current_hp = min(user.stats[Stats.HP.value], user.current_hp + amount)
    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} regained health!")


@register_effect("thaw")
def apply_thaw(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    targ : Pokemon = None
    if effect["target"] == "enemy":
        targ = target
    else:
        targ = user
    
    if targ.status == "freeze":
        targ.status == ""
        battle.log(f"{'Enemy ' if is_player else ''}{targ.nickname} thawed out!")


@register_effect("screen")
def apply_screen(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    screen_type = effect.get("screen_type", "special")
    side = battle.player if is_player else battle.enemy
    if screen_type == "physical":
        if side.reflect_active:
            battle.log("But it failed!")
            return
        else:
            side.reflect_active = True
            battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} gained armor!")
    elif screen_type == "special":
        if side.light_screen_active:
            battle.log("But it failed!")
            return
        else:
            side.light_screen_active = True
            battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname}'s protected against special attacks!")


@register_effect("miss_recoil")
def apply_miss_recoil(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    # This should do nothing, the effect is handled in the battle engine itself
    pass


@register_effect("no_effect")
def apply_no_effect(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    battle.log("No effect!")


# Effects belonging to 1 move
@register_effect("reset_battle_modifiers")
def apply_haze(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    # Reset stages
    user.stages = [0, 0, 0, 0, 0, 0]
    target.stages = [0, 0, 0, 0, 0, 0]

    # Lift statuses (or turn bad poison into regular poison)
    if user.status != "":
        if user.status != "bad_poison":
            user.status = ""
            user.afflicted_turns = 0
        else:
            user.status = "poison"
            user.toxic_counter = 0

    if target.status != "":
        if target.status != "bad_poison":
            target.status = ""
            target.afflicted_turns = 0
        else:
            target.status = "poison"
            target.toxic_counter = 0
    
    # Lift screens
    battle.player.light_screen_active = False
    battle.enemy.light_screen_active = False
    
    # Lift leech seed
    user.seeded = False
    target.seeded = False

    # Lift disable
    for move in user.moves:
        move.disabled = False
    for move in target.moves:
        move.disabled = False

    # Lift focus energy
    battle.player.active.focusing = False
    battle.enemy.active.focusing = False
    
    battle.log("All STATUS changes are eliminated!")


@register_effect("prevent_stat_drops")
def apply_mist(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    user.mist_active = True
    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname}'s shrouded in mist!")


@register_effect("change_type")
def apply_conversion(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    user.types = target.types
    battle.log(f"Converted type to {'Enemy ' if is_player else ''}{target.nickname}'s!")


@register_effect("disable_move")
def apply_disable(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    # Move fails if target already has a disabled move
    for move in target.moves:
        if move.disabled_turns > 0:
            battle.log("But it failed!")
            return
    
    # Find random move that is not yet drained
    randindex = randint(0,3)
    while target.moves[randindex].current_pp != 0:
        randindex = randint(0,3)
    
    target.moves[randindex].disabled_turns = randint(0, 7)
    battle.log(f"{'Enemy ' if is_player else ''}{user.nickname}'s {target.moves[randindex]} was disabled!")
    
    # Disable triggers rage building
    build_rage(battle, target, is_player)


@register_effect("metronome")
def apply_metronome(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    selectable_moves = list(data_loader.MOVE_DATA.keys())
    selectable_moves.remove("metronome")
    selectable_moves.remove("counter")
    selectable_moves.remove("mimic")
    selectable_moves.remove("mirror move")
    selectable_moves.remove("struggle")
    selectable_moves.remove("transform")

    selected_move_key = selectable_moves[randint(0, len(selectable_moves) - 1)]

    selected_move : Move = Move(selected_move_key, data_loader.MOVE_DATA[selected_move_key])

    from engine.battle_engine import execute_move
    execute_move(battle, user, selected_move, target, is_player)


@register_effect("use_last_move")
def apply_mirror_move(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    banned_list = [
        "acid armor",
        "agility",
        "amnesia",
        "barrier",
        "bide",
        "counter",
        "defense curl",
        "double team",
        "fissure",
        "focus energy",
        "growth",
        "guillotine",
        "harden",
        "haze",
        "horn drill",
        "light screen",
        "meditate",
        "metronome",
        "mimic",
        "minimize",
        "mirror move",
        "mist",
        "recover",
        "sharpen",
        "soft-boiled",
        "struggle",
        "swords dance",
        "teleport",
        "transform",
        "withdraw"
    ]
    
    if battle.previous_move == None or battle.previous_move.name.lower() in banned_list:
        battle.log("But it failed!")
        return
    
    from engine.battle_engine import execute_move
    execute_move(battle, user, battle.previous_move, target, is_player)


@register_effect("store_last_move")
def apply_mimic(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    
    if battle.previous_move == None or battle.previous_move.name.lower() == "struggle":
        battle.log("But it failed!")
        return
    
    copied_move = Move(battle.previous_move.name, data_loader.MOVE_DATA[battle.previous_move.name.lower()])
    copied_move.current_pp = battle.previous_move.current_pp

    # Replace Mimic
    for i, m in enumerate(user.moves):
        if m.name.lower() == "mimic":
            user.mimic_slot = i
            user.mimic_move = m
            user.moves[i] = copied_move
            battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} learned {copied_move.name}!")
            return


@register_effect("recharge")
def apply_recharge(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    # If rechargable move causes target to faint, no recharge necessary
    if target.is_fainted() or target.substitute_broken:
        return
    
    turns = effect.get("turns", 0)
    user.recharge_turns = turns
    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} must recharge!")


@register_effect("focus")
def apply_focus_energy(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.focusing == True:
        battle.log(f"But it failed!")
        return
    
    user.focusing = True
    battle.log(f"")


@register_effect("transform")
def apply_transform(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    user.species = target.species
    user.types = target.types
    user.moves = target.moves
    user.stats = target.stats
    user.stages = target.stages

    # User keeps its original HP
    user.stats[Stats.HP.value] = user.original_stats[Stats.HP.value]

    # Moves are copied with 5 PP
    for move in user.moves:
        move.current_pp = 5

    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} transformed into {target.nickname}!")


@register_effect("rest")
def apply_rest(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    
    if user.current_hp == user.stats[Stats.HP.value]:
        battle.log("But it failed!")
        return
    
    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} started sleeping!")
    user.current_hp = user.stats[Stats.HP.value]
    battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} regained health!")
    user.status = "sleep"
    user.afflicted_turns = 2
    # NOTE: Do not reset toxic_counter for gen 1 bug replication



@register_effect("bide_your_time")
def lie_in_wait(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.bide_turns == 0:
        user.bide_turns = randint(2,3)
        return

    if user.bide_turns > 0:
        user.bide_turns = max(0, user.bide_turns - 1)
        if user.bide_turns == 0:
            substitute_active = (target.substitute_hp > 0)
            battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} unleashed energy!")
            damage = user.bide_damage * 2
            if target.substitute_hp > 0:
                target.substitute_hp = max(0, target.substitute_hp - damage)
            else:
                target.current_hp = max(0, target.current_hp - damage)
            battle.log(f"{'Enemy ' if is_player else ''}{target.nickname}{chr(39)+'s substitute' if substitute_active else ''} took {damage} damage!")
            user.bide_damage = 0

            if target.is_fainted():
                battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} fainted!")


@register_effect("counter")
def apply_counter(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.counter_damage == 0:
        battle.log("But it failed!")
        return
    substitute_active = (target.substitute_hp > 0)
    damage = user.counter_damage * 2
    if target.substitute_hp > 0:
        target.substitute_hp = max(0, target.substitute_hp - damage)
    else:
        target.current_hp = max(0, target.current_hp - damage)
    battle.log(f"{'Enemy ' if is_player else ''}{target.nickname}{chr(39)+'s substitute' if substitute_active else ''} took {damage} damage!")
    user.counter_damage = 0

    if target.is_fainted():
        battle.log(f"{'Enemy ' if is_player else ''}{target.nickname} fainted!")


@register_effect("substitute")
def apply_substitute(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, effect : dict, is_player : bool, damage_dealt : int):
    if user.substitute_hp > 0:
        battle.log("But it failed!")
        return
    
    sub_recoil = floor(0.25 * user.stats[Stats.HP.value])
    user.current_hp = max(0, user.current_hp - sub_recoil)
    if user.is_fainted():
            battle.log(f"{'Enemy ' if not is_player else ''}{user.nickname} fainted!")
            return
    user.substitute_hp = sub_recoil + 1 # In gen 1, the sub has 1 more HP than the recoil
    battle.log("It created a substitute!")


def build_rage(battle: "BattleState", pkmn : Pokemon, is_player : bool):
    if pkmn.stages[Stats.ATTACK.value] >= 6:
        return
    
    if not pkmn.locked_move:
        return

    if pkmn.locked_move.name.lower() != "rage":
        return
    
    pkmn.stages[Stats.ATTACK.value] = min(pkmn.stages[Stats.ATTACK.value] + 1, 6)
    battle.log(f"{'Enemy ' if not is_player else ''}{pkmn.nickname}'s rage is building! ({pkmn.stages[Stats.ATTACK.value]})")


# End of Turn Statuses
def apply_end_of_turn_status(battle : "BattleState", pkmn: Pokemon, is_player: bool):
    # Apply burn or poison damage at the end of a turn.
    display_name = f"{'Enemy ' if not is_player else ''}{pkmn.nickname}"

    if pkmn.status == "burn":
        dmg = floor(pkmn.stats[Stats.HP.value] / 16)
        pkmn.current_hp = max(0, pkmn.current_hp - dmg)
        battle.log(f"{display_name} is hurt by its burn!")
        if pkmn.is_fainted():
            battle.log(f"{display_name} fainted!")

    elif pkmn.status == "poison":
        dmg = floor(pkmn.stats[Stats.HP.value] / 16)
        pkmn.current_hp = max(0, pkmn.current_hp - dmg)
        battle.log(f"{display_name} is hurt by poison!")
        if pkmn.is_fainted():
            battle.log(f"{display_name} fainted!")

    elif pkmn.status == "bad_poison":  # Toxic
        dmg = floor(pkmn.stats[Stats.HP.value] / 16) * pkmn.toxic_counter
        pkmn.current_hp = max(0, pkmn.current_hp - dmg)
        pkmn.toxic_counter += 1
        battle.log(f"{display_name} is hurt by poison!")
        if pkmn.is_fainted():
            battle.log(f"{display_name} fainted!")
            return
    
    # Apply leech seed
    if pkmn.seeded:
        amount = max(1,floor(pkmn.stats[Stats.HP.value] / 16))

        # In gen 1, Toxic counter affects Leech Seed's ratio
        if pkmn.status == "bad_poison":
            amount *= pkmn.toxic_counter
        
        pkmn.current_hp = max(0, pkmn.current_hp - amount)
        leecher : "Trainer" = battle.enemy if pkmn in battle.player.team else battle.player

        leecher.active.current_hp = min(leecher.active.stats[Stats.HP.value], leecher.active.current_hp + amount)
        battle.log(f"LEECH SEED saps {'Enemy ' if is_player else ''}{pkmn.nickname}!")

        if pkmn.is_fainted():
            battle.log(f"{display_name} fainted!")
            return
    
    # Apply trap damage
    if pkmn.trapped_turns > 0:
        battle.log(f"The attack continues!")
        pkmn.current_hp = max(0, pkmn.current_hp - pkmn.trap_damage)
        if pkmn.is_fainted():
            battle.log(f"{pkmn.nickname} fainted!")