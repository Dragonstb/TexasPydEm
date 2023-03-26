from Croupier import Croupier
from UserAgent import UserAgent as UA
import Localization as Loc
from random import randint
import CardUtils as CU
from time import sleep
from typing import List, Dict, Tuple
from Player import Player
from copy import copy
from Pot import Pot
import HandEvaluator as HE


class TexasHoldEmGame():

    PRE_GAME = 0
    IN_GAME = 1
    __MAX_PLAYERS = 10

    players: List[Player]  # the competing players
    spectators: List[UA]  # a throng of allknowing spectators
    sb: int               # current small blind
    bb: int               # current big blind
    startStack: int       # stack size at begin
    dealIdx: int          # index of current dealer in list self.players
    playIdx: int          # index of player in action in list self.players
    raiser: int           # player has raised last - DEPRECATED (unused)
    curBet: int           # current height of bet
    comCards: List[int]   # community cards
    pots: List[Pot]       # pot and split pots
    # player last to be asked for action DEPRECATED (unused)
    lastToBeAsked: Player

    def __init__(self):
        self.state = self.PRE_GAME
        self.croupier = Croupier()
        self.players = []
        self.spectators = []
        self.sb = 250
        self.bb = 2*self.sb
        self.startStack = 20*self.bb

    # _______________ pre game _______________

    def addPlayer(self, player):
        if self.state != TexasHoldEmGame.PRE_GAME:
            raise RuntimeError(Loc.getString(Loc.GAME_HAS_STARTED))

        if len(self.players) >= TexasHoldEmGame.__MAX_PLAYERS:
            raise RuntimeError(Loc.getString(Loc.TABLE_IS_FULL))

        if not isinstance(player, Player):
            raise RuntimeError(Loc.getString(Loc.NOT_AN_USERAGENT))

        if player in self.players:
            raise RuntimeError(Loc.getString(Loc.NAME_GIVEN))

        pos = randint(0, len(self.players))
        self.players.insert(pos, player)

    # _______________ in game _______________

    def getActivePlayers(self) -> List[Player]:
        activePlayers = list(filter(lambda pl: pl.isActive(), self.players))
        return activePlayers

    def hasSeveralActives(self) -> bool:
        return len(self.getActivePlayers()) > 1

    def getEligiblePlayers(self) -> List[Player]:
        return list(filter(lambda pl: pl.isEligible(), self.players))

    def hasSeveralEligibles(self) -> bool:
        return len(self.getEligiblePlayers()) > 1

    def getActiveRightToDealer(self) -> Player:
        """
        Gets the next active player right to the dealer, or the dealer if this one is still active.

        return:
        First active player right to the dealer. This can also be the dealer.

        raises:
        RuntimeError when no player is active.
        """
        for idx in range(len(self.players)):
            pl = self.players[(self.dealIdx + 1 - idx) % len(self.players)]
            if pl.isActive():
                return pl
        raise RuntimeError('no active players')

    def shiftPlayIndex(self, oldIdx: int) -> Player:
        self.playIdx = (oldIdx + 1) % len(self.players)
        while not self.players[self.playIdx].isActive():
            # print('  dbg: playIdx: '+str(self.playIdx)+', oldIdx: '+str(oldIdx))
            self.playIdx = (self.playIdx + 1) % len(self.players)
            if self.playIdx == oldIdx:
                if self.players[self.playIdx].isActive():
                    break
                else:
                    return None
        return self.players[self.playIdx]

    def deactivatePlayer(self, player: Player, eligible: bool):
        player.active = False
        if eligible:
            player.setEligibleOnly()
        else:
            player.setInactive()

    def findFirstDealer(self) -> int:
        highCard = -1
        highPlayer: UA
        for pl in self.players:
            cards = self.croupier.drawCards(1)
            drawn = cards[0]
            if CU.isHigherCard(drawn, highCard):
                highCard = drawn
                highPlayer = pl
            pl.opens = cards
            [ua.notifyCardDealing(pl) for ua in self.uas]
        return self.players.index(highPlayer)

    def fold(self, player: Player):
        player.setInactive()
        [ua.notifyFolding(player) for ua in self.uas]

    def check(self, player: Player, verbose: bool = True):
        if verbose:
            [ua.notifyCheck(player) for ua in self.uas]

    def raiseBet(self, player: Player, verbose: bool = True):
        self.raiser = player
        self.curBet = player.bet
        if verbose:
            [ua.notifyRaise(player) for ua in self.uas]

    def addToPot(self, players: List[Player], bet: int):
        """
        Adds the given players to the (side) pot created at the given value of 'bet'. If no such pot exists, a new pot
        becomes opened for the players.

        players:
        List of players to be added as eligible for winning the pot.

        bet:
        Betting level for the pot.
        """
        # look for an already existing pot that has been formed at this betting valuee
        alreadyAside = list(filter(lambda pot: pot.bet == bet, self.pots))
        if len(alreadyAside) == 0:
            # open new side pot
            sidePot = Pot(bet)
            # the original list might be used elsewhere, so just a copy here
            sidePot.eligible = copy(players)
            self.pots.append(sidePot)
        else:
            # join the existing pot
            # there can't be more than one side pot with the same value of bet as player has due
            #     to the way we construct new pots
            alreadyAside[0].eligible += players

    def allIn(self, player: Player):
        self.addToPot([player], player.bet)
        [ua.notifyAllIn(player) for ua in self.uas]

    def dealPocketCards(self):
        for idx in list(range(1, 1+len(self.players))):
            self.playIdx = (self.dealIdx + idx) % len(self.players)
            player = self.players[self.playIdx]
            cards = self.croupier.drawCards(2)
            player.pockets = cards

    def dealCommunityCards(self, numCards: int):
        self.comCards += self.croupier.drawCards(numCards)
        [ua.notifyCommunityCards(self.comCards) for ua in self.uas]
        sleep(1)

    def announceWins(self, wins: Dict[Player, int]):
        for winner, win in wins.items():
            [ua.notifyPotWin(winner, win) for ua in self.uas]

    def allSevenCards(self, player: Player) -> List[int]:
        """
        Gets the community cards ans the player's pocket cards.

        player:
        Player for which we need all of her/his seven cards.

        return:
        List containing the player's pockets along the community cards
        """
        return player.getPocketCards() + self.comCards

    def getBestHandOwner(self, comps: List[Player]) -> List[Player]:
        if len(comps) < 1:
            # TODO: localize
            raise ValueError('determining best hand of anybody')
        elif len(comps) > 1:
            lead = [comps[0]]
            leadHand = HE.evaluateHand(self.allSevenCards(lead[0]))
            others = comps[1: len(comps)]
            for pl in others:
                hand = HE.evaluateHand(self.allSevenCards(pl))
                compare = HE.compareHands(hand, leadHand)
                if compare == HE.BETTER:
                    lead = [pl]
                    leadHand = hand
                elif compare == HE.EQUAL:
                    lead.append(pl)
        else:
            lead = comps  # easy :)
        return lead

    def evaluateSinglePot(self, pot: Pot, nextPotBet: int) -> Dict[Player, int]:
        potSize = 0
        for pl in self.players:
            if pl.bet > nextPotBet:
                potSize += min(pl.bet, pot.bet) - nextPotBet
        winners: List[Player] = self.getBestHandOwner(pot.eligible)
        win = potSize // len(winners)
        remain = potSize % len(winners)
        winList = {winner: win for winner in winners}
        if remain > 0:
            # find first eligible player left to the dealer
            # TODO: one way chain of players makes life easy here
            receivers = [self.players[(self.dealIdx+1+idx) % len(self.players)] for idx in range(len(self.players))
                         if self.players[(self.dealIdx+1+idx) % len(self.players)] in pot.eligible]
            idx = 0
            while remain > 0:
                winList[receivers[idx]] += 1
                remain -= 1
                idx = (idx + 1) % len(receivers)
        return winList

    def evaluatePots(self) -> Dict[Player, int]:
        """
        Evaluates who wins how much.

        return:
        A dict that says which player wins how much. The wins are gross wins, i.e. the player's contribution to the
        pot is not


        raise:
        If no community cards have been dealt, the evaluation may raise an index error when addressing a kicker that
        is undefined.
        """
        # add remaining players to highest pot, create thsi pot if necessary
        self.addToPot(self.getActivePlayers(), self.curBet)
        # pots on decreasing order of betting value
        self.pots.sort(key=lambda pot: pot.bet, reverse=True)
        # a pivot pot at a betting value of 0, placed at the end of the list
        self.pots.append(Pot(0))
        wins = {}  # takes up a dict "player: win"

        # # TODO: All 5 com cards are revealed even if there is only one player left
        # # missing community cards if more than one player wanna cash in
        # if len( self.pots ) > 1 or len( self.pots[0].eligible ) > 1:
        #     if len( self.comCards ) < 5:
        #         self.dealCommunityCards( 5 - len(self.comCards) )
        #         sleep(0.5)

        for idx in range(len(self.pots) - 1):  # for all pots except pivot pot
            pot = self.pots[idx]
            nextPot = self.pots[idx + 1]
            winnersThisPot = self.evaluateSinglePot(pot, nextPot.bet)
            for winner, win in winnersThisPot.items():
                if winner in wins:
                    wins[winner] += win
                else:
                    wins[winner] = win
            # players eligible for higher pots are also eligible for lower pots
            nextPot.eligible += pot.eligible

        return wins

    def checkBilance(self, player: Player, verbose: bool = True):
        if player.bet > self.curBet:
            self.raiseBet(player, verbose)
        elif player.bet == self.curBet:
            if self.raiser is None:
                # setting the raiser here ensures that the bb player can also be aksed to raise his/her own bb in the
                # first betting interval in case all other players call or folds
                self.raiser = player
            if verbose:
                [ua.notifyCall(player) for ua in self.uas]
        else:
            if verbose:
                [ua.notifyLastPenny(player) for ua in self.uas]

        if player.stack == 0:
            self.allIn(player)
            player.setEligibleOnly()

    def playAction(self, player: Player):
        minRaise = self.curBet + self.bb

        playersBet = player.demandBet(self.curBet, minRaise)
        if playersBet < 0:
            self.fold(player)
        else:
            # clamp bet between the last bet and the number of chips the player is owning a.t.m.
            playersBet = min(player.stack + player.bet, playersBet)
            playersBet = max(player.bet, playersBet)
            if playersBet > self.curBet and playersBet < minRaise:
                playersBet = self.curBet
            if playersBet == player.bet:
                self.check(player)
            else:
                player.incBet(playersBet - player.bet)
                self.checkBilance(player)

    def doesIntervalGoOn(self, player: Player) -> bool:
        """
        Checks the condition for continuing / ending a betting interval.

        player:
        Player that will be asked for a reaction by the croupier in case this method return 'True'.

        return:
        Stop betting?
        """
        return player is not None and (player.bet < self.curBet or (player.yetUnasked and self.hasSeveralActives())) and self.hasSeveralEligibles()

    def playInterval(self):
        player = self.players[self.playIdx]
        while self.doesIntervalGoOn(player):
            if player.yetUnasked:
                player.yetUnasked = False  # remove flag
            self.playAction(player)
            player = self.shiftPlayIndex(self.playIdx)
            sleep(0.5)

    def firstInterval(self):
        for pl in self.getActivePlayers():
            pl.yetUnasked = True

        # set blinds
        if len(self.players) > 2:
            player = self.shiftPlayIndex(self.dealIdx)
        else:
            player = self.players[self.dealIdx]

        # small blind
        player.incBet(self.sb)
        [spec.notifySmallBlind(player) for spec in self.spectators]
        self.checkBilance(player, False)

        # big blind
        player = self.shiftPlayIndex(self.playIdx)
        player.incBet(self.bb)
        [spec.notifyBigBlind(player) for spec in self.spectators]
        self.checkBilance(player, False)

        self.lastToBeAsked = player
        self.raiser = None
        self.shiftPlayIndex(self.playIdx)
        self.playInterval()

    def playFurtherInterval(self):
        for pl in self.getActivePlayers():
            pl.yetUnasked = True
        self.lastToBeAsked = self.getActiveRightToDealer()
        self.raiser = None
        self.shiftPlayIndex(self.dealIdx)
        self.playInterval()

    def needsPlayingAnInterval(self) -> bool:
        """
        Checks if an interval needs to be played, or if we just can put the community card on the table.

        return:
        Is playing the betting interval required?
        """
        return len(self.getActivePlayers()) > 1

    def playAHand(self):
        # reset everything
        self.croupier.restoreDeck()
        self.curBet = 0
        self.comCards = []
        self.pots = []
        [pl.clearAll() for pl in self.players]
        [ua.notifyBeginOfPlay(self.players[self.dealIdx]) for ua in self.uas]

        # pockets
        self.dealPocketCards()
        for pl in self.players:
            [spec.notifyCardDealing(pl) for spec in self.spectators]
        sleep(0.5)

        # first interval
        self.firstInterval()
        if len(self.getEligiblePlayers()) == 1:
            return self.evaluatePots()

        # flop and second interval
        self.dealCommunityCards(3)
        sleep(0.5)
        if self.needsPlayingAnInterval():
            self.playFurtherInterval()
        if len(self.getEligiblePlayers()) == 1:
            return self.evaluatePots()

        # turn and third interval
        self.dealCommunityCards(1)
        sleep(0.5)
        if self.needsPlayingAnInterval():
            self.playFurtherInterval()
        if len(self.getEligiblePlayers()) == 1:
            return self.evaluatePots()

        # river and fourth interval
        self.dealCommunityCards(1)
        sleep(0.5)
        if self.needsPlayingAnInterval():
            self.playFurtherInterval()
        if len(self.getEligiblePlayers()) == 1:
            return self.evaluatePots()

        # showdown
        # TODO: reveal pocket cards to other players
        # TODO: allow for folding at this point
        return self.evaluatePots()

    def runGame(self):
        if len(self.players) < 2:
            raise ValueError(Loc.getString(Loc.LESS_THAN_TWO_PLAYERS))

        self.state = TexasHoldEmGame.PRE_GAME
        for pl in self.players:
            pl.stack = self.startStack
        self.uas = self.players + self.spectators
        [ua.setPlayers(self.players) for ua in self.uas]

        # get index of player that becomes the first dealer
        self.dealIdx = self.findFirstDealer()
        [ua.announceFirstDealer(self.players[self.dealIdx]) for ua in self.uas]

        # game loop
        while len(self.players) > 2:
            wins = self.playAHand()
            self.announceWins(wins)
            for pl, win in wins.items():
                pl.stack += win
            sleep(0.5)

            # eliminate players
            out = list(filter(lambda pl: pl.stack == 0, self.players))
            for pl in out:
                # remove from players, take care of dealIdx
                plIdx = self.players.index(pl)
                if self.dealIdx >= plIdx:
                    self.dealIdx -= 1
                del self.players[plIdx]
                [ua.notifyElimination(pl) for ua in self.uas]
                # players alive become spectators
                if pl.isHuman():
                    self.addSpectator(pl)
                else:
                    self.uas.remove(pl)

            # shift dealer
            self.dealIdx = (self.dealIdx + 1) % len(self.players)
            [ua.notifyEndOfHand() for ua in self.uas]
            sleep(0.5)

        # return winners
        return {pl: pl.stack for pl in self.players}

    # _______________ any time _______________

    def addSpectator(self, spec):
        if not isinstance(spec, UA):
            raise RuntimeError(Loc.getString(Loc.NOT_AN_USERAGENT))

        self.spectators.append(spec)
