"""GUI for the chess game using tkinter."""

import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Optional, Tuple
import sys
import os

from .board import Board
from .pieces import Color, PieceType
from .ai import ChessAI

# Import analysis modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
try:
    from analysis import GameTracker, EvaluationHistory, ReportGenerator
    print("Analysis modules loaded successfully")
except ImportError as e:
    print(f"Warning: Analysis modules not available: {e}")
    GameTracker = None
    EvaluationHistory = None
    ReportGenerator = None


class ChessGUI:
    """Graphical user interface for the chess game."""
    
    SQUARE_SIZE = 70  # Larger squares for better visibility
    BOARD_COLORS = {
        'light': '#E8D5B7',  # Slightly darker light square
        'dark': '#9D6B47',   # Darker dark square
        'highlight': '#F7F769',  # Yellow highlight for valid moves
        'selected': '#6B8E5A'   # Darker green for selected piece
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
        
        # Initialize game analysis tracking
        if GameTracker is not None:
            self.game_tracker = GameTracker()
            self.eval_history = EvaluationHistory()
            self.eval_history.add_evaluation(0, self.ai.evaluator.evaluate(self.board, Color.WHITE), Color.WHITE)
            self.move_number = 0
        else:
            self.game_tracker = None
            self.eval_history = None
        
        # Game over state
        self.game_over = False
        self.game_winner: Optional[Color] = None
        
        # Create main window with better styling
        self.root = tk.Tk()
        self.root.title("CheckM8 - Chess Game")
        self.root.resizable(False, False)
        self.root.configure(bg='#1e1e1e')  # Darker background
        
        # Create canvas with better styling (darker)
        board_size = 8 * self.SQUARE_SIZE
        self.canvas = tk.Canvas(
            self.root,
            width=board_size + 40,  # Add padding for coordinates
            height=board_size + 80,  # Add space for status and button
            bg='#1e1e1e',  # Darker background
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Status label with better styling
        self.status_label = tk.Label(
            self.root,
            text="White to move",
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff',
            pady=5
        )
        self.status_label.pack()
        
        # Analysis button (initially hidden) with better styling
        self.analysis_button = tk.Button(
            self.root,
            text="View Analysis",
            font=('Arial', 12, 'bold'),
            bg='#3C7ED9',
            fg='white',
            activebackground='#2d5fa3',
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.show_analysis_window,
            state='disabled'
        )
        # Don't pack it yet - only show after game ends
        # self.analysis_button.pack(pady=5)  # Will be packed when game ends
        
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
        
        # Draw board background/border (darker)
        board_offset = 20
        self.canvas.create_rectangle(
            board_offset - 2, board_offset - 2,
            8 * self.SQUARE_SIZE + board_offset + 2, 8 * self.SQUARE_SIZE + board_offset + 2,
            fill='#151515', outline='#333333', width=3
        )
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE + board_offset
                y1 = row * self.SQUARE_SIZE + board_offset
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
                
                # Draw square with subtle border
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='', width=0)
                # Add subtle border for definition
                if is_light:
                    border_color = '#d4c4a0'
                else:
                    border_color = '#8b6f47'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=border_color, width=1)
                
                # Draw piece with better styling
                piece = self.board.get_piece(row, col)
                if piece is not None:
                    symbol = self.PIECE_SYMBOLS.get((piece.color, piece.type), '?')
                    center_x = x1 + self.SQUARE_SIZE // 2
                    center_y = y1 + self.SQUARE_SIZE // 2
                    # Use larger font and better colors
                    piece_color = '#1a1a1a' if piece.color == Color.BLACK else '#ffffff'
                    # Add subtle shadow for depth (only for white pieces)
                    if piece.color == Color.WHITE:
                        self.canvas.create_text(
                            center_x + 1,
                            center_y + 1,
                            text=symbol,
                            font=('Arial', 42, 'bold'),
                            fill='#cccccc',
                            tags='shadow'
                        )
                    self.canvas.create_text(
                        center_x,
                        center_y,
                        text=symbol,
                        font=('Arial', 42, 'bold'),
                        fill=piece_color,
                        tags='piece'
                    )
        
        # Draw coordinates with better styling
        coord_color = '#aaaaaa'
        board_offset = 20
        for i in range(8):
            # Files (a-h) at bottom
            file_char = chr(97 + i)
            self.canvas.create_text(
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 + board_offset,
                8 * self.SQUARE_SIZE + board_offset + 15,
                text=file_char,
                font=('Arial', 12, 'bold'),
                fill=coord_color
            )
            # Ranks (1-8) on left
            rank_char = str(8 - i)
            self.canvas.create_text(
                10,
                i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 + board_offset,
                text=rank_char,
                font=('Arial', 12, 'bold'),
                fill=coord_color
            )
    
    def on_square_click(self, event):
        """Handle square click events."""
        if self.board.current_turn == self.ai.color:
            return  # Not player's turn
        
        # Account for board offset
        board_offset = 20
        col = (event.x - board_offset) // self.SQUARE_SIZE
        row = (event.y - board_offset) // self.SQUARE_SIZE
        
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
                
                # Get captured piece before move
                captured = self.board.get_piece(row, col)
                eval_before = self.ai.evaluator.evaluate(self.board, Color.WHITE)
                
                if self.board.make_move(from_row, from_col, row, col, promotion_piece):
                    self.selected_square = None
                    self.valid_moves = []
                    
                    # Track move for analysis
                    if self.game_tracker is not None:
                        self.move_number += 1
                        self.game_tracker.record_move(
                            self.board, (from_row, from_col), (row, col),
                            captured, Color.WHITE, eval_before
                        )
                        eval_after = self.ai.evaluator.evaluate(self.board, Color.WHITE)
                        self.eval_history.add_evaluation(self.move_number, eval_after, Color.BLACK)
                    
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
            # Get captured piece before move
            captured = self.board.get_piece(to_row, to_col)
            eval_before = self.ai.evaluator.evaluate(self.board, Color.WHITE)
            
            # AI always promotes to Queen
            self.board.make_move(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
            
            # Track move for analysis
            if self.game_tracker is not None:
                self.move_number += 1
                self.game_tracker.record_move(
                    self.board, (from_row, from_col), (to_row, to_col),
                    captured, Color.BLACK, eval_before
                )
                eval_after = self.ai.evaluator.evaluate(self.board, Color.WHITE)
                self.eval_history.add_evaluation(self.move_number, eval_after, Color.WHITE)
            
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
        if self.game_over:
            return
        
        winner = None
        if self.board.is_checkmate(Color.WHITE):
            messagebox.showinfo("Game Over", "Checkmate! Black wins!")
            winner = Color.BLACK
            self.game_over = True
            self.game_winner = winner
        elif self.board.is_checkmate(Color.BLACK):
            messagebox.showinfo("Game Over", "Checkmate! White wins!")
            winner = Color.WHITE
            self.game_over = True
            self.game_winner = winner
        elif self.board.is_stalemate(self.board.current_turn):
            messagebox.showinfo("Game Over", "Stalemate! Game is a draw.")
            winner = None
            self.game_over = True
            self.game_winner = None
        
        # Show and enable analysis button if available
        if self.game_over and self.game_tracker is not None and ReportGenerator is not None:
            # Pack the button if it's not already visible
            try:
                self.analysis_button.pack_info()
            except:
                # Button not packed yet, pack it now
                self.analysis_button.pack(pady=5)
            self.analysis_button.config(state='normal')
    
    def show_analysis_window(self):
        """Show the analysis window."""
        if self.game_tracker is None or ReportGenerator is None:
            messagebox.showwarning("Analysis Unavailable", "Analysis data is not available.")
            return
        
        # Generate report
        report_gen = ReportGenerator(self.game_tracker, self.eval_history, self.board)
        report = report_gen.generate_report(self.game_winner)
        
        # Create analysis window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Post-Game Analysis")
        analysis_window.geometry("700x600")
        analysis_window.resizable(True, True)
        
        # Create scrollable text widget
        text_widget = scrolledtext.ScrolledText(
            analysis_window,
            wrap=tk.WORD,
            font=('Courier', 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format and display report
        analysis_text = self._format_analysis_report(report)
        text_widget.insert('1.0', analysis_text)
        text_widget.config(state='disabled')  # Make read-only
        
        # Close button
        close_button = tk.Button(
            analysis_window,
            text="Close",
            command=analysis_window.destroy,
            font=('Arial', 12),
            bg='#3C7ED9',
            fg='white'
        )
        close_button.pack(pady=10)
    
    def _format_analysis_report(self, report: dict) -> str:
        """Format the analysis report as text."""
        lines = []
        lines.append("=" * 70)
        lines.append("POST-GAME ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        
        # Game Result
        lines.append(f"Game Result: {report['game_result']}")
        lines.append("")
        
        # Statistics
        stats = report['statistics']
        lines.append("GAME STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Total Moves: {stats['total_moves']}")
        lines.append(f"White Moves: {stats['white_moves']} | Black Moves: {stats['black_moves']}")
        lines.append(f"Game Duration: {stats['duration_formatted']}")
        lines.append(f"Average Move Time: {stats['average_move_time']:.2f}s")
        lines.append("")
        
        # Material Analysis
        mat = report['material_analysis']
        lines.append("MATERIAL ANALYSIS")
        lines.append("-" * 70)
        lines.append(f"White Captured: {mat['white_total_value']} points ({mat.get('white_capture_count', 0)} pieces)")
        lines.append(f"Black Captured: {mat['black_total_value']} points ({mat.get('black_capture_count', 0)} pieces)")
        if mat['material_advantage'] != 0:
            adv = "White" if mat['material_advantage'] > 0 else "Black"
            lines.append(f"Material Advantage: {adv} (+{abs(mat['material_advantage'])} points)")
        lines.append("")
        
        # Evaluation
        eval_stats = report['evaluation']
        lines.append("POSITION EVALUATION")
        lines.append("-" * 70)
        lines.append(f"Average Evaluation: {eval_stats['average_evaluation']/100:.2f}")
        lines.append(f"Evaluation Range: {eval_stats['min_evaluation']/100:.1f} to {eval_stats['max_evaluation']/100:.1f}")
        lines.append(f"Trend: {eval_stats['trend']}")
        lines.append(f"White Best Position: Move {eval_stats['white_best_position']['move']} ({eval_stats['white_best_position']['evaluation']:+.1f})")
        lines.append(f"White Worst Position: Move {eval_stats['white_worst_position']['move']} ({eval_stats['white_worst_position']['evaluation']:+.1f})")
        lines.append("")
        
        # Performance Metrics
        perf = report['performance_metrics']
        lines.append("PERFORMANCE METRICS")
        lines.append("-" * 70)
        lines.append(f"White: {perf['white']['moves']} moves | Avg Time: {perf['white']['avg_move_time']:.2f}s | Captures: {perf['white']['captures']}")
        lines.append(f"Black: {perf['black']['moves']} moves | Avg Time: {perf['black']['avg_move_time']:.2f}s | Captures: {perf['black']['captures']}")
        lines.append("")
        
        # Key Moments
        if report['key_moments']:
            lines.append("KEY MOMENTS")
            lines.append("-" * 70)
            for moment in report['key_moments'][:10]:
                lines.append(f"Move {moment['move']}: {moment['description']}")
            lines.append("")
        
        return "\n".join(lines)
    
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

