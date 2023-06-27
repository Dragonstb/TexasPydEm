import TestMain  # this includes the module pathes
import unittest as UT
import TexasPydEm.HandEvaluator as HE
from typing import Dict
from functools import reduce
import TexasPydEm.CardUtils as CU


class HandEvaluator_UT(UT.TestCase):

    # _____________ multiplettes ______________

    def test_checkPairs_noMultiples(self):
        val = 3  # a 5
        cards = [1, 4, 11, 7, 2, 6, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 2)
        self.assertEqual(0, len(pairs), 'wrong number of pairs detected')

    def test_checkPairs_onePair(self):
        val = 3  # a 5
        cards = [val, 4, val+13, 7, 2, 6, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 2)
        self.assertEqual(1, len(pairs), 'wrong number of pairs detected')
        self.assertEqual(val, pairs[0], 'wrong pair value detected')

    def test_checkPairs_twoPairs(self):
        valA = 3  # a 5
        valB = 7  # a 9
        cards = [valA, 4, valA+13, valB, valB+26, 6, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 2)
        self.assertEqual(2, len(pairs), 'wrong number of pairs detected')
        self.assertTrue(valA in pairs, 'valA not detected')
        self.assertTrue(valB in pairs, 'valB not detected')

    def test_checkPairs_threePairs(self):
        valA = 3  # a 5
        valB = 7  # a 9
        valC = 9  # a J
        cards = [valA, valC, valA+13, valB, valB+26, valC+26, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 2)
        self.assertEqual(3, len(pairs), 'wrong number of pairs detected')
        self.assertTrue(valA in pairs, 'valA not detected')
        self.assertTrue(valB in pairs, 'valB not detected')
        self.assertTrue(valC in pairs, 'valC not detected')

    def test_checkPairs_noPairButThree(self):
        val = 3  # a 5
        cards = [val, 4, 11, val, 2, val, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 2)
        self.assertEqual(0, len(pairs), 'wrong number of pairs detected')

    def test_checkThreeOAK_one_Three(self):
        val = 3  # a 5
        cards = [val, 4, val+13, 7, val+26, 6, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 3)
        self.assertEqual(
            1, len(pairs), 'wrong number of threes of a kind detected')
        self.assertTrue(val in pairs, 'val not detected')

    def test_checkThreeOAK_twoThrees(self):
        valA = 3  # a 5
        valB = 7  # a 9
        cards = [valA, valB, valA+13, valB+13, valB+26, 6, valA+26]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 3)
        self.assertEqual(
            2, len(pairs), 'wrong number of threes of a kind detected')
        self.assertTrue(valA in pairs, 'valA not detected')
        self.assertTrue(valB in pairs, 'valB not detected')

    def test_checkFourOAK_one_Three(self):
        val = 3  # a 5
        cards = [val, 4, val+13, 7, val+26, val+39, 8]
        freqs = HE.getValueFreqs(cards)
        pairs = HE._checkMultiples(freqs, 4)
        self.assertEqual(
            1, len(pairs), 'wrong number of fours of a kind detected')
        self.assertTrue(val in pairs, 'val not detected')

    # ______________ straights ______________

    def test_checkStraight_noStr(self):
        val = -1  # no straight
        cards = [1, 2, 3, 4, 7, 9, 10]
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 0, 'bogus straight detected, \nfreqs is ' +
                         reduce(lambda a, b: str(a)+', '+str(b), freqs))

    def test_checkStraight_oneStr(self):
        val = 10  # value of straight-ending card
        cards = [val, val-1, 1, val-2, 3, val-3, val-4]
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 1, 'straight missed')
        self.assertTrue(
            val in strgt, 'straight does not ends with expected card')

    def test_checkStraight_royalStr(self):
        val = 12  # value of straight-ending card
        cards = [val, val-1, 1, val-2, 3, val-3, val-4]
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 1, 'straight missed')
        self.assertTrue(
            val in strgt, 'straight does not ends with expected card')

    def test_checkStraight_roundTheCornerStr0(self):
        cards = [4, 10, 0, 6, 12, 11, 9]  # J to 2
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 0, 'bogus straight detected, \nfreqs is ' +
                         reduce(lambda a, b: str(a)+', '+str(b), freqs))

    def test_checkStraight_roundTheCornerStr1(self):
        cards = [2, 1, 0, 6, 12, 11, 9]  # 11, 12, 0, 1, 2 (K to 4)
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 0, 'bogus straight detected, \nfreqs is ' +
                         reduce(lambda a, b: str(a)+', '+str(b), freqs))

    def test_checkStraight_roundTheCornerStr2(self):
        val = 3  # value of straight-ending card
        cards = [val, 2, 1, 0, 12, 10, 8]  # A to 5
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 1, 'straight missed')
        self.assertTrue(
            val in strgt, 'straight does not ends with expected card')

    def test_checkStraight_threeStr(self):
        val = 8  # value of straight-ending card
        cards = [val, val-1, val+1, val-2, val+2, val-3, val-4]
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs)
        self.assertEqual(len(strgt), 3, 'straights missed')
        self.assertTrue(
            val in strgt, 'straight does not ends with expected card')
        self.assertTrue(
            val+1 in strgt, 'straight does not ends with expected card')
        self.assertTrue(
            val+2 in strgt, 'straight does not ends with expected card')

    def test_checkStraight_noStrCosNeedSixCards(self):
        val = 10
        # a five-card straigh ...
        cards = [val, val-1, 1, val-2, 3, val-3, val-4]
        freqs = HE.getValueFreqs(cards)
        strgt = HE._checkStraigh(freqs, 6)  # ... but demand six cards now
        self.assertEqual(len(strgt), 0, 'straight detected, \nfreqs is ' +
                         reduce(lambda a, b: str(a)+', '+str(b), freqs))

    # ______________ flushes ______________

    def test_checkFlush_noFlush(self):
        cards = [1, 4, 8, 14, 17, 20, 31]
        freqs = HE.getSuitFreqs(cards)
        flush = HE._checkFlushes(freqs)
        self.assertEqual(
            len(flush), 0, 'flush detected, freqs are '+self.asStr(freqs))

    def test_checkFlush_aFlush(self):
        cards = [1, 4, 8, 11, 9, 20, 42]
        freqs = HE.getSuitFreqs(cards)
        flush = HE._checkFlushes(freqs)
        self.assertEqual(
            len(flush), 1, 'flush missed, freqs are '+self.asStr(freqs))
        self.assertEqual(flush[0], 0, 'incorrect fkus suite')

    def test_checkFlush_fullFlush(self):
        cards = [1, 4, 8, 9, 10, 5, 11]
        freqs = HE.getSuitFreqs(cards)
        flush = HE._checkFlushes(freqs)
        self.assertEqual(
            len(flush), 1, 'flush missed, freqs are '+self.asStr(freqs))
        self.assertEqual(flush[0], 0, 'incorrect fkus suite')

    def test_checkFlush_noFlushCosWannaMore(self):
        cards = [1, 4, 8, 3, 10, 20, 31]
        freqs = HE.getSuitFreqs(cards)
        flush = HE._checkFlushes(freqs, 6)
        self.assertEqual(
            len(flush), 0, 'flush detected, freqs are '+self.asStr(freqs))

    # ______________ straight flushes ______________

    def test_checkSF_oneSF(self):
        cards = [27, 28, 14, 29, 30, 31, 50]
        ends = [CU.getCardValue(31)]
        sf = HE._checkStraightIsFlush(cards, ends)
        self.assertTrue(sf in ends, 'sf not detected')

    def test_chechSF_twoSFs(self):
        cards = [3, 4, 5, 6, 7, 33, 34, 35, 36, 37]
        ends = [CU.getCardValue(7), CU.getCardValue(37)]
        self.assertNotEqual(ends[0], ends[1], 'badly chosen test values')
        sf = HE._checkStraightIsFlush(cards, ends)
        self.assertEqual(sf, max(ends), 'did not detect highest SF')

    def test_checkSF_justStraight(self):
        cards = [27, 28, 14, 16, 30, 31, 50]
        ends = [CU.getCardValue(31)]
        sf = HE._checkStraightIsFlush(cards, ends)
        self.assertEqual(sf, -1, 'false sf detected')

    def test_checkSF_justFlush(self):
        cards = [27, 28, 14, 33, 30, 31, 50]
        ends = [CU.getCardValue(31)]
        sf = HE._checkStraightIsFlush(cards, ends)
        self.assertEqual(sf, -1, 'false sf detected')

    # ______________ utilities ______________

    def test_otherValues_1(self):
        cards = [4, 4+13, 5, 8, 11]
        others = HE._getCardsOfOtherValue(cards, [4])
        kickers = [11, 8, 5]
        self.assertEqual(len(others), len(kickers),
                         'other values have wrong length')
        for idx in range(len(others)):
            self.assertEqual(others[idx], kickers[idx],
                             'other value not in place')

    def test_otherValues_kickNone(self):
        cards = [11, 8, 5, 4, 4+13]
        others = HE._getCardsOfOtherValue(cards, [1])
        self.assertEqual(len(cards), len(others),
                         'not all cards detected: '+self.asStr(others))
        for idx in range(len(cards)):
            self.assertEqual(others[idx], CU.getCardValue(
                cards[idx]), 'incorrect value')

    def test_otherValues_2(self):
        cards = [4, 4+13, 5, 5+13, 11]
        others = HE._getCardsOfOtherValue(cards, [4, 5])
        self.assertEqual(len(others), 1, 'incorrect length')
        self.assertEqual(others[0], 11, 'incorrect value')

    # ______________ evaluate hand ______________

    hands = [
        [2+39, 3+26, 5, 7+13, 9, 11+13, 12],
        [3+39, 3+26, 5, 7+13, 9, 11+13, 12],
        [3+39, 3+26, 5, 7+13, 9, 9+13, 12],
        [2+39, 9+26, 5, 7+13, 9, 9+13, 12],
        [2+39, 3+26, 4, 5+13, 6, 11+13, 12],
        [2+39, 3, 5, 7+13, 9, 11, 12],
        [3+39, 3+26, 7, 7+13, 9, 7+26, 12],
        [5+39, 5+26, 5, 5+13, 9, 11+13, 12],
        [2, 3, 4, 5, 6, 11+13, 12],
    ]
    values = [
        [2, 3, 5, 7, 9, 11, 12],
        [3, 3, 5, 7, 9, 11, 12],
        [3, 3, 5, 7, 9, 9, 12],
        [2, 9, 5, 7, 9, 9, 12],
        [2, 3, 4, 5, 6, 11, 12],
        [2, 3, 5, 7, 9, 11, 12],
        [3, 3, 7, 7, 9, 7, 12],
        [5, 5, 5, 5, 9, 11, 12],
        [2, 3, 4, 5, 6, 11, 12],
    ]

    def test_eval_highCard(self):
        idx = HE.HIGH
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        vals = sorted(HandEvaluator_UT.values[idx], reverse=True)
        for kick in range(5):
            self.assertEqual(combi[kick+1], vals[kick],
                             'incorrect kicker: '+str(kick))

    def test_eval_pair(self):
        idx = HE.PAIR
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        pairVal = 3
        self.assertEqual(combi[1], pairVal)
        kickers = HE._getCardsOfOtherValue(hand, [pairVal])
        for kick in range(3):
            self.assertEqual(kickers[kick], combi[kick+2],
                             'incorrect kicker: '+str(kick))

    def test_eval_twoPair(self):
        idx = HE.TWOPAIR
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        pairValA = 9
        pairValB = 3
        self.assertEqual(pairValA, combi[1], 'incorrect high pair')
        self.assertEqual(pairValB, combi[2], 'incorrect lower pair')
        kicker = HE._getCardsOfOtherValue(hand, [pairValA, pairValB])
        self.assertEqual(kicker[0], combi[3], 'incorrect kicker')

    def test_eval_three(self):
        idx = HE.THREE_OAK
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        val = 9
        self.assertEqual(combi[1], val, 'incorrect value')
        kickers = HE._getCardsOfOtherValue(hand, [9])
        self.assertEqual(combi[2], kickers[0], 'incorrect first kicker')
        self.assertEqual(combi[3], kickers[1], 'incorrect second kicker')

    def test_eval_straight(self):
        idx = HE.STRAIGHT
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        val = 6
        self.assertEqual(combi[1], val, 'incorrect straingth end')

    def test_eval_flush(self):
        idx = HE.FLUSH
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        vals = [12, 11, 9, 5, 3]
        for val in range(5):
            self.assertEqual(combi[val+1], vals[val],
                             'incorrect value at '+str(val))

    def test_eval_fullHouse(self):
        idx = HE.FULLHOUSE
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        pairVal = 3
        threeVal = 7
        self.assertEqual(combi[1], threeVal, 'incorrect three value')
        self.assertEqual(combi[2], pairVal, 'incorrect pair value')

    def test_eval_four(self):
        idx = HE.FOUR_OAK
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        val = 5
        kicker = 12
        self.assertEqual(combi[1], val, 'incorrect value')
        self.assertEqual(combi[2], kicker, 'incorrect kicker')

    def test_eval_straightFlush(self):
        idx = HE.STRAIGHFLUSH
        hand = HandEvaluator_UT.hands[idx]
        combi = HE.evaluateHand(hand)
        for h in range(len(HandEvaluator_UT.hands)):
            if h == idx:
                self.assertEqual(combi[0], h, 'combination missed: '+str(h))
            else:
                self.assertNotEqual(
                    combi[0], h, 'wrong combination detected: '+str(h))
        val = 6
        self.assertEqual(combi[1], val, 'incorrect value')

    # _______________  outs  _______________

    def test_straightOuts_openEnds(self):
        cards = [3, 4, 5, 6, 10, 11, 12]
        expect = [2, 2+13, 2+26, 2+39, 7, 7+13, 7+26, 7+39]
        outs = HE.getStraightOuts(cards)
        self.assertEqual(len(expect), len(outs), 'incorrect number of outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_straightOuts_gutshot(self):
        cards = [1, 2, 5, 6, 8, 9, 12]
        expect = [7, 7+13, 7+26, 7+39]
        outs = HE.getStraightOuts(cards)
        self.assertEqual(len(expect), len(outs), 'incorrect number of outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_straightOuts_noStraightDraw(self):
        cards = [1, 2, 6, 7, 12]
        outs = HE.getStraightOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus straight outs: '+self.asStr(outs))

    def test_flushOuts_oneSuit(self):
        cards = [3, 5, 9, 11, 14, 15, 44]
        expect = [0, 1, 2, 4, 6, 7, 8, 10, 12]
        outs = HE.getFlushOuts(cards)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of flush outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing flush out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_flushOuts_noFlushDraw(self):
        cards = [3, 5, 9, 14, 15, 24, 44]
        outs = HE.getFlushOuts(cards)
        self.assertEqual(0, len(outs), 'bogus flush outs: '+self.asStr(outs))

    def test_straighFlushOuts_draw(self):
        cards = [3, 4, 5, 6, 23, 24, 25]
        expect = [2, 7]
        strOuts = HE.getStraightOuts(cards)
        fluOuts = HE.getFlushOuts(cards)
        outs = HE.getStraightFlushOuts(strOuts, fluOuts)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of straight flush outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing straight flush out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_straighFlushOuts_justStraightDraw(self):
        cards = [3, 4, 5, 19, 23, 24, 38]
        strOuts = HE.getStraightOuts(cards)
        fluOuts = HE.getFlushOuts(cards)
        outs = HE.getStraightFlushOuts(strOuts, fluOuts)
        self.assertEqual(
            0, len(outs), 'bogus straight flush outs: '+self.asStr(outs))

    def test_straighFlushOuts_justFlushDraw(self):
        cards = [3, 4, 5, 9, 23]
        strOuts = HE.getStraightOuts(cards)
        fluOuts = HE.getFlushOuts(cards)
        outs = HE.getStraightFlushOuts(strOuts, fluOuts)
        self.assertEqual(
            0, len(outs), 'bogus straight flush outs: '+self.asStr(outs))

    def test_straighFlushOuts_nothingAtAll(self):
        cards = [3, 4, 5, 22, 23]
        strOuts = HE.getStraightOuts(cards)
        fluOuts = HE.getFlushOuts(cards)
        outs = HE.getStraightFlushOuts(strOuts, fluOuts)
        self.assertEqual(
            0, len(outs), 'bogus straight flush outs: '+self.asStr(outs))

    def test_xOfAKindOuts_4draw(self):
        cards = [3, 16, 27, 42, 49]
        expect = [29]
        outs = HE.getXOfAKindOuts(cards, 4)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of X of a kind outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing X of a kind out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_xOfAKindOuts_3draw(self):
        cards = [3, 16, 27, 49]
        expect = [29, 42]
        outs = HE.getXOfAKindOuts(cards, 3)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of X of a kind outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing X of a kind out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_xOfAKindOuts_two3draws(self):
        cards = [3, 16, 27, 40]
        expect = [1, 14, 29, 42]
        outs = HE.getXOfAKindOuts(cards, 3)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of X of a kindouts')
        for out in expect:
            self.assertTrue(out in outs, 'Missing X of a kind out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_xOfAKindOuts_no3draws(self):
        cards = [3, 4, 5, 6, 7, 8]
        outs = HE.getXOfAKindOuts(cards, 3)
        self.assertEqual(
            0, len(outs), 'bogus X of a kind outs: '+self.asStr(outs))

    def test_fullHouseOuts_twoPairs(self):
        cards = [1, 5, 7, 14, 18]
        expect = [27, 40, 31, 44]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of full house outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing full house out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_fullHouseOuts_threePairs(self):
        cards = [1, 5, 7, 14, 18, 20]
        expect = [27, 40, 31, 44, 33, 46]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of full house outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing full house out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_fullHouseOuts_triplet(self):
        cards = [1, 5, 7, 14, 27]
        expect = [18, 31, 44, 20, 33, 46]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of full house outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing full house out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_fullHouseOuts_justOnePair(self):
        cards = [1, 3, 9, 12, 14]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus full house outs: '+self.asStr(outs))

    def test_fullHouseOuts_threeTriplets(self):
        cards = [1, 3, 14, 16, 27, 29]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus full house outs: '+self.asStr(outs))

    def test_fullHouseOuts_alreadyFullHouse(self):
        cards = [1, 14, 27, 4, 17]
        outs = HE.getFullHouseOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus full house outs: '+self.asStr(outs))

    def test_twoPiarOuts_onePairPresent(self):
        cards = [4, 17, 7, 10, 11]
        expect = [20, 33, 46, 23, 36, 49, 24, 37, 50]
        outs = HE.getTwoPairOuts(cards)
        self.assertEqual(len(expect), len(
            outs), 'incorrect number of two pair outs')
        for out in expect:
            self.assertTrue(out in outs, 'Missing two pair out: ' +
                            str(out)+', got outs: '+self.asStr(outs))

    def test_twoPairOuts_alreadyTwoPairs(self):
        cards = [1, 14, 7, 20, 8]
        outs = HE.getTwoPairOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus two pair outs: '+self.asStr(outs))

    def test_twoPairOuts_justSingles(self):
        cards = [1, 5, 8, 9, 12]
        outs = HE.getTwoPairOuts(cards)
        self.assertEqual(
            0, len(outs), 'bogus two pair outs: '+self.asStr(outs))

    #############

    def asStr(self, lst):
        if len(lst) > 1:
            return reduce(lambda a, b: str(a)+', '+str(b), lst)
        elif len(lst) == 1:
            return str(lst)
        else:
            return '><'
