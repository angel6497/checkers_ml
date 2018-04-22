#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import util
import pdb

class Trainer:
    '''
    Trainer class.

    Takes the data produced by the checkers matches and trains the existing parameters on it.
    '''

    def __init__(self, alpha = 0.1):

        self.alpha = alpha

        with open('parameters.csv', 'r') as params_file:
            params = params_file.read().split(',')
            self.params = np.array([ float(p) for p in params ], dtype=np.float64)


    def fit(self, data):
        '''
        Adjust the parameters using stochastic gradient descent with the game data.
        '''

        #pdb.set_trace()

        for row in data:
            score_train = row.pop()
            score_curr = util.evaluate(self.params, np.array(row))
            feature_values = np.array(row, dtype=np.float64)
            feature_values = np.insert(feature_values, 0, 1.0)


            self.params += self.alpha * ( score_train - score_curr ) * feature_values

        with open('parameters.csv', 'w') as params_file:
            params_file.write(','.join( [str(p) for p in self.params] ))
