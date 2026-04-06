from models.pokemon import Pokemon
from models.move import Move
from engine.battle_engine import resolve_turn
from ai.base_ai import BattleAI
from ai.enemy_ai import EnemyAI
from ai.heuristic_ai import PlayerHeuristicAI
from copy import deepcopy
import time

class Trainer:
    team : list[Pokemon]
    active : Pokemon
    reflect_active : bool
    light_screen_active : bool
    trainer_name : str
    ai_model : BattleAI

    def __init__(self, team : list[Pokemon], trainer_name : str, ai_model : BattleAI):
        self.team = team
        self.active = team[0]
        self.reflect_active = False
        self.light_screen_active = False
        self.trainer_name = trainer_name
        self.ai_model = ai_model
    
    def restore(self):
        for mon in self.team:
            mon.restore()
        
        self.reflect_active = False
        self.light_screen_active = False
        self.active = self.team[0]

class BattleState:
    player : Trainer
    enemy : Trainer
    turn : int
    finished : bool
    previous_move : Move
    silent : bool
    player_won : bool
    dt_string : str

    def __init__(self, player_team : list[Pokemon], enemy_team : list[Pokemon], player_name : str, enemy_name : str, enemy_categories : tuple[int], silent=False):
        self.turn = 1
        self.finished = False
        self.player_won = False
        self.previous_move = None
        self.silent = silent
        self.dt_string = f"{time.localtime()[0]}{time.localtime()[1]}{time.localtime()[2]}{time.localtime()[3]}{time.localtime()[4]}"

        eai = EnemyAI(enemy_categories)
        pai = PlayerHeuristicAI()

        self.player = Trainer(player_team, player_name, pai)
        self.enemy = Trainer(enemy_team, enemy_name, eai)
    
    def start_battle(self, player_opener : Pokemon = None) -> bool:
        if player_opener:
            self.player.active = player_opener
        
        self.log(f"You are challenged by {self.enemy.trainer_name}!")
        self.log(f"{self.enemy.trainer_name} sent out {self.enemy.active.nickname}!")
        self.log(f"Go, {self.player.active.nickname}!")
        return self.take_turn()
        
    
    def clone(self):
        return deepcopy(self)


    def take_turn(self) -> bool:
        while not self.finished:
            while not self.player.active.is_fainted() and not self.enemy.active.is_fainted():
                resolve_turn(self)
                self.turn += 1

                # Decrement trap counters
                self.player.active.trapped_turns = max(0, self.player.active.trapped_turns - 1)
                self.enemy.active.trapped_turns = max(0, self.enemy.active.trapped_turns - 1)

                # Decrement disable counters
                for move in self.player.active.moves:
                    if move.disabled_turns > 0:
                        move.disabled_turns = max(0, move.disabled_turns - 1)
                for move in self.enemy.active.moves:
                    if move.disabled_turns > 0:
                        move.disabled_turns = max(0, move.disabled_turns - 1)
                
            
            # Replace fainted Pokemon
            if self.player.active.is_fainted():
                next_up = self.player.ai_model.choose_switch(self)
                if next_up == None:
                    self.player_lose()
                else:
                    self.player.active = next_up
                    self.log(f"You're in charge, {self.player.active.nickname}!")
            else:
                next_up = self.enemy.ai_model.choose_switch(self)
                if next_up == None:
                    self.player_win()
                else:
                    self.enemy.active = next_up
                    self.log(f"{self.enemy.trainer_name} sent out {self.enemy.active.nickname}!")

        return self.player_won
    

    def switch_out(self, trainer : Trainer, replacement : Pokemon):
        benching = trainer.active

        if trainer == self.player:
            self.log(f"{benching.nickname}, switch out!")
            self.log(f"You're in charge, {replacement.nickname}!")
        else:
            self.log(f"{self.enemy.trainer_name} recalled {benching.nickname}!")
            self.log(f"{self.enemy.trainer_name} sent out {replacement.nickname}!")

        benching.on_switch_out()
        trainer.active = replacement


    def player_lose(self):
        self.log(f"{self.player.trainer_name} is out of useable POKéMON!")
        self.log(f"{self.player.trainer_name} blacked out!")
        self.finished = True
        self.player_won = False
    

    def player_win(self):
        self.log(f"{self.player.trainer_name} defeated {self.enemy.trainer_name}!")
        self.finished = True
        self.player_won = True
    

    def start_simulation(self, num_battles: int, progress_callback=None):
        times = []
        player_wins = 0
        team_size = len(self.player.team)

        lead_wins = [0] * team_size
        lead_battles = [0] * team_size

        for i in range(num_battles):
            if self.silent:
                try:
                    avg = sum(times) / len(times)
                    eta = avg * (num_battles - i)
                    eta_min = f"{int(eta // 60):02d}"
                    eta_sec = f"{int(eta % 60):02d}"
                except ZeroDivisionError:
                    eta_min = None
                    eta_sec = None

                print(
                    f"Running battle {i+1} of {num_battles}... "
                    f"(ETA: {eta_min if eta_min is not None else '--'}:"
                    f"{eta_sec if eta_sec is not None else '--'})",
                    end='\r'
                )

            start = time.perf_counter()

            lead_index = i % team_size
            lead = self.player.team[lead_index]
            self.log(f"\nBATTLE #{i+1}")
            result = self.start_battle(lead)

            player_wins += int(result)
            lead_wins[lead_index] += int(result)
            lead_battles[lead_index] += 1

            end = time.perf_counter()
            times.append(end - start)

            if progress_callback:
                progress_callback(i+1)
            
            # Clean-up
            self.player.restore()
            self.enemy.restore()
            self.finished = False
            self.player_won = False

        print("\n\n=== RESULTS ===")

        overall_win_rate = (player_wins / num_battles) * 100
        print(f"Win Rate: {overall_win_rate:.2f}%")

        best_index = lead_wins.index(max(lead_wins))
        best_name = self.player.team[best_index].nickname

        if lead_battles[best_index] > 0:
            best_win_rate = (lead_wins[best_index] / lead_battles[best_index]) * 100
        else:
            best_win_rate = 0

        print(
            f"Best Lead: {best_name}, "
            f"Win Rate: {best_win_rate:.2f}% "
            f"({lead_wins[best_index]} wins in {lead_battles[best_index]} battles)"
        )
    
        results = {
            "player_wins": player_wins,
            "num_battles": num_battles,
            "overall_win_rate": overall_win_rate,
            "best_lead": best_name,
            "best_win_rate": best_win_rate,
            "lead_wins": lead_wins,
            "lead_battles": lead_battles,
            "best_index": best_index,
            "log_file": f"log_{self.dt_string}.txt"
        }

        return results
    
    def log(self, message):
        if not self.silent:
            print(message)

        # Recording to logbook
        with open(f"logs/log_{self.dt_string}.txt", "a") as f:
            f.write("\n" + message)