#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def evaluate(params, features):
    '''
    Compute the score of a board state using the parameters given.
    '''
    
    features = np.insert(features, 0, 1)

    return np.dot(params, features) # Dot product of parameters and features
