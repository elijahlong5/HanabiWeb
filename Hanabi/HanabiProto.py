from enum import Enum

import colored
import collections
import random
import math


HINT_MAX = 8

PRINT_GAME_STATUS = False

PLAYER_COUNT = 4

class Card:

    def __init__(self, rank, color):
        self.rank = rank
        self.color = color

        hidden_chars = len(colored.stylize('', colored.fg(self.color.name.lower())))
        self.padding = ' ' * hidden_chars
        self.printed_chars = len(self.__str__()) - hidden_chars

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


class GameOverEvents(Enum):
    BOMBS = "you ran out of bombs."
    WIN = 'you successfully completed all of the firework piles'
    RAN_OUT_OF_TURNS = 'all of the cards in the deck were used up and you ran out of turns.'


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

        self.deck_empty = False

    def deal_hand(self):
        # assuming that you can't run out of cards in the dealing phase
        hand_size = 4
        hand = []
        for card in range(1, hand_size + 1):
            hand.append(self.deck_of_cards[self.top_of_deck])
            self.top_of_deck += 1
        return hand

    def draw_card(self):
        if self.deck_empty:
            return "NO_CARD"
        card = self.deck_of_cards[self.top_of_deck]
        self.top_of_deck += 1
        if self.top_of_deck == len(self.deck_of_cards):
            if PRINT_GAME_STATUS:
                print("Just drew the last card in the deck.")
            self.deck_empty = True
        return card

    def cards_remaining(self):
        return 50 - self.top_of_deck


class FireworkPiles:

    def __init__(self, game):

        # Default value for each color is 0, ie an empty pile.
        self.firework_dict = collections.defaultdict(int)
        self.played_cards = dict()
        self.game = game

    def play_card_on_pile(self, card):
        rank = card.rank
        color = card.color

        if rank == self.firework_dict[color]+1:
            self.firework_dict[color] += 1
            #self.played_cards.append(card)
            if PRINT_GAME_STATUS:
                print(f'{card} was played')
            self.played_cards[color] = self.firework_dict[color]
        else:
            if PRINT_GAME_STATUS:
                print(f'{card} card was unplayable')
            self.game.bombs -= 1
            if not self.game.bombs:
                self.game.game_over_event(GameOverEvents.BOMBS)

        # Game is a WIN!!!
        if self.firework_dict[Color.RED] == 5 and self.firework_dict[Color.GREEN] == 5 and self.firework_dict[Color.BLUE] == 5 and self.firework_dict[Color.YELLOW] == 5 and self.firework_dict[Color.WHITE] == 5:
            self.game.game_over_event(GameOverEvents.WIN)
        return False

    def is_playable(self, card):
        """

        :param card:
        :return: True if can play right now, false otherwise
        """
        return card.rank == self.firework_dict[card.color] + 1

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

        self.game_status = ''
        self.game_over_reason = ''

        self.game_display = FourPlayerGameDisplay(self)

        self.last_round = False
        self.last_to_play = -1

        self.players = []

        self.log = []

        # The players with names will be human players, otherwise they are AI
        for p in range(0, num_of_players):
            cur_hand = self.deck.deal_hand()
            if not player_names or player_names[p] == '':
                cur_name = f"Player {p}"
                self.players.append(AdvOmniAIPlayer(cur_name, cur_hand, self))
            else:
                cur_name = f'{player_names[p]} (p{p})'
                self.players.append(Player(cur_name, cur_hand, self))

        # Start the fun!
        self.handle_begin_turn()

    def remove_hint(self):
        if self.hints == 0:
            print("Error: can't remove hint")
        else:
            self.hints -= 1
        return

    def add_hint(self):
        """
        Adds a hint, but wont go above the HINT_MAX
        :return:
        """
        self.hints = min(self.hints + 1, HINT_MAX)

        return

    def notify_listeners(self):
        # TODO: Tell listeners what play happened.
        return

    def increment_turn(self):
        self.players_turn = (self.players_turn + 1) % len(self.players)
        return

    def handle_end_turn(self):
        # check if game is over, end the game
            # this is if all bombs have gone off, or the final round is complete
        # else call increment turn and call begin turn on that player.

        if self.deck.deck_empty and self.last_to_play == -1:
            self.last_to_play = self.players_turn
        elif self.last_to_play == self.players_turn:
            # This is the last play
            self.game_over_event(GameOverEvents.RAN_OUT_OF_TURNS)

        self.increment_turn()
        self.handle_begin_turn()
        return

    def handle_begin_turn(self):
        # handle beginning turn
        if self.game_status == 'Done':
            if PRINT_GAME_STATUS:
                print('game complete')
            return
        if PRINT_GAME_STATUS:
            self.game_display.display()

        cur_player = self.players[self.players_turn]

        if PRINT_GAME_STATUS:
            print(f'Turn: {cur_player.name}')
            next_p = (self.players[((self.players_turn + 1) % len(self.players))]).name
            print("Next players name is :", next_p)
        decision_dict = cur_player.get_decision()  # Retrieves what the player did

        self.handle_decision(decision_dict)

        # needs to notify the other players what just happened.
        # Every player is a listener, so do I have to create a registered listeners list?
        #       I think I can just notify all players except current players
        # maybe add this move to a game log?

        self.handle_end_turn()
        return

    def handle_decision(self, decision_dict):
        """

        :param decision_dict: A dictionary
            'choice': str: is either - hint, play, or discard
            'card': int:  is the index of the card they are choosing to play or discard:
            'hint' TODO: will be either a rank or a number
            'player' TODO: who the hint is told to
        :return:
        """

        cur_player = self.players[self.players_turn]

        move = decision_dict['choice']

        if move == 'play':
            card_ind = decision_dict['card']
            cur_hand = cur_player.hand

            # Play that card on the fireworks pile.
            self.firework_piles.play_card_on_pile(cur_hand[card_ind])
            # Put a new card in the players hand at card_index
            cur_hand[card_ind] = self.deck.draw_card()
        elif move == 'discard':
            card_ind = decision_dict['card']
            cur_hand = cur_player.hand

            # Add that card to the discard pile.
            self.discarded_cards.append(cur_hand[card_ind])
            self.add_hint()

            # Give that player a new card
            cur_hand[card_ind] = self.deck.draw_card()
        elif move == 'hint':
            self.remove_hint()

    def game_over_event(self, reason):
        self.game_over_reason = reason
        if PRINT_GAME_STATUS:
            print(f'The game is over because {reason.name}')
        self.game_status = 'Done'
        return

    def simple_player_view(self):
        """
        Displays what the current player can see:
            The 3 other players names and their hands.
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
                        cur_card = p.hand[card].__str__()
                        pad = p.hand[card].padding
                    except ValueError:
                        cur_card = ""
                        pad = ""

                    print(cur_card.ljust(buffer) + pad, end=end)

            print()
        print(divider)


class FourPlayerGameDisplay:

    """
    This class is the HUD for the terminal window. and is specific to this iteration of Hanabi.
    Methods:
        Display: for displaying the view for the current player
        The other 3 players hands
        The number of bombs
        The played cards
        Discarded cards

        Show Hand?:

        Possible addition:
            Display what players should know.
            Highlight cards in discard pile that are significant (ie. there is only 1 left outside of the pile)
            Suggest moves
    """

    def __init__(self, game):
        self.game = game

    def display(self):
        """
        Should be able to deal with the styling without calling padding on the stuff.

        GUI management
        1
            Are all rows and columns the same, or just one of them?
            doing the max length for each could result in lots of empty wasted space.
            My choice is that each row starts at the same depth. ie you can draw the grid out.
            My choice: Column length varies, but you can draw consistent lines inbetween columns.
        2
            so create the display grid,
            then populate it
        3

        So the problem I'm running into is that I want a grid within a grid, in the middle layer.
        and also the discard pile layer.  So the grid display should be stackable?
        Goal: build a grid consisting of 3 rows, and generally undefined columns.
        First row:
            Bomb information, Hint information,
            The player across from you.
            Number of cards left in the deck?

        Second row:
            Both players to the left and right.
            The played cards in the middle (organized in a dice pattern)
        Third row:
            Your hand (and what you know about it).
            The discard pile (Arranged in a table).

        :return:
        """

        def get_len(hand_of_cards):
            ret_val = 0
            for cur_card in hand_of_cards:
                try:
                    ret_val += 1 + cur_card.printed_chars
                except AttributeError:
                    continue
            return ret_val

        #  Finding the players based on their orientation to current player
        cur_player = self.game.players[self.game.players_turn]
        left_player = self.game.players[(self.game.players_turn + 1) % len(self.game.players)]
        across_player = self.game.players[(self.game.players_turn + 2) % len(self.game.players)]
        right_player = self.game.players[(self.game.players_turn + 3) % len(self.game.players)]

        left_buffer = get_len(left_player.hand)
        across_buffer = get_len(across_player.hand)
        right_buffer = get_len(right_player.hand)

        print("_" * (left_buffer + right_buffer + across_buffer))
        print()

        print(f'There are {self.game.bombs} bombs left.')
        print(f'There are {self.game.hints} hints left.')
        print(f'There are {self.game.deck.cards_remaining()} cards left in the deck.')

        #  Print top row
        #  is going to be a for loop of running past left players cards to display our cards
        print(" " * left_buffer, end="")  # Get past the left players cards.

        print(across_player.name.center(across_buffer))
        print(" " * left_buffer, end="")  # Get past the left players cards.
        for card in across_player.hand:
            print(card, end="")
            print(" ", end="")
        print()
        print()

        #  Print middle row

        print(left_player.name.center(left_buffer), end="")
        print("".center(across_buffer), end="")

        print(right_player.name.center(right_buffer))
        for card in left_player.hand:
            print(card, end="")
            print(" ", end="")
        print("".center(across_buffer), end="")

        right_player_cards = ''
        for card in right_player.hand:
            right_player_cards += card.__str__()
            right_player_cards += " "
        print(right_player_cards, end="")

        print()
        print()

        # ---------- print Firework info----------------
        print("".center(left_buffer), end="")
        print("Firework Piles".center(across_buffer), end="")

        print("".center(left_buffer), end="")
        print()
        max_played = 0
        for color in Color:
            max_played = max(max_played, self.game.firework_piles.firework_dict[color])

        print("".center(int(left_buffer * 4/5)), end="")

        pile_buffer = 15
        for c in Color:
            print(c.name.ljust(pile_buffer), end="")
        print()
        for row in range(1, max_played + 1):
            print("".center(int(left_buffer * 4/5)), end="")
            for color in Color:
                pc = self.game.firework_piles.firework_dict
                if pc[color] >= row:
                    card_fake = Card(row,color)
                    distance_to_pile_buffer = pile_buffer - card_fake.printed_chars
                    extra = ' ' * distance_to_pile_buffer
                    card_str = card_fake.__str__() + extra
                    print(card_str, end="")
                else:
                    print(''.center(pile_buffer), end="")

            print()
                #if color value is less than or = then print it with ljust 15

        print()
        print()

        # Print current player info
        print(" " * left_buffer, end="")  # Get past the left players cards.
        print(cur_player.name.center(across_buffer))
        print(" " * left_buffer, end="")
        for card in cur_player.hand:
            print(card.__str__().center(int(across_buffer / 4),"-"), end="")
            #print("?".center(int(across_buffer / 4),"-"), end="")
            print(" ", end="")

        print()
        print()

        # for x in self.game.discarded_cards:
        #     print(x.__str__())


class Player:

    def __init__(self, name, hand, game):
        self.name = name
        self.hand = hand
        self.game = game

    #  This is the method called on the player to decide what they do.
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
            decision['card'] = self.discard()
            return decision
        elif choice == 'hint':
            decision['choice'] = choice
            decision['index'] = self.give_hint()
            return decision

        else:
            return self.get_decision()

    def play_card(self):
        """
        :return: The card played
        """
        print('Which card would you like to play? (enter num 1-4)')
        num = self.get_card_from_input()

        return int(num)

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

        return num

    def give_hint(self):
        # TODO:
        return 1  # a ton of info.


class SimpleOmniAIPlayer:

    """
    Plays first card it can play
    else: discards first card it can discard
    else: gives a hint
    else: discards a random card
    """

    def __init__(self, name, hand, game):
        self.name = name
        self.hand = hand
        self.game = game

    def get_decision(self):

        if PRINT_GAME_STATUS:
            print('getting decision:')
            #continue_click = input()

        decision = dict()

        play = False
        discard = False

        for i in range(0, 4):
            cur = self.hand[i]

            if cur == "NO_CARD":
                print('empty card slot')
                continue

            if self.game.firework_piles.is_playable(cur):
                if PRINT_GAME_STATUS:
                    print(f'{cur.__str__()} is playable')
                play = True
                play_card_index = i
                break

            else:
                if PRINT_GAME_STATUS:
                    print(f'checked {cur.__str__()}')

        for i in range(0, 4):
            cur = self.hand[i]

            if cur.rank <= self.game.firework_piles.firework_dict[cur.color]:
                if PRINT_GAME_STATUS:
                    print(f'{cur.__str__()} is discardable')
                discard = True
                discard_card_index = i
                break
            else:
                if PRINT_GAME_STATUS:
                    print(f'checked {cur.__str__()} for discarding')

        if play:
            if PRINT_GAME_STATUS:
                print('chose to play')
            decision['choice'] = 'play'
            decision['card'] = play_card_index
        elif discard:
            if PRINT_GAME_STATUS:
                print('chose to discard')
            decision['choice'] = 'discard'
            decision['card'] = discard_card_index
        else:
            if self.game.hints > 0:
                decision['choice'] = 'hint'
            else:
                decision['choice'] = 'discard'
                rand_index = random.randint(0, 3)
                if self.hand[rand_index] == 'NO_CARD':
                    rand_index = (rand_index + 1) % rand_index

                if PRINT_GAME_STATUS:
                    print(f'deciding to discard a random card at ind {rand_index}')

                decision['card'] = rand_index
        return decision


class AdvOmniAIPlayer:

    """
    Plays a playable 5
    else: plays
    """

    def __init__(self, name, hand, game):
        self.name = name
        self.hand = hand
        self.game = game

    def get_decision(self):

        if PRINT_GAME_STATUS:
            print('getting decision:')
            #continue_click = input()

        decision = dict()

        playable = 0
        discardable = 0

        play_index = 0
        discard_index = 0

        oracle = self.game.firework_piles

        """
        Count playables and discardables
        """

        lp = self.game.players[(self.game.players_turn + 1) % PLAYER_COUNT].hand  # Left player
        ap = self.game.players[(self.game.players_turn + 2) % PLAYER_COUNT].hand  # Across player
        rp = self.game.players[(self.game.players_turn + 3) % PLAYER_COUNT].hand  # Right player

        for ind in range(0, 4):
            cur = self.hand[ind]

            if cur == "NO_CARD":
                print('empty card slot')
                continue

            if cur.rank <= self.game.firework_piles.firework_dict[cur.color]:# or cur in lp + ap + rp:
                discardable += 1
                discard_index = ind
            elif oracle.is_playable(cur):
                # Here we are hoping to determine what the best card to play is.
                # Hypothesis Goal: to give other players playable cards.

                # if 1 < self.hand[play_index].rank < self.hand[play_index].rank < cur.rank:
                #     play_index
                if cur.rank == 5:
                    decision['choice'] = 'play'
                    decision['card'] = ind
                    return decision



                play_index = ind
                playable += 1

        hint_boundary = 5

        if playable:
            decision['choice'] = 'play'
            decision['card'] = play_index
            return decision
        elif self.game.hints == HINT_MAX:
            decision['choice'] = 'hint'
            return decision
        elif 2 <= discardable and hint_boundary <= self.game.hints < HINT_MAX:
            decision['choice'] = 'discard'
            decision['card'] = discard_index
            return decision
        elif self.game.hints:
            decision['choice'] = 'hint'
            return decision
        elif discardable:
            decision['choice'] = 'discard'
            decision['card'] = discard_index
            return decision
        else:
            # There are no discardable cards, and there are no hints left. :(
            kill_index = -1
            for ind in range(0, 4):
                card = self.hand[ind]
                if card == "NO_CARD":
                    print('empty card slot')
                    continue
                elif card.rank == 5:
                    continue
                elif card in self.game.discarded_cards:
                    continue
                else:
                    # Could add feature to discard it if you can see the other one out there.
                    # Also could add feature about discarding the highest value (not a 2)
                    kill_index = ind

            if kill_index == -1:
                rand_index = random.randint(0, 3)
                if self.hand[rand_index] == 'NO_CARD':
                    rand_index = (rand_index + 1) % rand_index
            decision['choice'] = 'discard'
            decision['card'] = kill_index
            return decision

class SmarterOmniAIPlayer:
    """

    """

    def __init__(self, name, hand, game):
        self.name = name
        self.hand = hand
        self.game = game

    def analyze_hand(self):
        """

        :return: decision
        """
        decision = dict()

        left_p = self.game.players[((self.game.players_turn + 1) % PLAYER_COUNT)].hand
        across_p = self.game.players[((self.game.players_turn + 2) % PLAYER_COUNT)].hand
        right_p = self.game.players[((self.game.players_turn + 3) % PLAYER_COUNT)].hand

        oracle = self.game.firework_piles

        total_playable = 0
        total_discardable = 0

        for index in range(0, 3):
            card = self.hand[index]
            if card == "NO_CARD":
                print('empty card slot')
                continue
            if oracle.is_playable(card):
                total_playable += 1


    def get_decision(self):

        if PRINT_GAME_STATUS:
            print('getting decision:')
            # continue_click = input()

        decision = dict()

        play = False
        discard = False

        for i in range(0, 4):
            cur = self.hand[i]

            if cur == "NO_CARD":
                print('empty card slot')
                continue

            if self.game.firework_piles.is_playable(cur):
                if PRINT_GAME_STATUS:
                    print(f'{cur.__str__()} is playable')
                play = True
                play_card_index = i
                break

            else:
                if PRINT_GAME_STATUS:
                    print(f'checked {cur.__str__()}')

        for i in range(0, 4):
            cur = self.hand[i]

            if cur.rank <= self.game.firework_piles.firework_dict[cur.color]:
                if PRINT_GAME_STATUS:
                    print(f'{cur.__str__()} is discardable')
                discard = True
                discard_card_index = i
                break
            else:
                if PRINT_GAME_STATUS:
                    print(f'checked {cur.__str__()} for discarding')

        if play:
            if PRINT_GAME_STATUS:
                print('chose to play')
            decision['choice'] = 'play'
            decision['card'] = play_card_index
        elif discard:
            if PRINT_GAME_STATUS:
                print('chose to discard')
            decision['choice'] = 'discard'
            decision['card'] = discard_card_index
        else:
            if self.game.hints > 0:
                decision['choice'] = 'hint'
            else:
                decision['choice'] = 'discard'
                rand_index = random.randint(0, 3)
                if self.hand[rand_index] == 'NO_CARD':
                    rand_index = (rand_index + 1) % rand_index

                if PRINT_GAME_STATUS:
                    print(f'deciding to discard a random card at ind {rand_index}')

                decision['card'] = rand_index
        return decision


trials = 5_000

game_end_reasons = []

for i in range(1, trials + 1):
    if (i % 1000) == 0:
        print(str(i))
    game = HanabiGame(4, ['', '', '', ''])
    game.handle_begin_turn()
    game_end_reasons.append(game.game_over_reason.name)

print("_" * 40)
print()

print(f'Trial Stats:')
print(f'Wins: {game_end_reasons.count("WIN")/trials} %')
print(f'Ran out of cards/turns: {game_end_reasons.count("RAN_OUT_OF_TURNS")/trials} %')
print(f'Bomb defeat: {game_end_reasons.count("BOMBS")/trials} %')





