from Game import Game
from player import UserPlayer, RandomPlayer, BotOne, Move
import tensorflow as tf
import tensorflow.keras as keras
import random
import csv

# INITIAL BET SIZE
INITIAL_CHIP_COUNT = 25
ENCODING_SIZE = 8
INPUT_SIZE = INITIAL_CHIP_COUNT * 2 - 2 + 3 + ENCODING_SIZE
EPSILON = 0.1
action_index_map = {}
action_index_map[(Move.CHECK, None)] = 0
action_index_map[(Move.FOLD, None)] = 1
# all in isnt actually none encoding, but we'll put it like it here
action_index_map[(Move.ALLIN, None)] = 2
for x in range(1, INITIAL_CHIP_COUNT * 2 - 1):
	action_index_map[(Move.RAISE, x)] = 2 + x

model = tf.keras.models.Sequential([tf.keras.layers.InputLayer(input_shape=(INPUT_SIZE, )),
									tf.keras.layers.Dense(units=128, activation='softmax'),
									tf.keras.layers.Dense(units=128, activation='softmax'),
									tf.keras.layers.Dense(units=1)])
model.compile(
    optimizer=tf.keras.optimizers.Adam(lr=0.005),
    loss=tf.keras.losses.MeanSquaredError(),
    metrics=[tf.keras.metrics.MeanSquaredError()],
)

def get_action_ohe(action):
	if (action[0] == Move.ALLIN):
		action = (Move.ALLIN, None)
	return [1 if x == action_index_map[action] else 0 for x in range(INITIAL_CHIP_COUNT * 2 + 1)]

def get_action_from_state_action(state_action):
	action_ohe = state_action[-(INITIAL_CHIP_COUNT * 2 + 1):]
	for x in range(INITIAL_CHIP_COUNT * 2 + 1):
		if (action_ohe[x] == 1):
			if ( x == 0):
				return (Move.CHECK, None)
			elif (x == 1):
				return (Move.FOLD, None)
			elif (x == 2):
				return (Move.ALLIN, None)
			else:
				return (Move.RAISE, x - 2)
	return None
def make_decision(player, state, raise_amount, opponent_bet_size):
	valid_actions = player.get_valid_actions(raise_amount)
	if (random.uniform(0, 1) < EPSILON):
		best_action = random.choice(valid_actions)
	else:
		best_action = None
		best_q_val = None
		for action in valid_actions:
			input = state + get_action_ohe(action)
			input = tf.convert_to_tensor([input])
			# input = input.reshape((209,))
			q_val = model(tf.convert_to_tensor(input))[0]
			# print(action, q_val, best_q_val)
			if (best_q_val is None or best_q_val < q_val):
				# print('Replacing %.2f with %.2f' % (best_q_val if best_q_val is not None else q_val, q_val), action)
				best_q_val = q_val
				best_action = action
	
	if (player.get_name() == player1.get_name()):
		player1RoundActions.append(state + get_action_ohe(best_action))
		if (best_action[0] == Move.CHECK):
			counts[0] += 1
		elif (best_action[0] == Move.FOLD):
			counts[1] += 1
		elif (best_action[0] == Move.ALLIN):
			counts[2] += 1
		else:
			counts[3] += 1
			counts[4] += best_action[1]
	else:
		player2RoundActions.append(state + get_action_ohe(best_action))
	return best_action

player1 = BotOne("Jason", INITIAL_CHIP_COUNT, make_decision)
player2 = RandomPlayer("Brawner", INITIAL_CHIP_COUNT)
game = Game(2, player1, player2)
for batch_num in range(10):
	batchActions = []
	batchRewards = []
	counts = [0] * 6

	for game_num in range(200):
		print("Game Number ", game_num)
		player1.reset_chips(INITIAL_CHIP_COUNT)
		player2.reset_chips(INITIAL_CHIP_COUNT)
		can_continue = True
		round_num = 0
		while (can_continue):
			player1RoundActions = []
			player2RoundActions = []
			print("Round Number ", round_num)
			player1chipsPre, player2chipsPre = player1.get_chipcount(), player2.get_chipcount()
			can_continue = game.play_round()
			player1chipsPost, player2chipsPost = player1.get_chipcount(), player2.get_chipcount()
			print(len(player1RoundActions), len(player2RoundActions))

			player1Reward = player1chipsPost - player1chipsPre
			player2Reward = player2chipsPost - player2chipsPre
			
			batchActions += player1RoundActions
			batchRewards += [player1Reward] * len(player1RoundActions)

			# batchActions += player2RoundActions
			# batchRewards += [player2Reward] * len(player2RoundActions)
			round_num += 1

		if (player1.can_play()):
			print('%s won!\n' % (player1.get_name()))
			counts[5] += 1
		else:
			print('%s won!\n' % (player2.get_name()))
	print("fitting player batch rewards")
	with open('counts.csv', 'a', newline='') as file:
		mywriter = csv.writer(file, delimiter=',', lineterminator='\n')
		mywriter.writerow(counts)
	for x in range(len(batchActions)):
		print(len(batchActions), get_action_from_state_action(batchActions[x]), batchRewards[x])
	model.fit(x=batchActions, y=batchRewards, batch_size=16, epochs=40, verbose=1, shuffle=True)
model.save('poker-rl-agent.kmod')