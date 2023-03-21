from Player import Player

class AlwaysCallPlayer(Player):

    def demandBet(self, demand: int, minRaiseValue) -> int:
        return demand