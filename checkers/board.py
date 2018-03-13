#!/usr/bin/env python3

from pprint import pprint

####### CONSTANTS #######

EMPTY = 0

BLACK_PAWN = 1
BLACK_KING = 3
WHITE_PAWN = -1
WHITE_KING = -3

SELECTED_BLACK_PAWN = 10
SELECTED_BLACK_KING = 30
SELECTED_WHITE_PAWN = -10
SELECTED_WHITE_KING = -30


class Board:
    '''
    TODO
    '''
    
    def __init__(self, state = None):
        '''
        Initializes board object to a particular state if given or to
        beggining of game otherwise.
        '''

        self.state          = state if state else self._generate_initial_state()
        self.player_in_turn = 'black'
        self.legal_moves    = {}
        self.required_src   = None
        self.game_over      = False


    def __str__(self):
        s = ''
        for row in range(8):
            for col in range(8):
                s += '{} '.format( self.state[row][col] )

        return s[:-1]



####### INTERFACE METHODS #######

    def get_tile_state(self, x, y):
        '''
        Returns the current value for a tile.
        '''

        return self.state[y][x]


    def update(self, move):
        '''
        Updates the board state according to the given move if it is valid.
        '''
        
        # This means that the last move was a jump, and at least another jump is available
        # so the player is required to make it.
        if (self.required_src) and (move.src != self.required_src):
            raise ValueError('Illegal move: Choose another jump with the last piece selected. {}'.format(self.required_src))
        
        # If there is any jump available on the board it is mandatory that the player makes it.
        available_jumps = self._get_current_possible_jumps()
        legal_moves = self.get_legal_moves(*move.src)

        non_jump_moves = []
        if available_jumps:
            non_jump_moves = legal_moves
            legal_moves = available_jumps

        # Check if selected move is legal.
        full_move = None
        for m in legal_moves:
            if move == m:
                full_move = m

        # Use move from legal_moves because it cointains capture and promote information.
        if full_move:
            move = full_move
        elif move in non_jump_moves:
            raise ValueError('Illegal move: There are jumps available.')
        else:
            raise ValueError('Illegal move: That move is not allowed.')


        # Update location of the moving piece and promote piece if neccesary.
        if move.promote:
            self.state[move.dst[1]][move.dst[0]] = self.state[move.src[1]][move.src[0]] * 3
        else:
            self.state[move.dst[1]][move.dst[0]] = self.state[move.src[1]][move.src[0]]
        self.state[move.src[1]][move.src[0]] = EMPTY

        # Remove captured piece if any.
        if move.capture:
            delta_x = ( move.src[0] - move.dst[0] ) // 2
            delta_y = ( move.src[1] - move.dst[1] ) // 2
            captured_piece = ( move.dst[0] + delta_x, move.dst[1] + delta_y )
            self.state[captured_piece[1]][captured_piece[0]] = EMPTY

        # Check if the game is over.
        if self._is_game_over():
            self.game_over = True
            return

        # Update the current player.
        self.legal_moves = {}

        continue_turn = False
        if move.capture:
            legal_moves = self.get_legal_moves(*move.dst) 
            for m in legal_moves:
                if m.capture:
                    continue_turn = True

        if not continue_turn:
            self.required_src = None
            if self.player_in_turn == 'black':
                self.player_in_turn = 'white'
            else:
                self.player_in_turn = 'black'
        else:
            self.required_src = move.dst


    def get_legal_moves(self, x, y):
        '''
        Gets the list of possible moves from a given tile in the board.
        Additionally saves a copy of the legal moves for that tile until
        the board is updated.
        '''
       
        # Return cached version if available.
        if (x, y) in self.legal_moves:
            return self.legal_moves[(x, y)]

        legal_moves = []
        
        possible_capture = False

        # Pawns can only go forward and may be promoted, but go in opposite directions
        # depending on their color so must check separately.
        if self.state[y][x] == BLACK_PAWN:                                                # E.g.: Black pawns can go in two directions
            if ( (y + 1 <= 7) and (x - 1 >= 0) and (self.state[y+1][x-1] == EMPTY) ):     #       but produce 4 different outcomes:
                m = Move([x, y], [x-1, y+1], capture=False)
                if y + 1 == 7:                                                            # 1 down, 1 left - no capture
                    m.promote = True
                legal_moves.append(m)
            elif ( (y + 2 <= 7) and (x - 2 >= 0) and (self.state[y+1][x-1] < 0) and (self.state[y+2][x-2] == EMPTY) ):   
                m = Move([x, y], [x-2, y+2], capture=True)                                # 2 down, 2 left - with capture
                if y + 2 == 7:                                                  
                    m.promote = True
                legal_moves.append(m)
                possible_capture = True

            if ( (y + 1 <= 7) and (x + 1 <= 7) and (self.state[y+1][x+1] == EMPTY) ):     # 1 down, 1 right - no capture
                m = Move([x, y], [x+1, y+1], capture=False)
                if y + 1 == 7:                                                  
                    m.promote = True
                legal_moves.append(m)
            elif ( (y + 2 <= 7) and (x + 2 <= 7) and (self.state[y+1][x+1] < 0) and (self.state[y+2][x+2] == EMPTY) ):
                m = Move([x, y], [x+2, y+2], capture=True)                                # 2 down, 2 left - with capture
                if y + 2 == 7:                                                  
                    m.promote = True
                legal_moves.append(m)
                possible_capture = True
            

        elif self.state[y][x] == WHITE_PAWN:
            if ( (y - 1 >= 0) and (x - 1 >= 0) and (self.state[y-1][x-1] == EMPTY) ):
                m = Move([x, y], [x-1, y-1], capture=False)
                if y - 1 == 0:
                    m.promote = True
                legal_moves.append(m)
            elif ( (y - 2 >= 0) and (x - 2 >= 0) and (self.state[y-1][x-1] > 0) and (self.state[y-2][x-2] == EMPTY) ):
                m = Move([x, y], [x-2, y-2], capture=True)
                if y - 2 == 0:
                    m.promote = True
                legal_moves.append(m)
                possible_capture = True

            if ( (y - 1 >= 0) and (x + 1 <= 7) and (self.state[y-1][x+1] == EMPTY) ):
                m = Move([x, y], [x+1, y-1], capture=False)
                if y - 1 == 0:
                    m.promote = True
                legal_moves.append(m)
            elif ( (y - 2 >= 0) and (x + 2 <= 7) and (self.state[y-1][x+1] > 0) and (self.state[y-2][x+2] == EMPTY) ):
                m = Move([x, y], [x+2, y-2], capture=True)
                if y - 2 == 0:
                    m.promote = True
                legal_moves.append(m)
                possible_capture = True

        # Kings can go in any direction so another check is done separately.
        elif self.state[y][x] == BLACK_KING or self.state[y][x] == WHITE_KING:
            if ( (y + 1 <= 7) and (x - 1 >= 0) and (self.state[y+1][x-1] == EMPTY) ):
                m = Move([x, y], [x-1, y+1], capture=False)
                legal_moves.append(m)
            elif ( (y + 2 <= 7) and (x - 2 >= 0) and (self.state[y+1][x-1]*self.state[y][x] < 0) and (self.state[y+2][x-2] == EMPTY) ):
                m = Move([x, y], [x-2, y+2], capture=True)
                legal_moves.append(m)
                possible_capture = True

            if ( (y + 1 <= 7) and (x + 1 <= 7) and (self.state[y+1][x+1] == EMPTY) ):
                m = Move([x, y], [x+1, y+1], capture=False)
                legal_moves.append(m)
            elif ( (y + 2 <= 7) and (x + 2 <= 7) and (self.state[y+1][x+1]*self.state[y][x] < 0) and (self.state[y+2][x+2] == EMPTY) ):
                m = Move([x, y], [x+2, y+2], capture=True)
                legal_moves.append(m)
                possible_capture = True

            if ( (y - 1 >= 0) and (x - 1 >= 0) and (self.state[y-1][x-1] == EMPTY) ):
                m = Move([x, y], [x-1, y-1], capture=False)
                legal_moves.append(m)
            elif ( (y - 2 >= 0) and (x - 2 >= 0) and (self.state[y-1][x-1]*self.state[y][x] < 0) and (self.state[y-2][x-2] == EMPTY) ):
                m = Move([x, y], [x-2, y-2], capture=True)
                legal_moves.append(m)
                possible_capture = True

            if ( (y - 1 >= 0) and (x + 1 <= 7) and (self.state[y-1][x+1] == EMPTY) ):
                m = Move([x, y], [x+1, y-1], capture=False)
                legal_moves.append(m)
            elif ( (y - 2 >= 0) and (x + 2 <= 7) and (self.state[y-1][x+1]*self.state[y][x] < 0) and (self.state[y-2][x+2] == EMPTY) ):
                m = Move([x, y], [x+2, y-2], capture=True)
                legal_moves.append(m)
                possible_capture = True

        # Save the result into legal moves cache
        self.legal_moves[(x, y)] = legal_moves

        return legal_moves



####### PRIVATE METHODS #######

    def _generate_initial_state(self):
        '''
        Generates start of game board state.
        '''

        state = [
            [ BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY ],
            [ EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN ],
            [ BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY, BLACK_PAWN, EMPTY ],

            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY ],
            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY ],

            [ EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN ],
            [ WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY ],
            [ EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN, EMPTY, WHITE_PAWN ],
        ]

        return state


    def _get_current_possible_jumps(self):
        '''
        Finds all the possible jumps that can be made in the current state of
        the board if any.
        '''

        legal_moves = []

        PAWN_COLOR = BLACK_PAWN if self.player_in_turn == 'black' else WHITE_PAWN
        KING_COLOR = BLACK_KING if self.player_in_turn == 'black' else WHITE_KING
        
        for row in range(8):
            for col in range(8):
                if self.state[row][col] == PAWN_COLOR or self.state[row][col] == KING_COLOR:
                    legal_moves += self.get_legal_moves(col, row)

        # Return only jumps if any.
        possible_jumps = [ x for x in legal_moves if x.capture ]

        return possible_jumps


    def _is_game_over(self):
        '''
        Check if there are any pieces remaining for the color opposite to the
        current player.
        '''

        PAWN_COLOR = BLACK_PAWN if self.player_in_turn == 'white' else WHITE_PAWN
        KING_COLOR = BLACK_KING if self.player_in_turn == 'white' else WHITE_KING

        piece_found = False
        for row in range(8):
            for col in range(8):
                if self.state[row][col] == PAWN_COLOR or self.state[row][col] == KING_COLOR:
                    piece_found = True

        return not piece_found



####### HELPER CLASSES #######

class Move:
    '''
    Move object representation.

    This class represents the basic information of a move in the
    game of Checkers.
    '''

    def __init__(self, src, dst, capture=False, promote=False):
        self.src = src
        self.dst = dst
        self.capture = capture
        self.promote = promote

        return


    def __str__(self):
        return 'Move(src={}, dst={}, capture={}, promote={})'.format(self.src, self.dst, self.capture, self.promote)


    def __eq__(self, other):
        return ( self.src == other.src and self.dst == other.dst )
