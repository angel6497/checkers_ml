import os
import csv
import random
import datetime
import collections
import numpy as np
from abc import ABC, abstractmethod

from . import util
from . import features

import pdb

class Player(ABC):
    '''
    Abstract player class that declares the methods that are required by the game.
    '''

    def __init__(self, color, board):
        
        if color != 'black' and color != 'white':
            raise ValueError('A player\'s color can only be black or white.')

        self.color = color
        self.board = board

    @abstractmethod
    def make_move(self, move=None):
        pass



class RealPlayer(Player):
    '''
    Real player class.

    This class allows a real player to interact with the GUI and make a move.
    '''

    def make_move(self, move=None):
        '''
        Take move from the GUI and update it into the board.
        '''
        pass



class LinearRegressionPlayer(Player):
    '''
    Machine learning player class.
    
    This player will use a trained machine learning function that assigns scores to board
    possitions in order to choose the optimal move among the list of possible legal moves.
    '''

    def __init__(self, color, board, params_file='parameters.csv'):
        
        super().__init__(color, board)

        self.learn_rate = 0.01
        self.regularization_const = 0.005

        self.params_num  = 7
        self.params_file = params_file
        self.params      = util.get_params(params_file, self.params_num)
        self.records     = collections.deque()

        if self.color == 'black':
            self.features = [ features.BlackPiecesFeature(),
                              features.WhitePiecesFeature(),
                              features.BlackKingsFeature(),
                              features.WhiteKingsFeature(),
                              features.BlackThreatenedFeature(),
                              features.WhiteThreatenedFeature() ]
        else:
            self.features = [ features.WhitePiecesFeature(),
                              features.BlackPiecesFeature(),
                              features.WhiteKingsFeature(),
                              features.BlackKingsFeature(),
                              features.WhiteThreatenedFeature(),
                              features.BlackThreatenedFeature() ]

        dt = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
        self.logdir = os.path.join('training_data', dt)

        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)


    def compute_features(self):
        '''
        Computes the features of the board according to the current state.
        '''
        
        return [ f.compute_value(self.board) for f in self.features ]


    def make_move(self, move=None):
        '''
        Evaluate all possible moves using the trained evaluating function and choose
        the optimal one.
        '''

        move_scores = {}

        legal_moves = self.board.get_all_legal_moves(self.color)

        if not legal_moves:
            return None

        for move in legal_moves:
            move_features = self.board.get_move_features_values(move)
            score = util.evaluate(self.params, np.array(move_features))
            
            if not move_scores.get(score):
                move_scores[score] = []

            move_scores[score].append(move)
        
        best_moves = move_scores[max(move_scores.keys())]
        
        return random.choice(best_moves)


    def save_params(self):
        '''
        Saves current paramters into the parameters file, replacing the old ones.
        '''

        with open(self.params_file, 'w') as params_file:
            params_string = ','.join( [str(x) for x in self.params] )
            params_file.write( params_string )


    def get_parameters_string(self):
        '''
        Retunrs a formated string with the current values of all the features.
        '''

        line_format = '{:.<33}: {: >7.2f}'

        lines = [ line_format.format('Constant', self.params[0]) ]
        for i in range(1, self.params_num):
            lines.append( line_format.format(self.features[i-1].get_name(), self.params[i]) )

        return lines


    def add_record(self, record):
        '''
        Adds record for a board position and its calculated score.
        '''
        
        if len(record) != self.params_num:
            raise ValueError( ('Records for the current player must contain {} feature values '
                              +'plus the score.').format(self.params_num) )

        self.records.append(record)


    def write_records(self, records_file='match_data', cycle=''):
        '''
        Write current records to a file.
        '''
        
        records_file = '{}{}.rcd'.format(records_file, cycle)
        records_file = os.path.join(self.logdir, records_file)

        with open(records_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(self.records)


    def fit_data(self):
        '''
        Update the current parameters using new training data.
        '''

        for entry in self.records:

            train_score = entry.pop()
            pred_score  = util.evaluate(self.params, entry)

            entry = np.insert(entry, 0, 1)
            
            self.params = ( self.params + ( self.learn_rate * ( ((train_score - pred_score) * entry) 
                                                              - (self.regularization_const * self.params) ) ) )

        self.save_params()
        self.records.clear()



