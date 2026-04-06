from models.pokemon import Pokemon
from models.move import Move
from loading import data_loader
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle_state import BattleState, Trainer

class BattleAI(ABC):
    @abstractmethod
    def choose_move(self, battle : "BattleState", user : Pokemon, target : Pokemon) -> Move:
        raise NotImplementedError
    
    @abstractmethod
    def choose_switch(self, battle : "BattleState") -> Pokemon:
        raise NotImplementedError
    
    @abstractmethod
    def choose_action(self, battle : "BattleState", user : Pokemon, target : Pokemon) -> tuple:
        raise NotImplementedError