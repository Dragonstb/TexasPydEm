def isHigherCard(cardA: int, cardB: int) -> bool:
    """
    Check if card A is higher than card B, considering the order of suits if both cards have the same value.

    cardA:
    Numerical represent of card A. Valid are values ranging from 0 to 51.

    cardB:
    Numerical represent of card B. Valid are values ranging from 0 to 51.

    return:
    Is card A higher than card B? Equal arguments or an invalid value for cardA cause 'False' to be returned.
    Likewise, a valid value for cardA and an invalid value of cardB always results in 'True'.
    """
    if cardA >= 0 and cardA < 52 and cardB >= 0 and cardB < 52:
        if getCardValue(cardA) > getCardValue(cardB):
            return True
        elif getCardValue(cardA) < getCardValue(cardB):
            return False
        else:
            return getCardSuit(cardA) > getCardSuit(cardB)
    elif cardA < 0 or cardA >= 52:
        return False
    else:
        return True


def getCardValue(card: int) -> int:
    """
    Gets the value of the card.

    card:
    Numerical represent of the card.

    return:
    The value of the card.
    """
    return card % 13


def getCardSuit(card: int) -> int:
    """
    Gets the suit of the card.

    card:
    Numerical represent of the card.

    return:
    The suit of the card.
    """
    return card // 13
