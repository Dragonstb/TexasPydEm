import CardUtils as CU

NOT_AN_USERAGENT = 'not_an_useragent'
# trying to add a player with a name a player already at the table has
NAME_GIVEN = 'name_given'
# trying to add a player when the table is already full
TABLE_IS_FULL = 'table_is_full'
# trying to add a player when the game has already begun
GAME_HAS_STARTED = 'game_has_started'
# trying to start a game with less than two players
LESS_THAN_TWO_PLAYERS = 'less_than_two_players'
# invalid card
INVALID_CARD = 'invalid_card'

# a player has taken place at the table
PLAYER_TAKES_SEAT = 'player_takes_seat'
# a player's unconcealed cards
PLAYERS_OPEN_CARDS = 'players_open_cards'
# announce first dealer
FIRST_DEALER = 'first_dealer'
# deal cards
DEALS_CARDS = 'deals_cards'
# set small blind
SET_SMALL_BLIND = 'set_small_blind'
# set big blind
SET_BIG_BLIND = 'set_big_blind'
# a player folds
PLAYER_FOLDS = 'player_folds'
# a player raises the stakes
PLAYER_RAISES = 'player_raises'
# a player is all in
PLAYER_ALL_IN = 'player_all_in'
# a player checks
PLAYER_CHECKS = 'players_checks'
# pot win notification
POT_WIN = 'pot_win'
# community cards
COMMUNITY_CARDS = 'community_cards'
# player holds
PLAYER_CALLS = 'player_calls'
# player bets
PLAYER_BETS = 'player_bets'



loc_en_UK = {
    INVALID_CARD: 'invalid card',
    NOT_AN_USERAGENT: 'not a user agent',
    NAME_GIVEN: 'another player already has this name',
    TABLE_IS_FULL: 'the table is full',
    GAME_HAS_STARTED: 'the game has started already',
    LESS_THAN_TWO_PLAYERS: 'less than two players',
    PLAYER_TAKES_SEAT: '{0} has joined the table',
    PLAYERS_OPEN_CARDS: '{0} has cards {1}',
    FIRST_DEALER: '{0} is the first dealer',
    DEALS_CARDS: '{0} deals the cards',
    SET_SMALL_BLIND: '{0} sets the small blind',
    SET_BIG_BLIND: '{0} sets the big blind',
    PLAYER_FOLDS: '{0} folds',
    PLAYER_RAISES: '{0} raises to {1}',
    PLAYER_ALL_IN: '{0} is all in',
    PLAYER_CHECKS: '{0} checks',
    POT_WIN: '{0} wins {1}, a gain of {2}',
    COMMUNITY_CARDS: 'The community cards are {0}',
    PLAYER_CALLS: '{0} calls',
    PLAYER_BETS: '{0} bets {1}'

}


suits = [
    chr(0x2663),
    chr(0x2666),#chr(0x2662),
    chr(0x2665),#chr(0x2661),
    chr(0x2660),
]

values = [
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'T',
    'J',
    'Q',
    'K',
    'A',
]

def getString(key):
    try:
        value = loc_en_UK[key]
    except KeyError:
        value = '<' + key + '>'
    return value

#  0 = clubs 2, 1 = clubs 3, ... , 12 = clubs ace
# 13 = diamonds 2,
# 26 = heats 2,
# 39 = spades 2, ..., 51 = spades ace
def getCard(card: int):
    if card >= 0 and card < 52:
        return values[CU.getCardValue(card)] + suits[CU.getCardSuit(card)]
    else:
        return '?' + str(card) + '?'