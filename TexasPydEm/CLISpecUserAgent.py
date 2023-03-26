from UserAgent import UserAgent
import Localization as Loc
from functools import reduce
from typing import List
from Player import Player


class CLISpecUserAgent(UserAgent):

    def setPlayers(self, players: List[Player]):
        print()
        print('the game commences:')
        super().setPlayers(players)
        print('--------------')
        for pl in self.players:
            pattern = Loc.getString(Loc.PLAYER_TAKES_SEAT)
            print(pattern.format(pl.name))
        print('--------------')

    def notifyBeginOfPlay(self, dealer):
        print()
        pattern = Loc.getString(Loc.DEALS_CARDS)
        print(pattern.format(dealer.name))
        print()

    def notifyCardDealing(self, player: Player):
        pattern = Loc.getString(Loc.PLAYERS_OPEN_CARDS)
        cardNames = [Loc.getCard(card) for card in player.getAllCards()]
        formatted = reduce(lambda a, b: a+', '+b, cardNames)
        print(pattern.format(player.name, formatted))

    def announceFirstDealer(self, player):
        print()
        print(Loc.getString(Loc.FIRST_DEALER).format(player.name))
        print('---------------')

    def notifySmallBlind(self, player):
        print()
        pattern = Loc.getString(Loc.SET_SMALL_BLIND)
        print(pattern.format(player.name))

    def notifyBigBlind(self, player):
        pattern = Loc.getString(Loc.SET_BIG_BLIND)
        print(pattern.format(player.name))
        print()

    def notifyFolding(self, player):
        pattern = Loc.getString(Loc.PLAYER_FOLDS)
        print(pattern.format(player.name))

    def notifyCheck(self, player):
        pattern = Loc.getString(Loc.PLAYER_CHECKS)
        print(pattern.format(player.name))

    def notifyRaise(self, player):
        pattern = Loc.getString(Loc.PLAYER_RAISES)
        print(pattern.format(player.name, str(player.bet)))

    def notifyCall(self, player):
        pattern = Loc.getString(Loc.PLAYER_CALLS)
        print(pattern.format(player.name))

    def notifyLastPenny(self, player):
        pattern = Loc.getString(Loc.PLAYER_BETS)
        print(pattern.format(player.name, str(player.bet)))

    def notifyAllIn(self, player):
        pattern = Loc.getString(Loc.PLAYER_ALL_IN)
        print(pattern.format(player.name))

    def notifyPotWin(self, player, win: int):
        pattern = Loc.getString(Loc.POT_WIN)
        print()
        print(pattern.format(player.name, str(win), str(win - player.bet)))

    def notifyCommunityCards(self, cards: List[int]):
        pattern = Loc.getString(Loc.COMMUNITY_CARDS)
        cardNames = [Loc.getCard(card) for card in cards]
        formatted = reduce(lambda a, b: a+', '+b, cardNames)
        print()
        print(pattern.format(formatted))

    def notifyElimination(self, player):
        pattern = Loc.getString(Loc.PLAYER_ELIMINATED)
        print(pattern.format(player.name))

    def notifyEndOfHand(self):
        print('----------')
