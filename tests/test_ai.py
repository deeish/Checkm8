"""Tests for AI and evaluation."""

import pytest
import time
from chess_game.board import Board
from chess_game.ai import ChessAI
from chess_game.pieces import Color
from chess_game.evaluator import Evaluator


def test_ai_initialization():
    """Test AI initialization."""
    ai = ChessAI(depth=3, color=Color.BLACK)
    assert ai.depth == 3
    assert ai.color == Color.BLACK


def test_ai_finds_move():
    """Test that AI can find a move."""
    board = Board()
    ai = ChessAI(depth=2, color=Color.BLACK)
    
    # Make a move so it's black's turn
    board.make_move(6, 4, 4, 4)  # e2-e4
    
    move = ai.get_best_move(board)
    assert move is not None
    assert len(move) == 4


def test_ai_move_time():
    """Test that AI moves are reasonably fast."""
    board = Board()
    ai = ChessAI(depth=3, color=Color.BLACK)
    
    # Make a move so it's black's turn
    board.make_move(6, 4, 4, 4)  # e2-e4
    
    start_time = time.time()
    move = ai.get_best_move(board)
    elapsed = time.time() - start_time
    
    assert move is not None
    assert elapsed < 5.0  # Should be fast at depth 3


def test_evaluator():
    """Test the evaluation function."""
    board = Board()
    evaluator = Evaluator()
    
    # Evaluate starting position
    score = evaluator.evaluate(board, Color.WHITE)
    assert isinstance(score, (int, float))
    
    # Score should be close to 0 for starting position
    assert abs(score) < 100


def test_evaluator_material():
    """Test material evaluation."""
    board = Board()
    evaluator = Evaluator()
    
    # Starting position should have equal material
    material = evaluator._material_balance(board, Color.WHITE)
    assert abs(material) < 10  # Should be very close to 0


def test_ai_depth_impact():
    """Test that deeper search produces different results (usually better)."""
    board = Board()
    board.make_move(6, 4, 4, 4)  # e2-e4
    
    ai_shallow = ChessAI(depth=1, color=Color.BLACK)
    ai_deep = ChessAI(depth=3, color=Color.BLACK)
    
    move_shallow = ai_shallow.get_best_move(board)
    move_deep = ai_deep.get_best_move(board)
    
    # Both should find moves
    assert move_shallow is not None
    assert move_deep is not None
    
    # Deeper search should evaluate more nodes
    assert ai_deep.get_nodes_evaluated() > ai_shallow.get_nodes_evaluated()

