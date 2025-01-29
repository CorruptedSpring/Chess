import numpy as np
import random

# Import constants directly instead of importing from pieces
from pieces import (W_PAWN, W_ROOK, W_KNIGHT, W_BISHOP, W_QUEEN, W_KING,
                   B_PAWN, B_ROOK, B_KNIGHT, B_BISHOP, B_QUEEN, B_KING,
                   get_basic_moves)

def initialize_board():
    board = np.zeros((8, 8), dtype=np.int8)
    board[1, :] = B_PAWN
    board[6, :] = W_PAWN
    
    back_row = [W_ROOK, W_KNIGHT, W_BISHOP, W_QUEEN, W_KING, W_BISHOP, W_KNIGHT, W_ROOK]
    for i, piece in enumerate(back_row):
        board[0, i] = -piece  # Black pieces
        board[7, i] = piece   # White pieces
    
    # Define valid positions for joker pieces (excluding king position)
    valid_positions = [0, 1, 2, 3, 5, 6, 7]  # Position 4 is king
    
    # Select random positions for white joker pieces
    white_positions = random.sample(valid_positions, 2)
    # Select corresponding positions for black joker pieces
    black_positions = white_positions.copy()  # Use same positions on black side
    
    # Store original pieces for the joker system
    white_jokers = [board[7, white_positions[0]], board[7, white_positions[1]]]
    black_jokers = [board[0, black_positions[0]], board[0, black_positions[1]]]
    
    # Store complete positions and piece information
    joker_mapping = {
        'white': {
            'pieces': [(white_positions[0], white_jokers[0]), (white_positions[1], white_jokers[1])],
            'moves': [(white_positions[0], white_jokers[1]), (white_positions[1], white_jokers[0])]
        },
        'black': {
            'pieces': [(black_positions[0], black_jokers[0]), (black_positions[1], black_jokers[1])],
            'moves': [(black_positions[0], black_jokers[1]), (black_positions[1], black_jokers[0])]
        }
    }
    
    return board, joker_mapping

def is_checkmate(board, is_white, joker_mapping=None, moved_jokers=None):
    if not is_in_check(board, is_white, joker_mapping, moved_jokers):
        return False
    
    for i in range(8):
        for j in range(8):
            piece = board[i, j]
            if (is_white and piece > 0) or (not is_white and piece < 0):
                moves = get_valid_moves(piece, (i, j), board, None, None, joker_mapping, moved_jokers)
                for move in moves:
                    temp_board = board.copy()
                    temp_board[move[0], move[1]] = piece
                    temp_board[i, j] = 0
                    if not is_in_check(temp_board, is_white, joker_mapping, moved_jokers):
                        return False
    return True

def is_stalemate(board, is_white, joker_mapping=None, moved_jokers=None):
    if is_in_check(board, is_white, joker_mapping, moved_jokers):
        return False
        
    for i in range(8):
        for j in range(8):
            piece = board[i, j]
            if (is_white and piece > 0) or (not is_white and piece < 0):
                moves = get_valid_moves(piece, (i, j), board, None, None, joker_mapping, moved_jokers)
                for move in moves:
                    temp_board = board.copy()
                    temp_board[move[0], move[1]] = piece
                    temp_board[i, j] = 0
                    if not is_in_check(temp_board, is_white, joker_mapping, moved_jokers):
                        return False
    return True

def handle_castling(board, start_pos, end_pos, castling_rights):
    row, col = start_pos
    new_row, new_col = end_pos
    piece = board[row, col]
    
    if abs(piece) == W_KING and abs(col - new_col) == 2:  # Changed KING to W_KING
        if new_col > col:
            rook_start = (row, 7)
            rook_end = (row, 5)
        else:
            rook_start = (row, 0)
            rook_end = (row, 3)
            
        board[rook_end[0], rook_end[1]] = board[rook_start[0], rook_start[1]]
        board[rook_start[0], rook_start[1]] = 0
        
    if abs(piece) == W_KING:  # Changed KING to W_KING
        if piece > 0:
            castling_rights['White'] = {'kingside': False, 'queenside': False}
        else:
            castling_rights['Black'] = {'kingside': False, 'queenside': False}
    
    if row == 0 and col == 0:
        castling_rights['Black']['queenside'] = False
    elif row == 0 and col == 7:
        castling_rights['Black']['kingside'] = False
    elif row == 7 and col == 0:
        castling_rights['White']['queenside'] = False
    elif row == 7 and col == 7:
        castling_rights['White']['kingside'] = False

def handle_pawn_promotion(board, pos, is_white):
    """Handle pawn promotion"""
    row, col = pos
    if (is_white and row == 0) or (not is_white and row == 7):
        return board[row, col] * 5
    return board[row, col]

def handle_en_passant(board, start_pos, end_pos, last_move):
    """Handle en passant capture"""
    if last_move is None:
        return False
        
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    last_start_row, last_start_col = last_move[0]
    last_end_row, last_end_col = last_move[1]
    
    piece = board[start_row, start_col]
    if abs(piece) == W_PAWN:  # Changed PAWN to W_PAWN
        if abs(start_col - end_col) == 1 and board[end_row, end_col] == 0:
            if (piece > 0 and start_row == 3) or (piece < 0 and start_row == 4):
                if abs(last_start_row - last_end_row) == 2:
                    board[last_end_row, last_end_col] = 0
                    return True
    return False

def get_piece_at(board, pos):
    """Get piece at given position"""
    row, col = pos
    if 0 <= row < 8 and 0 <= col < 8:
        return board[row, col]
    return None

def get_piece_movement_type(pos, joker_mapping, moved_jokers=None):
    """Get the actual movement type for a piece considering joker rules and moved pieces"""
    row, col = pos
    
    # Check moved jokers first
    if moved_jokers:
        # Check if this position is in moved jokers
        if pos in moved_jokers['white']:
            orig_col = moved_jokers['white'][pos]
            for piece_pos, move_pos in zip(joker_mapping['white']['pieces'], joker_mapping['white']['moves']):
                if orig_col == piece_pos[0]:
                    return abs(move_pos[1])
                    
        if pos in moved_jokers['black']:
            orig_col = moved_jokers['black'][pos]
            for piece_pos, move_pos in zip(joker_mapping['black']['pieces'], joker_mapping['black']['moves']):
                if orig_col == piece_pos[0]:
                    return abs(move_pos[1])
    
    # Check initial positions (unchanged)
    if row == 7:
        for piece_pos, move_pos in zip(joker_mapping['white']['pieces'], joker_mapping['white']['moves']):
            if col == piece_pos[0]:
                return abs(move_pos[1])
    elif row == 0:
        for piece_pos, move_pos in zip(joker_mapping['black']['pieces'], joker_mapping['black']['moves']):
            if col == piece_pos[0]:
                return abs(move_pos[1])
    
    return None

def is_valid_move(board, start_pos, end_pos, is_white, joker_mapping, moved_jokers=None):
    piece = get_piece_at(board, start_pos)
    if piece is None:
        return False
        
    if (is_white and piece < 0) or (not is_white and piece > 0):
        return False
    
    # Check if piece is a joker and use its movement type
    movement_type = get_piece_movement_type(start_pos, joker_mapping, moved_jokers)
    if movement_type:
        piece_for_movement = movement_type if is_white else -movement_type
        moves = get_valid_moves(piece_for_movement, start_pos, board)
    else:
        moves = get_valid_moves(piece, start_pos, board)
    
    return end_pos in moves

def HasInsufficientMaterial(board):
    pieces = {'W': [], 'B': []}
    for i in range(8):
        for j in range(8):
            piece = board[i, j]
            if piece > 0:
                pieces['W'].append(abs(piece))
            elif piece < 0:
                pieces['B'].append(abs(piece))
    
    if len(pieces['W']) == 1 and len(pieces['B']) == 1:
        return True
    
    if (len(pieces['W']) == 2 and len(pieces['B']) == 1 and 
        (W_BISHOP in pieces['W'] or W_KNIGHT in pieces['W'])) or \
       (len(pieces['B']) == 2 and len(pieces['W']) == 1 and 
        (W_BISHOP in pieces['B'] or W_KNIGHT in pieces['B'])):
        return True
    
    return False

def get_piece_name(piece_value):
    """Convert piece value to readable name"""
    piece_names = {
        W_PAWN: "Pawn", W_ROOK: "Rook", W_KNIGHT: "Knight",
        W_BISHOP: "Bishop", W_QUEEN: "Queen", W_KING: "King",
        B_PAWN: "Pawn", B_ROOK: "Rook", B_KNIGHT: "Knight",
        B_BISHOP: "Bishop", B_QUEEN: "Queen", B_KING: "King"
    }
    return piece_names.get(abs(piece_value), "Unknown")

def format_joker_info(joker_mapping):
    """Format joker piece information for display"""
    info_lines = []
    
    # Format white joker pieces
    for i, (piece_pos, move_pos) in enumerate(zip(joker_mapping['white']['pieces'], joker_mapping['white']['moves'])):
        piece_col = piece_pos[0] + 1  # Convert to 1-based column number
        piece_name = get_piece_name(piece_pos[1])
        moves_like = get_piece_name(move_pos[1])
        info_lines.append(f"White Joker #{i+1}: {piece_name} at column {piece_col} moves like a {moves_like}")
    
    # Format black joker pieces
    for i, (piece_pos, move_pos) in enumerate(zip(joker_mapping['black']['pieces'], joker_mapping['black']['moves'])):
        piece_col = piece_pos[0] + 1  # Convert to 1-based column number
        piece_name = get_piece_name(abs(piece_pos[1]))  # Use abs() for black pieces
        moves_like = get_piece_name(abs(move_pos[1]))   # Use abs() for black pieces
        info_lines.append(f"Black Joker #{i+1}: {piece_name} at column {piece_col} moves like a {moves_like}")
    
    return info_lines

def is_in_check(board, is_white, joker_mapping=None, moved_jokers=None):
    """Check if the king is in check, considering joker pieces"""
    king = W_KING if is_white else B_KING
    king_pos = None
    
    # Find king position
    for i in range(8):
        for j in range(8):
            if board[i][j] == king:
                king_pos = (i, j)
                break
        if king_pos:
            break
            
    if not king_pos:
        return False
    
    # Check for attacking pieces
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != 0 and ((is_white and piece < 0) or (not is_white and piece > 0)):
                # Check if this piece is a joker
                movement_type = None
                if joker_mapping and moved_jokers:
                    movement_type = get_piece_movement_type((i, j), joker_mapping, moved_jokers)
                
                if movement_type:
                    # Use joker movement type
                    piece_for_moves = movement_type if not is_white else -movement_type
                    moves = get_basic_moves(piece_for_moves, (i, j), board)
                else:
                    # Use normal piece movement
                    moves = get_basic_moves(piece, (i, j), board)
                    
                if king_pos in moves:
                    return True
    return False

def get_valid_moves(piece, pos, board, castling_rights=None, en_passant=None, joker_mapping=None, moved_jokers=None):
    """Get valid moves considering check and joker pieces"""
    moves = get_basic_moves(piece, pos, board, castling_rights, en_passant)
    valid_moves = []
    is_white = piece > 0
    row, col = pos
    
    for move in moves:
        temp_board = board.copy()
        temp_board[move[0]][move[1]] = piece
        temp_board[row][col] = 0
        if not is_in_check(temp_board, is_white, joker_mapping, moved_jokers):
            valid_moves.append(move)
            
    return valid_moves
