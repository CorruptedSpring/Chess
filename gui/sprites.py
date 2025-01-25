import pygame

SquareSize = 80
BoardSize = SquareSize * 8
def LoadPieces():
    Pieces = {}
    PieceNames = {
        'K': 'K',
        'Q': 'Q',
        'B': 'B',
        'N': 'N',
        'R': 'R',
        'P': 'P'
    }
    
    for Color in ['W', 'B']:
        for Code, Name in PieceNames.items():
            ImagePath = f'gui/assets/{Color}{Name}.png'
            Image = pygame.image.load(ImagePath)
            Image = pygame.transform.scale(Image, (SquareSize, SquareSize))
            Pieces[Color + Code] = Image
            
    return Pieces

def GetSquareFromMouse(Pos):
    X, Y = Pos
    return (Y // SquareSize, X // SquareSize)
