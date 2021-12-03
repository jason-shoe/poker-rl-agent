from abc import ABC, abstractmethod
from enum import Enum
from treys import Evaluator
import random

class Move(Enum):
	CHECK = 1
	RAISE = 2
	FOLD = 3
	ALLIN = 4

class GenericPlayer(ABC):
	def __init__(self, name, chipcount):
		self.name = name
		self.chipcount = chipcount
		self.current_bet = 0
		self.evaluator = Evaluator()
		# should be size 2
		self.reset_cards()

	def make_bet(self, betsize):
		if (betsize + self.current_bet > self.chipcount):
			return False
		self.current_bet += betsize
		return True

	# negative if you loe chips, positive if you gain chips
	def end_round(self, chip_count_change):
		self.current_bet += chip_count_change

	def get_current_bet(self):
		return self.current_bet

	def reset_cards(self):
		self.hand = []
		self.community_cards = []

	def set_hand(self, cards):
		self.hand = cards

	def add_community_cards(self, cards):
		self.community_cards += cards;
		if (len(self.community_cards) > 5):
			print("ERROR: Player has more than 5 community cards")

	# returns (Move, integer / None)
		# examples 
		# 	(RAISE, 10)
		# 	(CHECK, None)
		# 	(FOLD, None)
	@abstractmethod
	# returns a valid action to take
	def make_decision(self, raise_amount):
		pass
	# returns (move, max_integer)
	def get_valid_actions(self, raise_amount):
		valid_moves = []
		available_for_betting = self.chipcount - self.current_bet
		valid_moves.append((Move.FOLD, None))
		valid_moves.append((Move.ALLIN, available_for_betting))
		if (raise_amount == 0):
			valid_moves.append((Move.CHECK, None))
		elif (raise_amount <= available_for_betting):
			valid_moves.append((Move.CHECK, None))
			for x in range(1, available_for_betting + 1):
				valid_moves.append((Move.RAISE, x))
		
		return valid_moves
	def make_move(self, raise_amount):
		move = self.make_decision(raise_amount)
		print('%s is doing ' % self.name, move)
		if (move[0] == Move.CHECK):
			self.make_bet(raise_amount)
		elif (move[0] == Move.RAISE):
			self.make_bet(move[1] + raise_amount)
		elif (move[0] == Move.FOLD):
			pass
		elif (move[0] == Move.ALLIN):
			self.make_bet(move[1])
		return move



	def get_hand_strength(self):
		self.evaluator.evaluate(self.community_cards, self.hand)
	
	def can_bet(self):
		return self.current_bet < self.chipcount

class UserPlayer(GenericPlayer):
	def make_decision(self, raise_amount):
		print('It is %s turn to make a move' % (self.name))
		print("The current raise amount is ", raise_amount)
		print("Your current chipcount is ", self.chipcount)
		print("This round you've bet ", self.current_bet)
		if (raise_amount == 0):
			val = input("\tCHECK or RAISE: ")
			if (val == "CHECK"):
				move = (Move.CHECK, None)
			elif (val == "RAISE"):
				raise_size = input("\tHow much would you like to raise by: ")
				raise_size = int(raise_size)
				move =  (Move.RAISE, raise_size)
		else:
			val = input("\tCHECK, RAISE or FOLD: ")
			if (val == "CHECK"):
				move = (Move.CHECK, None)
			if (val == "RAISE"):
				raise_size = input("\tHow much would you like to raise by: ")
				raise_size = int(raise_size)
				move =  (Move.RAISE, raise_size)
			elif (val == Move.FOLD):
				move = (Move.FOLD, None)
		return move
		print("\n")


class RandomPlayer(GenericPlayer):
	def make_decision(self, raise_amount):
		possible_moves = self.get_valid_actions(raise_amount)
		move = random.choice(possible_moves)
		return move

# class BotPlayer(GenericPlayer):
	
# 	def make_decision(self, raise_amount):
