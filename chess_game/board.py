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
        self.en_passant_target: Optional[Tuple[int, int]] = None  # Square behind pawn that just moved two squares
        # Castling rights: (kingside, queenside) for each color
        self.castling_rights = {
            Color.WHITE: (True, True),  # (kingside, queenside)
            Color.BLACK: (True, True)
        }
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
    
    def _apply_move_directly(self, from_row: int, from_col: int, to_row: int, to_col: int, promotion_piece: Optional[PieceType] = None):
        """Apply a move directly without validation (for testing moves)."""
        piece = self.board[from_row][from_col]
        if piece is None:
            return
        
        # Handle castling
        if piece.type == PieceType.KING and from_col == 4:  # King on e-file
            king_row = 7 if piece.color == Color.WHITE else 0
            if from_row == king_row:
                # Check if this is a castling move
                if to_col == 6:  # Kingside castling (O-O)
                    # Move rook from h-file to f-file
                    rook = self.board[king_row][7]
                    self.board[king_row][5] = rook  # f-file
                    self.board[king_row][7] = None
                    if rook is not None:
                        rook.has_moved = True
                elif to_col == 2:  # Queenside castling (O-O-O)
                    # Move rook from a-file to d-file
                    rook = self.board[king_row][0]
                    self.board[king_row][3] = rook  # d-file
                    self.board[king_row][0] = None
                    if rook is not None:
                        rook.has_moved = True
        
        # Handle en passant capture
        if piece.type == PieceType.PAWN and self.en_passant_target == (to_row, to_col):
            # This is an en passant capture - remove the captured pawn
            direction = -1 if piece.color == Color.WHITE else 1
            captured_row = to_row - direction
            self.board[captured_row][to_col] = None
        else:
            captured = self.board[to_row][to_col]
        
        # Handle pawn promotion
        if piece.type == PieceType.PAWN:
            if (piece.color == Color.WHITE and to_row == 0) or (piece.color == Color.BLACK and to_row == 7):
                # Promote pawn - default to Queen if not specified
                promotion = promotion_piece if promotion_piece else PieceType.QUEEN
                piece = Piece(promotion, piece.color)
                piece.has_moved = True
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Mark piece as moved if not already (for non-promoted pieces)
        if not piece.has_moved:
            piece.has_moved = True
        
        # Set en_passant_target for double pawn moves, clear it otherwise
        new_en_passant_target = None
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            start_row = 6 if piece.color == Color.WHITE else 1
            if from_row == start_row and to_row == from_row + 2 * direction:
                new_en_passant_target = (from_row + direction, from_col)
        
        self.en_passant_target = new_en_passant_target
        
        # Update castling rights (simplified for move validation)
        if piece.type == PieceType.KING:
            self.castling_rights[piece.color] = (False, False)
        elif piece.type == PieceType.ROOK:
            if from_col == 7:  # Kingside rook
                kingside, queenside = self.castling_rights[piece.color]
                self.castling_rights[piece.color] = (False, queenside)
            elif from_col == 0:  # Queenside rook
                kingside, queenside = self.castling_rights[piece.color]
                self.castling_rights[piece.color] = (kingside, False)
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
    
    def is_legal_move(self, from_row: int, from_col: int, to_row: int, to_col: int, color: Color) -> bool:
        """Check if a move is legal (doesn't leave own king in check)."""
        # Make the move on a copy
        new_board = deepcopy(self)
        new_board._apply_move_directly(from_row, from_col, to_row, to_col)
        
        # Check if the king is in check after the move
        return not new_board.is_in_check(color)
    
    def make_move_copy(self, from_row: int, from_col: int, to_row: int, to_col: int, promotion_piece: Optional[PieceType] = None) -> 'Board':
        """Create a copy of the board with a move made."""
        new_board = deepcopy(self)
        new_board._apply_move_directly(from_row, from_col, to_row, to_col, promotion_piece)
        return new_board
    
    def needs_promotion(self, from_row: int, from_col: int, to_row: int) -> bool:
        """Check if a move requires pawn promotion."""
        piece = self.board[from_row][from_col]
        if piece is None or piece.type != PieceType.PAWN:
            return False
        # White pawns promote on row 0, black pawns promote on row 7
        return (piece.color == Color.WHITE and to_row == 0) or (piece.color == Color.BLACK and to_row == 7)
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int, promotion_piece: Optional[PieceType] = None) -> bool:
        """
        Make a move on the board. Returns True if move was made.
        
        Args:
            from_row: Source row
            from_col: Source column
            to_row: Destination row
            to_col: Destination column
            promotion_piece: Piece type for pawn promotion (defaults to Queen if None and promotion needed)
        """
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
        
        # Handle castling
        is_castling = False
        if piece.type == PieceType.KING and from_col == 4:  # King on e-file
            king_row = 7 if piece.color == Color.WHITE else 0
            if from_row == king_row:
                # Check if this is a castling move
                if to_col == 6:  # Kingside castling (O-O)
                    is_castling = True
                    # Move rook from h-file to f-file
                    rook = self.board[king_row][7]
                    self.board[king_row][5] = rook  # f-file
                    self.board[king_row][7] = None
                    if rook is not None:
                        rook.has_moved = True
                elif to_col == 2:  # Queenside castling (O-O-O)
                    is_castling = True
                    # Move rook from a-file to d-file
                    rook = self.board[king_row][0]
                    self.board[king_row][3] = rook  # d-file
                    self.board[king_row][0] = None
                    if rook is not None:
                        rook.has_moved = True
        
        # Handle en passant capture
        is_en_passant = False
        if piece.type == PieceType.PAWN and self.en_passant_target == (to_row, to_col):
            # This is an en passant capture
            is_en_passant = True
            # The captured pawn is one row behind the destination (in the opposite direction)
            direction = -1 if piece.color == Color.WHITE else 1
            captured_row = to_row - direction
            captured = self.board[captured_row][to_col]
            self.board[captured_row][to_col] = None  # Remove the captured pawn
        else:
            captured = self.board[to_row][to_col]
        
        # Handle pawn promotion
        if piece.type == PieceType.PAWN:
            if (piece.color == Color.WHITE and to_row == 0) or (piece.color == Color.BLACK and to_row == 7):
                # Promote pawn - default to Queen if not specified
                promotion = promotion_piece if promotion_piece else PieceType.QUEEN
                piece = Piece(promotion, piece.color)
                piece.has_moved = True
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        if not piece.has_moved:
            piece.has_moved = True
        
        # Set en_passant_target for double pawn moves, clear it otherwise
        new_en_passant_target = None
        if piece.type == PieceType.PAWN:
            # Check if this was a double pawn move
            direction = -1 if piece.color == Color.WHITE else 1
            start_row = 6 if piece.color == Color.WHITE else 1
            if from_row == start_row and to_row == from_row + 2 * direction:
                # Double pawn move - set en passant target to the square behind the pawn
                new_en_passant_target = (from_row + direction, from_col)
        
        self.en_passant_target = new_en_passant_target
        
        # Update castling rights
        # If king moves, lose both castling rights
        if piece.type == PieceType.KING:
            self.castling_rights[piece.color] = (False, False)
        # If rook moves from starting position, lose that side's castling right
        elif piece.type == PieceType.ROOK:
            if from_col == 7:  # Kingside rook
                kingside, queenside = self.castling_rights[piece.color]
                self.castling_rights[piece.color] = (False, queenside)
            elif from_col == 0:  # Queenside rook
                kingside, queenside = self.castling_rights[piece.color]
                self.castling_rights[piece.color] = (kingside, False)
        # If a rook is captured, lose that side's castling right
        if captured is not None and captured.type == PieceType.ROOK:
            kingside, queenside = self.castling_rights[captured.color]
            if to_col == 7:  # Kingside rook captured (h-file)
                self.castling_rights[captured.color] = (False, queenside)
            elif to_col == 0:  # Queenside rook captured (a-file)
                self.castling_rights[captured.color] = (kingside, False)
        
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
    
    def _is_square_under_attack(self, row: int, col: int, attacker_color: Color) -> bool:
        """Check if a square is under attack by the given color."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == attacker_color:
                    # Skip castling when checking for attacks to prevent recursion
                    moves = MoveGenerator.get_moves(self, r, c, skip_castling=True)
                    if (row, col) in moves:
                        return True
        return False
    
    def can_castle_kingside(self, color: Color) -> bool:
        """Check if kingside castling is legal."""
        if not self.castling_rights[color][0]:
            return False
        
        king_row = 7 if color == Color.WHITE else 0
        king = self.board[king_row][4]
        rook = self.board[king_row][7]
        
        if (not king or king.type != PieceType.KING or king.has_moved or
            not rook or rook.type != PieceType.ROOK or rook.has_moved or
            self.board[king_row][5] or self.board[king_row][6]):
            return False
        
        # King can't be in check, move through check, or into check
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return (not self._is_square_under_attack(king_row, 4, opponent) and  # King not in check
                not self._is_square_under_attack(king_row, 5, opponent) and  # f-file not attacked
                not self._is_square_under_attack(king_row, 6, opponent))     # g-file not attacked
    
    def can_castle_queenside(self, color: Color) -> bool:
        """Check if queenside castling is legal."""
        if not self.castling_rights[color][1]:
            return False
        
        king_row = 7 if color == Color.WHITE else 0
        king = self.board[king_row][4]
        rook = self.board[king_row][0]
        
        if (not king or king.type != PieceType.KING or king.has_moved or
            not rook or rook.type != PieceType.ROOK or rook.has_moved or
            self.board[king_row][1] or self.board[king_row][2] or self.board[king_row][3]):
            return False
        
        # King can't be in check, move through check, or into check
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return (not self._is_square_under_attack(king_row, 4, opponent) and  # King not in check
                not self._is_square_under_attack(king_row, 2, opponent) and  # c-file not attacked
                not self._is_square_under_attack(king_row, 3, opponent))     # d-file not attacked
    
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
                    # Skip castling when checking for check to prevent recursion
                    moves = MoveGenerator.get_moves(self, row, col, skip_castling=True)
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

