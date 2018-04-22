import collections
import csv
import numpy as np

from . import util


class Trainer:
    '''
    TODO
    '''

    def __init__(self, b, player, params_file='parameters.csv'):

        self.learn_rate = 0.005
        self.board      = b
        self.player     = player
        self.records    = collections.deque()
        self.params     = player.params_num


    def add_record(self, record):
        '''
        Adds record for a board position and its calculated score.
        '''
        
        if len(record) != self.player.params_num:
            raise ValueError( ('Records for the current player must contain {} feature values '
                              +'plus the score.').format(self.player.params_num) )

        #print('Record: {}'.format(record))
        self.records.append(record)

    def write_records(self, records_file='match_data.rcd'):
        '''
        TODO
        '''
        
        with open(records_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(self.records)


    def fit(self, data=None):
        '''
        Update the current parameters using new training data.
        '''
        
        if not data:
            data = self.records

        for entry in data:
            tmp_params = np.zeros(self.player.params_num, dtype=float)
            h_estimate = util.evaluate(self.player.params, entry[:-1])
            for i in range(self.player.params_num):
                curr_param    = self.player.params[i]
                feature_val   = entry[i-1] if i > 0 else 1
                tmp_params[i] = curr_param + ( ( self.learn_rate * (entry[-1] - h_estimate) ) * feature_val )

            self.player.params = tmp_params

        self.player.save_params()
        self.records.clear()
