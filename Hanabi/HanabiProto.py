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

    def __str__(self):
        #return f"The {self.color.name} {self.rank}."

        return colored.stylize(f"The {self.color.name} {self.rank}.", colored.fg(self.color.name.lower()))


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
            print (c)


class Player:

    def __init__(self, name, hand):
        self.name = name
        self.hand = hand


class FireworkPiles:

    def __init__(self):

        # Default value for each color is 0, ie an empty pile.
        self.firework_dict = collections.defaultdict(int)

    def play_card_on_pile(self, card):
        rank = card.rank
        color = card.color

        if rank == self.firework_dict[color]+1:
            self.firework_dict[color] += 1

        return False


class HanabiGame():

    def __init__(self, num_of_players):
        self.deck = Deck()
        self.players = []
        for p in range(0, num_of_players):

            cur_name = f"Player {p}"
            cur_hand = Hand(self.deck.deal_hand())
            self.players.append(Player(cur_name, cur_hand))

        self.players_turn = 0
        self.hints = HINT_MAX
        self.firework_piles = FireworkPiles()
        self.discarded_cards = []
        self.bombs = 3

        # Start the fun!
        self.handle_begin_turn()

    def increment_turn(self):
        self.players_turn += (self.players_turn +1)%len(self.players)
        return self.players_turn

    def remove_hint(self):
        if self.hints == 0:
            print("Error: can't remove hint")
        else:
            self.hints += 1
        return

    def add_hint(self):
        self.hints = math.floor(self.hints + 1, HINT_MAX)
        return

    def handle_give_hint(self, hint):
        # TODO:
        self.increment_turn()
        return

    def handle_play_card(self, card_index):
        current_player = self.players[self.players_turn]
        print(f"{current_player.name} played {current_player.hand.cards[card_index]}")
        self.firework_piles.play_card_on_pile(current_player.hand.cards[card_index])
        new_card = self.deck.draw_card()
        current_player.hand.cards[card_index] = new_card
        print(f"{current_player.name} drew the {new_card}")
        return

    def handle_discard_card(self, card_index,add_hint=True):
        current_player = self.players[self.players_turn]

        if add_hint:
            self.add_hint()

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
        self.player_display()

        cur_player = self.players[self.players_turn]

        valid_play = False
        while not valid_play:
            print('please enter what youd like to do (play or discard)')
            choice = input()
            if choice == 'play':
                print('Which Card? (index)')
                num = input() # will break if input is bad
                self.handle_play_card(int(num))
                print(f"You played the {cur_player.hand.cards[int(num)]}")

                valid_play = True

            elif choice == 'discard':
                valid_play = True

        print()
        print()

        self.handle_end_turn()

        return

    def show_game_status(self):
        for p in self.players:
            print(p.name)
            p.hand.show_hand()

    def player_display(self):
        cur_player = self.players[self.players_turn]
        print(f"It is {cur_player.name}'s turn.")

        buffer = 30

        # Print Player names

        for p in self.players:
            if p != cur_player:
                print(p.name.ljust(buffer), end="")

        print()

        # Print Hand contents
        for card in range(0, 4):
            for p in self.players:
                if p != cur_player:
                    try:
                        cur_card = p.hand.cards[card].__str__()
                    except:
                        cur_card = ""
                    print(cur_card.ljust(buffer), end="")
            print()


game = HanabiGame(4)

