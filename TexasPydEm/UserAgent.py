import Localization as Loc
from typing import List

class UserAgent():

    def __init__(self, name):
        self.name = name

    def __hash__(self) -> int:
        return hash((self.name))



    # start a game

    def setPlayers(self, players):
        self.players = players

    def announceFirstDealer(self, player):
        return



    # tell user agent what is going on

    def notifyBeginOfPlay(self, dealer):
        return

    def notifyCardDealing(self, player):
        return

    def notifySmallBlind(self, player):
        return

    def notifyBigBlind(self, player):
        return

    def notifyFolding(seld, player):
        return

    def notifyCheck(self, player):
        return

    def notifyRaise(self, player):
        return

    def notifyCall(self, player):
        return

    def notifyLastPenny(self, player):
        return

    def notifyAllIn(self, player):
        return

    def notifyPotWin(self, player, win: int):
        return

    def notifyCommunityCards(self, cards: List[int]):
        return

    # other

    def debug(self):
        print(self.name)
        [cd.debug('  ') for pl,cd in self.comps.items()]
