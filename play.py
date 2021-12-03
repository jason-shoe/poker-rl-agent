from Game import Game
from player import UserPlayer, RandomPlayer

player1 = UserPlayer("Jason", 100)
player2 = RandomPlayer("Brawner", 100)

game = Game(2, player1, player2)

game.start_round()