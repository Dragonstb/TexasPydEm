from random import randint


class Croupier():
    """
    Handles the deck of cards.
    """

    def __init__(self):
        self.restoreDeck()

    def restoreDeck(self):
        """
        Restores the deck, which contains all cards again after this method has returned.
        """
        self.cards = list(range(0, 52))

    def drawCards(self, numCards: int):
        """
        Randomly picks removes cards from the deck and returns these cards removed.

        numCards:
        Number of cards to be drawn. This is clamped between 0 and the number of cards left in the deck.

        return:
        List of the cards drawn.
        """
        picks = min(max(0, numCards), len(self.cards))
        drawn = []
        for pick in range(picks):
            cardIndex = randint(0, len(self.cards) - 1)
            card = self.cards.pop(cardIndex)
            drawn.append(card)
        return drawn
