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
    spectators: List[UA]   # a throng of allknowing spectators
    sb: int                # current small blind
    bb: int                # current big blind
    startStack: int        # stack size at begin
    dealIdx: int           # index of current dealer in list self.players
    playIdx: int           # index of player in action in list self.players
    raiser: int            # player has raised last - DEPRECATED (unused)
    curBet: int            # current height of bet
    comCards: List[int]    # community cards
    pots: List[Pot]        # pot and side pots
    potSize: int           # current pot size
    # the game exits if all of the players in the list have been eliminated. 'None' deactivates this
    # criterion.
    playersNeeded: List[Player]
    playUntilLeft: int     # at how many players left the game will stop

    def __init__(self):
        self.state = self.PRE_GAME
        self.croupier = Croupier()
        self.players = []
        self.spectators = []
        self.sb = 250
        self.bb = 2*self.sb
        self.startStack = 20*self.bb
        self.playersNeeded = None
        self.playUntilLeft = 1

    # _______________ pre game _______________

    def addPlayer(self, player):
        if self.state != TexasHoldEmGame.PRE_GAME:
            raise RuntimeError(Loc.getString(Loc.GAME_HAS_STARTED))

        if len(self.players) >= TexasHoldEmGame.__MAX_PLAYERS:
            raise RuntimeError(Loc.getString(Loc.TABLE_IS_FULL))

        if not isinstance(player, Player):
            raise RuntimeError(Loc.getString(Loc.NOT_AN_USERAGENT))

        if player in self.players or player in self.spectators:
            raise RuntimeError(Loc.getString(Loc.NAME_GIVEN))

        pos = randint(0, len(self.players))
        self.players.insert(pos, player)

    # _______________ in game _______________

    def getActivePlayers(self) -> List[Player]:
        """
        Returns the list of players still actively participating in the current hand. These are players that have
        neither folded yet nor are all in.

        return:
        Players actively participating in the current hand.
        """
        activePlayers = list(filter(lambda pl: pl.isActive(), self.players))
        return activePlayers

    def hasSeveralActives(self) -> bool:
        """
        Checks if more than one player is actively participating in the current hand. Actively participating players
        have neither folded yet nor are all in.

        return:
        more than one player is active?
        """
        return len(self.getActivePlayers()) > 1

    def getEligiblePlayers(self) -> List[Player]:
        """
        Returns the list of players that may be eligible for winning a (side) pot. These are players that either
        still playing the hand or are all in. This list is, espeacially, a superset of the list of active
        players.

        return:
        List of players that are to be considered when the pots are distributed.
        """
        return list(filter(lambda pl: pl.isEligible(), self.players))

    def hasSeveralEligibles(self) -> bool:
        """
        Checks if there is more than one player whose hand is to be considered when when the pots are distributed
        at the end of the hand.

        return:
        More than one player eligible for a win?
        """
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
        """
        Determines the next active player right to the current player in turn. This
        player becomes the new player in turn. His/her index in self.players becomes the new value of 'self.playIdx'.
        This might be the old value pf 'playIndex' in case there are no other active players left. It might even be
        'None' if the old player in turn ceased to be active in this turn, too.

        return:
        New value of self.playIndex, i.e., the index of the player who's turn it is now, or NONE.
        """
        self.playIdx = (oldIdx + 1) % len(self.players)
        while not self.players[self.playIdx].isActive():
            self.playIdx = (self.playIdx + 1) % len(self.players)
            if self.playIdx == oldIdx:
                if self.players[self.playIdx].isActive():
                    break
                else:
                    return None
        return self.players[self.playIdx]

    def deactivatePlayer(self, player: Player, eligible: bool):
        """
        Sets the player's 'active' flag to 'false'. Also sets the player to either eligible or inactive,
        depending of the value of 'eligible'.

        eligible:
        When 'true', the player remains eligible for winning a (side) pot. When 'false', the player becomes
        fully inactive for the remainder of the hand and won't win any money this hand.
        """
        player.active = False
        if eligible:
            player.setEligibleOnly()
        else:
            player.setInactive()

    def findFirstDealer(self) -> int:
        """
        Deals one card to each player. The player with the highest card becomes the dealer in the
        first hand. All user agents are notified about the cards dealt.

        return:
        Index of first dealer in list self.players.
        """
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
        """
        Sets the player inactive and notifies all user agents.
        """
        player.setInactive()
        [ua.notifyFolding(player) for ua in self.uas]

    def check(self, player: Player, verbose: bool = True):
        """
        If and only if verbose is set, notifies all user agents. Does nothing else.
        """
        if verbose:
            [ua.notifyCheck(player) for ua in self.uas]

    def raiseBet(self, player: Player, verbose: bool = True):
        """
        Raises the current bet and sets the player as the last who raised. If verbose is set, all
        user agents are notified.
        """
        self.raiser = player
        self.curBet = player.bet
        if verbose:
            [ua.notifyRaise(player) for ua in self.uas]

    def addPlayerToPot(self, players: List[Player], bet: int):
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
        """
        Adds the player to the list of players eligible to the current pot (which may become a side pot)
        and notifies all user agents.
        """
        self.addPlayerToPot([player], player.bet)
        [ua.notifyAllIn(player) for ua in self.uas]

    def dealPocketCards(self, numCards: int = 2):
        """
        Sets the pocket cards to each player by drawing cards from the deck.

        numCards:
        Number of cards dealt to each player.
        """
        for idx in list(range(1, 1+len(self.players))):
            self.playIdx = (self.dealIdx + idx) % len(self.players)
            player = self.players[self.playIdx]
            cards = self.croupier.drawCards(numCards)
            player.pockets = cards

    def dealCommunityCards(self, numCards: int):
        """
        Adds cards to the community cards by drawing from the deck.

        numCards:
        Number of cards to be drawn.
        """
        self.comCards += self.croupier.drawCards(numCards)
        [ua.notifyCommunityCards(self.comCards) for ua in self.uas]
        sleep(1)

    def announceWins(self, wins: Dict[Player, int]):
        """
        Announces who has won how much to each user agent.

        wins:
        A dictonary that maps the players who have won something to the number of chips the have won in this hand.
        """
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
        """
        Gets the list of players with the best hand in the showdown.

        return:
        List of players whose hands have the highest rank.
        """
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
        """
        Finds out who gets how much of the pot.

        pot:
        The pot in question.

        nextPotBet:
        Betting level of the side pot to be discussed next. That's the one with next lower amount of
        money in.

        return:
        A dictonary that maps the players who have won something from this pot to the amount of money they got out
        of this pot.
        """
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
        pot is not taken into account.


        raise:
        If no community cards have been dealt, the evaluation may raise an index error when addressing a kicker that
        is undefined.
        """
        # add remaining players to highest pot, create thsi pot if necessary
        self.addPlayerToPot(self.getActivePlayers(), self.curBet)
        # pots on decreasing order of betting value
        self.pots.sort(key=lambda pot: pot.bet, reverse=True)
        # a pivot pot at a betting value of 0, placed at the end of the list
        self.pots.append(Pot(0))
        wins = {}  # takes up a dict "player: win"

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
        """
        Compares the polayers bet against the current bet and executes the action that follows from this
        comparison (raise, check, all in, ...). In some cases, the user agents are notified when verbose is set.

        player:
        Player we are talking about.

        verbose:
        Notify all user agents.
        """
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
        """
        Controls a single play of a single player: Demands a bet and reacts on the player's response.

        player:
        The player we are talking about.
        """
        minRaise = self.curBet + self.bb

        playersBet = player.demandBet(self.curBet, minRaise, self.potSize)
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
                self.potSize = sum([pl.bet for pl in self.players])

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
        """
        Plays an entire interval.
        """
        player = self.players[self.playIdx]
        while self.doesIntervalGoOn(player):
            if player.yetUnasked:
                player.yetUnasked = False  # remove flag
            self.playAction(player)
            player = self.shiftPlayIndex(self.playIdx)
            sleep(0.5)

    def firstInterval(self):
        """
        Prepares and plays the pre-flop interval.
        """
        for pl in self.getActivePlayers():
            pl.yetUnasked = True

        # set blinds
        if len(self.players) > 2:
            player = self.shiftPlayIndex(self.dealIdx)
        else:
            player = self.players[self.dealIdx]

        # small blind
        player.incBet(self.sb)
        [ua.notifySmallBlind(player) for ua in self.uas]
        self.checkBilance(player, False)
        self.potSize += player.bet

        # big blind
        player = self.shiftPlayIndex(self.playIdx)
        player.incBet(self.bb)
        [ua.notifyBigBlind(player) for ua in self.uas]
        self.checkBilance(player, False)
        self.potSize += player.bet

        self.raiser = None
        self.shiftPlayIndex(self.playIdx)
        self.playInterval()

    def playFurtherInterval(self):
        """
        Prepares and plays a single interval that is not the pre-flop interval.
        """
        for pl in self.getActivePlayers():
            pl.yetUnasked = True
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
        """
        Plays an entire hand including preparation, betting intervals, and showdown.

        return:
        The result of self.evaluatePots()
        """
        # reset everything
        self.croupier.restoreDeck()
        self.curBet = 0
        self.comCards = []
        self.pots = []
        self.potSize = 0
        [pl.clearAll() for pl in self.players]
        [ua.notifyBeginOfHand(self.players[self.dealIdx]) for ua in self.uas]

        # pockets
        self.dealPocketCards()
        for pl in self.players:
            pl.notifyCardDealing(pl)
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
        # TODO: allow for folding at this point
        for pl in self.getEligiblePlayers():
            [ua.revealAllCards(pl) for ua in self.uas]
        return self.evaluatePots()

    def continueGame(self):
        """
        Checks if the game at all continues with another hand.

        return:
        Continue game?
        """
        playersStillThere = self.playersNeeded is None
        if not playersStillThere:
            for pl in self.playersNeeded:
                if pl in self.players:
                    playersStillThere = True
                    break
        return len(self.players) > max(self.playUntilLeft, 1) and playersStillThere

    def runGame(self):
        """
        Starts and runs the game until the game stops to continue.

        return:
        A dictionary mapping all remaining players to their stack size.
        """
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
        while self.continueGame():
            wins = self.playAHand()
            self.announceWins(wins)
            for pl, win in wins.items():
                pl.stack += win

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
            sleep(2)

        # return winners
        return {pl: pl.stack for pl in self.players}

    # _______________ any time _______________

    def addSpectator(self, spec):
        """
        Adds a spectator to the list of spectators.

        spec:
        Spectator to be added.

        raises:
        RuntimeError if the spec is not of instance UserAgent or if there is a user agent with the same
        signature in players or spectators.
        """
        if not isinstance(spec, UA):
            raise RuntimeError(Loc.getString(Loc.NOT_AN_USERAGENT))

        if spec in self.players or spec in self.spectators:
            raise RuntimeError(Loc.getString(Loc.NAME_GIVEN))

        self.spectators.append(spec)
