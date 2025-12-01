"""AI player using Minimax with Alpha-Beta Pruning."""

from typing import Optional, Tuple, List
from .board import Board
from .pieces import Color
from .evaluator import Evaluator


class ChessAI:
    """Chess AI using Minimax algorithm with Alpha-Beta Pruning."""
    
    def __init__(self, depth: int = 1, color: Color = Color.BLACK):
        """
        Initialize the AI.
        
        Args:
            depth: Search depth (1 for very fast ~0.1s, 2 for fast ~0.5s, 3+ for stronger)
            color: Color the AI plays as
        """
        self.depth = max(1, depth)  # Minimum depth 1
        self.color = color
        self.evaluator = Evaluator()
        self.nodes_evaluated = 0
    
    def get_best_move(self, board: Board) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the best move using Minimax with Alpha-Beta Pruning and move ordering.
        
        Returns:
            Tuple of (from_row, from_col, to_row, to_col) or None if no moves available
        """
        self.nodes_evaluated = 0
        
        if board.current_turn != self.color:
            return None
        
        moves = board.get_all_moves(self.color)
        if not moves:
            return None
        
        # Sort moves for better alpha-beta pruning (captures first, then others)
        moves = self._order_moves(board, moves)
        
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
    
    def _order_moves(self, board: Board, moves: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Order moves to improve alpha-beta pruning efficiency (captures first)."""
        def move_score(move):
            from_row, from_col, to_row, to_col = move
            # Check if it's a capture
            target = board.get_piece(to_row, to_col)
            if target is not None:
                # Higher value for capturing more valuable pieces
                return 1000 + target.get_value()
            return 0
        
        # Sort by score (captures first)
        return sorted(moves, key=move_score, reverse=True)
    
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
            # Fast evaluation at leaf nodes
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
        
        # Order moves for better pruning (only at very top level to save time)
        if depth == self.depth - 1:
            moves = self._order_moves(board, moves)
        
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

