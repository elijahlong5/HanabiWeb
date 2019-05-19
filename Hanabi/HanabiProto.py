from enum import Enum

import colored
import collections
import random
import math


HINT_MAX = 8


class Card:

    def __init__(self, rank, color):
        self.rank = rank
        self.color = color

        hidden_chars = len(colored.stylize('', colored.fg(self.color.name.lower())))
        self.padding = ' ' * hidden_chars

    def __str__(self):
        str = f"The {self.color.name} {self.rank}."

        return colored.stylize(f"{str}", colored.fg(self.color.name.lower()))

    def unprintable_chars(self):
        """
        Counts how many characters there are that are not printable in the string version of the element
        :return: int
        """
        count = len(self.__str__())

        for c in self.__str__():
            if c.isprintable():
                count -= 1

                print(c)

        return count


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    WHITE = "white"


class Deck:

    def __init__(self):

        self.top_of_deck = 0

        deck = []

        for color in Color:
            for rank in range(1, 5):

                deck.append(Card(rank, color))
                deck.append(Card(rank, color))

            deck.append(Card(1, color))
            deck.append(Card(5, color))

        random.shuffle(deck)

        self.deck_of_cards = deck

    def deal_hand(self):
        hand_size = 4
        hand = []
        for card in range(1, hand_size + 1):
            hand.append(self.deck_of_cards[self.top_of_deck])
            self.top_of_deck += 1
        return hand

    def draw_card(self):
        card = self.deck_of_cards[self.top_of_deck]
        self.top_of_deck += 1
        if self.top_of_deck == len(self.deck_of_cards):
            print("Just drew the last card in the deck.")
        return card


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def show_hand(self):
        for c in self.cards:
            print(c)


class Player:

    def __init__(self, name, hand, game):
        self.name = name
        self.hand = hand
        self.game = game

    def get_decision(self):
        print('asking for a decision (play,discard,hint)')
        choice = input()
        decision = dict()
        if choice == 'play':
            decision['choice'] = choice
            decision['card'] = self.play_card()
            return decision
        elif choice == 'discard':
            decision['choice'] = choice
            decision['index'] = self.discard()
            return decision
        elif choice == 'hint':
            decision['choice'] = choice
            decision['index'] = self.give_hint()
            return decision
        elif choice == 'show cards' or choice == 'show hand' or choice == 'show':
            self.hand.show_hand() # If you wish to cheat.
            return self.get_decision()
        else:
            return self.get_decision()

    def play_card(self):
        """
        :return: The card index to play
        """
        print('Which card would you like to play? (enter num 1-4)')
        num = self.get_card_from_input()

        action_card = self.hand.cards[int(num)]
        self.game.firework_piles.play_card_on_pile(action_card)
        self.hand.cards[int(num)] = self.game.deck.draw_card()
        return action_card

    @staticmethod
    def get_card_from_input():
        asking = True
        while asking:
            num = input()
            try:
                num = int(num) - 1  # to align it with the cards.
                if num in range(0, 4):
                    asking = False
            except ValueError:
                print('invalid number. enter a number between 1 and 4')
                # Eventually have people be able to change their minds and chose another move option?
        return num

    def discard(self):
        """
        :return: The card index to discard
        """
        print('asking for a number')
        num = self.get_card_from_input()

        action_card = self.hand.cards[num]
        self.game.discarded_cards.append(action_card)
        self.hand.cards[num] = self.game.deck.draw_card()
        return action_card

    def give_hint(self):
        # TODO:
        return 1# a ton of info.


class FireworkPiles:

    def __init__(self, game):

        # Default value for each color is 0, ie an empty pile.
        self.firework_dict = collections.defaultdict(int)
        self.played_cards = []
        self.game = game

    def play_card_on_pile(self, card):
        rank = card.rank
        color = card.color

        if rank == self.firework_dict[color]+1:
            self.firework_dict[color] += 1
            self.played_cards.append(card)
            print(f'{card} was played')
        else:
            print(f'{card} card was unplayable')
            self.game.bombs -= 1
            if not self.game.bombs:
                print("the game is over. need to handle this")

        return False

    def get_played_cards(self):

        return self.played_cards


class HanabiGame:

    def __init__(self, num_of_players, player_names=None):
        self.deck = Deck()
        self.players_turn = 0
        self.hints = HINT_MAX
        self.firework_piles = FireworkPiles(self)
        self.discarded_cards = []
        self.bombs = 3

        self.players = []

        for p in range(0, num_of_players):
            if not player_names or player_names[p] == '':
                cur_name = f"Player {p}"
            else:
                cur_name = f'{player_names[p]} (p{p})'
            cur_hand = Hand(self.deck.deal_hand())
            self.players.append(Player(cur_name, cur_hand, self))

        # Start the fun!
        self.handle_begin_turn()

    def increment_turn(self):
        self.players_turn += (self.players_turn + 1) % len(self.players)
        return self.players_turn

    def remove_hint(self):
        if self.hints == 0:
            print("Error: can't remove hint")
        else:
            self.hints += 1
        return

    def add_hint(self):
        """
        Adds a hint, but wont go above the HINT_MAX
        :return:
        """
        self.hints = math.min(self.hints + 1, HINT_MAX)
        return

    def handle_end_turn(self):
        # check if game is over, end the game
            # this is if all bombs have gone off, or the final round is complete
        # else call increment turn and call begin turn on that player.

        self.increment_turn()
        self.handle_begin_turn()
        return

    def handle_begin_turn(self):
        # handle beginning turn
        print(f"There are {self.hints} hint(s) available.")
        print(f'There are {self.bombs} bomb(s) left.')
        self.player_display()

        cur_player = self.players[self.players_turn]

        dec = cur_player.get_decision()  # Retrieves what the player did
        # notify the other players what just happened.
        # Every player is a listener, so do I have to create a registered listeners list?
        #       I think I can just notify all players except current players
        # maybe add this move to a game log?

        print()
        print()

        self.handle_end_turn()

        return

    def show_game_status(self):
        for p in self.players:
            print(p.name)
            p.hand.show_hand()

    def player_display(self):
        """
        Displays what the current player can see:
            The 3 other players hands, but their hand is hidden.
        :return:
        """
        cur_player = self.players[self.players_turn]
        print(f"It is {cur_player.name}'s turn.")

        buffer = 30

        # Print Player names
        end = "|  "

        divider = '_' * (buffer * (len(self.players) - 1)) + "_" * len(end) * 2
        print(divider)
        for p in self.players:
            if p != cur_player:
                print(p.name.ljust(buffer), end=end)

        print()
        print(divider)

        # Print Hand contents
        for card in range(0, 4):
            for p in self.players:
                if p != cur_player:
                    try:
                        cur_card = p.hand.cards[card].__str__()
                        pad = p.hand.cards[card].padding
                    except ValueError:
                        cur_card = ""
                        pad = ""

                    print(cur_card.ljust(buffer) + pad, end=end)

            print()
        print(divider)


game = HanabiGame(4, ['Elijah', 'John', 'Sam', 'Chathan'])
# showing that the colored letters dont align
c = Card(4, Color.BLUE)
# print(str(c.unprintable_chars()))
#
#
#
# s = "The GREEN 4."
# print(s.ljust(15)+'|x')
#
# print(str(len(c.__str__())))
print(c.__str__().ljust(15), end="")
print("|")



