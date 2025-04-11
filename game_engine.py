"""
Game engine for the Reverse Turing Test game.
"""
import random
import time
from character import get_character_profiles
from questions import get_question_bank, select_game_questions
from ai_player import AIPlayer

class GameEngine:
    def __init__(self, interface=None, num_rounds=5):
        """
        Initialize the game engine.
        
        Args:
            interface: User interface object (terminal or graphical)
            num_rounds (int): Number of question rounds
        """
        self.interface = interface
        self.num_rounds = num_rounds
        self.characters = get_character_profiles()
        self.question_bank = get_question_bank()
        self.game_questions = []
        self.human_character = None
        self.ai_players = []
        self.current_round = 0
        self.use_gui = False
    
    def setup_game(self):
        """Set up the game by selecting characters and questions."""
        if not self.use_gui:
            # Display welcome screen
            self.interface.display_title()
            input("Press Enter to start...")
            
            # Let human player select character
            human_char_index = self.interface.display_character_selection(self.characters)
            self.human_character = self.characters[human_char_index]
            
            # Create AI players with remaining characters
            for i, char in enumerate(self.characters):
                if i != human_char_index:
                    self.ai_players.append(self.create_ai_player(char))
            
            # Select questions for the game
            self.game_questions = self.select_game_questions()
        
        return True
        
    def create_ai_player(self, character):
        """Create an AI player for a character."""
        return AIPlayer(character)
    
    def select_game_questions(self):
        """Select questions for the game."""
        return select_game_questions(self.question_bank, self.num_rounds)
    
    def run_game(self):
        """Run the main game loop."""
        if self.use_gui:
            # GUI mode - the GUI will handle the game flow
            from gui import GUI
            gui = GUI()
            return gui.run(self)
        else:
            # Terminal mode
            self.setup_game()
            
            # Run each round
            for round_num in range(1, self.num_rounds + 1):
                self.current_round = round_num
                self.run_round(round_num)
                
                # Pause between rounds
                if round_num < self.num_rounds:
                    input("\nPress Enter to continue to the next round...")
            
            # Final voting phase
            self.run_voting_phase()
            
            return True
    
    def run_round(self, round_num):
        """
        Run a single round of the game.
        
        Args:
            round_num (int): Current round number (1-indexed)
        """
        question = self.game_questions[round_num - 1]
        
        # Display the question
        self.interface.clear_screen()
        self.interface.display_title()
        self.interface.display_question(question, round_num, self.num_rounds)
        
        # Get human response
        human_response = self.interface.get_text_input(f"Enter {self.human_character.name}'s response:")
        self.human_character.add_response(human_response)
        
        # Show "thinking" message for AI responses
        print("\nAI characters are thinking...")
        
        # Get AI responses
        for ai_player in self.ai_players:
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 2.5))
            ai_player.generate_response(question, round_num)
        
        # Display all responses
        self.interface.display_responses(self.characters, round_num - 1)
        
        # Show "analyzing" message for AI suspicions
        print("\nAI characters are analyzing responses...")
        
        # Get human suspicion
        human_suspicion = self.interface.get_text_input(
            f"As {self.human_character.name}, express your suspicions about who might be human (1-2 sentences):"
        )
        self.human_character.add_suspicion(human_suspicion)
        
        # Get AI suspicions
        for ai_player in self.ai_players:
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 2.0))
            ai_player.analyze_responses(self.characters, question, round_num)
        
        # Display all suspicions
        self.interface.display_suspicions(self.characters, round_num - 1)
    
    def run_voting_phase(self):
        """Run the final voting phase."""
        # Display voting instructions
        self.interface.clear_screen()
        self.interface.display_title()
        print("\nFinal Voting Phase")
        print("\nBased on all the responses and suspicions, each player will now vote on who they think is the human.")
        
        # Get human vote
        options = [char.name for char in self.characters if char != self.human_character]
        print("\nAs the human player, you must vote for someone else to maintain your cover.")
        
        for i, name in enumerate(options, 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(options):
                    self.human_character.set_vote(options[choice - 1])
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Get AI votes
        print("\nAI characters are voting...")
        for ai_player in self.ai_players:
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 1.5))
            ai_player.generate_vote(self.characters)
        
        # Display votes and results
        human_won = self.interface.display_votes(self.characters, self.human_character)
        
        # Display game over screen
        self.interface.display_game_over(human_won)
        
        return human_won
        
    def reset(self):
        """Reset the game state for a new game."""
        self.game_questions = []
        self.human_character = None
        self.ai_players = []
        self.current_round = 0
        
        # Reset character states
        for character in self.characters:
            character.responses = []
            character.suspicions = []
            character.vote = None
