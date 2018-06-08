import os
import logging
from collections import deque

from checkersml import board, player, features
from swinggui import CheckersSwingGUI

import sys
import pdb
from pprint import pprint


class CheckersController:
    '''
    Checkers Controller class.

    This class uses the checkersml and swinggui modules to either train a ML Checkers 
    player model by having it play against itself or to provide regular game functionality.
    '''

    def __init__(self, no_train=False, no_data=False):

        self.logger   = logging.getLogger()
        self.no_train = no_train
        self.no_data  = no_data
        
        if not os.path.isdir('parameters'):
            os.mkdir('parameters')


    def play(self, real_players):
        '''
        Starts a regular game using a GUI, where the argument 'real_players' decides the
        amount of real players in the game. If there are zero real players the GUI will
        just show two ML players playing against itself never giving control to the user.
        '''
        
        b = board.Board()

        if real_players == 0:
            player1 = player.LinearRegressionPlayer('black', b, save_file='pickled_models/model1.pickle')
            player2 = player.LinearRegressionPlayer('white', b, save_file='pickled_models/zeros.pickle')
        elif real_players == 1:
            player1 = player.RealPlayer('black', b)
            player2 = player.LinearRegressionPlayer('white', b, save_file='pickled_models/model1.pickle')
        else:
            self.no_train = True
            player1 = player.RealPlayer('black', b)
            player2 = player.RealPlayer('white', b)

        b.set_players(player1, player2)

        if real_players < 2:
            trainee = player2

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
                if b.player_in_turn.color != trainee.color and not prev_features:
                    prev_features = trainee.compute_features()
                elif b.player_in_turn.color == trainee.color and prev_features:
                    score = trainee.evaluate(trainee.compute_features())
                    trainee.add_record(prev_features, score)
                    prev_features = None

            gui.display( str(b) )

            if b.game_over:
                # Make sure to record the winning or loosing state information.
                # This step is critical during the first cycles because it generates experience
                # propagation.
                if not self.no_train:
                    if b.player_in_turn.color == trainee.color:
                        prev_features = trainee.pop_record()[0]

                    score = trainee.evaluate(trainee.compute_features())
                    trainee.add_record(prev_features, score)

                    if not self.no_data:
                        trainee.save_records()

                    # Train on the newly generated data.
                    if not self.no_train:
                        trainee.fit_data()

                winner = b.player_in_turn.color

                if b.game_over == 2:
                    gui.set_status('No moves available')
                    gui.set_status('Game Over')
                elif b.game_over == 3:
                    gui.set_status('Tie')
                    gui.set_status('Game Over')
                    winner = None

                response = gui.game_over( winner )
                
                if response == 'restart':
                    b.__init__()
                    b.set_players(player1, player2)
                    prev_features = None
                    gui.display( str(b) )
                elif response == 'exit':
                    gui.exit()
                    sys.exit(0)
        
    
    def train(self, max_cycles=None):
        '''
        Trains a machine learning model by having it play against itself or other ML Player.
        The 'max_cycles' argument specifies the amount of cycles to play before stoping where
        a cycle represents a full checkers match. If the argument is 0 it will keep going until
        manually stopped.
        '''
    
        b = board.Board()

        black_player = player.LinearRegressionPlayer('black', b, save_file='pickled_models/model1.pickle', simple_features=False)
        white_player = player.LinearRegressionPlayer('white', b, save_file='pickled_models/zeros.pickle')

        trainee = black_player
        
        curr_cycle   = 1

        trainee_wins  = 0
        trainee_ties  = 0
        trainee_loses = 0

        total_turns  = 0

        while(True):

            try:

                # Reset the board values on every cycle.
                b.__init__()
                b.set_players(black_player, white_player)

                prev_features = None
                turn_count    = 0

                while(not b.game_over):

                    turn_count += 1

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
                    if b.player_in_turn.color != trainee.color and not prev_features:
                        prev_features = trainee.compute_features()
                    elif b.player_in_turn.color == trainee.color and prev_features:
                        score = trainee.evaluate(trainee.compute_features())
                        trainee.add_record(prev_features, score)
                        prev_features = None

                    if b.game_over:
                        # Make sure to record the winning or loosing state information.
                        # This step is critical during the first cycles because it generates experience
                        # propagation.
                        if b.player_in_turn.color == trainee.color:
                            prev_features = trainee.pop_record()[0]

                        score = trainee.evaluate(trainee.compute_features())
                        trainee.add_record(prev_features, score)

                        if not self.no_data:
                            trainee.save_records(cycle=curr_cycle)

                        if b.game_over < 3:
                            if b.player_in_turn.color == trainee.color:
                                trainee_wins += 1
                            else:
                                trainee_loses += 1
                        elif b.game_over == 3:
                            trainee_ties += 1

                        total_turns += turn_count

                # Train on the newly generated data.
                if not self.no_train:
                    trainee.fit_data()

                self.logger.info( '---------------------------------------------' )
                self.logger.info( 'Current cycle: {}\n'.format(curr_cycle) )
                self.logger.info( 'Total turns: {}'.format(turn_count) )
                self.logger.info( 'Average turns per match: {:.2f}\n'.format( total_turns/curr_cycle ) )
                self.logger.info( 'Trainee parameters:' )
                for line in trainee.get_parameters_string().split('\n'):
                    self.logger.info( '   {}'.format(line) )
                self.logger.info( 'Trainee win rate:  {:.2%}'.format( trainee_wins/curr_cycle ) )
                self.logger.info( 'Trainee tie rate:  {:.2%}'.format( trainee_ties/curr_cycle ) )
                self.logger.info( 'Trainee lose rate: {:.2%}'.format (trainee_loses/curr_cycle ) )
                self.logger.info( '---------------------------------------------\n' )
                
                # Stop training is max number of cycles if reached.
                curr_cycle += 1
                if max_cycles and curr_cycle > max_cycles:
                    self.logger.info('Final trainee win rate: {:.2%}'.format(trainee_wins/max_cycles))
                    sys.exit(0)

            except KeyboardInterrupt:
                self.logger.info( 'Training simulation ended manually.' )
                self.logger.info( 'Final data: \n' )
                self.logger.info( '---------------------------------------------' )
                self.logger.info( 'Current cycle: {}\n'.format(curr_cycle) )
                self.logger.info( 'Total turns: {}'.format(turn_count) )
                self.logger.info( 'Average turns per match: {:.2f}\n'.format( total_turns/(curr_cycle - 1)) )
                self.logger.info( 'Trainee parameters:' )
                for line in trainee.get_parameters_string().split('\n'):
                    self.logger.info( '   {}'.format(line) )
                self.logger.info( 'Trainee win rate:  {:.2%}'.format( trainee_wins/(curr_cycle - 1) ) )
                self.logger.info( 'Trainee tie rate:  {:.2%}'.format( trainee_ties/(curr_cycle - 1) ) )
                self.logger.info( 'Trainee lose rate: {:.2%}'.format( trainee_loses/(curr_cycle - 1) ) )
                self.logger.info( '---------------------------------------------\n' )

                sys.exit(0)
                

