from Player import Player
from random import randint

class FullyRandomPlayer(Player):

    FOLD = 0
    RAISE = 1
    CHECK = 2

    def demandBet(self, demand: int, minRaiseValue) -> int:
        # assemble your options
        opts = [FullyRandomPlayer.FOLD]
        if(self.bet + self.stack >= minRaiseValue):
            opts.append(FullyRandomPlayer.RAISE)
        if self.bet + self.stack >= demand:
            opts.append( FullyRandomPlayer.CHECK )

        # choose an option
        dice = randint( 0, len(opts)-1 )
        opt = opts[ dice ]
        if opt == FullyRandomPlayer.RAISE:
            dice = randint(minRaiseValue, round( 1.025 * (self.stack + self.bet) ))
            return dice
        elif opt == FullyRandomPlayer.CHECK:
            return demand
        else:
            return -1