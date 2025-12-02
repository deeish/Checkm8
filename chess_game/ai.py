"""AI player using Minimax with Alpha-Beta Pruning."""

from typing import Optional, Tuple, List
from .board import Board
from .pieces import Color, PieceType
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
        Get the best move using improved Minimax with Alpha-Beta Pruning.
        Uses iterative deepening for better move selection at higher depths.
        
        Returns:
            Tuple of (from_row, from_col, to_row, to_col) or None if no moves available
        """
        self.nodes_evaluated = 0
        
        if board.current_turn != self.color:
            return None
        
        moves = board.get_all_moves(self.color)
        if not moves:
            return None
        
        # Use iterative deepening for depth >= 2
        if self.depth >= 2:
            return self._iterative_deepening(board, moves)
        else:
            return self._search_at_depth(board, moves, self.depth)
    
    def _iterative_deepening(self, board: Board, moves: List[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
        """Use iterative deepening to find best move efficiently."""
        best_move = None
        
        # Search at increasing depths (reuses previous best move as starting point)
        for current_depth in range(1, self.depth + 1):
            result = self._search_at_depth(board, moves, current_depth)
            if result is not None:
                best_move = result
                # Reorder moves to put best move first for next iteration
                if best_move in moves:
                    moves.remove(best_move)
                    moves.insert(0, best_move)
        
        return best_move
    
    def _search_at_depth(self, board: Board, moves: List[Tuple[int, int, int, int]], depth: int) -> Optional[Tuple[int, int, int, int]]:
        """Search for best move at a specific depth."""
        # Sort moves for better alpha-beta pruning (captures first, then others)
        # Only reorder if not already ordered from iterative deepening
        if depth == self.depth or len(moves) > 1:
            moves = self._order_moves(board, moves)
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in moves:
            from_row, from_col, to_row, to_col = move
            # AI always promotes to Queen (best choice)
            new_board = board.make_move_copy(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
            
            value = self._minimax(new_board, depth - 1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break  # Alpha-beta pruning
        
        return best_move
    
    def _order_moves(self, board: Board, moves: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Order moves to improve alpha-beta pruning efficiency.
        Prioritizes: captures, checks, center moves, then others.
        """
        def move_score(move):
            from_row, from_col, to_row, to_col = move
            score = 0
            
            # Check if it's a capture (highest priority)
            target = board.get_piece(to_row, to_col)
            if target is not None:
                # Higher value for capturing more valuable pieces
                score += 10000 + target.get_value()
            
            # Check if move gives check
            test_board = board.make_move_copy(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
            opponent_color = Color.BLACK if board.current_turn == Color.WHITE else Color.WHITE
            if test_board.is_in_check(opponent_color):
                score += 5000
            
            # Center control bonus
            center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
            if (to_row, to_col) in center_squares:
                score += 100
            
            return score
        
        # Sort by score (best moves first)
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
        
        # Order moves for better pruning (at top 2 levels for efficiency)
        if depth >= self.depth - 2:
            moves = self._order_moves(board, moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                from_row, from_col, to_row, to_col = move
                # AI always promotes to Queen
                new_board = board.make_move_copy(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
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
                # Opponent also promotes to Queen (assume best play)
                new_board = board.make_move_copy(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return min_eval
    
    def get_nodes_evaluated(self) -> int:
        """Get the number of nodes evaluated in the last search."""
        return self.nodes_evaluated

