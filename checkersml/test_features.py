#!/usr/bin/env python3

import board
import features



state = [
        [0, 0, 0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 3, 0],
        [0, 0, -1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

b = board.Board(state=state)

f1 = features.BlackPiecesFeature()
f2 = features.WhitePiecesFeature()

f3 = features.BlackKingsFeature()
f4 = features.WhiteKingsFeature()

f5 = features.BlackThreatenedFeature()
f6 = features.WhiteThreatenedFeature()

value1 = f1.compute_value(b)
value2 = f2.compute_value(b)
value3 = f3.compute_value(b)
value4 = f4.compute_value(b)
value5 = f5.compute_value(b)
value6 = f6.compute_value(b)

print( '''
Black Pieces:     {}
White Pieces:     {}
Black Kings:      {}
White Kings:      {}
Black Threatened: {}
White Threatened: {}
'''.format(value1, value2, value3, value4, value5, value6) )
