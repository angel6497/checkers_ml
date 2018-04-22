from abc import ABC, abstractmethod

from . import board


class Feature(ABC):
    '''
    Abstract feature class.

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

        return value


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

        return value


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

        return value


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

        return value


class WhiteThreatenedFeature(Feature):
    '''
    This feature compute the number of regular white threatened pieces on the board.
    '''

    def get_name(self):
        return 'White Threatened Pieces Feature'

    
    def compute_value(self, b):

        threatened_pieces = set()
        legal_moves = b.get_all_legal_moves('black') 
        
        for move in legal_moves:
            if move.capture:
                delta_x = ( move.src[0] - move.dst[0] ) // 2
                delta_y = ( move.src[1] - move.dst[1] ) // 2
                threatened_piece = ( move.dst[0] + delta_x, move.dst[1] + delta_y )
                threatened_pieces.add(threatened_piece)

        return len(threatened_pieces)


class BlackThreatenedFeature(Feature):
    '''
    This feature compute the number of regular white threatened pieces on the board.
    '''

    def get_name(self):
        return 'Black Threatened Pieces Feature'

    
    def compute_value(self, b):
        threatened_pieces = set()
        legal_moves = b.get_all_legal_moves('white') 
        
        for move in legal_moves:
            if move.capture:
                delta_x = ( move.src[0] - move.dst[0] ) // 2
                delta_y = ( move.src[1] - move.dst[1] ) // 2
                threatened_piece = ( move.dst[0] + delta_x, move.dst[1] + delta_y )
                threatened_pieces.add(threatened_piece)

        return len(threatened_pieces)
