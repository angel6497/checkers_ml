import os
import logging
from collections import deque

from checkersml import board, player, features
from checkersgui import CheckersSwingGUI

import sys
import pdb
from pprint import pprint
import numpy as np


class CheckersController:
    '''
    Checkers Controller class.

    This class uses the checkersml and checkersgui modules to either train a ML Checkers 
    player model by having it play against itself or to provide regular game functionality.
    '''

    def __init__(self, no_train=False, no_data=False):

        self.logger   = logging.getLogger()
        self.no_train = no_train
        self.no_data  = no_data
        

    def play(self, real_players):
        '''
        Starts a regular game using a GUI, where the argument 'real_players' decides the
        amount of real players in the game. If there are zero real players the GUI will
        just show two ML players playing against itself never giving control to the user.
        '''
        
        b = board.Board()

        if real_players == 0:
            black_player = player.LinearModelPlayer('black', b, train         = True,
                                                           learning_rate = 0.01,
                                                           reg_const     = 0,
                                                           lambda_const  = 0.7,
                                                           search_depth  = 3,
                                                           epsilon       = 0.05,
                                                           save_file     = 'pickled_models/model_test3.pickle')

            white_player = player.LinearModelPlayer('white', b, train         = False,
                                                           learning_rate = 0,
                                                           reg_const     = 0,
                                                           lambda_const  = 0,
                                                           search_depth  = 0,
                                                           epsilon       = 1,
                                                           save_file     = 'pickled_models/zeros.pickle')

        elif real_players == 1:
            black_player = player.LinearModelPlayer('black', b, train         = True,
                                                           learning_rate = 0.01,
                                                           reg_const     = 0,
                                                           lambda_const  = 0.7,
                                                           search_depth  = 3,
                                                           epsilon       = 0.05,
                                                           save_file     = 'pickled_models/model_test3.pickle')

            white_player = player.RealPlayer('white', b)

        else:
            self.no_train = True
            black_player = player.RealPlayer('black', b)
            whiteplayer = player.RealPlayer('white', b)

        b.set_players(black_player, white_player)

        try:
            gui = CheckersSwingGUI()
        except RuntimeError:
            self.logger.error("The Checkers GUI is not installed. Please run 'pipenv run install_gui' or 'make' to install it.")
            sys.exit(1)

        gui.display( str(b) )

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
                raise ValueError("Player didn't pick a move.")

            try:
                b.update(move)
            except ValueError as e:
                gui.show_message( str(e) )

            gui.display( str(b) )

            if b.game_over:
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
                    for p in [black_player, white_player]:
                        if isinstance(p, player.MLPlayer) and p.train:
                            p.reset()

                    b.__init__()
                    b.set_players(black_player, white_player)
                    gui.display( str(b) )

                elif response == 'exit':
                    for p in [black_player, white_player]:
                        if isinstance(p, player.MLPlayer) and p.train:
                            p.save_model()

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

        black_player = player.LinearModelPlayer('black', b, train         = True,
                                                            learning_rate = 0.01,
                                                            reg_const     = 0,
                                                            lambda_const  = 0.7,
                                                            search_depth  = 2,
                                                            epsilon       = 0.05,
                                                            save_file     = 'pickled_models/model_test3.pickle')

        white_player = player.LinearModelPlayer('white', b, train         = False,
                                                            learning_rate = 0,
                                                            reg_const     = 0,
                                                            lambda_const  = 0,
                                                            search_depth  = 0,
                                                            epsilon       = 1,
                                                            save_file     = 'pickled_models/zeros.pickle')

        b.set_players(black_player, white_player)
        trainee = black_player
        
        curr_cycle    = 1
        cycle_outcome = None

        trainee_wins  = 0
        trainee_ties  = 0
        trainee_loses = 0

        total_turns  = 0

        while(True):

            try:

                turn_count = 0

                while(not b.game_over):

                    turn_count += 1

                    move = b.player_in_turn.make_move()

                    # Current player has no possible legal moves, so turn is passed to the next one.
                    if not move:
                        raise ValueError("Player didn't pick a move.")

                    try:
                        b.update(move)
                    except ValueError:
                        pass

                    if b.game_over:
                        if b.game_over < 3:
                            if b.player_in_turn.color == trainee.color:
                                trainee_wins += 1
                                cycle_outcome = 'Win'
                            else:
                                trainee_loses += 1
                                cycle_outcome = 'Loss'
                        elif b.game_over == 3:
                            trainee_ties += 1
                            cycle_outcome = 'Tie'

                        total_turns += turn_count

                self.print_info( curr_cycle, cycle_outcome, turn_count, total_turns, trainee, trainee_wins, trainee_ties,
                                 trainee_loses )
                
                # Stop training is max number of cycles if reached.
                curr_cycle += 1
                if max_cycles and curr_cycle > max_cycles:
                    for p in [black_player, white_player]:
                        if p.train:
                            p.save_model()

                    self.logger.info('Final trainee win rate: {:.2%}'.format(trainee_wins/max_cycles))
                    sys.exit(0)

                # Reset the board values on every cycle.
                b.__init__()
                b.set_players(black_player, white_player)
                trainee.reset()

            except KeyboardInterrupt:
                for p in [black_player, white_player]:
                    if p.train:
                        p.save_model()

                self.logger.info( 'Training simulation ended manually.' )
                if curr_cycle > 1:
                    self.logger.info( 'Final data: \n' )
                    self.print_info( curr_cycle-1, cycle_outcome, turn_count, total_turns, trainee, trainee_wins, trainee_ties,
                                     trainee_loses )
                else:
                    print('No cycles were completed.')

                sys.exit(0)
                

    def print_info(self, cycle, outcome, turn_count, total_turns, trainee, trainee_wins, trainee_ties, trainee_loses):
        '''
        Prints the information gathered after a cycle of training.
        '''

        self.logger.info( '---------------------------------------------' )
        self.logger.info( 'Current cycle: {}'.format(cycle) )
        self.logger.info( 'Outcome: {}\n'.format(outcome) )
        self.logger.info( 'Total turns: {}'.format(turn_count) )
        self.logger.info( 'Average turns per match: {:.2f}\n'.format( total_turns/cycle ) )
        self.logger.info( 'Trainee parameters:' )

        # Format the parameter strings according to how many there are.
        parameter_lines = trainee.get_parameters_string().split('\n')
        if len(parameter_lines) <= 25:
            for line in parameter_lines:
                self.logger.info( '   {}'.format(line) )
        else:
            midpoint = len(parameter_lines) // 2
            for i in range(midpoint):
                if i + midpoint < len(parameter_lines):
                    self.logger.info( '   {}      {}'.format(parameter_lines[i], parameter_lines[i+midpoint]) )
                else:
                    self.logger.info( '   {}'.format(parameter_lines[i]) )

        self.logger.info( '' )

        self.logger.info( 'Trainee win rate:  {:>8.2%} [{}/{}]'.format( trainee_wins/cycle, trainee_wins, cycle ) )
        self.logger.info( 'Trainee tie rate:  {:>8.2%} [{}/{}]'.format( trainee_ties/cycle, trainee_ties, cycle ) )
        self.logger.info( 'Trainee lose rate: {:>8.2%} [{}/{}]'.format (trainee_loses/cycle, trainee_loses, cycle ) )
        self.logger.info( '---------------------------------------------\n' )
