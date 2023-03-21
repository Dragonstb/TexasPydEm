from TestMain import TestPlayer as TP
import unittest as UT
from TexasPydEm.Pot import Pot
from TexasPydEm.TexasHoldEmGame import TexasHoldEmGame as Game

class TexasPydEmGame_UT(UT.TestCase):

    # _______________ pot evaluation _______________


    def setUp(self) -> None:
        self.pair = TP( 'Player_pair' )
        self.twoPair = TP( 'Player_twoPair' )
        self.flush = TP( 'Player_flush' )
        self.players = [ self.pair, self.twoPair, self.flush ]
        for pl in self.players:
            pl.active = True
        self.game = Game()
        self.game.dealIdx = 0
        self.game.players = self.players
        self.numPlayers = len( self.players )
        self.game.comCards = [0, 1, 2, 3, 5+13] # 2 to 5 of clubs and 7 of diamonds
        self.pair.pockets = [1+13, 7+26]  # 3 of diamonds and 9 of hearts: pair
        self.twoPair.pockets = [1+13, 2+26]  # 3 and 4 of diamonds: two pair
        self.flush.pockets = [4, 7+26]     # 4 of clubs and 9 of hearts: straight flush


    def test_singlePot(self):
        bet = 100
        for pl in self.game.players:
            pl.bet = bet
        stakes = 3*100
        pot = Pot(bet)
        pot.eligible = self.players
        winners = self.game.evaluateSinglePot( pot, 0 )
        self.assertEqual( len(winners), 1, 'wrong number of winners')
        self.assertTrue( self.flush in winners, 'winner not deteced')
        self.assertEqual( winners[self.flush], stakes, 'incorrect win')


    def test_splitPot(self):
        self.flush.pockets = self.twoPair.pockets
        bet = 100 # => pot size: 300
        for pl in self.game.players:
            pl.bet = bet
        stakes = 150 # share 300 among 2
        pot = Pot(bet)
        pot.eligible = self.players
        winners = self.game.evaluateSinglePot( pot, 0 )
        self.assertEqual( len(winners), 2, 'wrong number of winners')
        self.assertTrue( self.flush in winners, 'winner not deteced: flush')
        self.assertTrue( self.twoPair in winners, 'winner not deteced: twoPair')
        self.assertEqual( winners[self.flush], stakes, 'incorrect win')
        self.assertEqual( winners[self.twoPair], stakes, 'incorrect win')


    def test_splitPotWithRemainder1(self):
        self.flush.pockets = self.twoPair.pockets
        bet = 101 # => pot size: 303
        for pl in self.game.players:
            pl.bet = bet
        stakes = 151 # share 300 among 2, but 1 remains
        pot = Pot(bet)
        pot.eligible = self.players
        winners = self.game.evaluateSinglePot( pot, 0 )
        self.assertEqual( len(winners), 2, 'wrong number of winners')
        self.assertTrue( self.flush in winners, 'winner not deteced: flush')
        self.assertTrue( self.twoPair in winners, 'winner not deteced: twoPair')
        self.assertEqual( winners[self.flush], stakes, 'incorrect lower win')
        # player twoPair sits left to the dealer
        self.assertEqual( winners[self.twoPair], stakes+1, 'incorrect higher win')


    def test_splitPotWithRemainder2(self):
        self.flush.pockets = self.twoPair.pockets
        further = TP( 'Player_further' )
        further.pockets = self.twoPair.pockets
        self.players.append( further )
        bet = 101 # => pot size: 404
        for pl in self.game.players:
            pl.bet = bet
        stakes = 134 # share 402 among 3, but 2 remain
        pot = Pot(bet)
        pot.eligible = self.players
        winners = self.game.evaluateSinglePot( pot, 0 )
        self.assertEqual( len(winners), 3, 'wrong number of winners')
        self.assertTrue( self.flush in winners, 'winner not deteced: flush')
        self.assertTrue( self.twoPair in winners, 'winner not deteced: twoPair')
        self.assertTrue( further in winners, 'winner not deteced: further')
        # player twoPair sits left to the dealer
        self.assertEqual( winners[self.twoPair], stakes+1, 'incorrect higher win: twoPair')
        # flush sits left to twoPair
        self.assertEqual( winners[self.flush], stakes+1, 'incorrect higher win: flush')
        self.assertEqual( winners[further], stakes, 'incorrect win: further')



    # _______________ evaluate all pots _______________


    def test_sidePotWithDifferentWinnersNoFolders(self):
        betA = 100
        betB = 200
        potA = Pot(betA)
        # wins main pot A
        potA.eligible = [self.flush]
        self.flush.active = False
        self.flush.bet = betA
        # fighting for pot A and B
        self.pair.bet = betB
        self.twoPair.bet = betB
        self.game.pots = [ potA ]
        self.game.curBet = betB

        wins = self.game.evaluatePots()
        self.assertEqual( len(wins), 2, 'incorrect number of winners')
        self.assertTrue( self.flush in wins, 'player flush not detected')
        self.assertTrue( self.twoPair in wins, 'player twoPait not deteced')
        self.assertEqual( wins[self.flush], 300, 'player flush got incorrect value')
        self.assertEqual( wins[self.twoPair], 200, 'player twoPair got incorrect value')


    def test_sidePotWithDifferentWinnersAndFolders(self):
        betA = 100
        betB = 200
        potA = Pot(betA)
        # has folded at 150
        further = TP( 'Player_further' )
        further.pockets = self.twoPair.pockets
        further.bet = 150
        further.active = False
        self.players.append( further )
        # wins main pot A
        potA.eligible = [self.flush]
        self.flush.active = False
        self.flush.bet = betA
        # fighting for pot A and B
        self.pair.bet = betB
        self.twoPair.bet = betB
        self.game.pots = [ potA ]
        self.game.curBet = betB

        wins = self.game.evaluatePots()
        self.assertEqual( len(wins), 2, 'incorrect number of winners')
        self.assertTrue( self.flush in wins, 'player flush not detected')
        self.assertTrue( self.twoPair in wins, 'player twoPait not deteced')
        self.assertEqual( wins[self.flush], 400, 'player flush got incorrect value')
        self.assertEqual( wins[self.twoPair], 250, 'player twoPair got incorrect value')


