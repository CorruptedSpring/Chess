import pygame
import numpy as np
from pieces import *
from chess_logic import *
from gui.sprites import *

class GameState:
    def __init__(self):
        self.board, self.joker_mapping = initialize_board()
        self.current_player_white = True
        self.move_history = []
        self.castling_rights = {
            'White': {'kingside': True, 'queenside': True},
            'Black': {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None
        self.last_move = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        # Add tracking of moved joker pieces
        self.moved_jokers = {
            'white': {},  # Will store {new_pos: original_col}
            'black': {}
        }

def draw_board(screen, board, pieces_sprites, selected=None, valid_moves=None):
    for row in range(8):
        for col in range(8):
            # Draw square
            color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, color, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Highlight selected square
            if selected and selected == (row, col):
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(128)
                s.fill((255, 255, 0))
                screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Highlight valid moves
            if valid_moves and (row, col) in valid_moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(128)
                s.fill((0, 255, 0))
                screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Draw piece
            piece = board[row][col]
            if piece != 0:  # If not empty
                screen.blit(pieces_sprites[piece], 
                          (col * SQUARE_SIZE, row * SQUARE_SIZE))

def ShowGameOverWindow(screen, message):
    """Display game over message and handle replay choice"""
    overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    
    text = font.render(message, True, (255, 255, 255))
    play_again = small_font.render("Press SPACE to play again or ESC to quit", True, (255, 255, 255))
    
    text_rect = text.get_rect(center=(BOARD_SIZE/2, BOARD_SIZE/2 - 50))
    play_rect = play_again.get_rect(center=(BOARD_SIZE/2, BOARD_SIZE/2 + 50))
    
    screen.blit(text, text_rect)
    screen.blit(play_again, play_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption('Chess with Jokers')  # Fixed method name from setCaption to set_caption
    
    play_again = True
    while play_again:
        game = GameState()
        
        # Print joker piece information more clearly
        print("\n=== Joker Pieces for this game ===")
        print("*********************************")
        joker_info = format_joker_info(game.joker_mapping)
        for line in joker_info:
            print(line)
        print("*********************************")
        print("Press any key to start the game...")
        print()
        
        # Wait for user acknowledgment
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                if event.type == pygame.QUIT:
                    return
        
        pieces_sprites = load_pieces()
        selected = None
        valid_moves = []
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    play_again = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        row, col = get_square_from_mouse(event.pos)
                        
                        if selected is None:
                            piece = game.board[row][col]
                            if piece != 0 and ((game.current_player_white and piece > 0) or 
                                             (not game.current_player_white and piece < 0)):
                                selected = (row, col)
                                # Get movement type for joker pieces
                                movement_type = get_piece_movement_type((row, col), game.joker_mapping, game.moved_jokers)
                                if movement_type:
                                    piece_for_moves = movement_type if game.current_player_white else -movement_type
                                    valid_moves = get_valid_moves(piece_for_moves, (row, col), game.board, 
                                                                None, None, game.joker_mapping, game.moved_jokers)
                                else:
                                    valid_moves = get_valid_moves(piece, (row, col), game.board, 
                                                                game.castling_rights[
                                                                    'White' if game.current_player_white else 'Black'
                                                                ],
                                                                game.en_passant_target,
                                                                game.joker_mapping, game.moved_jokers)
                        else:
                            if (row, col) in valid_moves:
                                # Store move information
                                start_pos = selected
                                end_pos = (row, col)
                                moving_piece = game.board[start_pos[0]][start_pos[1]]
                                
                                # Update joker piece tracking
                                if start_pos[0] == 7 or (start_pos[0], start_pos[1]) in game.moved_jokers['white'].keys():
                                    # Check if it's a joker piece or a moved joker
                                    orig_col = None
                                    if start_pos in game.moved_jokers['white']:
                                        orig_col = game.moved_jokers['white'][start_pos]
                                    else:
                                        for piece_info in game.joker_mapping['white']['pieces']:
                                            if start_pos[1] == piece_info[0]:
                                                orig_col = piece_info[0]
                                                break
                                    
                                    if orig_col is not None:
                                        # Remove the old position
                                        to_remove = []
                                        for pos, col in game.moved_jokers['white'].items():
                                            if col == orig_col:
                                                to_remove.append(pos)
                                        for pos in to_remove:
                                            del game.moved_jokers['white'][pos]
                                        # Add the new position
                                        game.moved_jokers['white'][end_pos] = orig_col

                                elif start_pos[0] == 0 or (start_pos[0], start_pos[1]) in game.moved_jokers['black'].keys():
                                    # Check if it's a joker piece or a moved joker
                                    orig_col = None
                                    if start_pos in game.moved_jokers['black']:
                                        orig_col = game.moved_jokers['black'][start_pos]
                                    else:
                                        for piece_info in game.joker_mapping['black']['pieces']:
                                            if start_pos[1] == piece_info[0]:
                                                orig_col = piece_info[0]
                                                break
                                    
                                    if orig_col is not None:
                                        # Remove the old position
                                        to_remove = []
                                        for pos, col in game.moved_jokers['black'].items():
                                            if col == orig_col:
                                                to_remove.append(pos)
                                        for pos in to_remove:
                                            del game.moved_jokers['black'][pos]
                                        # Add the new position
                                        game.moved_jokers['black'][end_pos] = orig_col
                                
                                # Handle special moves
                                if abs(moving_piece) == 6:  # King
                                    handle_castling(game.board, start_pos, end_pos, game.castling_rights)
                                
                                # Make the move
                                game.board[end_pos[0]][end_pos[1]] = moving_piece
                                game.board[start_pos[0]][start_pos[1]] = 0
                                
                                # Handle pawn promotion
                                if abs(moving_piece) == 1 and (row == 0 or row == 7):
                                    game.board[row][col] = (W_QUEEN if moving_piece > 0 else B_QUEEN)
                                
                                # Handle en passant
                                if abs(moving_piece) == 1 and abs(start_pos[0] - end_pos[0]) == 2:
                                    game.en_passant_target = (
                                        (start_pos[0] + end_pos[0]) // 2,
                                        start_pos[1]
                                    )
                                else:
                                    game.en_passant_target = None
                                
                                game.last_move = (start_pos, end_pos)
                                game.current_player_white = not game.current_player_white
                                
                            selected = None
                            valid_moves = []
            
            draw_board(screen, game.board, pieces_sprites, selected, valid_moves)
            pygame.display.flip()
            
            # Check game end conditions
            is_white = game.current_player_white
            if is_in_check(game.board, is_white, game.joker_mapping, game.moved_jokers):
                if is_checkmate(game.board, is_white, game.joker_mapping, game.moved_jokers):
                    winner = "Black" if is_white else "White"
                    play_again = ShowGameOverWindow(screen, f"{winner} Wins!")
                    running = False
            elif is_stalemate(game.board, is_white, game.joker_mapping, game.moved_jokers):
                play_again = ShowGameOverWindow(screen, "Stalemate!")
                running = False
            elif HasInsufficientMaterial(game.board):
                play_again = ShowGameOverWindow(screen, "Draw - Insufficient Material!")
                running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()