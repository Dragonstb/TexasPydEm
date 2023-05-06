from Player import Player as Pl
import CardUtils as CU
from random import randint
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

    def __init__(self, name):
        super().__init__(name)
        self._tightness = randint(-25, 25)
        self._bluffiness = randint(1, 30)
        self._usePotOdds = randint(0, 1) == 1

    def notifyBeginOfHand(self, dealer):
        self._coms = []
        self._bluffing = self._bluffiness

    def notifyCommunityCards(self, cards: List[int]):
        self._coms = copy(cards)

    def demandBet(self, demand: int, minRaiseValue: int, potSize: int) -> int:
        if len(self._coms) < 3:
            return self._preFlopBet(demand, minRaiseValue)
        elif len(self._coms) == 3:
            return self._postFlopBet(demand, minRaiseValue)
        elif len(self._coms) == 4:
            return self._postFlopBet(demand, minRaiseValue)
        else:
            return self._postFlopBet(demand, minRaiseValue)

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
        hand = HE.evaluateHand(self.pockets + self._coms)
        threshold = 13 * hand[0] + hand[1]           # TODO: make deck agnostic
        dice = randint(0, 13 * HE.STRAIGHFLUSH + 12)
        return self._getBet(demand, minRaiseValue, threshold, dice)

    def _getOuts(self, handRank):
        pass

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
