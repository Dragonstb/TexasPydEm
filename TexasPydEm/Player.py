from UserAgent import UserAgent
from typing import List


class Player(UserAgent):
    
    FOLD = -1
    
    opens: List[int]
    pockets: List[int]
    stack: int
    bet: int
    active: bool
    
    def __init__(self, name):
        super().__init__(name)
        self.opens = []
        self.pockets = []
        self.bet = 0
        self.stack = 0
    
    def getOpenCards(self) -> List[int]:
        return self.opens
        
    def getPocketCards(self) -> List[int]:
        return self.pockets
    
    def getAllCards(self) -> List[int]:
        return self.opens + self.pockets
    
    def clearAllCards(self):
        self.opens = []
        self.pockets = []
        
    def clearAll(self):
        self.clearAllCards()
        self.bet = 0
        self.active = True
        
    def incBet(self, value: int):
        self.bet += value
        self.stack -= value
        if(self.stack < 0):
            self.bet += self.stack
            self.stack = 0
                
    # croupier demands a decision
    # demand: current bet value demanded
    # minRaiseValue: minimum value of bet to be reached when raising
    # return: >= 0: chips additionally transferred into the personal bet (on top on the chips already placed)
    #          < 0: fold
    def demandBet(self, demand: int, minRaiseValue) -> int:
        return Player.FOLD