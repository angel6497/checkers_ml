from abc import ABC, abstractmethod

from . import board


class Feature(ABC):
    '''
    Abstract feature class

    This class describes the basic functionality required by all features.
    '''

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def compute_value(self, board):
        pass



class WhitePiecesFeature(Feature):
    '''
    This feature computes the number of regular white pieces on the board.
    '''

    def get_name(self):
        return 'White Pieces Feature'

    
    def compute_value(self, b):
        value = 0
        for row in b.state:
            for tile in row:
                if tile < 0:
                    value += 1

        return value/12



class BlackPiecesFeature(Feature):
    '''
    This feature compute the number of regular black pieces on the board.
    '''

    def get_name(self):
        return 'Black Pieces Feature'

    
    def compute_value(self, b):
        value = 0
        for row in b.state:
            for tile in row:
                if tile > 0:
                    value += 1

        return value/12



class WhiteKingsFeature(Feature):
    '''
    This feature compute the number of white kings on the board.
    '''

    def get_name(self):
        return 'White Kings Feature'

    
    def compute_value(self, b):
        value = 0
        for row in b.state:
            for tile in row:
                if tile == board.WHITE_KING:
                    value += 1

        return value/12



class BlackKingsFeature(Feature):
    '''
    This feature compute the number of black kings on the board.
    '''

    def get_name(self):
        return 'Black Kings Feature'

    
    def compute_value(self, b):
        value = 0
        for row in b.state:
            for tile in row:
                if tile == board.BLACK_KING:
                    value += 1

        return value/12



class WhiteThreatenedFeature(Feature):
    '''
    This feature compute the number of regular white threatened pieces on the board.
    '''

    def get_name(self):
        return 'White Threatened Pieces Feature'

    
    def compute_value(self, b):

        threatened_pieces = set()
        legal_moves = b.get_all_legal_moves('black', cache=False) 
        
        for move in legal_moves:
            if move.capture:
                delta_x = ( move.src[0] - move.dst[0] ) // 2
                delta_y = ( move.src[1] - move.dst[1] ) // 2
                threatened_piece = ( move.dst[0] + delta_x, move.dst[1] + delta_y )
                threatened_pieces.add(threatened_piece)

        return len(threatened_pieces)/12



class BlackThreatenedFeature(Feature):
    '''
    This feature compute the number of regular white threatened pieces on the board.
    '''

    def get_name(self):
        return 'Black Threatened Pieces Feature'

    
    def compute_value(self, b):
        threatened_pieces = set()
        legal_moves = b.get_all_legal_moves('white', cache=False) 
        
        for move in legal_moves:
            if move.capture:
                delta_x = ( move.src[0] - move.dst[0] ) // 2
                delta_y = ( move.src[1] - move.dst[1] ) // 2
                threatened_piece = ( move.dst[0] + delta_x, move.dst[1] + delta_y )
                threatened_pieces.add(threatened_piece)

        return len(threatened_pieces)/12



class PositionValueFeature(Feature):
    '''
    This feature gets the current piece value of a certain location at the board.
    The location to be used in each instance is provided in the contructor.
    '''

    def __init__(self, col, row, color):
        self.col = col
        self.row = row
        self.color = color

        if color == 'black':
            self.value_map = {  3: 1, 
                                1: 0.75,
                                0: 0.5,
                               -1: 0.25,
                               -3: 0  }
        else:
            self.value_map = {  3: 0, 
                                1: 0.25,
                                0: 0.5,
                               -1: 0.75,
                               -3: 1  }


    def get_name(self):
        return 'Position Value Feature [{}, {}]'.format(self.col+1, self.row+1)


    def compute_value(self, b):
        return self.value_map[ b.state[self.row][self.col] ]
