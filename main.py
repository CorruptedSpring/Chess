import numpy as np
import pygame
import random
from pieces import *
from gui.sprites import *
from gui.sprites import SquareSize, BoardSize
class GameState:
    def __init__(self):
        self.Board = InitializeBoard()
        self.CurrentPlayer = 'White'
        self.MoveHistory = []
        self.CastlingRights = {
            'White': {'kingside': True, 'queenside': True},
            'Black': {'kingside': True, 'queenside': True}
        }
        self.EnPassantTarget = None
        self.HalfmoveClock = 0
        self.FullmoveNumber = 1
        self.JokerPieces = self.InitializeJokerPieces()

    def InitializeJokerPieces(self):
        PieceTypes = ['P', 'N', 'B', 'R', 'Q']
        Jokers = {
            'White': {'positions': {}, 'movements': {}},
            'Black': {'positions': {}, 'movements': {}}
        }
        
        for Color in ['White', 'Black']:
            SelectedTypes = random.sample(PieceTypes, 2)
            
            for i, PieceType in enumerate(SelectedTypes):
                Pieces = []
                for Row in range(8):
                    for Col in range(8):
                        Piece = self.Board[Row][Col]
                        if Piece != 'Empty' and Piece[0] == Color[0] and Piece[1] == PieceType:
                            Pieces.append((Row, Col))
                
                if Pieces:
                    SelectedPos = random.choice(Pieces)
                    MovementType = SelectedTypes[1 if i == 0 else 0]
                    Jokers[Color]['positions'][SelectedPos] = PieceType
                    Jokers[Color]['movements'][SelectedPos] = MovementType
                    print(f"{Color} joker: {PieceType} at {SelectedPos} moves like {MovementType}")
        
        return Jokers

def InitializeBoard():
    board = np.full((8, 8), 'Empty')
    for i in range(8):
        board[1][i] = 'BP'
        board[6][i] = 'WP'
    
    pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    for i in range(8):
        board[0][i] = 'B' + pieces[i]
        board[7][i] = 'W' + pieces[i]
    
    return board

def PrintBoard(board):
    pass

def IsValidMove(board, start_pos, end_pos, current_player, joker_pieces):
    piece = board[start_pos[0]][start_pos[1]]
    if piece == 'Empty' or piece[0] != current_player[0]:
        return False
        
    valid_moves = GetValidMoves(piece, start_pos, board, joker_pieces=joker_pieces)
    if end_pos not in valid_moves:
        return False
        
    temp_board = board.copy()
    temp_board[end_pos[0]][end_pos[1]] = piece
    temp_board[start_pos[0]][start_pos[1]] = 'Empty'
    
    
    return not IsInCheck(temp_board, current_player == 'White')

def IsStalemate(board, current_player):
    if IsInCheck(board, current_player == 'White'):
        return False
    
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != 'Empty' and piece[0] == current_player[0]:
                moves = GetValidMoves(piece, (i,j), board)
                if moves:
                    return False
    return True

def HasInsufficientMaterial(board):
    pieces = {'W': [], 'B': []}
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != 'Empty':
                pieces[piece[0]].append(piece[1])
    
    if len(pieces['W']) == 1 and len(pieces['B']) == 1:
        return True
    if (len(pieces['W']) == 2 and len(pieces['B']) == 1 and 
        ('B' in pieces['W'] or 'N' in pieces['W'])) or \
       (len(pieces['B']) == 2 and len(pieces['W']) == 1 and 
        ('B' in pieces['B'] or 'N' in pieces['B'])):
        return True
    return False

def DrawBoard(screen, board, pieces_sprites, selected=None, valid_moves=None, game_instance=None):
    for row in range(8):
        for col in range(8):
            color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, color, 
                           (col * SquareSize, row * SquareSize, SquareSize, SquareSize))
            
            if selected and selected == (row, col):
                s = pygame.Surface((SquareSize, SquareSize))
                s.set_alpha(128)
                s.fill((255, 255, 0))
                screen.blit(s, (col * SquareSize, row * SquareSize))
            
            if valid_moves and (row, col) in valid_moves:
                s = pygame.Surface((SquareSize, SquareSize))
                s.set_alpha(128)
                s.fill((0, 255, 0))
                screen.blit(s, (col * SquareSize, row * SquareSize))
            
            piece = board[row][col]
            if piece != 'Empty':
                screen.blit(pieces_sprites[piece], 
                          (col * SquareSize, row * SquareSize))
                
                if game_instance:
                    color = 'White' if piece[0] == 'W' else 'Black'
                    if (row, col) in game_instance.JokerPieces[color]['positions']:
                        center_transparent = (col * SquareSize + SquareSize - 15, 
                                              row * SquareSize + SquareSize - 45)
                        pygame.draw.circle(screen, (0, 0, 255, 128), center_transparent, 5)

def Main():
    pygame.init()
    Screen = pygame.display.set_mode((BoardSize, BoardSize))
    pygame.display.set_caption('Chess')
    
    GameInstance = GameState()
    PiecesSprites = LoadPieces()
    Selected = None
    ValidMoves = []
    FirstMove = True

    Running = True
    while Running:
        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                Running = False
            
            elif Event.type == pygame.MOUSEBUTTONDOWN:
                if Event.button == 1:
                    Row, Col = GetSquareFromMouse(Event.pos)
                    
                    if Selected is None:
                        Piece = GameInstance.Board[Row][Col]
                        if Piece != 'Empty' and Piece[0] == GameInstance.CurrentPlayer[0]:
                            Selected = (Row, Col)
                            ValidMoves = GetValidMoves(Piece, (Row, Col), 
                                                    GameInstance.Board,
                                                    GameInstance.CastlingRights[GameInstance.CurrentPlayer],
                                                    GameInstance.EnPassantTarget,
                                                    GameInstance.JokerPieces)
                    else:
                        if (Row, Col) in ValidMoves:
                            Piece = GameInstance.Board[Selected[0]][Selected[1]]
                            GameInstance.Board[Selected[0]][Selected[1]] = 'Empty'
                            GameInstance.Board[Row][Col] = Piece
                            
                            if Piece.endswith('P') and (Row == 0 or Row == 7):
                                GameInstance.Board[Row][Col] = Piece[0] + 'Q'
                            
                            if FirstMove and GameInstance.CurrentPlayer == 'White':
                                FirstMove = False
                            else:
                                # Preserve joker piece movements even if one is captured
                                for color in ['White', 'Black']:
                                    for pos in list(GameInstance.JokerPieces[color]['positions'].keys()):
                                        if GameInstance.Board[pos[0]][pos[1]] == 'Empty':
                                            if pos in GameInstance.JokerPieces[color]['positions']:
                                                del GameInstance.JokerPieces[color]['positions'][pos]
                                            if pos in GameInstance.JokerPieces[color]['movements']:
                                                del GameInstance.JokerPieces[color]['movements'][pos]
                                        elif (Selected[0], Selected[1]) in GameInstance.JokerPieces[color]['positions']:
                                            # Update the position of the joker piece
                                            GameInstance.JokerPieces[color]['positions'][(Row, Col)] = GameInstance.JokerPieces[color]['positions'].pop((Selected[0], Selected[1]))
                                            GameInstance.JokerPieces[color]['movements'][(Row, Col)] = GameInstance.JokerPieces[color]['movements'].pop((Selected[0], Selected[1]))
                                            break  # Ensure only the moved joker piece is updated
                            
                            GameInstance.CurrentPlayer = 'Black' if GameInstance.CurrentPlayer == 'White' else 'White'
                        Selected = None
                        ValidMoves = []
        
        DrawBoard(Screen, GameInstance.Board, PiecesSprites, Selected, ValidMoves, GameInstance)
        pygame.display.flip()
        
        if IsCheckmate(GameInstance.Board, GameInstance.CurrentPlayer == 'White'):
            Running = False
        elif IsStalemate(GameInstance.Board, GameInstance.CurrentPlayer):
            Running = False
    
    pygame.quit()

if __name__ == "__main__":
    Main()
