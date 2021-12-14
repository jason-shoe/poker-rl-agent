from Game import Game
from player import UserPlayer, RandomPlayer, BotOne, Move
import tensorflow as tf
import tensorflow.keras as keras
import random
import csv
from MovesBuffer import MovesBuffer

# INITIAL BET SIZE
INITIAL_CHIP_COUNT = 25
ENCODING_SIZE = 9
# ACTION_OHE_SIZE = INITIAL_CHIP_COUNT * 2 - 2 + 3
ACTION_OHE_SIZE = 5
INPUT_SIZE = ACTION_OHE_SIZE + ENCODING_SIZE
LSTM_MEMORY = 10
EPSILON = 0.1

NUM_BATCHES = 10
NUM_GAMES = 100


action_index_map = {}
action_index_map[(Move.CHECK, None)] = 0
action_index_map[(Move.FOLD, None)] = 1
# all in isnt actually none encoding, but we'll put it like it here
action_index_map[(Move.ALLIN, None)] = 2
for x in range(1, INITIAL_CHIP_COUNT * 2 - 1):
    action_index_map[(Move.RAISE, x)] = 2 + x

model = tf.keras.models.Sequential([tf.keras.layers.InputLayer(input_shape=(LSTM_MEMORY, INPUT_SIZE, )),
                                    tf.keras.layers.LSTM(128, return_sequences=False, return_state=False),
                                    tf.keras.layers.Dense(units=128, activation='softmax'),
                                    tf.keras.layers.Dense(units=1)])
model.compile(
    optimizer=tf.keras.optimizers.Adam(lr=0.001),
    loss=tf.keras.losses.MeanSquaredError(),
    metrics=[tf.keras.metrics.MeanSquaredError()],
)

# def get_action_ohe(action):
#     if (action[0] == Move.ALLIN):
#         action = (Move.ALLIN, None)
#     return [1 if x == action_index_map[action] else 0 for x in range(INITIAL_CHIP_COUNT * 2 + 1)]

# def get_action_from_state_action(state_action):
#     action_ohe = state_action[-(INITIAL_CHIP_COUNT * 2 + 1):]
#     for x in range(INITIAL_CHIP_COUNT * 2 + 1):
#         if (action_ohe[x] == 1):
#             if ( x == 0):
#                 return (Move.CHECK, None)
#             elif (x == 1):
#                 return (Move.FOLD, None)
#             elif (x == 2):
#                 return (Move.ALLIN, None)
#             else:
#                 return (Move.RAISE, x - 2)
#     return None

def get_action_ohe(action):
    ohe = [1 if x == action[0].value else 0 for x in range(ACTION_OHE_SIZE)]
    if (action[0] == Move.RAISE):
        ohe[4] = action[1]
    return ohe

def get_action_from_state_action(state_action):
    action_ohe = state_action[-ACTION_OHE_SIZE:]
    print(action_ohe, )
    for x in range(ACTION_OHE_SIZE - 1):
        if (action_ohe[x] == 1):
            return (Move(x), action_ohe[-1] if x == 3 else None)
    return None

def make_decision(player, state, raise_amount, opponent_bet_size):
    valid_actions = player.get_valid_actions(raise_amount)
    moves = player1Moves.getMoves()[1:]
    isPlayer1 = player.get_name() == player1.get_name()
    if (isPlayer1 and player1Random):
        best_action = random.choice(valid_actions)
    elif (not isPlayer1 and player2Random):
        best_action = random.choice(valid_actions)
    else:
        best_action = None
        best_q_val = None
        for action in valid_actions:
            input = [state + get_action_ohe(action)]
            input = tf.convert_to_tensor([moves + input])
            
            q_val = model(input)[0]
            # print(action, q_val, best_q_val)
            if (best_q_val is None or best_q_val < q_val):
                # print('Replacing %.2f with %.2f' % (best_q_val if best_q_val is not None else q_val, q_val), action)
                best_q_val = q_val
                best_action = action
    
    if (isPlayer1):
        player1Moves.addMove(state + get_action_ohe(best_action))
        player1RoundActions.append(player1Moves.getMoves())
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
        player2Moves.addMove(state + get_action_ohe(best_action))
        player2RoundActions.append(player2Moves.getMoves())
    return best_action

if __name__ == "__main__":
    player1 = BotOne("Jason", INITIAL_CHIP_COUNT, make_decision)
    player2 = RandomPlayer("Brawner", INITIAL_CHIP_COUNT)
    game = Game(2, player1, player2)
    for batch_num in range(NUM_BATCHES):
        if (batch_num ==  1):
            player2 = BotOne("BrawnerRL", INITIAL_CHIP_COUNT, make_decision)
            game.set_player2(player2)
        batchActions = []
        batchRewards = []
        counts = [0] * 6
    
        for game_num in range(NUM_GAMES):
            player1.reset_chips(INITIAL_CHIP_COUNT)
            player2.reset_chips(INITIAL_CHIP_COUNT)
            player1Moves = MovesBuffer(LSTM_MEMORY, INPUT_SIZE)
            player2Moves = MovesBuffer(LSTM_MEMORY, INPUT_SIZE)
            can_continue = True
            round_num = 0
            while (can_continue):
                player1RoundActions = []
                player2RoundActions = []
                player1Random = random.uniform(0, 1) < EPSILON
                player2Random = random.uniform(0, 1) < EPSILON
                print('Batch %d / %d , Game %d / %d, Round %d' % (batch_num + 1, NUM_BATCHES, game_num + 1, NUM_GAMES, round_num + 1))
                if (player1Random):
                    print('%10s is acting random' % player1.get_name())
                if (player2Random):
                     print('%10s is acting random' % player2.get_name())
                player1chipsPre, player2chipsPre = player1.get_chipcount(), player2.get_chipcount()
                can_continue = game.play_round()
                player1chipsPost, player2chipsPost = player1.get_chipcount(), player2.get_chipcount()
                # print(len(player1RoundActions), len(player2RoundActions))
    
                # player1Reward = 1 if player1chipsPost - player1chipsPre > 0 else -1
                # player2Reward = 1 if player2chipsPost - player2chipsPre > 0 else -1
                
                player1Reward = player1chipsPost - player1chipsPre
                player2Reward = player2chipsPost - player2chipsPre
                
                batchActions += player1RoundActions
                batchRewards += [player1Reward] * len(player1RoundActions)
    
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
            print(len(batchActions), get_action_from_state_action(batchActions[x][-1]), batchRewards[x])
        model.fit(x=batchActions, y=batchRewards, batch_size=16, epochs=40, verbose=1, shuffle=True)
        model.save('poker-rl-agent.kmod')