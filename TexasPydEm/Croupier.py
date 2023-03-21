from random import randint;

class Croupier():
    
    def __init__(self):
        self.restoreDeck()
        
    def restoreDeck(self):
        self.cards = list(range(0, 52))
    
    def drawCards(self, numCards: int):
        picks = min(numCards, len(self.cards))
        drawn = []
        for pick in range(picks):
            cardIndex = randint(0, len(self.cards) - 1)
            card = self.cards.pop(cardIndex)
            drawn.append(card)
        return drawn