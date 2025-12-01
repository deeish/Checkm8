"""Heuristic evaluation function for chess positions."""

from typing import List, Tuple
from .board import Board
from .pieces import Color, PieceType, Piece, MoveGenerator


class Evaluator:
    """Evaluates chess positions using heuristics."""
    
    # Piece values
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    # Center control bonuses
    CENTER_SQUARES = [(3, 3), (3, 4), (4, 3), (4, 4)]
    EXTENDED_CENTER = [(2, 2), (2, 3), (2, 4), (2, 5),
                       (3, 2), (3, 5), (4, 2), (4, 5),
                       (5, 2), (5, 3), (5, 4), (5, 5)]
    
    def evaluate(self, board: Board, color: Color) -> int:
        """
        Evaluate the position from the perspective of the given color.
        Returns a score where positive is good for the color.
        """
        score = 0
        
        # Material balance
        score += self._material_balance(board, color)
        
        # Piece mobility
        score += self._piece_mobility(board, color) * 2
        
        # Center control
        score += self._center_control(board, color) * 3
        
        # King safety
        score += self._king_safety(board, color) * 5
        
        return score
    
    def _material_balance(self, board: Board, color: Color) -> int:
        """Calculate material balance."""
        own_material = 0
        opponent_material = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece is not None:
                    value = self.PIECE_VALUES[piece.type]
                    if piece.color == color:
                        own_material += value
                    else:
                        opponent_material += value
        
        return own_material - opponent_material
    
    def _piece_mobility(self, board: Board, color: Color) -> int:
        """Calculate piece mobility (number of legal moves)."""
        own_moves = len(board.get_all_moves(color))
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        opponent_moves = len(board.get_all_moves(opponent_color))
        
        return own_moves - opponent_moves
    
    def _center_control(self, board: Board, color: Color) -> int:
        """Calculate center control."""
        score = 0
        
        # Check center squares
        for row, col in self.CENTER_SQUARES:
            piece = board.board[row][col]
            if piece is not None and piece.color == color:
                score += 2
        
        # Check extended center
        for row, col in self.EXTENDED_CENTER:
            piece = board.board[row][col]
            if piece is not None and piece.color == color:
                score += 1
        
        # Check if pieces can attack center
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece is not None and piece.color == color:
                    piece_moves = MoveGenerator.get_moves(board, row, col)
                    for to_row, to_col in piece_moves:
                        if (to_row, to_col) in self.CENTER_SQUARES:
                            score += 1
                            break
        
        return score
    
    def _king_safety(self, board: Board, color: Color) -> int:
        """Calculate king safety."""
        king_pos = board.find_king(color)
        if king_pos is None:
            return -1000  # King missing is very bad
        
        king_row, king_col = king_pos
        safety_score = 0
        
        # Check if king is in check
        if board.is_in_check(color):
            safety_score -= 50
        
        # Count friendly pieces around king
        friendly_pieces = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = king_row + dr, king_col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.board[new_row][new_col]
                    if piece is not None and piece.color == color:
                        friendly_pieces += 1
        
        safety_score += friendly_pieces * 5
        
        # Penalize king being too far forward in opening
        if color == Color.WHITE and king_row < 4:
            safety_score -= 10
        elif color == Color.BLACK and king_row > 3:
            safety_score -= 10
        
        return safety_score

