import pygame
from pieces import *

SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8

def load_pieces():
    pieces = {}
    piece_mapping = {
        W_KING: 'WK', W_QUEEN: 'WQ', W_BISHOP: 'WB',
        W_KNIGHT: 'WN', W_ROOK: 'WR', W_PAWN: 'WP',
        B_KING: 'BK', B_QUEEN: 'BQ', B_BISHOP: 'BB',
        B_KNIGHT: 'BN', B_ROOK: 'BR', B_PAWN: 'BP'
    }
    
    for piece_num, piece_name in piece_mapping.items():
        image_path = f'gui/assets/{piece_name}.png'
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
        pieces[piece_num] = image
    
    return pieces

def get_square_from_mouse(pos):
    x, y = pos
    return (y // SQUARE_SIZE, x // SQUARE_SIZE)
