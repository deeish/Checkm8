"""Tracks game statistics during gameplay."""

import time
from typing import List, Tuple, Optional, Dict
from chess_game.board import Board
from chess_game.pieces import Color, PieceType, Piece


class GameTracker:
    """Tracks comprehensive game statistics."""
    
    def __init__(self):
        """Initialize the game tracker."""
        self.start_time = time.time()
        self.move_times: List[Tuple[Color, float]] = []  # (color, time_taken)
        self.evaluations: List[Tuple[int, Color]] = []  # (evaluation, color_to_move)
        self.material_captured: Dict[Color, Dict[PieceType, int]] = {
            Color.WHITE: {},
            Color.BLACK: {}
        }
        self.total_moves = 0
        self.white_moves = 0
        self.black_moves = 0
        self.last_move_time = time.time()
        self.captures: List[Tuple[Color, PieceType, int]] = []  # (capturing_color, piece_type, move_number)
        
    def record_move(self, board: Board, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                   captured: Optional[Piece], color: Color, evaluation: int):
        """Record a move with all relevant statistics."""
        current_time = time.time()
        move_time = current_time - self.last_move_time
        self.last_move_time = current_time
        
        self.move_times.append((color, move_time))
        self.evaluations.append((evaluation, color))
        self.total_moves += 1
        
        if color == Color.WHITE:
            self.white_moves += 1
        else:
            self.black_moves += 1
        
        # Track captures
        if captured is not None:
            piece_type = captured.type
            if piece_type not in self.material_captured[color]:
                self.material_captured[color][piece_type] = 0
            self.material_captured[color][piece_type] += 1
            self.captures.append((color, piece_type, self.total_moves))
    
    def get_game_duration(self) -> float:
        """Get total game duration in seconds."""
        return time.time() - self.start_time
    
    def get_average_move_time(self, color: Optional[Color] = None) -> float:
        """Get average move time for a color or overall."""
        if not self.move_times:
            return 0.0
        
        if color is None:
            times = [t for _, t in self.move_times]
        else:
            times = [t for c, t in self.move_times if c == color]
        
        return sum(times) / len(times) if times else 0.0
    
    def get_total_material_captured(self, color: Color) -> int:
        """Get total material value captured by a color."""
        total = 0
        piece_values = Piece.VALUES
        
        for piece_type, count in self.material_captured[color].items():
            total += piece_values[piece_type] * count
        
        return total
    
    def get_capture_count(self, color: Color) -> int:
        """Get number of pieces captured by a color."""
        return sum(self.material_captured[color].values())
    
    def get_statistics(self) -> Dict:
        """Get comprehensive game statistics."""
        duration = self.get_game_duration()
        
        return {
            'total_moves': self.total_moves,
            'white_moves': self.white_moves,
            'black_moves': self.black_moves,
            'duration_seconds': duration,
            'duration_formatted': self._format_duration(duration),
            'average_move_time': self.get_average_move_time(),
            'white_avg_move_time': self.get_average_move_time(Color.WHITE),
            'black_avg_move_time': self.get_average_move_time(Color.BLACK),
            'white_material_captured': self.get_total_material_captured(Color.WHITE),
            'black_material_captured': self.get_total_material_captured(Color.BLACK),
            'white_capture_count': self.get_capture_count(Color.WHITE),
            'black_capture_count': self.get_capture_count(Color.BLACK),
            'captures': self.captures.copy(),
            'move_times': self.move_times.copy()
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

