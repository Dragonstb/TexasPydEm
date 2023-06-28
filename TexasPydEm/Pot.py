from Player import Player
from typing import List


class Pot():

    # how high the stakes are/were when the pot is/has been founded
    bet: int
    # list of players eligible for getting some money out of this pot
    eligible: List[Player]

    def __init__(self, value: int = 0) -> None:
        """
        Generates with an empty list of eligible players.

        value:
        Height of the stakes.
        """
        self.bet = value
        self.eligible = []
