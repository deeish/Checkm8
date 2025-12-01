"""Chess piece definitions and move generation."""

from enum import Enum
from typing import List, Tuple, Optional


class Color(Enum):
    """Chess piece colors."""
    WHITE = 1
    BLACK = 2


class PieceType(Enum):
    """Chess piece types."""
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6


class Piece:
    """Represents a chess piece."""
    
    # Piece values for material evaluation
    VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    def __init__(self, piece_type: PieceType, color: Color):
        self.type = piece_type
        self.color = color
        self.has_moved = False
    
    def __repr__(self):
        color_char = 'w' if self.color == Color.WHITE else 'b'
        type_chars = {
            PieceType.PAWN: 'P',
            PieceType.ROOK: 'R',
            PieceType.KNIGHT: 'N',
            PieceType.BISHOP: 'B',
            PieceType.QUEEN: 'Q',
            PieceType.KING: 'K'
        }
        return f"{color_char}{type_chars[self.type]}"
    
    def get_value(self) -> int:
        """Get the material value of this piece."""
        return self.VALUES[self.type]


class MoveGenerator:
    """Generates legal moves for chess pieces."""
    
    @staticmethod
    def get_pawn_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate pawn moves."""
        moves = []
        direction = -1 if color == Color.WHITE else 1
        start_row = 6 if color == Color.WHITE else 1
        
        # Move forward one square
        if 0 <= row + direction < 8 and board.board[row + direction][col] is None:
            moves.append((row + direction, col))
            
            # Move forward two squares from starting position
            if row == start_row and board.board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))
        
        # Capture diagonally
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= row + direction < 8 and 0 <= new_col < 8:
                target = board.board[row + direction][new_col]
                if target is not None and target.color != color:
                    moves.append((row + direction, new_col))
        
        return moves
    
    @staticmethod
    def get_rook_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate rook moves."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    @staticmethod
    def get_knight_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate knight moves."""
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.board[new_row][new_col]
                if target is None or target.color != color:
                    moves.append((new_row, new_col))
        
        return moves
    
    @staticmethod
    def get_bishop_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate bishop moves."""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    @staticmethod
    def get_queen_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate queen moves (rook + bishop)."""
        moves = MoveGenerator.get_rook_moves(board, row, col, color)
        moves.extend(MoveGenerator.get_bishop_moves(board, row, col, color))
        return moves
    
    @staticmethod
    def get_king_moves(board: 'Board', row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate king moves."""
        moves = []
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in king_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.board[new_row][new_col]
                if target is None or target.color != color:
                    moves.append((new_row, new_col))
        
        return moves
    
    @staticmethod
    def get_moves(board: 'Board', row: int, col: int) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece at the given position."""
        piece = board.board[row][col]
        if piece is None:
            return []
        
        move_generators = {
            PieceType.PAWN: MoveGenerator.get_pawn_moves,
            PieceType.ROOK: MoveGenerator.get_rook_moves,
            PieceType.KNIGHT: MoveGenerator.get_knight_moves,
            PieceType.BISHOP: MoveGenerator.get_bishop_moves,
            PieceType.QUEEN: MoveGenerator.get_queen_moves,
            PieceType.KING: MoveGenerator.get_king_moves
        }
        
        generator = move_generators.get(piece.type)
        if generator:
            return generator(board, row, col, piece.color)
        return []

