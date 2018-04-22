import os
import numpy as np

def evaluate(params, features):
    '''
    Compute the score of a board state using the parameters given.
    '''

    if features[0] == 0:
        return -100
    elif features[1] == 0:
        return 100

    features = np.insert(features, 0, 1)

    return np.dot(params, features) # Dot product of parameters and features


def get_params(params_file, params_num):
    '''
    Parses csv file cointaining the stored parameters or creates a new one if it cannot be found.
    '''

    if os.path.isfile(params_file):
        with open(params_file, 'r') as params_file:
            params = params_file.read().split(',')
            params = np.array(params, dtype=float)
    else:
        with open(params_file, 'w') as params_file:
            params = np.zeros(params_num)
            params_file.write(','.join( list('0' * params_num) ))

    return params

