"""Pygame-based GUI for the chess game with 2D chess pieces."""

import pygame
import sys
from typing import Optional, Tuple

from .board import Board
from .pieces import Color, PieceType
from .ai import ChessAI


class ChessPygameGUI:
    """Pygame-based graphical user interface for the chess game."""
    
    # Colors
    LIGHT_SQUARE = (240, 217, 181)  # #F0D9B5
    DARK_SQUARE = (181, 136, 99)     # #B58863
    HIGHLIGHT = (247, 247, 105)      # #F7F769
    SELECTED = (118, 150, 86)        # #769656
    TEXT_COLOR = (0, 0, 0)
    BG_COLOR = (255, 255, 255)
    
    SQUARE_SIZE = 75
    BOARD_SIZE = SQUARE_SIZE * 8
    PANEL_HEIGHT = 100
    WINDOW_WIDTH = BOARD_SIZE
    WINDOW_HEIGHT = BOARD_SIZE + PANEL_HEIGHT
    
    def __init__(self, ai_depth: int = 3):
        """Initialize the Pygame GUI."""
        pygame.init()
        pygame.font.init()  # Initialize font system early
        
        self.board = Board()
        self.ai = ChessAI(depth=ai_depth, color=Color.BLACK)
        self.selected_square: Optional[Tuple[int, int]] = None
        self.valid_moves: list = []
        
        # Create window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("CheckM8 - Chess Game")
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Create piece images/surfaces (this will use chess symbols)
        self.piece_images = self._create_piece_images()
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # AI thinking flag
        self.ai_thinking = False
        
        # Start AI move if it's AI's turn
        if self.board.current_turn == self.ai.color:
            self.ai_thinking = True
            pygame.time.set_timer(pygame.USEREVENT, 100)  # Trigger AI move after 100ms
    
    def _create_piece_images(self) -> dict:
        """Create 2D chess piece images with better rendering."""
        images = {}
        piece_size = int(self.SQUARE_SIZE * 0.85)
        border_size = 3
        
        # Unicode chess symbols (larger, clearer)
        symbols = {
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
            (Color.BLACK, PieceType.KING): '♚',
        }
        
        # Find a font that supports chess symbols - use arialunicode explicitly
        chess_font_name = 'arialunicode'  # Force use of arialunicode
        available_fonts = pygame.font.get_fonts()
        
        # Verify arialunicode works, otherwise find alternative
        if 'arialunicode' in available_fonts:
            try:
                test_font = pygame.font.SysFont('arialunicode', 50, bold=True)
                test_surf = test_font.render('♔', True, (0, 0, 0))
                if test_surf.get_width() < 20:
                    chess_font_name = None  # Font doesn't work well
            except:
                chess_font_name = None
        else:
            chess_font_name = None
        
        # If arialunicode not available or doesn't work, try alternatives
        if chess_font_name is None:
            for font_name in ['dejavu', 'noto', 'liberation']:
                matching = [f for f in available_fonts if font_name in f.lower()]
                if matching:
                    try:
                        test_font = pygame.font.SysFont(matching[0], 50, bold=True)
                        test_surf = test_font.render('♔', True, (0, 0, 0))
                        if test_surf.get_width() > 20:
                            chess_font_name = matching[0]
                            break
                    except:
                        continue
        
        for (color, piece_type), symbol in symbols.items():
            # Create surface for piece with transparency
            surface = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Draw base circle with gradient effect
            # Use exact center coordinates for precise alignment
            center_x = piece_size / 2.0
            center_y = piece_size / 2.0
            center = (int(center_x), int(center_y))
            radius = piece_size // 2 - border_size
            
            if color == Color.WHITE:
                # White piece: light base with dark border
                base_color = (255, 255, 255)
                border_color = (100, 100, 100)
                text_color = (0, 0, 0)
            else:
                # Black piece: dark base with light border
                base_color = (60, 60, 60)
                border_color = (180, 180, 180)
                text_color = (255, 255, 255)
            
            # Draw main circle
            pygame.draw.circle(surface, base_color, center, radius)
            
            # Draw border
            pygame.draw.circle(surface, border_color, center, radius, border_size)
            
            # Draw inner highlight for 3D effect
            if color == Color.WHITE:
                highlight_color = (240, 240, 240)
            else:
                highlight_color = (80, 80, 80)
            pygame.draw.circle(surface, highlight_color, 
                             (center[0] - radius//3, center[1] - radius//3), 
                             radius // 3)
            
            # Draw symbol text - use arialunicode explicitly for chess symbols
            font_size = int(piece_size * 0.9)  # Even larger symbol
            
            # Always try arialunicode first (we know it works from testing)
            if chess_font_name:
                try:
                    font = pygame.font.SysFont(chess_font_name, font_size, bold=True)
                except:
                    font = pygame.font.SysFont('arialunicode', font_size, bold=True)
            else:
                # Fallback: try arialunicode anyway
                try:
                    font = pygame.font.SysFont('arialunicode', font_size, bold=True)
                except:
                    # Last resort fallback
                    font = pygame.font.SysFont(None, font_size, bold=True)
            
            # Render the chess symbol with proper centering
            text = font.render(symbol, True, text_color)
            
            # Get the actual rendered text dimensions
            text_width = text.get_width()
            text_height = text.get_height()
            
            # Calculate centered position using exact center coordinates
            # Use get_rect(center=...) for perfect centering
            text_rect = text.get_rect()
            text_rect.center = (center_x, center_y)
            
            # Always try to render the symbol first
            # Add a subtle shadow for better visibility
            if color == Color.WHITE:
                shadow_color = (50, 50, 50)
            else:
                shadow_color = (0, 0, 0)
            
            shadow = font.render(symbol, True, shadow_color)
            shadow_rect = shadow.get_rect()
            shadow_rect.center = (center_x + 1, center_y + 1)  # Slight offset for shadow
            
            # Blit shadow first, then text on top (perfectly centered)
            surface.blit(shadow, shadow_rect)
            surface.blit(text, text_rect)
            
            # If symbol didn't render properly (too small), add letter fallback
            if text_width < 10:
                piece_letters = {
                    PieceType.PAWN: 'P',
                    PieceType.ROOK: 'R',
                    PieceType.KNIGHT: 'N',
                    PieceType.BISHOP: 'B',
                    PieceType.QUEEN: 'Q',
                    PieceType.KING: 'K'
                }
                letter = piece_letters.get(piece_type, '?')
                letter_font = pygame.font.SysFont(None, int(font_size * 0.5), bold=True)
                letter_text = letter_font.render(letter, True, text_color)
                letter_width = letter_text.get_width()
                letter_height = letter_text.get_height()
                letter_x = center[0] - letter_width // 2
                letter_y = center[1] - letter_height // 2
                surface.blit(letter_text, (letter_x, letter_y))
            
            images[(color, piece_type)] = surface
        
        return images
    
    def _get_square_color(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get the color for a square."""
        is_light = (row + col) % 2 == 0
        
        # Highlight selected square
        if self.selected_square == (row, col):
            return self.SELECTED
        
        # Highlight valid moves
        if (row, col) in self.valid_moves:
            return self.HIGHLIGHT
        
        return self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
    
    def draw_board(self):
        """Draw the chess board and pieces."""
        # Draw squares
        for row in range(8):
            for col in range(8):
                x = col * self.SQUARE_SIZE
                y = row * self.SQUARE_SIZE
                
                # Draw square
                color = self._get_square_color(row, col)
                pygame.draw.rect(self.screen, color, 
                              (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Draw piece
                piece = self.board.get_piece(row, col)
                if piece is not None:
                    piece_img = self.piece_images.get((piece.color, piece.type))
                    if piece_img:
                        # Center the piece image precisely in the square
                        img_width = piece_img.get_width()
                        img_height = piece_img.get_height()
                        img_x = x + (self.SQUARE_SIZE - img_width) // 2
                        img_y = y + (self.SQUARE_SIZE - img_height) // 2
                        self.screen.blit(piece_img, (img_x, img_y))
        
        # Draw coordinates
        for i in range(8):
            # Files (a-h) at bottom
            file_text = self.font_small.render(chr(97 + i), True, self.TEXT_COLOR)
            self.screen.blit(file_text, (i * self.SQUARE_SIZE + 5, self.BOARD_SIZE - 15))
            
            # Ranks (1-8) on left
            rank_text = self.font_small.render(str(8 - i), True, self.TEXT_COLOR)
            self.screen.blit(rank_text, (5, i * self.SQUARE_SIZE + 5))
    
    def draw_panel(self):
        """Draw the status panel at the bottom."""
        panel_y = self.BOARD_SIZE
        
        # Draw panel background
        pygame.draw.rect(self.screen, self.BG_COLOR, 
                       (0, panel_y, self.WINDOW_WIDTH, self.PANEL_HEIGHT))
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (0, panel_y), (self.WINDOW_WIDTH, panel_y), 2)
        
        # Status text
        if self.board.is_checkmate(self.board.current_turn):
            winner = "Black" if self.board.current_turn == Color.WHITE else "White"
            status_text = f"Checkmate! {winner} wins!"
            color = (200, 0, 0)
        elif self.board.is_stalemate(self.board.current_turn):
            status_text = "Stalemate! Game is a draw."
            color = (100, 100, 100)
        elif self.board.is_in_check(self.board.current_turn):
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            status_text = f"{turn} to move (Check!)"
            color = (200, 0, 0)
        elif self.ai_thinking:
            status_text = "AI is thinking..."
            color = (0, 100, 200)
        else:
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            status_text = f"{turn} to move"
            color = self.TEXT_COLOR
        
        text = self.font_medium.render(status_text, True, color)
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, panel_y + 30))
        self.screen.blit(text, text_rect)
        
        # Instructions
        if self.board.current_turn == Color.WHITE and not self.ai_thinking:
            inst_text = self.font_small.render("Click a piece, then click a highlighted square to move", 
                                             True, (100, 100, 100))
            inst_rect = inst_text.get_rect(center=(self.WINDOW_WIDTH // 2, panel_y + 60))
            self.screen.blit(inst_text, inst_rect)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on the board."""
        if self.board.current_turn == self.ai.color or self.ai_thinking:
            return  # Not player's turn or AI is thinking
        
        x, y = pos
        if y > self.BOARD_SIZE:
            return  # Clicked on panel, not board
        
        col = x // self.SQUARE_SIZE
        row = y // self.SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        piece = self.board.get_piece(row, col)
        
        # If a square is already selected
        if self.selected_square is not None:
            from_row, from_col = self.selected_square
            
            # If clicking on a valid move square, make the move
            if (row, col) in self.valid_moves:
                if self.board.make_move(from_row, from_col, row, col):
                    self.selected_square = None
                    self.valid_moves = []
                    self.check_game_over()
                    
                    # Trigger AI move
                    if self.board.current_turn == self.ai.color:
                        self.ai_thinking = True
                        pygame.time.set_timer(pygame.USEREVENT, 100)
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
    
    def make_ai_move(self):
        """Make the AI's move."""
        if self.board.current_turn != self.ai.color or not self.ai_thinking:
            return
        
        move = self.ai.get_best_move(self.board)
        if move is not None:
            from_row, from_col, to_row, to_col = move
            self.board.make_move(from_row, from_col, to_row, to_col)
            self.check_game_over()
        else:
            self.check_game_over()
        
        self.ai_thinking = False
        pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel timer
    
    def check_game_over(self):
        """Check if the game is over and show message."""
        if self.board.is_checkmate(Color.WHITE):
            self.show_message("Game Over", "Checkmate! Black wins!")
        elif self.board.is_checkmate(Color.BLACK):
            self.show_message("Game Over", "Checkmate! White wins!")
        elif self.board.is_stalemate(self.board.current_turn):
            self.show_message("Game Over", "Stalemate! Game is a draw.")
    
    def show_message(self, title: str, message: str):
        """Show a message dialog (simple text on screen)."""
        # Simple message display - could be enhanced with a proper dialog
        print(f"{title}: {message}")
    
    def run(self):
        """Run the game loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.USEREVENT:
                    # AI move timer
                    self.make_ai_move()
            
            # Draw everything
            self.screen.fill(self.BG_COLOR)
            self.draw_board()
            self.draw_panel()
            pygame.display.flip()
            
            # Cap frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point for Pygame GUI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CheckM8 Chess Game (Pygame GUI)')
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='AI search depth (default: 3)'
    )
    
    args = parser.parse_args()
    
    app = ChessPygameGUI(ai_depth=args.depth)
    app.run()


if __name__ == '__main__':
    main()

