#!/usr/bin/env python3

import sys
sys.path.append('../swing_gui/src/')

from pprint import pprint
import time

import board
from CheckersSwingGUI import CheckersSwingGUI


def main():

    state = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -3, 0, 0, 0],
            [0, 0, 0, 0, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ]

    b = board.Board(state=state)

    gui = CheckersSwingGUI()
    gui.display( str(b) )

    while(True):
        status = 'Black' if b.player_in_turn == 'black' else 'White'
        status += ' Player\'s Turn'
        gui.set_status(status)
        move = gui.get_move(b.player_in_turn)
        try:
            b.update(move)
        except ValueError as e:
            gui.show_message(str(e))

        gui.display( str(b) )

        if b.game_over:
            gui.set_status('Game Over')
            response = gui.game_over(b.player_in_turn)
            
            if response == 'restart':
                b = board.Board()
                gui.display( str(b) )
            elif response == 'exit':
                gui.exit()
                sys.exit(0)


if __name__ == '__main__':
        main() 
