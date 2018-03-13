#!/usr/bin/env python3

import board
from player import RealPlayer, MLPlayer
from trainer import Trainer

import subprocess
import time

import pdb


class Controller():
    '''
    TODO
    '''

    def __init__(self, train = False):

        self.b = board.Board()

        #self.player1 = RealPlayer(board.BLACK, b)
        #self.player2 = RealPlayer(board.WHITE, b)

        self.jumped = False

        self.GUI = subprocess.Popen(['java', 'GamePage'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, cwd='/Users/angelortiz/Code/projects/checkers-ml/swing_gui')

    
    def start(self):
        '''
        TODO
        '''

        #pdb.set_trace()

        colors = ['white', 'black']
        color_index = 0;
        current_color = colors[color_index]

        while (True):
            move = self.get_move_from_gui(current_color)
            self.b.update(move)
            self.update_gui()

            color_index = (color_index + 1) % 2
            current_color = colors[color_index]
        

    def update_gui(self):
        '''
        TODO
        '''
        print('display {}'.format(repr(self.b)))
        self.GUI.stdin.write('display {}'.format(repr(self.b)) + '\n')


    def get_move_from_gui(self, color):
        '''
        TODO
        '''
        self.GUI.stdin.write('get_move ' + color + ' \n')
        self.GUI.stdin.flush()

        #response = self.GUI.stdout.readline()
        response = ''
        while(not response.startswith('SELECTED_MOVE')):
            response = self.GUI.stdout.readline()
            time.sleep(0.01)

        coordinates = response.split()[1:]
        coordinates = [ int(x) for x in coordinates ]
        x1, y1, x2, y2 = coordinates
        move = board.Move([x1//2, y1], [x2//2, y2])

        print(repr(move))

        return move
