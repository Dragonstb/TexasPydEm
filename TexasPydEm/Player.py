from UserAgent import UserAgent
from typing import List


class Player(UserAgent):

    FOLD = -1
    _INACTIVE = 0
    _ELIGIBLE = 1
    _ACTIVE = 2

    opens: List[int]    # player's open cards
    pockets: List[int]  # player's concealed cards
    stack: int          # number of chips the player owns and that have not been betted
    bet: int            # number of chips the player is betting in the current hand
    active: bool        # DEPRECATED (replaced by __status)
    # has the player yet *not* been asked for action in the current betting interval
    yetUnasked: bool
    __status: int       # status when playing a hand: active, eligible, or inactive

    def __init__(self, name):
        super().__init__(name)
        self.opens = []
        self.pockets = []
        self.bet = 0
        self.stack = 0
        self.__status = Player._ACTIVE

    def isActive(self):
        """
        A player is active when he/she is still actively participating in playing a hand.

        return:
        Is this player active?
        """
        return self.__status == Player._ACTIVE

    def isEligible(self):
        """
        An eligible player may still win at least one (side) pot. She/he can be active, or out of play
        while eligible for winning at least one (side) pot (i.e, the player is all in).

        return:
        Is this player eligible?
        """
        return self.__status == Player._ELIGIBLE or self.__status == Player._ACTIVE

    def setActive(self):
        """
        A player is active when he/she is still actively participating in playing a hand. ACTIVE players are also
        ELIGIBLE.
        """
        self.__status = Player._ACTIVE

    def setEligibleOnly(self):
        """
        An eligible player may still win at least one (side) pot. She/he can be active, or out of play
        while eligible for winning at least one (side) pot (i.e, the player is all in).

        This method sets this player's status to ELIGIBLE. Note that this player won't be ACTIVE anymore.
        """
        self.__status = Player._ELIGIBLE

    def setInactive(self):
        """
        An inactive player neither participates in the ongoing hand any longer nor is he/she eligible
        for winning any pot of the hand. This status is usually gained by folding.

        This method sets this player's status to INACTIVE.
        """
        self.__status = Player._INACTIVE

    def getOpenCards(self) -> List[int]:
        return self.opens

    def getPocketCards(self) -> List[int]:
        return self.pockets

    def getAllCards(self) -> List[int]:
        return self.opens + self.pockets

    def clearAllCards(self):
        self.opens = []
        self.pockets = []

    def clearAll(self):
        self.clearAllCards()
        self.bet = 0
        self.active = True
        self.__status = Player._ACTIVE

    def incBet(self, value: int):
        """
        Increases this player's stakes by 'value' and decreases the player's stack by the same amount. If the stack is
        lower than the argument, the transfer from stack to stakes is limited to the stack size.

        value:
        Number of chips to become at stakes now. Passing a negative number indeed "unbets" the chips and puts them back
        to the player's stack. Thsi could lead to a negative bet.
        """
        self.bet += value
        self.stack -= value
        if (self.stack < 0):
            self.bet += self.stack
            self.stack = 0

    def demandBet(self, demand: int, minRaiseValue: int, potSize: int) -> int:
        """
        The croupier asks the player for an action.

        demand:
        Betting height of the stakes in the current hand.

        minRaiseVale:
        How much the player has to bet in case she/he wanna raise.

        potSize:
        The current pot size. This is a convenient argument, because players could compute the pot size by themselfs.

        return:
        Negative number for folding. Non-negative values is how much the player wants to bet in total now. 'In total'
        here means that former bets in this hand are included. I.e. the value returned should be at least 'demand'.
        """
        return Player.FOLD
