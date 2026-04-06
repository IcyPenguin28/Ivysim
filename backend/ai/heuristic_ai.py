from ai.base_ai import BattleAI
from models.pokemon import Pokemon, Stats, Stages
from models.move import Move
from engine.damage import calculate_damage, get_type_effectiveness
from random import choice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState

from engine.effects.battle_effects import STAT_MAP

class PlayerHeuristicAI(BattleAI):
    def evaluate_move(self, battle : BattleAI, user : Pokemon, move : Move, target : Pokemon) -> int:
        # If move is depleted, don't use it
        if move.current_pp <= 0:
            return -65536
        
        score = 0

        # Consider potential max damage user can dish out
        damages = [calculate_damage(battle, user, target, m)["damage"] for m in user.moves if m.power]
        max_damage = max(damages) if damages else 0
        enemy_faster = (user.stats[Stats.SPEED.value] <= target.stats[Stats.SPEED.value])

        # Consider potential max damage user will have to tank
        enemy_damages = [calculate_damage(battle, target, user, m)["damage"] for m in target.moves if m.power]
        enemy_damage = max(enemy_damages) if enemy_damages else 0

        if not move.power:
            # Status move
            for effect in move.effects:
                if effect.get("class") == "status_condition":
                    # Encourage status moves when player does not have one
                    if target.status == "":
                        if effect.get("status_condition") == "sleep" or effect.get("status_condition") == "freeze":
                            score += 60
                        elif effect.get("status_condition") == "paralysis":
                            score += 50
                        elif effect.get("status_condition") == "bad_poison":
                            score += 40
                        elif effect.get("status_condition") == "poison" or effect.get("status_condition") == "burn":
                            score += 30
                        elif effect.get("status_condition") == "confusion":
                            score += 20
                        
                        if max_damage >= target.current_hp:
                            # Discourage setup if can KO
                            score -= 50
                        
                        if enemy_damage >= user.current_hp and enemy_faster:
                            # Discourage risky setup
                            score -= 40
                        
                        if max_damage > target.current_hp // 2:
                            # Discourage setup when can deal decent damage as is
                            score -= 40
                    else:
                        # Heavily discourage status moves if they will fail
                        score -= 100

                elif effect.get("class") == "stat_boost":
                    if enemy_damage < user.current_hp:
                        stages = effect.get("stages", 0)
                        stat = effect.get("stat")

                        if max_damage >= target.current_hp:
                            # Discourage setup if can KO
                            score -= 50
                            continue

                        if enemy_damage >= user.current_hp and enemy_faster:
                            # Discourage risky setup
                            score -= 40
                            continue

                        if stages > 0:
                            # Positive self boost
                            # Encourage more if stages are lower
                            score += (30 * stages) if user.stages[STAT_MAP[stat]] < 3 else (5 * stages)
                        
                        elif stages < 0:
                            # Negative target debuff
                            # Encourage more if stages are higher
                            score += (30 * abs(stages)) if target.stages[STAT_MAP[stat]] > -3 else (5 * abs(stages))

                elif effect.get("class") == "heal":
                    if user.current_hp <= user.stats[Stats.HP.value] // 2:
                        if enemy_damage < user.current_hp:
                            # Safe heal
                            score += 30
                        
                        elif enemy_damage < user.stats[Stats.HP.value] // 2:
                            # Risky but potentially useful heal
                            score += 15
                        else:
                            # Pointless heal (will die anyway)
                            score -= 20
                    if max_damage >= target.current_hp:
                        # Discourage heal if can KO
                        score -= 40
        else:
            # Damaging move
            dmg_results = calculate_damage(battle, user, target, move)
            expected_damage = dmg_results["damage"]
            bonus = dmg_results["type_bonus"]

            # Favor moves that do higher damage or nearly KO
            score += expected_damage // 2
            if expected_damage >= target.current_hp * 0.7:
                score += 15

            # Favor KO moves
            if expected_damage >= target.current_hp:
                if user.stats[Stats.SPEED.value] > target.stats[Stats.SPEED.value]:
                    score += 120
                elif user.stats[Stats.SPEED.value] == target.stats[Stats.SPEED.value]:
                    score += 90
                else:
                    if enemy_damage >= user.current_hp:
                        score -= 30
                    else:
                        score += 60

            # Favor super-effective, discourage not-very-effective
            if bonus > 1:
                score += 75
            if bonus < 1:
                score -= 25
            
            # Favor STAB
            if move.type in user.types:
                score += 10
        
        if move.accuracy:
            if move.accuracy < 90:
                # The lower the move's accuracy is below 90, the more it is disfavored
                score -= (100 - move.accuracy) // 2
        else:
            score += 5
        
        return score
    
    def consider_switch(self, battle : "BattleState", user : Pokemon, target : Pokemon):
        damaging_moves = [m for m in user.moves if m.power and m.current_pp > 0]
        best_damage = 0

        if damaging_moves:
            best_damage = max(
                calculate_damage(battle, user, target, m)["damage"]
                for m in damaging_moves
            )
        else:
            best_damage = 0

        damages = [
            calculate_damage(battle, target, user, m)["damage"]
            for m in target.moves if m.power and m.current_pp > 0
        ]
        enemy_damage = max(damages) if damages else 0
        enemy_faster = target.stats[Stats.SPEED.value] > user.stats[Stats.SPEED.value]

        if enemy_damage >= user.current_hp and enemy_faster:
            if best_damage < target.current_hp:
                return True
        return False
    
    
    def choose_move(self, battle, user, target) -> Move:
        top_score = float("-inf")
        top_moves = []
        for move in user.moves:
            score = self.evaluate_move(battle, user, move, target)

            if score > top_score:
                top_score = score
                top_moves = [move]
            elif score == top_score:
                top_moves.append(move)
        return choice(top_moves)
    

    def choose_switch(self, battle) -> Pokemon:
        scores = [0] * len(battle.player.team)

        for i in range(len(battle.player.team)):
            mon = battle.player.team[i]
            
            # Cannot switch in a fainted Pokemon
            if mon.is_fainted():
                scores[i] = -65536
                continue

            if mon == battle.player.active:
                # Cannot switch in current Pokemon
                scores[i] = -65536
                continue
            
            # Evaluate candidate's moves' effectiveness against current enemy
            for move in mon.moves:
                if move.current_pp <= 0:
                    continue
                if move.power:
                    # Accounts for STAB, total damage, and type effectiveness
                    scores[i] += calculate_damage(battle, mon, battle.enemy.active, move)["damage"] // 2
            # Also consider potential max damage user will have to tank on switch in
            damages = [calculate_damage(battle, battle.enemy.active, mon, m)["damage"] for m in battle.enemy.active.moves if m.power]
            enemy_damage = max(damages) if damages else 0
            
            if mon.current_hp <= enemy_damage:
                scores[i] -= 200
        
        best_score = max(scores)
        best_index = scores.index(best_score)
        return battle.player.team[best_index] if best_score != -65536 else None
    

    def choose_action(self, battle : "BattleState", user : Pokemon, target : Pokemon):
        if self.consider_switch(battle, user, target):
            replacement = self.choose_switch(battle)
            if replacement:
                return ("switch", replacement)

        move = self.choose_move(battle, user, target)
        return ("move", move)