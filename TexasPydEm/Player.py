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
    yetUnasked: bool    # has the player yet *not* been asked for action in the current betting interval
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
        self.bet += value
        self.stack -= value
        if(self.stack < 0):
            self.bet += self.stack
            self.stack = 0

    # croupier demands a decision
    # demand: current bet value demanded
    # minRaiseValue: minimum value of bet to be reached when raising
    # return: >= 0: chips additionally transferred into the personal bet (on top on the chips already placed)
    #          < 0: fold
    def demandBet(self, demand: int, minRaiseValue) -> int:
        return Player.FOLD