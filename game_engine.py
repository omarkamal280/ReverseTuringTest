"""
Game engine for the Reverse Turing Test game.
"""
import random
import time
from character import get_character_profiles
from questions import get_question_bank, select_game_questions
from ai_player import AIPlayer
from ai_judge import AIJudge

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
        self.ai_judges = []
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
            
            # Create AI judges with different approaches
            self.ai_judges = [
                AIJudge("Holmes", "human_traits"),
                AIJudge("Watson", "odd_one_out"),
                AIJudge("Poirot", "mixed")
            ]
            
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
        
        # Show "analyzing" message for AI judges
        print("\nAI judges are analyzing responses...")
        
        # Get AI judge suspicions
        for judge in self.ai_judges:
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 2.0))
            suspicion = judge.analyze_responses(self.characters, question, round_num)
            print(f"Judge {judge.name}: {suspicion}")
    
    def run_voting_phase(self):
        """Run the voting phase of the game."""
        print("\n===== VOTING PHASE =====\n")
        print("The judges are now discussing and voting on who they think is the human player...")
        
        # Initial votes from AI judges
        judge_votes = {}
        for judge in self.ai_judges:
            vote = judge.generate_vote(self.characters, self.game_questions)
            judge_votes[judge.name] = vote
            print(f"Judge {judge.name}'s initial vote: {vote}")
        
        # Have judges discuss and try to reach consensus
        print("\n===== JUDGES' DISCUSSION =====\n")
        main_judge = self.ai_judges[0]  # Use the first judge to lead the discussion
        other_judges = self.ai_judges[1:]
        
        final_verdict, discussion_history = main_judge.discuss(
            other_judges, self.characters, self.game_questions
        )
        
        # Display the discussion
        for round_idx, round_messages in enumerate(discussion_history):
            print(f"\n--- DISCUSSION ROUND {round_idx + 1} ---")
            for message in round_messages:
                print(f"{message['judge']}: {message['message']}")
        
        # Get final votes after discussion
        final_judge_votes = {}
        for judge in self.ai_judges:
            # Check if the judge's vote changed during discussion
            if judge.name in judge_votes and judge_votes[judge.name] != final_verdict:
                print(f"Judge {judge.name} changed their vote from {judge_votes[judge.name]} to {final_verdict}")
            final_judge_votes[judge.name] = final_verdict
        
        # Store the discussion history and final votes
        self.judge_discussion = discussion_history
        self.final_judge_votes = final_judge_votes
        
        # Check if human player was identified
        human_identified = (final_verdict == self.human_character.name)
        
        print(f"\nAfter discussion, the judges have reached a verdict: {final_verdict}")
        if human_identified:
            print("\nThe judges have correctly identified you as the human player!")
            print("Game over - you lose.")
        else:
            print("\nThe judges failed to identify you as the human player!")
            print("Game over - you win!")
        
        # Display game over screen
        self.interface.display_game_over(not human_identified)
        
        return not human_identified
        
    def reset(self):
        """Reset the game state for a new game."""
        self.game_questions = []
        self.human_character = None
        self.ai_players = []
        self.ai_judges = []
        self.current_round = 0
        
        # Reset character states
        for character in self.characters:
            character.responses = []
            character.suspicions = []
            character.vote = None
