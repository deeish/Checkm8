"""Tests for board and move generation."""

import pytest
from chess_game.board import Board
from chess_game.pieces import Color, PieceType


def test_board_initialization():
    """Test that board initializes correctly."""
    board = Board()
    
    # Check that pieces are in correct starting positions
    assert board.get_piece(0, 0).type == PieceType.ROOK
    assert board.get_piece(0, 0).color == Color.BLACK
    assert board.get_piece(7, 0).type == PieceType.ROOK
    assert board.get_piece(7, 0).color == Color.WHITE
    
    assert board.get_piece(1, 0).type == PieceType.PAWN
    assert board.get_piece(6, 0).type == PieceType.PAWN
    
    assert board.current_turn == Color.WHITE


def test_pawn_moves():
    """Test pawn move generation."""
    board = Board()
    
    # White pawn should be able to move forward
    moves = board.get_all_moves(Color.WHITE)
    pawn_moves = [m for m in moves if m[0] == 6]  # From rank 6 (white pawns)
    
    assert len(pawn_moves) > 0
    # Each pawn should have at least 1 move (forward)
    assert any(m[2] == 5 for m in pawn_moves)  # Moving to rank 5


def test_move_validation():
    """Test that moves are validated correctly."""
    board = Board()
    
    # Try to make a legal move
    assert board.make_move(6, 4, 4, 4)  # White pawn e2-e4
    
    # Try to make an illegal move (wrong turn)
    board2 = Board()
    assert not board2.make_move(1, 4, 3, 4)  # Black can't move on white's turn


def test_check_detection():
    """Test check detection."""
    board = Board()
    
    # Starting position should not be in check
    assert not board.is_in_check(Color.WHITE)
    assert not board.is_in_check(Color.BLACK)


def test_legal_moves_count():
    """Test that we get reasonable number of legal moves."""
    board = Board()
    
    # Starting position should have 20 legal moves for white
    moves = board.get_all_moves(Color.WHITE)
    assert len(moves) == 20  # Standard chess opening has 20 legal moves


def test_king_finding():
    """Test finding the king."""
    board = Board()
    
    white_king = board.find_king(Color.WHITE)
    assert white_king == (7, 4)
    
    black_king = board.find_king(Color.BLACK)
    assert black_king == (0, 4)

