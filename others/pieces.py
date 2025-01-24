def GetValidMoves(PieceType, CurrentPos, Board, CastlingRights=None, EnPassantTarget=None, JokerPieces=None):
    Color = 'White' if PieceType.startswith('W') else 'Black'
    PieceChar = PieceType[1]
    
    if JokerPieces and CurrentPos in JokerPieces[Color]['positions']:
        PieceChar = JokerPieces[Color]['movements'][CurrentPos]
    
    if PieceChar == 'P':
        return PawnMoves(CurrentPos, Board, PieceType.startswith('W'), EnPassantTarget)
    elif PieceChar == 'N':
        return KnightMoves(CurrentPos, Board)
    elif PieceChar == 'B':
        return BishopMoves(CurrentPos, Board)
    elif PieceChar == 'R':
        return RookMoves(CurrentPos, Board)
    elif PieceChar == 'Q':
        return QueenMoves(CurrentPos, Board)
    elif PieceChar == 'K':
        Moves = KingMoves(CurrentPos, Board)
        if CastlingRights:
            Moves += GetCastlingMoves(CurrentPos, Board, CastlingRights, PieceType.startswith('W'))
        return Moves
    return []

def PawnMoves(Pos, Board, IsWhite, EnPassantTarget=None):
    Moves = []
    Direction = -1 if IsWhite else 1
    Row, Col = Pos
    
    if 0 <= Row + Direction < 8 and Board[Row + Direction][Col] == 'Empty':
        Moves.append((Row + Direction, Col))
        if (IsWhite and Row == 6) or (not IsWhite and Row == 1):
            if Board[Row + 2*Direction][Col] == 'Empty':
                Moves.append((Row + 2*Direction, Col))
    
    for Dcol in [-1, 1]:
        NewCol = Col + Dcol
        if 0 <= NewCol < 8 and 0 <= Row + Direction < 8:
            Target = Board[Row + Direction][NewCol]
            if Target != 'Empty' and Target[0] != ('W' if IsWhite else 'B'):
                Moves.append((Row + Direction, NewCol))
    
    if EnPassantTarget:
        if Row == (3 if IsWhite else 4):
            if abs(Col - EnPassantTarget[1]) == 1:
                Moves.append(EnPassantTarget)
    
    print(f"Pawn moves from {Pos}: {Moves}")
    return Moves

def KnightMoves(Pos, Board):
    Moves = []
    Row, Col = Pos
    Offsets = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
    
    for Drow, Dcol in Offsets:
        NewRow, NewCol = Row + Drow, Col + Dcol
        if 0 <= NewRow < 8 and 0 <= NewCol < 8:
            if Board[NewRow][NewCol] == 'Empty' or Board[NewRow][NewCol][0] != Board[Row][Col][0]:
                Moves.append((NewRow, NewCol))
    
    print(f"Knight moves from {Pos}: {Moves}")
    return Moves

def BishopMoves(Pos, Board):
    Moves = []
    Row, Col = Pos
    Directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    
    for Drow, Dcol in Directions:
        NewRow, NewCol = Row + Drow, Col + Dcol
        while 0 <= NewRow < 8 and 0 <= NewCol < 8:
            Target = Board[NewRow][NewCol]
            if Target == 'Empty':
                Moves.append((NewRow, NewCol))
            elif Target[0] != Board[Row][Col][0]:
                Moves.append((NewRow, NewCol))
                break
            else:
                break
            NewRow, NewCol = NewRow + Drow, NewCol + Dcol
    
    print(f"Bishop moves from {Pos}: {Moves}")
    return Moves

def RookMoves(Pos, Board):
    Moves = []
    Row, Col = Pos
    Directions = [(0,1), (0,-1), (1,0), (-1,0)]
    
    for Drow, Dcol in Directions:
        NewRow, NewCol = Row + Drow, Col + Dcol
        while 0 <= NewRow < 8 and 0 <= NewCol < 8:
            Target = Board[NewRow][NewCol]
            if Target == 'Empty':
                Moves.append((NewRow, NewCol))
            elif Target[0] != Board[Row][Col][0]:
                Moves.append((NewRow, NewCol))
                break
            else:
                break
            NewRow, NewCol = NewRow + Drow, NewCol + Dcol
    
    print(f"Rook moves from {Pos}: {Moves}")
    return Moves

def QueenMoves(Pos, Board):
    Moves = RookMoves(Pos, Board) + BishopMoves(Pos, Board)
    print(f"Queen moves from {Pos}: {Moves}")
    return Moves

def KingMoves(Pos, Board):
    Moves = []
    Row, Col = Pos
    Directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    
    for Drow, Dcol in Directions:
        NewRow, NewCol = Row + Drow, Col + Dcol
        if 0 <= NewRow < 8 and 0 <= NewCol < 8:
            Target = Board[NewRow][NewCol]
            if Target == 'Empty' or Target[0] != Board[Row][Col][0]:
                Moves.append((NewRow, NewCol))
    
    print(f"King moves from {Pos}: {Moves}")
    return Moves

def GetCastlingMoves(Pos, Board, CastlingRights, IsWhite):
    Moves = []
    Row = 7 if IsWhite else 0
    
    if Pos != (Row, 4):
        return Moves
        
    if CastlingRights['kingside']:
        if (Board[Row][5] == 'Empty' and 
            Board[Row][6] == 'Empty' and 
            Board[Row][7] == ('W' if IsWhite else 'B') + 'R'):
            Moves.append((Row, 6))
            
    if CastlingRights['queenside']:
        if (Board[Row][3] == 'Empty' and 
            Board[Row][2] == 'Empty' and 
            Board[Row][1] == 'Empty' and 
            Board[Row][0] == ('W' if IsWhite else 'B') + 'R'):
            Moves.append((Row, 2))
    
    print(f"Castling moves from {Pos}: {Moves}")
    return Moves

def HandleCastling(GameState, Kingside=True):
    IsWhite = GameState.CurrentPlayer == 'White'
    Row = 7 if IsWhite else 0
    KingCol = 4
    
    if not GameState.CastlingRights[GameState.CurrentPlayer]['kingside' if Kingside else 'queenside']:
        return False
        
    if IsInCheck(GameState.Board, IsWhite):
        return False
        
    if Kingside:
        if not all(GameState.Board[Row][Col] == 'Empty' for Col in [5, 6]):
            return False
        for Col in [4, 5, 6]:
            if SquareUnderAttack(GameState.Board, (Row, Col), IsWhite):
                return False
        RookCol = 7
        NewKingCol = 6
        NewRookCol = 5
    else:
        if not all(GameState.Board[Row][Col] == 'Empty' for Col in [1, 2, 3]):
            return False
        for Col in [2, 3, 4]:
            if SquareUnderAttack(GameState.Board, (Row, Col), IsWhite):
                return False
        RookCol = 0
        NewKingCol = 2
        NewRookCol = 3
    
    Color = 'W' if IsWhite else 'B'
    GameState.Board[Row][NewKingCol] = Color + 'K'
    GameState.Board[Row][NewRookCol] = Color + 'R'
    GameState.Board[Row][KingCol] = 'Empty'
    GameState.Board[Row][RookCol] = 'Empty'
    
    GameState.CastlingRights[GameState.CurrentPlayer]['kingside'] = False
    GameState.CastlingRights[GameState.CurrentPlayer]['queenside'] = False
    
    return True

def SquareUnderAttack(Board, Pos, IsWhite):
    OpponentColor = 'B' if IsWhite else 'W'
    for I in range(8):
        for J in range(8):
            Piece = Board[I][J]
            if Piece != 'Empty' and Piece[0] == OpponentColor:
                if Pos in GetValidMoves(Piece, (I,J), Board):
                    return True
    return False

def IsInCheck(Board, IsWhite):
    KingPiece = 'WK' if IsWhite else 'BK'
    KingPos = None
    for I in range(8):
        for J in range(8):
            if Board[I][J] == KingPiece:
                KingPos = (I, J)
                break
        if KingPos:
            break
    
    OpponentColor = 'B' if IsWhite else 'W'
    for I in range(8):
        for J in range(8):
            Piece = Board[I][J]
            if Piece != 'Empty' and Piece[0] == OpponentColor:
                Moves = GetValidMoves(Piece, (I,J), Board)
                if KingPos in Moves:
                    return True
    return False

def IsCheckmate(Board, IsWhite):
    if not IsInCheck(Board, IsWhite):
        return False
        
    PlayerColor = 'W' if IsWhite else 'B'
    for I in range(8):
        for J in range(8):
            Piece = Board[I][J]
            if Piece != 'Empty' and Piece[0] == PlayerColor:
                Moves = GetValidMoves(Piece, (I,J), Board)
                for Move in Moves:
                    TempBoard = Board.copy()
                    TempBoard[Move[0]][Move[1]] = Piece
                    TempBoard[I][J] = 'Empty'
                    if not IsInCheck(TempBoard, IsWhite):
                        return False
    return True

