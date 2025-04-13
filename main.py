"""
Main entry point for the Reverse Turing Test game.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from human_interface import TerminalInterface
from game_engine import GameEngine
from interrogation_mode import InterrogationGameEngine

def check_api_key():
    """Check if OpenAI API key is available."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: OpenAI API key not found!")
        print("Please create a .env file in the project root with your API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    return True

def main():
    """Main entry point for the game."""
    print("Initializing Reverse Turing Test game...")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Reverse Turing Test Game')
    parser.add_argument('--terminal', action='store_true', help='Run in terminal mode')
    parser.add_argument('--mode', choices=['standard', 'interrogation'], default='standard',
                      help='Game mode: standard (preset questions) or interrogation (characters question each other)')
    args = parser.parse_args()
    
    # Check for API key
    if not check_api_key():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create appropriate game engine based on mode
    if args.mode == 'interrogation':
        game = InterrogationGameEngine(None)
    else:
        game = GameEngine()
    
    # Set interface based on arguments
    if args.terminal:
        # Terminal mode
        interface = TerminalInterface()
        interface.game_mode = args.mode
        game.interface = interface
    else:
        # GUI mode
        game.use_gui = True
    
    try:
        game.run_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Exiting...")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
