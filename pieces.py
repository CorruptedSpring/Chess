import numpy as np

# Remove the import from chess_logic to break circular dependency
# from chess_logic import get_piece_movement_type

EMPTY = 0

W_PAWN = 1
W_ROOK = 2
W_KNIGHT = 3
W_BISHOP = 4
W_QUEEN = 5
W_KING = 6

B_PAWN = -1
B_ROOK = -2
B_KNIGHT = -3
B_BISHOP = -4
B_QUEEN = -5
B_KING = -6

def get_basic_moves(piece, pos, board, castling_rights=None, en_passant=None):
    """Get all possible moves without considering check"""
    row, col = pos
    moves = []
    
    def is_valid_square(r, c, piece):
        if 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] == 0:  # Empty square
                return True
            return (piece > 0 and board[r][c] < 0) or (piece < 0 and board[r][c] > 0)
        return False

    # Pawn moves
    if abs(piece) == 1:
        direction = -1 if piece > 0 else 1
        # Forward move
        if 0 <= row + direction < 8 and board[row + direction][col] == 0:
            moves.append((row + direction, col))
            # Initial two-square move
            if ((piece > 0 and row == 6) or (piece < 0 and row == 1)) and \
               board[row + 2*direction][col] == 0:
                moves.append((row + 2*direction, col))
        
        for dcol in [-1, 1]:
            if 0 <= col + dcol < 8 and 0 <= row + direction < 8:
                target = board[row + direction][col + dcol]
                if (piece > 0 and target < 0) or (piece < 0 and target > 0):
                    moves.append((row + direction, col + dcol))
                
        if en_passant and row == (3 if piece > 0 else 4):
            if abs(col - en_passant[1]) == 1 and row == en_passant[0] - direction:
                moves.append(en_passant)

    elif abs(piece) == 3:
        knight_moves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
        for dr, dc in knight_moves:
            if is_valid_square(row + dr, col + dc, piece):
                moves.append((row + dr, col + dc))

    elif abs(piece) == 4:
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while is_valid_square(r, c, piece):
                moves.append((r, c))
                if board[r][c] != 0:
                    break
                r, c = r + dr, c + dc

    elif abs(piece) == 2:
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while is_valid_square(r, c, piece):
                moves.append((r, c))
                if board[r][c] != 0:
                    break
                r, c = r + dr, c + dc

    elif abs(piece) == 5:
        directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while is_valid_square(r, c, piece):
                moves.append((r, c))
                if board[r][c] != 0:
                    break
                r, c = r + dr, c + dc

    elif abs(piece) == 6:
        directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            if is_valid_square(row + dr, col + dc, piece):
                moves.append((row + dr, col + dc))
        if castling_rights:
            is_white = piece > 0
            base_row = 7 if is_white else 0
            if row == base_row and col == 4:
                if castling_rights['kingside'] and \
                   all(board[base_row][c] == 0 for c in [5, 6]) and \
                   board[base_row][7] == (W_ROOK if is_white else B_ROOK):
                    moves.append((base_row, 6))
                if castling_rights['queenside'] and \
                   all(board[base_row][c] == 0 for c in [1, 2, 3]) and \
                   board[base_row][0] == (W_ROOK if is_white else B_ROOK):
                    moves.append((base_row, 2))

    return moves

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

def get_valid_moves(piece, pos, board, castling_rights=None, en_passant=None):
    """Get valid moves considering check"""
    moves = get_basic_moves(piece, pos, board, castling_rights, en_passant)
    valid_moves = []
    is_white = piece > 0
    row, col = pos
    
    for move in moves:
        temp_board = board.copy()
        temp_board[move[0]][move[1]] = piece
        temp_board[row][col] = 0
        if not is_in_check(temp_board, is_white):
            valid_moves.append(move)
            
    return valid_moves

