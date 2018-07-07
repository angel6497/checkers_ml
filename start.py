#!/usr/bin/env python3

import sys
if sys.version_info < (3, 4):
    print('[ERROR]: This project requires Python 3.4 or higher. Running on Python {}.{}.{}.'.format(*sys.version_info[:3]))
    sys.exit(1)

import os
import time
import logging
import datetime
import argparse

from checkersml.controller import CheckersController


def main():
    '''
    Main Funtction.
    '''

    args   = parse_arguments()
    logger = setup_logger(args.debug, args.nolog)

    controller = CheckersController(args.notrain, args.nodata)

    if args.play != None:
        controller.play(args.play)
    elif args.train != None:
        controller.train(args.train)
    else:
        logger.error("Error in command line arguments.")



def parse_arguments():
    '''
    Get the command line arguments.
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument( '-train', type=int,
                         help='Train the ML Player model by having it play against itself.' )
    parser.add_argument( '-play', type=int, 
                         help='Play a real game using a GUI. Argument determines number of real players.' )
    parser.add_argument( '-notrain', action='store_true', help='Prevents training during real games.' )
    parser.add_argument( '-nolog', action='store_true', help='Prevents the program from generating logs.' )
    parser.add_argument( '-nodata', action='store_true', help='Stops training data from being saved to files.' )
    parser.add_argument( '-debug', action='store_true', help='Enable debug messages.' )

    args = parser.parse_args()

    if args.train is None and args.play is None:
        print('Either the \'--play\' or \'--train\' options must be specified.\nPlease see usage:')
        parser.print_help()
        sys.exit(1)

    return args


def setup_logger(debug, no_log):
    '''
    Create and setup logger instance.
    '''

    if not no_log and not os.path.isdir('logs'):
        os.mkdir('logs')
        
    dt      = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S.log')
    logfile = os.path.join('logs', dt)

    logger = logging.getLogger()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter( ColoredFormatter() )
    logger.addHandler(stream_handler)

    if not no_log:
        file_handler   = logging.FileHandler(logfile, mode='w')
        file_formatter = logging.Formatter('[{asctime} {levelname}] {message}', datefmt='%H:%M:%S', style='{')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger



####### COLORED FORMATTER SUBCLASS #######

class ColoredFormatter(logging.Formatter):
    '''
    Adds ANSI escape color codes to the logger messages by overriding
    the format method and defines a custom message format.
    '''

    def __init__(self):
        super().__init__()
        self.color_map = { 'NORMAL'   : u'\u001b[0m',
                           'DEBUG'    : u'\u001b[38;5;39m',
                           'INFO'     : u'\u001b[38;5;4m',
                           'WARNING'  : u'\u001b[38;5;178m',
                           'ERROR'    : u'\u001b[38;5;196m',
                           'CRITICAL' : u'\u001b[48;5;196m' }

    def format(self, record):
        msg = '{color}[{asctime} {level}]{endcolor} {msg}'

        return msg.format( color    = self.color_map[record.levelname],
                           asctime  = datetime.datetime.now().strftime('%H:%M:%S'),
                           level    = record.levelname,
                           endcolor = self.color_map['NORMAL'],
                           msg      = record.msg )


if __name__ == '__main__':
    main()
