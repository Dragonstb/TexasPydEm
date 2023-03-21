def isHigherCard(cardA: int, cardB: int) -> bool:
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
    return card % 13

def getCardSuit(card: int) -> int:
    return card // 13