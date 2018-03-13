#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import util
import random
import numpy as np
import os.path

class Player(ABC):
    '''
    Abstract Player class that declares the methods that are required by the game.
    '''

    def __init__(self, color, board):
        self.color = color
        self.board = board

    @abstractmethod
    def make_move(self, move=None):
        pass



class MLPlayer(Player):
    '''
    Machine learning player.
    
    This player will use a trained machine learning function that assigns scores to board
    possitions to choose the optimal move among the list of possible legal moves.
    '''

    def __init__(self, color, board):
        
        super().__init__(color, board)

        self.params_num = 7

        # Get the latest trained parameters for the predicting function or create new ones
        # they can't be found
        if os.path.isfile('parameters.csv'):
            with open('parameters.csv', 'r') as params_file:
                params = params_file.read().split(',')
                self.params = np.array([ float(p) for p in params ])
        else:
            with open('parameters.csv', 'w') as params_file:
                params_file.write(','.join( list('0'*self.params_num) ))


    def make_move(self, move=None):
        '''
        Evaluate all possible moves using the trained evaluating function and choose
        the optimal one.
        '''

        move_scores = {}

        legal_moves = board.get_legal_moves(self.color)
        for move in legal_moves:
            move_features = board.get_move_features_values(move)
            score = util.evaluate(self.params, np.array(move_features))
            
            if not move_scores.get(score):
                move_scores[score] = []

            move_scores[score].append(move)
        
        best_moves = move_scores[max(move_scores.keys())]
        self.board.update(random.choice(best_moves))



class RealPlayer(Player):
    '''
    Real player class.

    This class allows a real player to interact with the GUI and make a move.
    '''

    def __init__(self, color, board):
        
        super().__init__(color, board)

    
    def make_move(self, move=None):
        '''
        Take move from the GUI and update it into the board.
        '''
        
        self.board.update(move)
