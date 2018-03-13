#!/usr/bin/env python3

from abc import ABC, abstractmethod
from . import board


class Feature(ABC):
    '''
    Abstract feature class.

    This class describes the basic functionality required by all features.
    '''

    @abstractmethod
    def compute_value(self, board):
        pass


class WhitePiecesFeature(Feature):
    '''
    This feature computes the number of regular white pieces on the board.
    '''
    
    def compute_value(self, board):
        value = 0
        for row in board.state:
            for tile in row:
                if tile == WHITE_PAWN:
                    value += 1

        return value


class BlackPiecesFeature(Feature):
    '''
    This feature compute the number of regular black pieces on the board.
    '''

    def compute_value(self, board):
        value = 0
        for row in board.state:
            for tile in row:
                if tile == BLACK_PAWN:
                    value += 1

        return value

class WhiteKingsFeature(Feature):
    '''
    This feature compute the number of white kings on the board.
    '''

    def compute_value(self, board):
        value = 0
        for row in board.state:
            for tile in row:
                if tile == WHITE_KING:
                    value += 1

        return value

class BlackKingsFeature(Feature):
    '''
    This feature compute the number of black kings on the board.
    '''

    def compute_value(self, board):
        value = 0
        for row in board.state:
            for tile in row:
                if tile == BLACK_KING:
                    value += 1

        return value

class WhiteThreatenedFeature(Feature):
    '''
    This feature compute the number of regular white threatened pieces on the board.
    '''

    def compute_value(self, b):
        value = 0
        removed = []
        for i in range(8):
            for j in range(4):
                if b.state[i][j] & board.BLACK:
                    inner_moves = board.get_inner_moves_by_coordinate(j, i)
                    for move in inner_moves:
                        if i % 2 == 1:
                            if move[1] < i and i >= 2 and b.state[move[1]][move[0]] & board.WHITE:
                                if (move[0] == j and j <= 2 and b.state[i-2][j+1] == board.EMPTY) or (move[0] < j and j >= 1 and b.state[i-2][j-1] == board.EMPTY): 
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY
                            elif move[1] > i and i <=5 and b.state[i][j] == board.BLACK_KING and b.state[move[1]][move[0]] & board.WHITE:
                                if (move[0] == j and j <= 2 and b.state[i+2][j+1] == board.EMPTY) or (move[0] < j and j >= 1 and b.state[i+2][j-1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY

                        elif i % 2 == 0:
                            if move [1] < i and i >=2 and b.state[move[1]][move[0]] & board.WHITE:
                                if (move[0] == j and j >= 1 and b.state[i-2][j-1] == board.EMPTY) or (move[0] > j and j <= 2 and b.state[i-2][j+1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY
                            elif move[1] > i and i <=5 and b.state[i][j] == board.BLACK_KING and b.state[move[1]][move[0]] & board.WHITE:
                                if (move[0] == j and j >= 1 and b.state[i+2][j-1] == board.EMPTY) or (move[0] > j and j <= 2 and b.state[i+2][j+1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY

        for tile in removed:
            b.state[tile[1]][tile[0]] = tile[2]

        return value





class BlackThreatenedFeature(Feature):
    '''
    This feature compute the number of regular black threatened pieces on the board.
    '''

    def compute_value(self, b):
        value = 0
        removed = []
        for i in range(8):
            for j in range(4):
                if b.state[i][j] & board.WHITE:
                    inner_moves = board.get_inner_moves_by_coordinate(j, i)
                    for move in inner_moves:
                        if i % 2 == 1:
                            if move[1] < i and i >= 2 and b.state[i][j] == board.WHITE_KING and b.state[move[1]][move[0]] & board.BLACK:
                                if (move[0] == j and j <= 2 and b.state[i-2][j+1] == board.EMPTY) or (move[0] < j and j >= 1 and b.state[i-2][j-1] == board.EMPTY): 
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY
                            elif move[1] > i and i <=5 and b.state[move[1]][move[0]] & board.BLACK:
                                if (move[0] == j and j <= 2 and b.state[i+2][j+1] == board.EMPTY) or (move[0] < j and j >= 1 and b.state[i+2][j-1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY

                        elif i % 2 == 0:
                            if move [1] < i and i >=2 and b.state[i][j] == board.WHITE_KING and b.state[move[1]][move[0]] & board.BLACK:
                                if (move[0] == j and j >= 1 and b.state[i-2][j-1] == board.EMPTY) or (move[0] > j and j <= 2 and b.state[i-2][j+1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY
                            elif move[1] > i and i <=5 and b.state[move[1]][move[0]] & board.BLACK:
                                if (move[0] == j and j >= 1 and b.state[i+2][j-1] == board.EMPTY) or (move[0] > j and j <= 2 and b.state[i+2][j+1] == board.EMPTY):
                                    value += 1
                                    removed.append((move[0], move[1], b.state[move[1]][move[0]]))
                                    b.state[move[1]][move[0]] = board.EMPTY

        for tile in removed:
            b.state[tile[1]][tile[0]] = tile[2]

        return value
