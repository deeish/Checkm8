"""Console-based interface for the chess game (fallback when GUI is unavailable)."""

from .board import Board
from .pieces import Color, PieceType
from .ai import ChessAI


class ChessConsole:
    """Console-based chess game interface."""
    
    def __init__(self, ai_depth: int = 3):
        """Initialize the console game."""
        self.board = Board()
        self.ai = ChessAI(depth=ai_depth, color=Color.BLACK)
    
    def display_board(self):
        """Display the current board state."""
        print("\n" + "="*50)
        print(str(self.board))
        print("="*50 + "\n")
    
    def get_move_from_user(self) -> tuple:
        """Get a move from the user via console input."""
        print("Enter your move (format: e2 e4, or 'quit' to exit):")
        while True:
            try:
                move_input = input("> ").strip().lower()
                if move_input == 'quit':
                    return None
                
                parts = move_input.split()
                if len(parts) != 2:
                    print("Invalid format. Use: e2 e4")
                    continue
                
                from_square = parts[0]
                to_square = parts[1]
                
                # Convert algebraic notation to coordinates
                from_col = ord(from_square[0]) - ord('a')
                from_row = 8 - int(from_square[1])
                to_col = ord(to_square[0]) - ord('a')
                to_row = 8 - int(to_square[1])
                
                if not (0 <= from_row < 8 and 0 <= from_col < 8 and 
                        0 <= to_row < 8 and 0 <= to_col < 8):
                    print("Invalid coordinates. Use format like: e2 e4")
                    continue
                
                return (from_row, from_col, to_row, to_col)
            except (ValueError, IndexError):
                print("Invalid input. Use format: e2 e4")
            except KeyboardInterrupt:
                print("\nExiting...")
                return None
    
    def show_valid_moves(self, row: int, col: int):
        """Show valid moves for a piece."""
        moves = self.board.get_all_moves(self.board.current_turn)
        piece_moves = [
            (to_row, to_col) 
            for from_row, from_col, to_row, to_col in moves
            if from_row == row and from_col == col
        ]
        if piece_moves:
            print(f"Valid moves: {', '.join([chr(97+c)+str(8-r) for r, c in piece_moves])}")
        return piece_moves
    
    def get_promotion_choice(self) -> PieceType:
        """Get promotion piece choice from user."""
        print("\nPawn promotion! Choose a piece:")
        print("1. Queen (Q)")
        print("2. Rook (R)")
        print("3. Bishop (B)")
        print("4. Knight (N)")
        
        while True:
            try:
                choice = input("Enter choice (1-4, default=1): ").strip()
                if not choice:
                    return PieceType.QUEEN
                
                choice_map = {
                    '1': PieceType.QUEEN,
                    '2': PieceType.ROOK,
                    '3': PieceType.BISHOP,
                    '4': PieceType.KNIGHT
                }
                
                if choice in choice_map:
                    return choice_map[choice]
                else:
                    print("Invalid choice. Enter 1, 2, 3, or 4.")
            except (KeyboardInterrupt, EOFError):
                print("\nDefaulting to Queen.")
                return PieceType.QUEEN
    
    def run(self):
        """Run the console game loop."""
        print("="*50)
        print("CheckM8 Chess Game - Console Mode")
        print("="*50)
        print("You are playing as White. The AI is playing as Black.")
        print("Enter moves in algebraic notation (e.g., 'e2 e4')")
        print("Type 'quit' to exit\n")
        
        while True:
            self.display_board()
            
            # Check for game over
            if self.board.is_checkmate(Color.WHITE):
                print("Checkmate! Black wins!")
                break
            elif self.board.is_checkmate(Color.BLACK):
                print("Checkmate! White wins!")
                break
            elif self.board.is_stalemate(self.board.current_turn):
                print("Stalemate! Game is a draw.")
                break
            
            # Show current turn
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            if self.board.is_in_check(self.board.current_turn):
                print(f"{turn} to move (CHECK!)")
            else:
                print(f"{turn} to move")
            
            if self.board.current_turn == Color.WHITE:
                # Player's turn
                move = self.get_move_from_user()
                if move is None:
                    break
                
                from_row, from_col, to_row, to_col = move
                
                # Check if promotion is needed
                promotion_piece = None
                if self.board.needs_promotion(from_row, from_col, to_row):
                    promotion_piece = self.get_promotion_choice()
                    if promotion_piece is None:
                        promotion_piece = PieceType.QUEEN  # Default to Queen
                
                if self.board.make_move(from_row, from_col, to_row, to_col, promotion_piece):
                    print("Move made successfully!")
                else:
                    print("Invalid move! Try again.")
            else:
                # AI's turn
                print("AI is thinking...")
                move = self.ai.get_best_move(self.board)
                if move:
                    from_row, from_col, to_row, to_col = move
                    from_sq = chr(97 + from_col) + str(8 - from_row)
                    to_sq = chr(97 + to_col) + str(8 - to_row)
                    # AI always promotes to Queen
                    self.board.make_move(from_row, from_col, to_row, to_col, promotion_piece=PieceType.QUEEN)
                    print(f"AI plays: {from_sq} {to_sq}")
                else:
                    print("AI has no moves available.")
                    break


def main():
    """Main entry point for console mode."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CheckM8 Chess Game (Console Mode)')
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='AI search depth (default: 3)'
    )
    
    args = parser.parse_args()
    
    game = ChessConsole(ai_depth=args.depth)
    game.run()


if __name__ == '__main__':
    main()

