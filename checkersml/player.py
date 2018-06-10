import os
import pickle
import random
import datetime
import collections
import numpy as np
from abc import ABC, abstractmethod

from . import features
from . import model

import pdb
from pprint import pprint


State = collections.namedtuple('State', ['score', 'features'])


class Player(ABC):
    '''
    Abstract player class
    
    Declares the methods that are required by the checkers engine to play a game.
    '''

    def __init__(self, color, board):
        
        if color != 'black' and color != 'white':
            raise ValueError('A player\'s color can only be black or white.')

        self.color = color
        self.board = board

    @abstractmethod
    def make_move(self):
        pass



class RealPlayer(Player):
    '''
    Real player class

    This class allows a real player to interact with the GUI and make a move.
    '''

    def make_move(self):
        '''
        Take move from the GUI and update it into the board.
        '''
        pass



class MLPlayer(Player):
    '''
    MLPlayer Abstract Class

    This class implements a player framework that can interact with the checkers engine
    and use an arbitrary machine learning model to play and train.
    '''

    def __init__(self, color, board, train         = False, 
                                     learning_rate = 0,
                                     reg_const     = 0,
                                     lambda_const  = 0,
                                     search_depth  = 0,
                                     epsilon       = 0,
                                     save_file     = 'parameters.pickle', 
                                     no_records    = False):
        
        super().__init__(color, board)

        self.train = train

        self.curr_cycle = 1
        self.no_records = no_records

        self.learning_rate = learning_rate
        self.reg_const     = reg_const
        self.lambda_const  = lambda_const
        self.search_depth  = search_depth
        self.epsilon       = epsilon

        self.save_file  = save_file
        self.records_X  = None
        self.records_y  = None
        self.prev_state = None

        save_file_dir = os.path.dirname(save_file)
        if save_file_dir and not os.path.exists(save_file_dir):
            os.makedirs(save_file_dir)

        self.set_features()
        self.set_model()

        dt = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
        self.logdir = os.path.join('training_data', dt)

        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)


    @abstractmethod
    def compute_features(self):
        pass

    
    @abstractmethod
    def set_features(self):
        pass


    @abstractmethod
    def set_model(self):
        pass 


    def save_model(self):
        '''
        Save the current model state into a pickle.
        '''

        pickle.dump(self.model, open(self.save_file, 'wb'))


    def get_parameters_string(self):
        '''
        Return a string representation of the model current weights.
        '''

        return str(self.model.coefs_)


    def evaluate(self, x):
        '''
        Use the current movel to evaluate a certain board state.
        '''

        return self.model.predict(x)


    def fit_data(self):
        '''
        Adjust the model using the latest gathered data.
        '''

        self.model.partial_fit(self.records_X, self.records_y)
        self.save_model()
        self.records_X = None
        self.records_y = None


    def make_move(self):
        '''
        Evaluate all possible moves using the trained evaluating function and choose
        the optimal one.
        '''

        legal_moves = self.board.get_all_legal_moves(self.color)

        if not legal_moves:
            return None

        # Use epsilon-greedy policy to pick next move with %5 chance of exploring. 
        if random.random() < self.epsilon:
            return random.choice(legal_moves)

        else:
            best_score = float('-inf')
            best_move  = None
            next_color = 'white' if self.color == 'black' else 'black'

            for move in legal_moves:
                score, leaf_features = self.minimax_search(move, 'min', next_color, 0)
                if score > best_score:
                    best_score  = score
                    best_move   = move
                    pv_features = leaf_features

            # Call the TD(lambda) function to update the model based on the next state.
            if self.train:
                next_state = State(best_score, np.array(pv_features))
                self.model.td_lambda(self.prev_state, next_state)
                self.prev_state = next_state

                if not self.no_records:
                    self.add_record(pv_features, best_score)

            return best_move


    def minimax_search(self, move, agent, color, depth):
        '''
        Does a minimax look ahead search from the position resulting after picking the given move.
        '''

        next_agent = 'min' if agent == 'max' else 'max'
        next_color = 'white' if color == 'black' else 'black'

        # Perform the given move as a temporary update.
        undo_key = self.board.temporary_update(move)

        # Check if a second jump is available.
        if move.capture:
            sequential_jumps = [ m for m in self.board.get_legal_moves(move.dst[0], move.dst[1], cache=False) if m.capture ]
        else:
            sequential_jumps = None

        # A second available jump means the same player gets to move again, but has to pick one of those jumps.
        if sequential_jumps:
            legal_moves = sequential_jumps
            agent, next_agent = next_agent, agent
        else:
            legal_moves = self.board.get_all_legal_moves(color, cache=False)

        # A player with no possible moves loses the game.
        if not legal_moves:
            leaf_features = self.compute_features()
            self.board.undo_temporary_update(undo_key)
            if self.color == color:
                return -1, leaf_features
            else:
                return  1, leaf_features

        # If the max depth is reached, bootstrap the value using the value function approximation.
        if depth == self.search_depth:
            self.board.undo_temporary_update(undo_key)
            features = self.compute_features()
            return self.evaluate(features), features

        if agent == 'min':
            best_score = float('inf')
        elif agent == 'max':
            best_score = float('-inf')

        for next_move in legal_moves:
            if sequential_jumps:
                score, leaf_features = self.minimax_search(next_move, next_agent, color, depth)
            else:
                score, leaf_features = self.minimax_search(next_move, next_agent, next_color, depth+1)

            # Update the best score if necessary.
            if agent == 'min' and score < best_score:
                best_score  = score
                pv_features = leaf_features
            elif agent == 'max' and score > best_score:
                best_score  = score
                pv_features = leaf_features

        # Revert the temporary move.
        self.board.undo_temporary_update(undo_key)

        return best_score, pv_features
             

    def add_record(self, x, y):
        '''
        Adds record for a board position and its calculated score.
        '''
        
        if isinstance(self.records_X, np.ndarray) and len(x) != len(self.records_X[0]):
            raise ValueError('All records must be of the same length.')

        # Initialize the records variables if adding the first entries.
        if not isinstance(self.records_X, np.ndarray):
            self.records_X = np.array([x])
            self.records_y = np.array([y])
        else:
            self.records_X = np.append(self.records_X, [x], axis=0)
            self.records_y = np.append(self.records_y, [y], axis=0)


    def pop_record(self):
        '''
        Remove the last record added.
        '''

        poped_x = self.records_X[-1]
        poped_y = self.records_y[-1]

        self.records_X = np.delete(self.records_X, -1, axis=0)
        self.records_y = np.delete(self.records_y, -1, axis=0)

        return poped_x, poped_y


    def save_records(self, records_file='match_data', cycle=''):
        '''
        Write current records to a csv file.
        '''
        
        records_file = '{}{}.rcd'.format(records_file, cycle)
        records_file = os.path.join(self.logdir, records_file)

        full_records = np.c_[self.records_X, self.records_y]

        np.savetxt(records_file, full_records, delimiter=',', fmt='%1.4f')


    def reset(self):
        '''
        Does resets some variables in the model that depend on the current game and
        saves the records if any.
        '''

        self.model.reset()
        self.save_records(cycle=self.curr_cycle)
        self.records_X = None
        self.records_y = None

        self.curr_cycle += 1



class LinearModelPlayer(MLPlayer):
    '''
    LinearModelPlayer class.
    
    This player class uses a linear regression model to assign values to board positions
    in order to chose the optimal move among the list of possible legal moves.
    '''

    def set_features(self):
        '''
        Initialize the features to be used for the value function approximator.
        '''
        
        if self.color == 'black':
            self.features = [ features.BlackPiecesFeature(),
                              features.WhitePiecesFeature(),
                              features.BlackKingsFeature(),
                              features.WhiteKingsFeature(),
                              features.BlackThreatenedFeature(),
                              features.WhiteThreatenedFeature() ]

            for col in range(8):
                for row in range(8):
                    if (col % 2 == 0 and row % 2 == 0) or (col % 2 == 1 and row % 2 == 1):
                        self.features.append(features.PositionValueFeature(col, row, self.color))

        else:
            self.features = [ features.WhitePiecesFeature(),
                              features.BlackPiecesFeature(),
                              features.WhiteKingsFeature(),
                              features.BlackKingsFeature(),
                              features.WhiteThreatenedFeature(),
                              features.BlackThreatenedFeature() ]

            for col in reversed(range(8)):
                for row in reversed(range(8)):
                    if (col % 2 == 0 and row % 2 == 0) or (col % 2 == 1 and row % 2 == 1):
                        self.features.append(features.PositionValueFeature(col, row, self.color))



    def compute_features(self):
        '''
        Computes the features of the board according to the current state.
        '''
        
        return [ f.compute_value(self.board) for f in self.features ]


    def set_model(self):
        '''
        Initialize a new linear regression model or load existing one from 'save_file'.
        '''

        try:
            self.model = pickle.load( open(self.save_file, 'rb') )
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            self.model = model.LinearRegressionModel( dimension     = len(self.features),
                                                      learning_rate = self.learning_rate,
                                                      alpha         = self.reg_const,
                                                      lambda_const  = self.lambda_const ) 


    # Override
    def get_parameters_string(self):
        '''
        Returns a formated string with the current values of all the features.
        '''

        line_format = '{:.<33}: {: >7.4f}\n'

        lines = ''
        for i in range(0, len(self.features)):
            lines += ( line_format.format(self.features[i].get_name(), self.model.coefs_[i]) )

        return lines


    # Override
    def evaluate(self, x):
        '''
        Use the current model to evaluate a certain board state. 
        Predefined values are used for terminal states.
        '''

        # Return 1 if the game is won, -1 if the game is lost, or 0 if it is a tie.
        if self.board.game_over == 3:
            return 0

        if x[0] == 0:
            return -1
        elif x[1] == 0:
            return 1 

        return super().evaluate(x)
