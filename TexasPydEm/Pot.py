from Player import Player
from typing import List

class Pot():
    
    bet: int
    eligible: List[Player]
    
    def __init__(self, value: int=0) -> None:
        self.bet = value
        self.eligible = []
