"""Generates comprehensive post-game analysis reports."""

from typing import Dict, List, Tuple, Optional
from chess_game.pieces import Color, PieceType, Piece
from .game_tracker import GameTracker
from .evaluation_history import EvaluationHistory
from chess_game.board import Board


class ReportGenerator:
    """Generates detailed post-game analysis reports."""
    
    PIECE_NAMES = {
        PieceType.PAWN: "Pawn",
        PieceType.KNIGHT: "Knight",
        PieceType.BISHOP: "Bishop",
        PieceType.ROOK: "Rook",
        PieceType.QUEEN: "Queen",
        PieceType.KING: "King"
    }
    
    def __init__(self, tracker: GameTracker, eval_history: EvaluationHistory, board: Board):
        """Initialize the report generator."""
        self.tracker = tracker
        self.eval_history = eval_history
        self.board = board
    
    def generate_report(self, winner: Optional[Color] = None) -> Dict:
        """Generate a comprehensive post-game analysis report."""
        stats = self.tracker.get_statistics()
        eval_stats = self._get_evaluation_stats()
        
        report = {
            'game_result': self._get_game_result(winner),
            'statistics': stats,
            'evaluation': eval_stats,
            'material_analysis': self._get_material_analysis(),
            'performance_metrics': self._get_performance_metrics(),
            'key_moments': self._get_key_moments(),
            'summary': self._generate_summary(winner, stats, eval_stats)
        }
        
        return report
    
    def _get_game_result(self, winner: Optional[Color]) -> str:
        """Get game result description."""
        if winner is None:
            if self.board.is_stalemate(self.board.current_turn):
                return "Draw by Stalemate"
            return "Draw"
        elif winner == Color.WHITE:
            return "White Wins"
        else:
            return "Black Wins"
    
    def _get_evaluation_stats(self) -> Dict:
        """Get evaluation statistics."""
        white_best = self.eval_history.get_best_position_for(Color.WHITE)
        white_worst = self.eval_history.get_worst_position_for(Color.WHITE)
        black_best = self.eval_history.get_best_position_for(Color.BLACK)
        black_worst = self.eval_history.get_worst_position_for(Color.BLACK)
        
        return {
            'average_evaluation': self.eval_history.get_average_evaluation(),
            'min_evaluation': self.eval_history.min_eval,
            'max_evaluation': self.eval_history.max_eval,
            'white_best_position': {
                'move': white_best[0],
                'evaluation': white_best[1] / 100.0
            },
            'white_worst_position': {
                'move': white_worst[0],
                'evaluation': white_worst[1] / 100.0
            },
            'black_best_position': {
                'move': black_best[0],
                'evaluation': black_best[1] / 100.0
            },
            'black_worst_position': {
                'move': black_worst[0],
                'evaluation': black_worst[1] / 100.0
            },
            'trend': self.eval_history.get_evaluation_trend()
        }
    
    def _get_material_analysis(self) -> Dict:
        """Get material capture analysis."""
        white_captured = self.tracker.material_captured[Color.WHITE]
        black_captured = self.tracker.material_captured[Color.BLACK]
        
        white_details = {self.PIECE_NAMES[pt]: count for pt, count in white_captured.items()}
        black_details = {self.PIECE_NAMES[pt]: count for pt, count in black_captured.items()}
        
        return {
            'white_captures': white_details,
            'black_captures': black_details,
            'white_total_value': self.tracker.get_total_material_captured(Color.WHITE),
            'black_total_value': self.tracker.get_total_material_captured(Color.BLACK),
            'white_capture_count': self.tracker.get_capture_count(Color.WHITE),
            'black_capture_count': self.tracker.get_capture_count(Color.BLACK),
            'material_advantage': self.tracker.get_total_material_captured(Color.WHITE) - \
                                 self.tracker.get_total_material_captured(Color.BLACK)
        }
    
    def _get_performance_metrics(self) -> Dict:
        """Get performance metrics for both players."""
        stats = self.tracker.get_statistics()
        
        return {
            'white': {
                'moves': stats['white_moves'],
                'avg_move_time': stats['white_avg_move_time'],
                'total_time': sum(t for c, t in stats['move_times'] if c == Color.WHITE),
                'captures': stats['white_capture_count'],
                'material_captured': stats['white_material_captured']
            },
            'black': {
                'moves': stats['black_moves'],
                'avg_move_time': stats['black_avg_move_time'],
                'total_time': sum(t for c, t in stats['move_times'] if c == Color.BLACK),
                'captures': stats['black_capture_count'],
                'material_captured': stats['black_material_captured']
            }
        }
    
    def _get_key_moments(self) -> List[Dict]:
        """Identify key moments in the game."""
        moments = []
        
        # Significant captures
        for color, piece_type, move_num in self.tracker.captures:
            piece_value = Piece.VALUES[piece_type]
            if piece_value >= 500:  # Rook, Queen, or King
                moments.append({
                    'move': move_num,
                    'type': 'capture',
                    'description': f"{'White' if color == Color.WHITE else 'Black'} captured {self.PIECE_NAMES[piece_type]}",
                    'importance': 'high' if piece_value >= 900 else 'medium'
                })
        
        # Significant evaluation swings
        history = self.eval_history.get_history()
        for i in range(1, len(history)):
            prev_eval = history[i-1][1]
            curr_eval = history[i][1]
            swing = abs(curr_eval - prev_eval)
            
            if swing > 500:  # Significant swing
                moments.append({
                    'move': history[i][0],
                    'type': 'evaluation_swing',
                    'description': f"Evaluation swing: {prev_eval/100:.1f} to {curr_eval/100:.1f}",
                    'importance': 'high' if swing > 1000 else 'medium'
                })
        
        # Sort by move number
        moments.sort(key=lambda x: x['move'])
        return moments[:10]  # Return top 10 key moments
    
    def _generate_summary(self, winner: Optional[Color], stats: Dict, eval_stats: Dict) -> str:
        """Generate a text summary of the game."""
        lines = []
        
        # Game result
        result = self._get_game_result(winner)
        lines.append(f"Game Result: {result}")
        lines.append("")
        
        # Game length
        lines.append(f"Game Duration: {stats['duration_formatted']}")
        lines.append(f"Total Moves: {stats['total_moves']} ({stats['white_moves']} White, {stats['black_moves']} Black)")
        lines.append("")
        
        # Material
        mat_adv = stats['white_material_captured'] - stats['black_material_captured']
        if mat_adv > 0:
            lines.append(f"Material Advantage: White (+{mat_adv} points)")
        elif mat_adv < 0:
            lines.append(f"Material Advantage: Black (+{abs(mat_adv)} points)")
        else:
            lines.append("Material: Even")
        lines.append("")
        
        # Evaluation trend
        lines.append(f"Evaluation Trend: {eval_stats['trend']}")
        lines.append(f"Average Evaluation: {eval_stats['average_evaluation']/100:.2f}")
        lines.append("")
        
        # Performance
        perf = self._get_performance_metrics()
        lines.append(f"White Average Move Time: {perf['white']['avg_move_time']:.2f}s")
        lines.append(f"Black Average Move Time: {perf['black']['avg_move_time']:.2f}s")
        
        return "\n".join(lines)

