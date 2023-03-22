import CardUtils as CU
from typing import List, Tuple

HIGH = 0
PAIR = 1
TWOPAIR = 2
THREE_OAK = 3
STRAIGHT = 4
FLUSH = 5
FULLHOUSE = 6
FOUR_OAK = 7
STRAIGHFLUSH = 8

BETTER = 1
EQUAL = 0
WORSE = -1


def getValueFreqs(cards: List[int]) -> List[int]:
    """
    Checks how many cards of each possible *value* the hand contains.

    cards:
    The list of cards in the integer representation.

    return:
    List of value frequencies. The index represents the card value, the entry in this position the value frequency.
    """
    freqs = [0 for _ in range(13) ]
    for card in cards:
        freqs[ CU.getCardValue(card) ] += 1
    return freqs


def getSuitFreqs(cards: List[int]) -> List[int]:
    """
    Checks how many cards of each possible *suit* the hand contains.

    cards:
    The list of cards in the integer representation.

    return:
    List of suit frequencies. The index represents the card suit, the entry in this position the suit frequency.
    """
    freqs = [0 for _ in range(4) ]
    for card in cards:
        freqs[ CU.getCardSuit(card) ] += 1
    return freqs


# return: hand value, combination value, kicker values
def evaluateHand(cards: List[int]) -> Tuple[int]:
    flushLength = 5
    straighLength = 5
    valFreqs = getValueFreqs( cards )
    suitFreqs = getSuitFreqs( cards )
    pairVals = _checkMultiples(valFreqs, 2)
    threeVals = _checkMultiples(valFreqs, 3)
    fourVals = _checkMultiples(valFreqs, 4)
    straightEnds = _checkStraigh(valFreqs)
    flushSuits = _checkFlushes( suitFreqs )

    if len( flushSuits ) > 0 and len(straightEnds) > 0:
        sfVal = _checkStraighIsFlush( cards, straightEnds)
        if sfVal >= 0:
            combi = (STRAIGHFLUSH, sfVal, -1)

    elif len( fourVals ) > 0:
        fourVal = max(fourVals)
        kickers = _getCardsOfOtherValue( cards, [fourVal] )
        print(kickers)
        combi = (FOUR_OAK, fourVal, kickers[0])

    elif len( pairVals ) > 0 and len( threeVals ) > 0:
        threeVal = max( threeVals )
        pairVal = max( pairVals )
        combi = (FULLHOUSE, threeVal, pairVal)

    elif len( flushSuits ) > 0:
        maxVal = -1
        for suit in flushSuits:
            suitedValues = [ CU.getCardValue(card) for card in cards if CU.getCardSuit(card) == suit]
            if len( suitedValues ) >= flushLength:
                suitMax = max( suitedValues )
                if suitMax > maxVal:
                    maxVal = suitMax
                    useVals = suitedValues
        useVals.sort(reverse=True)
        combi = (FLUSH, useVals[0], useVals[1], useVals[2], useVals[3], useVals[4])

    elif len( straightEnds ) > 0:
        val = max( straightEnds )
        combi = (STRAIGHT, val, -1)

    elif len( threeVals ) > 0:
        val = max( threeVals )
        kickers = _getCardsOfOtherValue( cards, [val])
        combi = (THREE_OAK, val, kickers[0], kickers[1])

    elif len( pairVals ) >= 2:
        highVal = max( pairVals )
        pairVals.remove( highVal )
        lowVal = max( pairVals )
        kickers = _getCardsOfOtherValue( cards, [highVal, lowVal] )

        combi = (TWOPAIR, highVal, lowVal, kickers[0] )
    elif len( pairVals ) == 1:
        kickers = _getCardsOfOtherValue( cards, pairVals)
        combi = (PAIR, pairVals[0], kickers[0], kickers[1], kickers[2])

    else:
        kickers = [ CU.getCardValue(card) for card in cards ]
        kickers.sort(reverse=True)
        combi = (HIGH, kickers[0], kickers[1], kickers[2], kickers[3], kickers[4])

    return combi


def compareHands(hand: Tuple[int], against: Tuple[int]) -> int:
    """
    Checks how good one hand is in comparison to another.

    hand:
    The *hand evaluation result* for which we wanna know how good it is relative to 'against'

    against:
    The *hand evaluation result* 'hand' is compaired against.

    return:
    BETTER if 'hand' is a better result than 'against', WORSE if 'against' is better, or EQUAL if
    both evaluation results are equally good.
    """
    steps = max( len( hand ), len( against ) )
    for idx in range( steps ):
        if hand[idx] > against[idx]:
            return BETTER
        elif against[idx] > hand[idx]:
            return WORSE
    # tie
    return EQUAL



# return: card value of each pair detected
def _checkMultiples(freqs: List[int], multiplicy: int) -> List[int]:
    """
    Determines X of a kind.

    freqs:
    how often a certain card value appears in the hand.

    multiplicy:
    2 for detecing pairs, 3 for detecting three of a kind, ...

    return: a list with the card values of each detected multiplett, empty
            if no multiplett is detected.
    """
    pairs = []
    for val in range( len(freqs) ):
        if( freqs[val] == multiplicy ):
            pairs.append( val )
    return pairs


def _checkStraigh( freqs: List[int], length: int=5 ) -> List[int]:
    """
    checks if a straight is in the hand.

    freqs:
    how often a certain card value appears in the hand.

    length = 5:
    Number of consecutive cards needed to form a straight.

    return:
    values of last card of each straigh, empty list if no straigh is detected.
    """
    vals = []
    ext = freqs + freqs[0:length-1] # straigh may start with an ace, so mirror frequencies of 2 to 5 to the end as pivots
    for val in range( len(freqs) ):
        if ext[val:val+length].count( 0 ) == 0:
            vals.append( ( val+length-1 ) % len(freqs) )
    return vals


def _checkFlushes( freqs: List[int], multiplicy: int=5 ) -> List[int]:
    """
    Checks if a suit appears a certain number of times.

    freqs:
    How many cards belong to a certain suit.

    multiplicy = 5:
    How often a suit must appear at least to trigger the flush detection.

    return:
    List of all suit values that make up a hand in the hand. Empty if no flush is present.
    """
    return [suit for suit in range( len(freqs) ) if freqs[suit] >= multiplicy ]


def _checkStraighIsFlush( cards: List[int], ends: List[int], length: int=5) -> int:
    """
    Checks is the cards that make up a straigh also form the flush.

    cards:
    The actual cards of the hand.

    ends:
    Card values of all straight-ending cards.

    return:
    The value of the end card of the straight flush, or -1 if no straight flush has been found.
    """
    # TODO: make this agnostic of card deck parameter "cards per suit"

    # all cards of the hand that have a straight-ending value
    possibleEndCards = list( filter( lambda card:CU.getCardValue(card) in ends, cards) )
    if len( possibleEndCards ) == 0:
        raise ValueError('no straight-ending cards at hand')
    # sort decreasing by card value
    possibleEndCards.sort( key = lambda val:CU.getCardValue(val), reverse = True)
    # check if the other cards that would make up a straight flush together with an end cards
    # are also part of the hand
    for endCard in possibleEndCards:
        vals = [ (CU.getCardValue(card)%13) + CU.getCardSuit(endCard)*13 for card in range(endCard-length+1, endCard, 1) ]
        inHand = list( filter( lambda val: val in cards, vals ) )
        if len( vals ) == len( inHand ):
            # all the cards below 'endCard' are part of the hand, the endCard itself had been checked beforehand
            # as 'endCard' decreases, this is the straight flush we are looking for
            return CU.getCardValue( endCard )
    return -1


def _getCardsOfOtherValue( cards: List[int], excludeValues: List[int]) -> List[int]:
    """
    Gets a list of the cards that do *not* have the given value.

    cards:
    The actual cards. Does *not* becomes altered.

    excludeValue:
    Cards of this values are to be excluded.

    return:
    New list with the values of all cards that do not have the given excludeValue, in descending order. Can be empty.
    """
    kickers = [ CU.getCardValue(card) for card in cards if CU.getCardValue(card) not in excludeValues ]
    if len( kickers ) > 0:
        kickers.sort( key=lambda card: CU.getCardValue(card), reverse=True)
    return kickers