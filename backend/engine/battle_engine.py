from models.pokemon import *
from models.move import *
from .stat_modifiers import apply_stage
from .damage import hits_target, calculate_damage, calculate_confusion_damage
from .effects.apply_effect import apply_effect
from .effects.battle_effects import apply_end_of_turn_status, build_rage
from loading import data_loader
from random import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .battle_state import BattleState, Trainer
    from ai.enemy_ai import EnemyAI

def resolve_turn(battle : "BattleState"):
    first_user = None
    first_move = None
    second_user = None
    second_move = None

    pkmn1 = battle.player.active
    pkmn2 = battle.enemy.active
    action1 = battle.player.ai_model.choose_action(battle, pkmn1, pkmn2)
    action2 = battle.enemy.ai_model.choose_action(battle, pkmn2, pkmn1)

    if action1[0] == "switch":
        battle.switch_out(battle.player, action1[1])
        pkmn1 = battle.player.active
    
    if action2[0] == "switch":
        battle.switch_out(battle.enemy, action2[1])
        pkmn2 = battle.enemy.active
    
    if action1[0] == "switch" and action2[0] == "switch":
        # Both trainers switched, no moves execute
        apply_end_of_turn_status(battle, battle.player.active, True)
        apply_end_of_turn_status(battle, battle.enemy.active, False)
        return

    move1 : Move = action1[1] if action1[0] == "move" else None
    move2 : Move = action2[1] if action2[0] == "move" else None
    
    if move1 and not move2:
        execute_move(battle, pkmn1, move1, pkmn2, True)
        apply_end_of_turn_status(battle, pkmn1, True)
        apply_end_of_turn_status(battle, pkmn2, False)
        return
    elif move2 and not move1:
        execute_move(battle, pkmn2, move2, pkmn1, False)
        apply_end_of_turn_status(battle, pkmn1, True)
        apply_end_of_turn_status(battle, pkmn2, False)
    else:
        # Both players used moves, determine who goes first

        # Priority Moves
        if move1.priority > move2.priority:
            first_user = pkmn1
            first_move = move1
            second_user = pkmn2
            second_move = move2
        elif move2.priority > move1.priority:
            first_user = pkmn2
            first_move = move2
            second_user = pkmn1
            second_move = move1
        else:
            # If priority is tied, then Speed
            speed1 = apply_stage(pkmn1.stats[Stats.SPEED.value], pkmn1.stages[Stages.SPEED.value])
            speed2 = apply_stage(pkmn2.stats[Stats.SPEED.value], pkmn2.stages[Stages.SPEED.value])

            # Apply paralysis speed debuff
            speed1 = speed1 if pkmn1.status != "paralysis" else floor(speed1 * 0.25)
            speed2 = speed2 if pkmn2.status != "paralysis" else floor(speed2 * 0.25)

            if speed1 > speed2:
                first_user = pkmn1
                first_move = move1
                second_user = pkmn2
                second_move = move2
            elif speed2 > speed1:
                first_user = pkmn2
                first_move = move2
                second_user = pkmn1
                second_move = move1
            else:
                # Speed tie, choose randomly
                if randint(0, 1) == 0:
                    first_user = pkmn1
                    first_move = move1
                    second_user = pkmn2
                    second_move = move2
                else:
                    first_user = pkmn2
                    first_move = move2
                    second_user = pkmn1
                    second_move = move1
        
        # Remove flinch from both mons
        if first_user.flinching:
            first_user.flinching = False
        if second_user.flinching:
            second_user.flinching = False

        # Execute moves
        execute_move(battle, first_user, first_move, second_user, first_user == pkmn1)
        apply_end_of_turn_status(battle, first_user, first_user == pkmn1)

        if second_user.is_fainted() or first_user.is_fainted():
            return
        
        execute_move(battle, second_user, second_move, first_user, second_user == pkmn1)
        apply_end_of_turn_status(battle, second_user, second_user == pkmn1)


def execute_move(battle : "BattleState", user : Pokemon, move : Move, target : Pokemon, is_player : bool):
    if user.is_fainted():
        return
    
    target_name = f"{'Enemy ' if is_player else ''}{target.nickname}"
    user_name = f"{'Enemy ' if not is_player else ''}{user.nickname}"

    # User skips turn if they are recharging
    if user.recharge_turns > 0:
        user.recharge_turns = max(0, user.recharge_turns - 1)
        battle.log(f"{user_name} must recharge!")
        return

    # User cannot act if they are trapped
    if user.trapped_turns > 0:
        if is_player:
            battle.log(f"{user_name} can't move!")
        return

    # Return out if user is trying to use disabled move
    if move.disabled_turns > 0:
        battle.log(f"{user_name}'s {move.name} is disabled!")
        return
    
    # If target is trapped, the trapping attack continues, user cannot choose another move
    if target.trapped_turns > 0:
        return


    # Act on paralysis, confusion, sleep, freeze, or flinch if applicable
    if user.status == "paralysis":
        if randint(1, 4) == 1:
            battle.log(f"{user_name} is paralyzed! It can't move!")
            if user.locked_move:
                if user.locked_move.name.lower() != "rage":
                    user.locked_move = None
                    user.locked_turns = 0
            return
    if user.status == "confusion":
        if user.afflicted_turns > 0:
            user.afflicted_turns -= 1
            battle.log(f"{user_name} is confused!")
            if randint(1, 2) == 1:
                battle.log("It hurt itself in its confusion!")
                # In gen 1 only, confusion damage is applied to an active substitute
                if user.substitute_hp > 0:
                    user.substitute_hp = max(0, user.substitute_hp - calculate_confusion_damage(battle, user))
                    if user.substitute_hp <= 0:
                        battle.log("The substitute was broken!")
                else:
                    user.current_hp = max(0, user.current_hp - calculate_confusion_damage(battle, user))
                if user.locked_move:
                    if user.locked_move.name.lower() != "rage":
                        user.locked_move = None
                        user.locked_turns = 0
                if user.is_fainted():
                    battle.log(f"{user_name} fainted!")
                return
        else:
            battle.log(f"{user_name} snapped out of its confusion!")
            user.status = ""
            user.afflicted_turns = 0
    elif user.status == "freeze":
        battle.log(f"{user_name} is frozen solid!")
        return
    elif user.status == "sleep":
        if user.afflicted_turns > 0:
            battle.log(f"{user_name} is fast asleep!")
            user.afflicted_turns -= 1
            return
        else:
            battle.log(f"{user_name} woke up!")
            user.status = ""
            # In gen 1, Pokemon cannot act on the turn they wake up
            return

    if user.flinching:
        battle.log(f"{user_name} flinched and couldn't move!")
        user.flinching = False
        return
    
    # If currently readying a chargeable move, ignore selected move and reuse charging move
    if user.charging_move and user.charge_turns == user.charging_move.charge_turns:
        move = user.charging_move
    # Else, if locked down, use that move instead
    elif user.locked_move and user.locked_turns:
        move = user.locked_move
    # Else, if biding, bide
    elif user.bide_turns > 0:
        move = Move("bide", data_loader.MOVE_DATA["bide"])
        for effect in move.effects:
            apply_effect(battle, user, move, target, effect, is_player, 0)
            return


    # Continue with move execution
    battle.log(f"{user_name} used {move.name}!")

    # Reduce PP by 1
    # Only reduce PP if the move actually executes (not charging, not subsequent locked execution)
    if user.charge_turns >= move.charge_turns or (move.charge_turns == 0 and user.locked_turns == 0):
        move.current_pp = max(0, move.current_pp - 1)

    # Record as last used move
    battle.previous_move = move

    # If needs a charge, charge
    if move.charge_turns > 0 and user.charge_turns < move.charge_turns:
        user.charge_turns += 1
        user.charging_move = move

        # Apply semi-invulnerable state before returning out
        for effect in move.effects:
            if effect["class"] == "semi_invulnerable":
                apply_effect(battle, user, move, target, effect, is_player, 0)

        # Display different message dependent on chargable move
        # Yes, I know this is not scaleable, but it doesn't matter for, what, 6 or 7 moves total?
        if move.name.lower() == "dig":
            battle.log(f"{user_name} dug a hole!")
        elif move.name.lower() == "fly":
            battle.log(f"{user_name} flew up high!")
        elif move.name.lower() == "razor wind":
            battle.log(f"{user_name} made a whirlwind!")
        elif move.name.lower() == "skull bash":
            battle.log(f"{user_name} lowered its head!")
        elif move.name.lower() == "skull bash":
            battle.log(f"{user_name} lowered its head!")
        elif move.name.lower() == "sky attack":
            battle.log(f"{user_name} is glowing!")
        elif move.name.lower() == "solar beam":
            battle.log(f"{user_name} took in sunlight!")
        return
    
    

    # Accuracy check
    if not hits_target(move, user, target):
        battle.log(f"{target_name} avoided the attack!")

        # I'm just gonna handle miss recoil now. We return out anyway and there's no other effects tied to the moves that have this one.
        if len(move.effects) > 0:
            if move.effects[0]["class"] == "miss_recoil":
                # In gen 1, crash damage is absorbed by the user's active substitute
                if user.substitute_hp > 0:
                    user.substitute_hp = max(0, user.substitute_hp - move.effects[0]["value"])
                    if user.substitute_hp <= 0:
                        battle.log("The substitute was broken!")
                else:
                    user.current_hp = max(0, user.current_hp - move.effects[0]["value"])
                battle.log(f"{user_name}'s hit with recoil!")
                if user.is_fainted():
                    battle.log(f"{user_name} fainted!")
        return
    
    # Leech Seed
    # Yes, this is bad practice, no I don't care
    # I'm not registering a new battle effect just for 1 move
    if move.name.lower() == "leech seed":
        if target.seeded:
            battle.log("But it failed!")
            return
        target.seeded = True
        battle.log(f"{target_name} was seeded!")
        return
    
    # Resolve multihit
    num_hits = 1
    if move.multihit:
        x, y = move.multihit
        if x == y:
            # Guaranteed to hit X times with no variation
            num_hits = x
        else:
            # Will hit X-Y times
            # Gen 1 only has moves that hit 2-5 times, so we can cheat
            distribution = [2, 2, 2, 3, 3, 3, 4, 5]
            num_hits = distribution[randint(0, 7)]
            
    # Prep moving drain damage to larger scope
    damage_dealt = 0

    # Execute move
    if move.power and move.power > 0:
        # Regular Physical/Special move
        for i in range(num_hits):
            substitute_active = (target.substitute_hp > 0)
            damage_results = calculate_damage(battle, user, target, move)
            damage = damage_results["damage"]
            damage_dealt = damage
            crit = damage_results["crit"]
            type_bonus = damage_results["type_bonus"]
            if target.substitute_hp > 0:
                target.substitute_hp = max(0, target.substitute_hp - damage)
                if target.substitute_hp <= 0:
                    battle.log("The substitute was broken!")
            else:
                target.current_hp = max(0, target.current_hp - damage)

            if target.bide_turns > 0:
                target.bide_damage += damage_dealt
            if move.type.lower() == "fighting" or move.type.lower() == "normal":
                target.counter_damage = damage_dealt
            
            # Type bonus messages (Plus the new ones from Champions)
            if type_bonus == 4:
                battle.log("It's extremely effective!")
            elif type_bonus == 2:
                battle.log("It's super effective!")
            elif type_bonus == 0.5:
                battle.log("It's not very effective...")
            elif type_bonus == 0.25:
                battle.log("It's mostly ineffective...")
            elif type_bonus == 0:
                battle.log(f"It doesn't affect {target.nickname}!")
            
            # Crit message
            if crit > 1:
                battle.log("Critical hit!")

            # Standard messaegs
            battle.log(f"{target_name}{chr(39)+'s substitute' if substitute_active else ''} took {damage} damage!")

            if target.is_fainted():
                if num_hits > 1:
                    battle.log(f"Hit {i+1} time(s)!")
                battle.log(f"{target_name} fainted!")
                break

            # Apply rage if applicable (applicability checks happen in the func itself)
            build_rage(battle, target, is_player)

            # Multihit ends immediately if substitute is broken
            if target.substitute_broken:
                break
        if num_hits > 1 and not target.is_fainted():
            battle.log(f"Hit {num_hits} time(s)!")
        
        # Apply recoil
        if not target.substitute_broken:
            if move.recoil > 0:
                user.current_hp = max(0, user.current_hp - damage_dealt * move.recoil)
                battle.log(f"{user_name}'s hit with recoil!")
                if user.is_fainted():
                    battle.log(f"{user_name} fainted!")
                    return
    
    # Resolve secondary effects
    # Substitute exceptions are handled per effect
    for effect in move.effects:
        apply_effect(battle, user, move, target, effect, is_player, damage_dealt)

    # If move that was used was a chargeable or caused semi-invulnerability, reset charge stats
    # After finishing a charge move
    if user.charging_move:
        user.semi_invulnerable_state = ""
        user.charging_move = None
        user.charge_turns = 0
    
    # This flag is only relevant on the turn the substitute was broken
    target.substitute_broken = False