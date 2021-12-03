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

	def start_round(self):
		print("Starting the round")
		self.dealer_is_player1 = not self.dealer_is_player1
		self.deck.shuffle()

		self.player1.set_hand(self.deck.draw(2))
		self.player2.set_hand(self.deck.draw(2))
		winner = self.betting_round()
		if (winner is not None):
			return winner

		# flop
		self.add_community_cards(3)
		winner = self.betting_round()
		if (winner is not None):
			return winner

		# turn
		self.add_community_cards(3)
		winner = self.betting_round()
		if (winner is not None):
			return winner

		# river
		self.add_community_cards(3)
		winner = self.betting_round()
		if (winner is not None):
			return winner

		return self.determine_winner()

	def determine_winner():
		player1HandStrength = self.player1.get_hand_strength()
		player2HandStrength = self.player2.get_hand_strength()
		if (player1HandStrength > player2HandStrength):
			return self.player1
		elif (player2HandStrength > player1HandStrength):
			return self.player2
		return None

	def add_community_cards(self, num_cards):
		cards = self.deck.draw(num_cards)
		self.player1.add_community_cards(cards)
		self.player2.add_community_cards(cards)


	# return None for continue, otherwise return player object of winner
	# def make_decision(self, check_amount):
	def betting_round(self):
		print("New betting round")
		if (not self.player1.can_bet() or not self.player2.can_bet()):
			return None
		current_raise_amount = 0
		turn = not self.dealer_is_player1
		last_move = None
		while (True):
			current_player = self.player1 if turn else self.player2 
			other_player = self.player2 if turn else self.player1
			# (move, int)
			result = current_player.make_move(current_raise_amount)
			if (result[0] == Move.FOLD):
				return other_player
			elif (result[0] == Move.CHECK):
				# no winner determined
				if (last_move == Move.CHECK or last_move == Move.RAISE):
					return None
			elif (result[0] == Move.RAISE):
				current_raise_amount = result[1]
			last_move = result[0]
			turn = not turn