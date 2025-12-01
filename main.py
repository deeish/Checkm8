"""Main entry point for CheckM8 chess game."""

import argparse
import sys


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='CheckM8 - Chess Game with AI')
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='AI search depth (3-5 recommended, default: 3)'
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Force console mode (skip GUI)'
    )
    
    args = parser.parse_args()
    
    # Validate depth
    if args.depth < 1 or args.depth > 5:
        print("Warning: Depth should be between 1 and 5. Using default depth 3.")
        args.depth = 3
    
    # Try Pygame GUI first (most reliable), fall back to tkinter, then console
    if not args.console:
        # Try Pygame GUI
        try:
            from chess_game.pygame_gui import ChessPygameGUI
            print(f"Starting CheckM8 Chess Game with AI depth {args.depth}")
            print("You are playing as White. The AI is playing as Black.")
            app = ChessPygameGUI(ai_depth=args.depth)
            app.run()
            return
        except (ImportError, ModuleNotFoundError) as e:
            print(f"Pygame not available ({e})")
            print("Trying tkinter GUI...")
        except Exception as e:
            print(f"Pygame GUI error: {e}")
            print("Trying tkinter GUI...")
        
        # Try tkinter GUI as fallback
        try:
            from chess_game.gui import ChessGUI
            print(f"Starting CheckM8 Chess Game with AI depth {args.depth}")
            print("You are playing as White. The AI is playing as Black.")
            app = ChessGUI(ai_depth=args.depth)
            app.run()
            return
        except (ImportError, ModuleNotFoundError) as e:
            print(f"GUI not available ({e})")
            print("Falling back to console mode...\n")
        except Exception as e:
            print(f"GUI error: {e}")
            print("Falling back to console mode...\n")
    
    # Console mode
    from chess_game.console import ChessConsole
    game = ChessConsole(ai_depth=args.depth)
    game.run()


if __name__ == '__main__':
    main()

