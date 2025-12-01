"""AI player using Minimax with Alpha-Beta Pruning."""

from typing import Optional, Tuple
from .board import Board
from .pieces import Color
from .evaluator import Evaluator


class ChessAI:
    """Chess AI using Minimax algorithm with Alpha-Beta Pruning."""
    
    def __init__(self, depth: int = 3, color: Color = Color.BLACK):
        """
        Initialize the AI.
        
        Args:
            depth: Search depth (3-5 recommended)
            color: Color the AI plays as
        """
        self.depth = depth
        self.color = color
        self.evaluator = Evaluator()
        self.nodes_evaluated = 0
    
    def get_best_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the best move using Minimax with Alpha-Beta Pruning.
        
        Returns:
            Tuple of (from_row, from_col, to_row, to_col) or None if no moves available
        """
        self.nodes_evaluated = 0
        
        if board.current_turn != self.color:
            return None
        
        moves = board.get_all_moves(self.color)
        if not moves:
            return None
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in moves:
            from_row, from_col, to_row, to_col = move
            new_board = board.make_move_copy(from_row, from_col, to_row, to_col)
            
            value = self._minimax(new_board, self.depth - 1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break  # Alpha-beta pruning
        
        return best_move
    
    def _minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool
    ) -> float:
        """
        Minimax algorithm with Alpha-Beta Pruning.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Best value for maximizing player
            beta: Best value for minimizing player
            maximizing: True if maximizing (AI's turn), False if minimizing (opponent's turn)
        
        Returns:
            Evaluation score
        """
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if depth == 0:
            return self.evaluator.evaluate(board, self.color)
        
        current_color = self.color if maximizing else (Color.BLACK if self.color == Color.WHITE else Color.WHITE)
        moves = board.get_all_moves(current_color)
        
        # Check for checkmate or stalemate
        if not moves:
            if board.is_in_check(current_color):
                # Checkmate
                return float('-inf') if maximizing else float('inf')
            else:
                # Stalemate
                return 0
        
        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                from_row, from_col, to_row, to_col = move
                new_board = board.make_move_copy(from_row, from_col, to_row, to_col)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                from_row, from_col, to_row, to_col = move
                new_board = board.make_move_copy(from_row, from_col, to_row, to_col)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return min_eval
    
    def get_nodes_evaluated(self) -> int:
        """Get the number of nodes evaluated in the last search."""
        return self.nodes_evaluated

