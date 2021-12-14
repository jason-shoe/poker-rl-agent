import random
from treys import Card, Deck
from enum import Enum
from treys import Evaluator
from player import Move

class Game():
    def __init__(self, initial_blind, player1, player2):
        self.dealer_is_player1 = True
        self.initial_blind = initial_blind
        self.curr_blind = self.initial_blind
        self.deck = Deck()

        self.player1 = player1
        self.player2 = player2
    def set_player2(self, player2):
        self.player2 = player2

    def play_round(self):
        print('Chip Counts: %s (%d) %s (%d)' % (self.player1.get_name(), self.player1.get_chipcount(), self.player2.get_name(), self.player2.get_chipcount()))
        winner = self.start_round()
        # result is a tie
        if (winner is None):
            self.player1.end_round(0)
            self.player2.end_round(0)
        else:
            self.player1.print_hand()
            self.player2.print_hand()
            self.player2.print_community_cards()
            loser = self.player1 if self.player2.get_name() == winner.get_name() else self.player2
            winner_bet_size = winner.get_current_bet()
            loser_bet_size = loser.get_current_bet()
            if (loser_bet_size <= winner_bet_size):
                print("%10s won  %d with hand strength %d" % (winner.get_name(), loser_bet_size, winner.get_hand_strength()))
                print("%10s lost %d with hand strength %d" % (loser.get_name(), loser_bet_size, loser.get_hand_strength()))
                winner.end_round(loser_bet_size)
                loser.end_round(-1 * loser_bet_size)
                
            else:
                # this only happens if the winner went all in
                print('%10s won  %d with hand strength %d' % (winner.get_name(), winner_bet_size, winner.get_hand_strength()))
                print('%10s lost %d with hand strength %d' % (loser.get_name(), winner_bet_size, loser.get_hand_strength()))
                winner.end_round(winner_bet_size)
                loser.end_round(-1 * winner_bet_size)
                
        return self.player1.can_play() and self.player2.can_play()


    def start_round(self):
        self.dealer_is_player1 = not self.dealer_is_player1
        self.deck.shuffle()

        # antes
        self.player1.make_bet(1)
        self.player2.make_bet(1)
        self.player1.set_hand(self.deck.draw(2))
        self.player2.set_hand(self.deck.draw(2))
        # winner = self.betting_round()
        # if (winner is not None):
        #     return winner

        # flop
        self.add_community_cards(3)
        print("Post Flop")
        winner = self.betting_round()
        if (winner is not None):
            return winner

        # turn
        self.add_community_cards(1)
        print("Post Turn")
        winner = self.betting_round()
        if (winner is not None):
            return winner

        # river
        self.add_community_cards(1)
        print("Post River")
        winner = self.betting_round()
        if (winner is not None):
            return winner

        return self.determine_winner()

    def determine_winner(self):
        player1HandStrength = self.player1.get_hand_strength()
        player2HandStrength = self.player2.get_hand_strength()
        if (player1HandStrength < player2HandStrength):
            return self.player1
        elif (player2HandStrength < player1HandStrength):
            return self.player2
        return None

    def add_community_cards(self, num_cards):
        cards = self.deck.draw(num_cards)
        if (num_cards == 1):
            cards = [cards]
        self.player1.add_community_cards(cards)
        self.player2.add_community_cards(cards)


    # return None for continue, otherwise return player object of winner
    # def make_decision(self, check_amount):
    def betting_round(self):
        if (not self.player1.can_bet() or not self.player2.can_bet()):
            return None
        current_raise_amount = 0
        turn = not self.dealer_is_player1
        last_move = None
        while (True):
            current_player = self.player1 if turn else self.player2 
            other_player = self.player2 if turn else self.player1
            # (move, int)
            result = current_player.make_move(current_raise_amount, other_player.get_current_bet())
            if (result[0] == Move.FOLD):
                return other_player
            elif (result[0] == Move.CHECK):
                # no winner determined
                if (last_move == Move.CHECK or last_move == Move.RAISE or last_move == Move.ALLIN):
                    return None
            elif (result[0] == Move.RAISE):
                current_raise_amount = result[1] 
            elif (result[0] == Move.ALLIN):
                if (result[1] <= current_raise_amount or last_move == Move.ALLIN):
                    return None
                else:
                    current_raise_amount = result[1] - current_raise_amount
            last_move = result[0]
            turn = not turn