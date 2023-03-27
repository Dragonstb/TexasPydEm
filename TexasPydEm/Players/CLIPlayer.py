from Player import Player
import Localization as Loc
from functools import reduce
from typing import List


class CLIPlayer(Player):

    # TODO: localize
    # TODO: When entering a value, it always ends in the 'cannot bet lower than demand' branch (words work, though)
    comCards: str
    myCards: str
    nameLen: int
    valLen: int
    you: str

    def isHuman(self):
        return True

    def setPlayers(self, players: List[Player]):
        super().setPlayers(players)
        self.you = '+ YOU +'
        self.valLen = 8
        self.nameLen = 0
        for pl in self.players:
            self.nameLen = max(self.nameLen, len(pl.name))
        self.nameLen = max(self.nameLen, len(self.you))
        self.nameLen += 1

    def notifyBeginOfHand(self, dealer):
        self.comCards = '-'
        print()
        pattern = Loc.getString(Loc.DEALS_CARDS)
        print(pattern.format(dealer.name))

    def notifyCardDealing(self, player: Player):
        if player is self and len(player.getAllCards()) > 1:
            pattern = Loc.getString(Loc.PLAYERS_OPEN_CARDS)
            cardNames = [Loc.getCard(card) for card in player.getAllCards()]
            self.myCards = reduce(lambda a, b: a+', '+b, cardNames)
            print(pattern.format(player.name, self.myCards))

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

    def demandBet(self, demand: int, minRaiseValue) -> int:
        inp = None
        while inp is None:
            self.printPlayerStats()
            print()
            pattern = 'pocket cards: {0}, community cards: {1}'
            print(pattern.format(self.myCards, self.comCards))
            print('current bet: '+str(demand) +
                  ', for raise: '+str(minRaiseValue))
            inp = input('enter your action: ')
            if inp == 'call' and self.bet < demand:
                return demand
            elif inp == 'check' and self.bet == demand:
                return demand
            elif inp == 'fold':
                return -1
            elif inp == 'help':
                self.printHelp()
                inp = None
            else:
                try:
                    value = str.isdigit(inp)
                    value = self.cleanValue(value, demand, minRaiseValue)
                    if value is not None:
                        return value
                    else:
                        inp = None
                except KeyboardInterrupt:
                    pass
                except BaseException:
                    inp = None

    def notifyPotWin(self, player, win: int):
        pattern = Loc.getString(Loc.POT_WIN)
        print()
        print(pattern.format(player.name, str(win), str(win - player.bet)))

    def notifyCommunityCards(self, cards: List[int]):
        pattern = Loc.getString(Loc.COMMUNITY_CARDS)
        cardNames = [Loc.getCard(card) for card in cards]
        self.comCards = reduce(lambda a, b: a+', '+b, cardNames)
        print()
        print(pattern.format(self.comCards))

    def notifyElimination(self, player):
        pattern = Loc.getString(Loc.PLAYER_ELIMINATED)
        print(pattern.format(player.name))

    def notifyEndOfHand(self):
        print('----------')

    # _______________ utilities _______________

    def fitToLength(self, string: str, length: int) -> str:
        if len(string) < length:
            return string + ' '*(length - len(string))
        else:
            return string[0:length]

    def singlePlayerStats(self, pl: Player) -> str:
        pattern = '  {0} {1} {2} {3}'
        if pl is not self:
            name = pl.name
        else:
            name = self.you
        name = self.fitToLength(name, self.nameLen)
        stack = str(pl.stack)
        stack = self.fitToLength(stack, self.valLen)
        bet = str(pl.bet)
        bet = self.fitToLength(bet, self.valLen)
        if pl.isActive():
            status = ''
        elif pl.isEligible():
            if pl.stack == 0:
                status = 'all in'
            else:
                status = ''
        else:
            status = 'folded'
        return pattern.format(name, stack, bet, status)

    def printPlayerStats(self):
        print()
        print('  '+self.fitToLength('NAME', self.nameLen)+' ' +
              self.fitToLength('STACK', self.valLen)+' '+self.fitToLength('BET', self.valLen))
        for pl in self.players:
            print(self.singlePlayerStats(pl))

    def cleanValue(self, value: int, demand: int, minRaiseValue: int):
        bet = min(value, self.bet+self.stack)
        if bet < 0:
            # folding, that's fine
            return -1
        elif bet < demand and bet < self.bet + self.stack:
            print('can\'t bet less than demanded value of ' +
                  str(demand)+', except for all in')
            print()
            return None
        elif bet < demand and bet == self.bet + self.stack:
            # all in
            return bet
        elif bet == demand:
            # checking, that's fine, too
            return bet
        elif bet < minRaiseValue:
            print('needs to bet at least '+str(minRaiseValue)+' for raising')
            print()
            return None
        else:
            return bet

    def printHelp(self):
        """
        Once fully implemented, this method prints the available commands and what they are do to standard output.
        """
        print()
        print('help has yet not been fully implemented yet. We are sorry for hte inconvenience')
        print()
