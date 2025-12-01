"""Performance tests for move generation and AI speed."""

import pytest
import time
import statistics
from chess_game.board import Board
from chess_game.ai import ChessAI
from chess_game.pieces import Color


def test_move_generation_speed():
    """Test that move generation is fast."""
    board = Board()
    
    start_time = time.time()
    moves = board.get_all_moves(Color.WHITE)
    elapsed = time.time() - start_time
    
    assert len(moves) > 0
    assert elapsed < 0.1  # Should be very fast


def test_ai_move_timing():
    """Test AI move timing at different depths."""
    board = Board()
    board.make_move(6, 4, 4, 4)  # e2-e4
    
    times = []
    for depth in [2, 3]:
        ai = ChessAI(depth=depth, color=Color.BLACK)
        start_time = time.time()
        move = ai.get_best_move(board)
        elapsed = time.time() - start_time
        times.append(elapsed)
        assert move is not None
    
    # Depth 3 should take longer than depth 2
    assert times[1] > times[0]


def test_ai_depth_3_performance():
    """Test that AI at depth 3 completes moves in reasonable time."""
    board = Board()
    board.make_move(6, 4, 4, 4)  # e2-e4
    
    ai = ChessAI(depth=3, color=Color.BLACK)
    
    times = []
    for _ in range(5):
        start_time = time.time()
        move = ai.get_best_move(board)
        elapsed = time.time() - start_time
        times.append(elapsed)
        assert move is not None
    
    # Average should be under 2 seconds (target is <= 1 second, but allow some margin)
    avg_time = statistics.mean(times)
    assert avg_time < 2.0, f"Average time {avg_time:.2f}s exceeds target"


def test_multiple_positions_timing():
    """Test AI performance on multiple positions."""
    positions = [
        # Position 1: After e4
        lambda: (Board(), lambda b: b.make_move(6, 4, 4, 4)),
        # Position 2: After e4 e5
        lambda: (Board(), lambda b: (b.make_move(6, 4, 4, 4), b.make_move(1, 4, 3, 4))),
        # Position 3: After e4 e5 Nf3
        lambda: (Board(), lambda b: (
            b.make_move(6, 4, 4, 4),
            b.make_move(1, 4, 3, 4),
            b.make_move(7, 6, 5, 5)
        )),
    ]
    
    times = []
    for pos_setup in positions:
        board, setup_func = pos_setup()
        setup_func(board)
        
        ai = ChessAI(depth=3, color=board.current_turn)
        start_time = time.time()
        move = ai.get_best_move(board)
        elapsed = time.time() - start_time
        times.append(elapsed)
        assert move is not None
    
    # All moves should complete in reasonable time
    assert all(t < 5.0 for t in times)

