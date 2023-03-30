import Localization as Loc
from typing import List


class UserAgent():

    def __init__(self, name):
        self.name = name

    def __hash__(self) -> int:
        return hash((self.name))

    # _______________ start a game _______________

    def setPlayers(self, players):
        self.players = players

    def announceFirstDealer(self, player):
        pass

    # _______________ tell user agent what is going on _______________

    def notifyBeginOfHand(self, dealer):
        pass

    def notifyCardDealing(self, player):
        pass

    def notifySmallBlind(self, player):
        pass

    def notifyBigBlind(self, player):
        pass

    def notifyFolding(seld, player):
        pass

    def notifyCheck(self, player):
        pass

    def notifyRaise(self, player):
        pass

    def notifyCall(self, player):
        pass

    def notifyLastPenny(self, player):
        pass

    def notifyAllIn(self, player):
        pass

    def notifyPotWin(self, player, win: int):
        pass

    def notifyCommunityCards(self, cards: List[int]):
        pass

    def notifyShowdown(self):
        pass

    def notifyElimination(self, player):
        pass

    def notifyEndOfHand(self):
        pass

    def revealAllCards(self, player):
        pass

    # _______________ other _______________

    def isHuman(self):
        """
        Does this instance represent a human player or any kind of bot?

        returns:
        True for humans and aliens and super-intelligent, poker-playing cats and alike, and False for bots.
        """
        return False

    def debug(self):
        print(self.name)
        [cd.debug('  ') for pl, cd in self.comps.items()]
