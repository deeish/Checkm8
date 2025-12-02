"""GUI for the chess game using tkinter."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple

from .board import Board
from .pieces import Color, PieceType
from .ai import ChessAI


class ChessGUI:
    """Graphical user interface for the chess game."""
    
    SQUARE_SIZE = 60
    BOARD_COLORS = {
        'light': '#F0D9B5',
        'dark': '#B58863',
        'highlight': '#F7F769',
        'selected': '#769656'
    }
    
    PIECE_SYMBOLS = {
        (Color.WHITE, PieceType.PAWN): '♙',
        (Color.WHITE, PieceType.ROOK): '♖',
        (Color.WHITE, PieceType.KNIGHT): '♘',
        (Color.WHITE, PieceType.BISHOP): '♗',
        (Color.WHITE, PieceType.QUEEN): '♕',
        (Color.WHITE, PieceType.KING): '♔',
        (Color.BLACK, PieceType.PAWN): '♟',
        (Color.BLACK, PieceType.ROOK): '♜',
        (Color.BLACK, PieceType.KNIGHT): '♞',
        (Color.BLACK, PieceType.BISHOP): '♝',
        (Color.BLACK, PieceType.QUEEN): '♛',
        (Color.BLACK, PieceType.KING): '♚'
    }
    
    def __init__(self, ai_depth: int = 3):
        """Initialize the GUI."""
        self.board = Board()
        self.ai = ChessAI(depth=ai_depth, color=Color.BLACK)
        self.selected_square: Optional[Tuple[int, int]] = None
        self.valid_moves: list = []
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("CheckM8 - Chess Game")
        self.root.resizable(False, False)
        
        # Create canvas
        board_size = 8 * self.SQUARE_SIZE
        self.canvas = tk.Canvas(
            self.root,
            width=board_size,
            height=board_size + 40,
            bg='white'
        )
        self.canvas.pack()
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="White to move",
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack()
        
        # Bind canvas click
        self.canvas.bind("<Button-1>", self.on_square_click)
        
        # Draw initial board
        self.draw_board()
        
        # Start AI move if it's AI's turn
        if self.board.current_turn == self.ai.color:
            self.root.after(100, self.make_ai_move)
    
    def draw_board(self):
        """Draw the chess board and pieces."""
        self.canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE
                y1 = row * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.BOARD_COLORS['light'] if is_light else self.BOARD_COLORS['dark']
                
                # Highlight selected square
                if self.selected_square == (row, col):
                    color = self.BOARD_COLORS['selected']
                
                # Highlight valid moves
                if (row, col) in self.valid_moves:
                    color = self.BOARD_COLORS['highlight']
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')
                
                # Draw piece
                piece = self.board.get_piece(row, col)
                if piece is not None:
                    symbol = self.PIECE_SYMBOLS.get((piece.color, piece.type), '?')
                    center_x = x1 + self.SQUARE_SIZE // 2
                    center_y = y1 + self.SQUARE_SIZE // 2
                    self.canvas.create_text(
                        center_x,
                        center_y,
                        text=symbol,
                        font=('Arial', 36),
                        fill='black' if piece.color == Color.BLACK else 'white'
                    )
        
        # Draw coordinates
        for i in range(8):
            # Files (a-h)
            self.canvas.create_text(
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                8 * self.SQUARE_SIZE + 15,
                text=chr(97 + i),
                font=('Arial', 10)
            )
            # Ranks (1-8)
            self.canvas.create_text(
                8 * self.SQUARE_SIZE - 5,
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                text=str(8 - i),
                font=('Arial', 10)
            )
    
    def on_square_click(self, event):
        """Handle square click events."""
        if self.board.current_turn == self.ai.color:
            return  # Not player's turn
        
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        piece = self.board.get_piece(row, col)
        
        # If a square is already selected
        if self.selected_square is not None:
            from_row, from_col = self.selected_square
            
            # If clicking on a valid move square, make the move
            if (row, col) in self.valid_moves:
                # Check if promotion is needed
                promotion_piece = None
                if self.board.needs_promotion(from_row, from_col, row):
                    promotion_piece = self.show_promotion_dialog()
                    if promotion_piece is None:
                        promotion_piece = PieceType.QUEEN  # Default to Queen
                
                if self.board.make_move(from_row, from_col, row, col, promotion_piece):
                    self.selected_square = None
                    self.valid_moves = []
                    self.draw_board()
                    self.update_status()
                    self.check_game_over()
                    
                    # Make AI move
                    if self.board.current_turn == self.ai.color:
                        self.root.after(100, self.make_ai_move)
                else:
                    self.selected_square = None
                    self.valid_moves = []
            else:
                # Deselect or select new piece
                self.selected_square = None
                self.valid_moves = []
                if piece is not None and piece.color == self.board.current_turn:
                    self.selected_square = (row, col)
                    self.valid_moves = [
                        (to_row, to_col)
                        for from_row, from_col, to_row, to_col in self.board.get_all_moves(piece.color)
                        if from_row == row and from_col == col
                    ]
        else:
            # Select a piece
            if piece is not None and piece.color == self.board.current_turn:
                self.selected_square = (row, col)
                self.valid_moves = [
                    (to_row, to_col)
                    for from_row, from_col, to_row, to_col in self.board.get_all_moves(piece.color)
                    if from_row == row and from_col == col
                ]
        
        self.draw_board()
    
    def make_ai_move(self):
        """Make the AI's move."""
        if self.board.current_turn != self.ai.color:
            return
        
        move = self.ai.get_best_move(self.board)
        if move is not None:
            from_row, from_col, to_row, to_col = move
            # AI always promotes to Queen
            self.board.make_move(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
            self.draw_board()
            self.update_status()
            self.check_game_over()
        else:
            # No moves available
            self.check_game_over()
    
    def update_status(self):
        """Update the status label."""
        if self.board.is_checkmate(self.board.current_turn):
            winner = "Black" if self.board.current_turn == Color.WHITE else "White"
            self.status_label.config(text=f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate(self.board.current_turn):
            self.status_label.config(text="Stalemate! Game is a draw.")
        elif self.board.is_in_check(self.board.current_turn):
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            self.status_label.config(text=f"{turn} to move (Check!)")
        else:
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            self.status_label.config(text=f"{turn} to move")
    
    def show_promotion_dialog(self) -> Optional[PieceType]:
        """Show a dialog to select promotion piece. Returns the selected piece type or None."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pawn Promotion")
        dialog.geometry("380x160")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (380 // 2)
        y = (dialog.winfo_screenheight() // 2) - (160 // 2)
        dialog.geometry(f"380x160+{x}+{y}")
        
        label = tk.Label(dialog, text="Choose a piece to promote to:", font=('Arial', 12))
        label.pack(pady=10)
        
        selected_piece = [None]  # Use list to allow modification in nested function
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        pieces = [
            (PieceType.QUEEN, '♕', 'Queen'),
            (PieceType.ROOK, '♖', 'Rook'),
            (PieceType.BISHOP, '♗', 'Bishop'),
            (PieceType.KNIGHT, '♘', 'Knight')
        ]
        
        for piece_type, symbol, name in pieces:
            btn = tk.Button(
                button_frame,
                text=f"{symbol}\n{name}",
                font=('Arial', 14),
                width=7,
                height=2,
                command=lambda pt=piece_type: self._select_promotion(dialog, selected_piece, pt)
            )
            btn.pack(side=tk.LEFT, padx=6)
        
        dialog.wait_window()
        return selected_piece[0]
    
    def _select_promotion(self, dialog, selected_piece, piece_type):
        """Handle promotion piece selection."""
        selected_piece[0] = piece_type
        dialog.destroy()
    
    def check_game_over(self):
        """Check if the game is over and show message."""
        if self.board.is_checkmate(Color.WHITE):
            messagebox.showinfo("Game Over", "Checkmate! Black wins!")
        elif self.board.is_checkmate(Color.BLACK):
            messagebox.showinfo("Game Over", "Checkmate! White wins!")
        elif self.board.is_stalemate(self.board.current_turn):
            messagebox.showinfo("Game Over", "Stalemate! Game is a draw.")
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CheckM8 Chess Game')
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='AI search depth (default: 3)'
    )
    
    args = parser.parse_args()
    
    app = ChessGUI(ai_depth=args.depth)
    app.run()


if __name__ == '__main__':
    main()

