from Player import Player as Pl
import CardUtils as CU
from random import randint, random
from typing import List
from copy import copy
import HandEvaluator as HE


class SimpleAIPlayer(Pl):
    _pocketStrength = [
        [100, 100,  90,  90,  80,  60,  60,  60,  60,  60,  60,  60,  60],  # A
        [90, 100,  90,  80,  70,  50,  40,  40,  40,  40,  40,  40,  40],   # K
        [80,  70, 100,  80,  70,  60,  40,   0,   0,   0,   0,   0,   0],   # Q
        [70,  60,  60, 100,  80,  70,  50,  30,   0,   0,   0,   0,   0],   # J
        [50,  50,  50,  60,  90,  70,  60,  40,   0,   0,   0,   0,   0],   # T
        [30,  30,  30,  40,  40,  80,  70,  60,  30,   0,   0,   0,   0],   # 9
        [0,   0,   0,  30,  30,  40,  70,  60,  50,  30,   0,   0,   0],    # 8
        [0,   0,   0,   0,   0,   0,  30,  60,  60,  40,  30,   0,   0],    # 7
        [0,   0,   0,   0,   0,   0,   0,  30,  50,  60,  40,   0,   0],    # 6
        [0,   0,   0,   0,   0,   0,   0,   0,  30,  40,  40,  30,   0],    # 5
        [0,   0,   0,   0,   0,   0,   0,   0,   0,  30,  40,  40,  30],    # 4
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  40,  30],    # 3
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  40]     # 2
    ]

    # subtracted from playing probabilities, rendering the player tighter or looser
    _tightness: int
    _coms: List[int]  # community cards
    # minimum probability of playing a hand, thus, a measure for how prone the AI is to bluff when having a bad hand
    _bluffiness: int
    # lower probability threshold of not folding. Resetted to 'bluffiness' at the beginning of each hand, but rises during a
    # hand when bluffing, making going on with the bluff more likely.
    _bluffing: int
    # does the AI computes pot odds for making a decision
    _usePotOdds: bool
    # range of a random added on pot odd calculations. This simulates computational imprecision

    def __init__(self, name):
        super().__init__(name)
        self._tightness = randint(-25, 25)
        self._bluffiness = randint(1, 30)
        self._usePotOdds = randint(0, 1) == 1
        self._calcAccuracy = random() * 0.05

    def notifyBeginOfHand(self, dealer):
        self._coms = []
        self._bluffing = self._bluffiness

    def notifyCommunityCards(self, cards: List[int]):
        self._coms = copy(cards)

    def demandBet(self, demand: int, minRaiseValue: int, potSize: int) -> int:
        if len(self._coms) < 3:
            return self._preFlopBet(demand, minRaiseValue)
        elif len(self._coms) == 3:
            return self._postFlopBet(demand, minRaiseValue, potSize)
        elif len(self._coms) == 4:
            return self._postFlopBet(demand, minRaiseValue, potSize)
        else:
            return self._postFlopBet(demand, minRaiseValue, potSize)

    # _______________ evaluate pocket cards _______________

    def _preFlopBet(self, demand: int, minRaiseValue: int) -> int:
        threshold = self._getPocketStrength() + randint(-3, 3)
        dice = randint(0, 99)
        return self._getBet(demand, minRaiseValue, threshold, dice)

    def _getPocketStrength(self) -> int:
        highVal = CU.getCardValue(self.pockets[0])
        lowVal = CU.getCardValue(self.pockets[1])
        if (lowVal < highVal):
            aux = highVal
            highVal = lowVal
            lowVal = aux

        highVal = len(self._pocketStrength) - highVal - 1
        lowVal = len(self._pocketStrength) - lowVal - 1

        if CU.getCardSuit(self.pockets[0]) != CU.getCardSuit(self.pockets[1]):
            pktStr = self._pocketStrength[lowVal][highVal]
        else:
            pktStr = self._pocketStrength[highVal][lowVal]

        return pktStr - self._tightness

    # _______________  evaluate post flop hands  _______________

    def _postFlopBet(self, demand: int, minRaiseValue: int, potSize: int) -> int:
        cards = self.pockets + self._coms
        hand = HE.evaluateHand(cards)
        # threshold by current hand
        # TODO: make deck agnostic
        rankThreshold = 13 * hand[0] + hand[1]
        # threshold by outs
        outThreshold = 0
        if self._usePotOdds:
            outs = self._getOuts(cards, hand[0])
            improveProp = len(outs) / 52 - len(cards)
            improveProp += 2 * self._calcAccuracy * random() - self._calcAccuracy
            improveProp = max(improveProp, 0)
            potShare = demand / (potSize + demand - self.bet)
            potShare += 2 * self._calcAccuracy * random() - self._calcAccuracy
            potShare = max(potShare, 0)
            if improveProp > potShare:
                outThreshold = 100
        # decide
        threshold = max(rankThreshold, outThreshold)
        dice = randint(0, 13 * HE.STRAIGHFLUSH + 12)
        return self._getBet(demand, minRaiseValue, threshold, dice)

    def _getOuts(self, cards, handRank):
        """
        Computes all outs for hands where exactly one card is missing.

        cards:
        Your hand cards.

        handRank:
        Rank of the hand.

        return:
        outs for hands with improbed hand rank.
        """
        outs = set()
        straightOuts = HE.getStraightOuts(cards)
        flushOuts = HE.getFlushOuts(cards)

        if handRank < HE.STRAIGHFLUSH:
            outs |= HE.getStraightFlushOuts(straightOuts, flushOuts)
        if handRank < HE.FOUR_OAK:
            outs |= HE.getXOfAKindOuts(cards, 4)
        if handRank < HE.FULLHOUSE:
            outs |= HE.getFullHouseOuts(cards)
        if handRank < HE.FLUSH:
            outs |= flushOuts
        if handRank < HE.STRAIGHT:
            outs |= straightOuts
        if handRank < HE.THREE_OAK:
            outs |= HE.getXOfAKindOuts(cards, 3)
        if handRank < HE.TWOPAIR:
            outs |= HE.getTwoPairOuts(cards)
        if handRank < HE.PAIR:
            outs |= HE.getXOfAKindOuts(cards, 2)

        return outs

    # _______________  get bet  _______________

    def _getBet(self, demand: int, minRaiseValue: int, threshold: int, dice: int, potSize: int = 0) -> int:
        """
        Computes the decision made when asked for a bet. Basically, the hand is not folded when 'dice' is below
        'threshold'. The '_bluffing' acts as a lower limit for the folding threshold. It is also increased for
        further bet demands for the current hand in case the 'threshold' passed is below the '_bluffing'.

        demand:
        Minimum bet demanded, same as in function demandBet().

        minRaiseValue:
        Minimum bet for a raise, same as in function demandBet().

        threshold:
        A threshold 'dice' might be compared against to decide if the hand is folded or not.

        dice:
        A value compared agains max(threshold, self._bluffing) to decide if the hand is folded or not.

        return:
        A valid return value for function demandBet().
        """
        if threshold < self._bluffing:
            threshold = self._bluffing
            self._bluffing += 20 + randint(-3, 3)

        if dice >= threshold:
            return -1  # fold

        own = self.stack + self.bet
        if own < demand:
            return own  # all in

        if own < minRaiseValue:
            return own  # call / check

        betNow = randint(minRaiseValue, own)
        return betNow
