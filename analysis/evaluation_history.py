"""Tracks evaluation history throughout the game."""

from typing import List, Tuple
from chess_game.pieces import Color


class EvaluationHistory:
    """Tracks position evaluations over time."""
    
    def __init__(self):
        """Initialize evaluation history."""
        self.history: List[Tuple[int, int, Color]] = []  # (move_number, evaluation, color_to_move)
        self.min_eval = 0
        self.max_eval = 0
    
    def add_evaluation(self, move_number: int, evaluation: int, color: Color):
        """Add an evaluation to the history."""
        # Evaluation is from White's perspective
        self.history.append((move_number, evaluation, color))
        
        if not self.history:
            self.min_eval = self.max_eval = evaluation
        else:
            self.min_eval = min(self.min_eval, evaluation)
            self.max_eval = max(self.max_eval, evaluation)
    
    def get_evaluation_range(self) -> Tuple[int, int]:
        """Get the min and max evaluation values."""
        if not self.history:
            return (0, 0)
        return (self.min_eval, self.max_eval)
    
    def get_average_evaluation(self) -> float:
        """Get average evaluation throughout the game."""
        if not self.history:
            return 0.0
        return sum(eval_val for _, eval_val, _ in self.history) / len(self.history)
    
    def get_evaluation_at_move(self, move_number: int) -> int:
        """Get evaluation at a specific move number."""
        for move, eval_val, _ in self.history:
            if move == move_number:
                return eval_val
        return 0
    
    def get_best_position_for(self, color: Color) -> Tuple[int, int]:
        """Get the move number and evaluation of the best position for a color."""
        if not self.history:
            return (0, 0)
        
        if color == Color.WHITE:
            # Higher is better for White
            best = max(self.history, key=lambda x: x[1])
        else:
            # Lower is better for Black (negative is good)
            best = min(self.history, key=lambda x: x[1])
        
        return (best[0], best[1])
    
    def get_worst_position_for(self, color: Color) -> Tuple[int, int]:
        """Get the move number and evaluation of the worst position for a color."""
        if not self.history:
            return (0, 0)
        
        if color == Color.WHITE:
            # Lower is worse for White
            worst = min(self.history, key=lambda x: x[1])
        else:
            # Higher is worse for Black
            worst = max(self.history, key=lambda x: x[1])
        
        return (worst[0], worst[1])
    
    def get_history(self) -> List[Tuple[int, int, Color]]:
        """Get the full evaluation history."""
        return self.history.copy()
    
    def get_evaluation_trend(self) -> str:
        """Get a simple trend description of the evaluation."""
        if len(self.history) < 2:
            return "Insufficient data"
        
        # Compare first and last evaluations
        first_eval = self.history[0][1]
        last_eval = self.history[-1][1]
        
        diff = last_eval - first_eval
        
        if diff > 200:
            return "White gained significant advantage"
        elif diff > 50:
            return "White gained advantage"
        elif diff < -200:
            return "Black gained significant advantage"
        elif diff < -50:
            return "Black gained advantage"
        else:
            return "Position remained relatively balanced"

