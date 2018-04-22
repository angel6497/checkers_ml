import os
import logging

from checkersml import board, player, trainer, features, util
from swinggui import CheckersSwingGUI

import sys
import pdb


class CheckersController:
    '''
    TODO
    '''

    def __init__(self, no_train=False):
        '''
        TODO
        '''

        self.logger   = logging.getLogger()
        self.no_train = no_train
        
        if not os.path.isdir('parameters'):
            os.mkdir('parameters')


    def play(self, real_players):
        '''
        TODO
        '''
        
        b = board.Board()

        if real_players == 0:
            player1 = player.MLPlayer('black', b, params_file='parameters/black_parameters.csv')
            player2 = player.MLPlayer('white', b, params_file='parameters/white_parameters.csv')
        elif real_players == 1:
            player1 = player.RealPlayer('black', b)
            player2 = player.MLPlayer('white', b, params_file='parameters/white_parameters.csv')
        else:
            self.no_train = True
            player1 = player.RealPlayer('black', b)
            player2 = player.RealPlayer('white', b)

        b.set_players(player1, player2)

        if real_players < 2:
            t = trainer.Trainer(b, player2)

        gui = CheckersSwingGUI()
        gui.display( str(b) )

        prev_features = None

        while(True):

            status = 'Black' if b.player_in_turn.color == 'black' else 'White'
            status += ' Player\'s Turn'
            gui.set_status(status)

            if isinstance(b.player_in_turn, player.RealPlayer):
                move = gui.get_move(b.player_in_turn.color)
            else:
                move = b.player_in_turn.make_move()

            # Current player has no possible legal moves, so turn is passed to the next one.
            if not move:
                b.pass_turn()
                continue

            try:
                b.update(move)
            except ValueError as e:
                gui.show_message( str(e) )

            # Save the board features after the trainee player moves, but don't assign a score
            # to the board state until the other player has made a move too. This generates new 
            # training data.
            if not self.no_train:
                if b.player_in_turn.color != t.player.color and not prev_features:
                    prev_features = t.player.compute_features()
                elif b.player_in_turn.color == t.player.color and prev_features:
                    score = util.evaluate(t.player.params, t.player.compute_features())
                    prev_features.append(score)
                    t.add_record(prev_features)
                    prev_features = None

            gui.display( str(b) )

            if b.game_over:
                # Make sure to record the winning or loosing state information.
                # This step is critical during the first cycles because it generates experience
                # propagation.
                if not self.no_train:
                    if b.player_in_turn.color == t.player.color:
                        prev_features = t.records.pop()[:-1]

                    score = util.evaluate(t.player.params, t.player.compute_features())
                    prev_features.append(score)
                    t.add_record(prev_features)

                    t.write_records()

                    # Train on the newly generated data.
                    if not self.no_train:
                        t.fit()

                gui.set_status('Game Over')
                response = gui.game_over( b.player_in_turn.color )
                
                if response == 'restart':
                    b.__init__()
                    b.set_players(player1, player2)
                    prev_features = None
                    gui.display( str(b) )
                elif response == 'exit':
                    gui.exit()
                    sys.exit(0)
        
    
    def train(self, max_cycles=None, refresh=False, verbose=False):
        '''
        TODO
        '''
    
        b = board.Board()

        trainee  = player.MLPlayer('black', b, params_file='parameters/black_parameters.csv')
        opponent = player.MLPlayer('white', b, params_file='parameters/white_parameters.csv')
        
        t = trainer.Trainer(b, opponent)

        curr_cycle   = 1
        trainee_wins = 0
        total_turns  = 0

        while(True):

            # Reset the board values on every cycle.
            b.__init__()
            b.set_players(trainee, opponent)

            prev_features = None
            turn_count    = 0

            while(not b.game_over):

                turn_count += 1
                if turn_count >= 1000: 
                    break

                move = b.player_in_turn.make_move()

                # Current player has no possible legal moves, so turn is passed to the next one.
                if not move:
                    b.pass_turn()
                    continue

                try:
                    b.update(move)
                except ValueError:
                    pass

                # Save the board features after the trainee player moves, but don't assign a score
                # to the board state until the other player has made a move too. This generates new 
                # training data.
                if b.player_in_turn.color != t.player.color and not prev_features:
                    prev_features = t.player.compute_features()
                elif b.player_in_turn.color == t.player.color and prev_features:
                    score = util.evaluate(t.player.params, t.player.compute_features())
                    prev_features.append(score)
                    t.add_record(prev_features)
                    prev_features = None

                if b.game_over:
                    # Make sure to record the winning or loosing state information.
                    # This step is critical during the first cycles because it generates experience
                    # propagation.
                    if b.player_in_turn.color == t.player.color:
                        prev_features = t.records.pop()[:-1]

                    score = util.evaluate(t.player.params, t.player.compute_features())
                    prev_features.append(score)
                    t.add_record(prev_features)

                    t.write_records()

                    if b.player_in_turn.color == t.player.color:
                        trainee_wins += 1

                    total_turns += turn_count

            # Train on the newly generated data.
            t.fit()
            self.logger.info( '------------------------' )
            self.logger.info( 'Total turns: {}'.format(turn_count) )
            self.logger.info( 'Average turns per match: {:.2}'.format(total_turns/curr_cycle) )
            self.logger.info( 'Trainee parameters: \n{}'.format(t.player.get_parameters_string()) )
            self.logger.info( 'Current cycle: {}'.format(curr_cycle) )
            self.logger.info( 'Trainee win rate: {:.2%}'.format(trainee_wins/curr_cycle) )
            
            # Stop training is max number of cycles if reached.
            curr_cycle += 1
            if max_cycles and curr_cycle >= max_cycles:
                self.logger.info('Final trainee win rate: {:.2%}'.format(trainee_wins/max_cycles))
                sys.exit(0)
            # Take the opponent to the trainee's level after some amount of cycles.
            elif refresh and curr_cycle % refresh == 0:
                opponent.params = trainee.params
                opponent.save_params()
                

