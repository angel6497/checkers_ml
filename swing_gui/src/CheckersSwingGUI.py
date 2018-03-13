#!/usr/bin/env python3

import sys
sys.path.append('../checkers/')

import os
import subprocess
import time

import board



class CheckersSwingGUI():
    '''
    Container class for the Java Swing Checkers GUI.

    This class initiates the Java GUI process and provides a simple
    interface that implements the required interprocess communication
    so that any python program can use it.
    '''

    def __init__(self):
        '''
        Initiates Java GUI process, effectively making the GUI visible
        the user.
        '''

        self.GUI = subprocess.Popen(['java', 'GamePage'],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True,
                                    cwd='../swing_gui/bin'
                                    )

        # Set the parent process ID attribute in the Swing process.
        self.GUI.stdin.write( 'set_ppid {} \n'.format(os.getpid()) )
        self.GUI.stdin.flush()


    def display(self, state):
        '''
        Displays new board state.
        '''
        
        ipc_cmd = 'display ' + state + ' \n'
        self.GUI.stdin.write(ipc_cmd)
        self.GUI.stdin.flush()


    def get_move(self, color):
        '''
        Gets a move from the user of a certain color.
        '''

        if color not in ['white', 'black']:
            raise ValueError('Color must be white or black.')

        ipc_cmd = 'get_move ' + color + ' \n'
        self.GUI.stdin.write(ipc_cmd)
        self.GUI.stdin.flush()

        response = ''
        while( not response.startswith('SELECTED_MOVE') ):
            response = self.GUI.stdout.readline()
            time.sleep(0.01)

        coordinates = response.split()[1:]
        coordinates = [ int(x) for x in coordinates ]
        x1, y1, x2, y2 = coordinates
        move = board.Move( [x1, y1], [x2, y2] )

        return move

    def show_message(self, msg):
        '''
        Display pop up message.
        '''

        self.GUI.stdin.write('popup {} EOM \n'.format(msg))
        self.GUI.stdin.flush()


    def set_status(self, msg):
        '''
        Change status message.
        '''

        self.GUI.stdin.write('set_status {} EOM \n'.format(msg))
        self.GUI.stdin.flush()


    def game_over(self, winner):
        '''
        Display game over message as a pop up and ask player whether
        to restart game or exit.
        '''

        response_map = {'0': 'exit',
                        '1': 'restart'}

        self.GUI.stdin.write('game_over {} \n'.format(winner))
        self.GUI.stdin.flush()
        
        response = ''

        while ( not response.startswith('RESPONSE:') ):
            response = self.GUI.stdout.readline()

        response = ( response.split(':')[1] ).strip()

        return response_map[response] 


    def exit(self):
        '''
        Stop GUI Swing process.
        '''

        self.GUI.terminate()

