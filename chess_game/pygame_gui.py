"""Pygame-based GUI for the chess game with 2D chess pieces."""

import pygame
import sys
from typing import Optional, Tuple

from .board import Board
from .pieces import Color, PieceType
from .ai import ChessAI


class ChessPygameGUI:
    """Pygame-based graphical user interface for the chess game."""
    
    # Professional color scheme
    LIGHT_SQUARE = (238, 238, 210)    # Classic light square
    DARK_SQUARE = (118, 150, 86)      # Classic dark square
    HIGHLIGHT = (247, 247, 105)       # Yellow highlight for valid moves
    SELECTED = (186, 202, 68)         # Green for selected piece
    CHECK_HIGHLIGHT = (255, 100, 100) # Red tint for check
    BORDER_COLOR = (50, 50, 50)       # Board border
    TEXT_COLOR = (40, 40, 40)         # Dark text
    TEXT_LIGHT = (240, 240, 240)      # Light text
    BG_COLOR = (45, 45, 45)           # Dark background
    PANEL_BG = (35, 35, 35)           # Dark panel background
    
    SQUARE_SIZE = 80  # Larger squares for better visibility
    BOARD_SIZE = SQUARE_SIZE * 8
    BOARD_BORDER = 20
    PANEL_HEIGHT = 120
    WINDOW_WIDTH = BOARD_SIZE + (BOARD_BORDER * 2)
    WINDOW_HEIGHT = BOARD_SIZE + (BOARD_BORDER * 2) + PANEL_HEIGHT
    
    def __init__(self, ai_depth: int = 1):
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
        
        # Load professional fonts (not used directly, but available)
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 18)
        
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
        """Create 2D chess piece images with professional rendering."""
        images = {}
        piece_size = int(self.SQUARE_SIZE * 0.75)  # Smaller pieces for cleaner look
        border_size = 2
        
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
                # White piece: elegant white with subtle gradient
                base_color = (255, 255, 255)
                border_color = (180, 180, 180)
                text_color = (30, 30, 30)
                highlight_color = (250, 250, 250)
                shadow_color = (200, 200, 200)
            else:
                # Black piece: rich dark with metallic look
                base_color = (50, 50, 50)
                border_color = (120, 120, 120)
                text_color = (255, 255, 255)
                highlight_color = (70, 70, 70)
                shadow_color = (30, 30, 30)
            
            # Draw subtle shadow for depth
            pygame.draw.circle(surface, shadow_color, 
                             (int(center_x + 1), int(center_y + 1)), 
                             radius + 1)
            
            # Draw main circle with gradient effect
            pygame.draw.circle(surface, base_color, center, radius)
            
            # Draw subtle inner highlight for 3D effect
            pygame.draw.circle(surface, highlight_color, 
                             (int(center_x - radius//4), int(center_y - radius//4)), 
                             radius // 2)
            
            # Draw elegant border
            pygame.draw.circle(surface, border_color, center, radius, border_size)
            
            # Draw symbol text - use arialunicode explicitly for chess symbols
            font_size = int(piece_size * 0.55)  # Smaller, more elegant symbols
            
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
            # First render to get exact dimensions
            text = font.render(symbol, True, text_color)
            
            # Get text dimensions for validation
            text_width = text.get_width()
            text_height = text.get_height()
            
            # Get text bounding box for precise centering
            text_rect = text.get_rect()
            
            # Center the text rectangle at the exact center of the piece
            # Use centerx/centery for pixel-perfect alignment
            text_rect.centerx = center_x
            text_rect.centery = center_y
            
            # Always try to render the symbol first
            # Add a subtle shadow for better visibility
            if color == Color.WHITE:
                shadow_color = (50, 50, 50)
            else:
                shadow_color = (0, 0, 0)
            
            shadow = font.render(symbol, True, shadow_color)
            shadow_rect = shadow.get_rect()
            shadow_rect.centerx = center_x + 1
            shadow_rect.centery = center_y + 1  # Slight offset for shadow
            
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
        """Draw the chess board and pieces with professional styling."""
        # Draw board background
        board_x = self.BOARD_BORDER
        board_y = self.BOARD_BORDER
        
        # Draw board border/shadow
        border_rect = pygame.Rect(board_x - 2, board_y - 2, 
                                 self.BOARD_SIZE + 4, self.BOARD_SIZE + 4)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, border_rect, 3)
        
        # Draw squares with professional styling
        for row in range(8):
            for col in range(8):
                x = board_x + col * self.SQUARE_SIZE
                y = board_y + row * self.SQUARE_SIZE
                
                # Draw square
                color = self._get_square_color(row, col)
                square_rect = pygame.Rect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, square_rect)
                
                # Add subtle border to squares
                pygame.draw.rect(self.screen, (200, 200, 200), square_rect, 1)
                
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
                        self.screen.blit(piece_img, (int(img_x), int(img_y)))
        
        # Draw coordinates with professional styling
        coord_font = pygame.font.SysFont('Arial', 14, bold=True)
        for i in range(8):
            # Files (a-h) at bottom
            file_char = chr(97 + i)
            file_text = coord_font.render(file_char, True, self.TEXT_COLOR)
            file_x = board_x + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 - file_text.get_width() // 2
            file_y = board_y + self.BOARD_SIZE + 5
            self.screen.blit(file_text, (file_x, file_y))
            
            # Ranks (1-8) on left
            rank_char = str(8 - i)
            rank_text = coord_font.render(rank_char, True, self.TEXT_COLOR)
            rank_x = board_x - 18
            rank_y = board_y + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 - rank_text.get_height() // 2
            self.screen.blit(rank_text, (rank_x, rank_y))
    
    def draw_panel(self):
        """Draw the professional status panel at the bottom."""
        panel_y = self.BOARD_SIZE + (self.BOARD_BORDER * 2)
        
        # Draw panel background with gradient effect
        panel_rect = pygame.Rect(0, panel_y, self.WINDOW_WIDTH, self.PANEL_HEIGHT)
        pygame.draw.rect(self.screen, self.PANEL_BG, panel_rect)
        
        # Draw elegant separator line
        line_y = panel_y
        pygame.draw.line(self.screen, (80, 80, 80), 
                        (0, line_y), (self.WINDOW_WIDTH, line_y), 2)
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (0, line_y + 1), (self.WINDOW_WIDTH, line_y + 1), 1)
        
        # Status text with professional styling
        status_font = pygame.font.SysFont('Arial', 22, bold=True)
        if self.board.is_checkmate(self.board.current_turn):
            winner = "Black" if self.board.current_turn == Color.WHITE else "White"
            status_text = f"Checkmate! {winner} wins!"
            color = (255, 80, 80)
        elif self.board.is_stalemate(self.board.current_turn):
            status_text = "Stalemate! Game is a draw."
            color = (150, 150, 150)
        elif self.board.is_in_check(self.board.current_turn):
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            status_text = f"{turn} to move • CHECK!"
            color = (255, 100, 100)
        elif self.ai_thinking:
            status_text = "AI is thinking..."
            color = (100, 180, 255)
        else:
            turn = "White" if self.board.current_turn == Color.WHITE else "Black"
            status_text = f"{turn} to move"
            color = self.TEXT_LIGHT
        
        text = status_font.render(status_text, True, color)
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, panel_y + 35))
        self.screen.blit(text, text_rect)
        
        # Instructions with subtle styling
        if self.board.current_turn == Color.WHITE and not self.ai_thinking:
            inst_font = pygame.font.SysFont('Arial', 14)
            inst_text = inst_font.render("Click a piece, then click a highlighted square to move", 
                                        True, (150, 150, 150))
            inst_rect = inst_text.get_rect(center=(self.WINDOW_WIDTH // 2, panel_y + 70))
            self.screen.blit(inst_text, inst_rect)
        
        # Draw turn indicator (small circle)
        indicator_y = panel_y + 35
        if self.board.current_turn == Color.WHITE:
            indicator_color = (255, 255, 255)
        else:
            indicator_color = (50, 50, 50)
        
        indicator_x = self.WINDOW_WIDTH // 2 - text.get_width() // 2 - 25
        pygame.draw.circle(self.screen, indicator_color, (indicator_x, indicator_y), 6)
        pygame.draw.circle(self.screen, (100, 100, 100), (indicator_x, indicator_y), 6, 1)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on the board."""
        if self.board.current_turn == self.ai.color or self.ai_thinking:
            return  # Not player's turn or AI is thinking
        
        x, y = pos
        board_start_y = self.BOARD_BORDER
        board_end_y = board_start_y + self.BOARD_SIZE
        board_start_x = self.BOARD_BORDER
        board_end_x = board_start_x + self.BOARD_SIZE
        
        # Check if click is within board bounds
        if not (board_start_x <= x <= board_end_x and board_start_y <= y <= board_end_y):
            return  # Clicked outside board
        
        # Adjust coordinates for board offset
        x -= board_start_x
        y -= board_start_y
        
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
            
            # Draw everything with professional background
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

