"""Chess board representation and game state management."""

from typing import List, Tuple, Optional
from copy import deepcopy

from .pieces import Piece, PieceType, Color, MoveGenerator


class Board:
    """Represents a chess board and game state."""
    
    def __init__(self):
        """Initialize a chess board with starting position."""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = Color.WHITE
        self.move_history = []
        self._initialize_board()
    
    def _initialize_board(self):
        """Set up the initial chess position."""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        
        # Place back rank pieces
        back_rank_pieces = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for col, piece_type in enumerate(back_rank_pieces):
            self.board[0][col] = Piece(piece_type, Color.BLACK)
            self.board[7][col] = Piece(piece_type, Color.WHITE)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at the given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the position is valid."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_all_moves(self, color: Color) -> List[Tuple[int, int, int, int]]:
        """Get all legal moves for a color. Returns list of (from_row, from_col, to_row, to_col)."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == color:
                    piece_moves = MoveGenerator.get_moves(self, row, col)
                    for to_row, to_col in piece_moves:
                        # Check if move is legal (doesn't leave king in check)
                        if self.is_legal_move(row, col, to_row, to_col, color):
                            moves.append((row, col, to_row, to_col))
        return moves
    
    def _apply_move_directly(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Apply a move directly without validation (for testing moves)."""
        piece = self.board[from_row][from_col]
        if piece is None:
            return
        
        captured = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
    
    def is_legal_move(self, from_row: int, from_col: int, to_row: int, to_col: int, color: Color) -> bool:
        """Check if a move is legal (doesn't leave own king in check)."""
        # Make the move on a copy
        new_board = deepcopy(self)
        new_board._apply_move_directly(from_row, from_col, to_row, to_col)
        
        # Check if the king is in check after the move
        return not new_board.is_in_check(color)
    
    def make_move_copy(self, from_row: int, from_col: int, to_row: int, to_col: int) -> 'Board':
        """Create a copy of the board with a move made."""
        new_board = deepcopy(self)
        new_board._apply_move_directly(from_row, from_col, to_row, to_col)
        return new_board
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Make a move on the board. Returns True if move was made."""
        if not self.is_valid_position(from_row, from_col) or not self.is_valid_position(to_row, to_col):
            return False
        
        piece = self.board[from_row][from_col]
        if piece is None or piece.color != self.current_turn:
            return False
        
        # Check if move is in legal moves
        legal_moves = MoveGenerator.get_moves(self, from_row, from_col)
        if (to_row, to_col) not in legal_moves:
            return False
        
        # Check if move is legal (doesn't leave king in check)
        if not self.is_legal_move(from_row, from_col, to_row, to_col, piece.color):
            return False
        
        # Make the move
        captured = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True
        
        # Record move
        self.move_history.append((from_row, from_col, to_row, to_col, captured))
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        return True
    
    def find_king(self, color: Color) -> Optional[Tuple[int, int]]:
        """Find the king of the given color."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the king of the given color is in check."""
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        
        king_row, king_col = king_pos
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    moves = MoveGenerator.get_moves(self, row, col)
                    if (king_row, king_col) in moves:
                        return True
        
        return False
    
    def is_checkmate(self, color: Color) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        
        # Check if there are any legal moves
        return len(self.get_all_moves(color)) == 0
    
    def is_stalemate(self, color: Color) -> bool:
        """Check if the given color is in stalemate."""
        if self.is_in_check(color):
            return False
        
        # Check if there are any legal moves
        return len(self.get_all_moves(color)) == 0
    
    def get_fen(self) -> str:
        """Get FEN representation of the board (simplified)."""
        fen_rows = []
        for row in range(8):
            fen_row = ""
            empty_count = 0
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    char = piece.type.name[0].lower() if piece.color == Color.BLACK else piece.type.name[0]
                    if piece.type == PieceType.KNIGHT:
                        char = 'n' if piece.color == Color.BLACK else 'N'
                    fen_row += char
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        return "/".join(fen_rows)
    
    def __str__(self):
        """String representation of the board."""
        result = "  a b c d e f g h\n"
        for row in range(8):
            result += f"{8 - row} "
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    result += ". "
                else:
                    result += str(piece) + " "
            result += f"{8 - row}\n"
        result += "  a b c d e f g h"
        return result

