"""
Interrogation mode for the Reverse Turing Test game.
"""
import random
import time
from character import get_character_profiles
from ai_player import AIPlayer

class InterrogationGameEngine:
    """Game engine for the pure interrogation mode."""
    
    def __init__(self, interface, num_rounds=3):
        """
        Initialize the interrogation game engine.
        
        Args:
            interface: User interface object
            num_rounds: Number of interrogation rounds
        """
        self.interface = interface
        self.num_rounds = num_rounds
        self.characters = get_character_profiles()
        self.human_character = None
        self.ai_players = []
        self.current_round = 0
        self.interrogation_history = {}
        self.use_gui = False
    
    def setup_game(self):
        """Set up the game by selecting characters."""
        if not self.use_gui:
            # Display welcome screen
            self.interface.display_title()
            self.interface.display_interrogation_mode_intro()
            input("Press Enter to start...")
            
            # Let human player select character
            human_char_index = self.interface.display_character_selection(self.characters)
            self.human_character = self.characters[human_char_index]
            
            # Create AI players with remaining characters
            for i, char in enumerate(self.characters):
                if i != human_char_index:
                    self.ai_players.append(AIPlayer(char))
        
        return True
    
    def run_game(self):
        """Run the main game loop."""
        if self.use_gui:
            # GUI mode - the GUI will handle the game flow
            from interrogation_gui import InterrogationGUI
            gui = InterrogationGUI()
            return gui.run(self)
        else:
            # Terminal mode
            self.setup_game()
            
            # Introduction phase
            self.run_introduction_phase()
            
            # Run interrogation rounds
            for round_num in range(1, self.num_rounds + 1):
                self.current_round = round_num
                self.run_interrogation_round(round_num)
                
                # Run suspicion phase after each round
                self.run_suspicion_phase(round_num)
                
                # Pause between rounds
                if round_num < self.num_rounds:
                    input("\nPress Enter to continue to the next round...")
            
            # Final voting phase
            self.run_voting_phase()
            
            return True
    
    def run_introduction_phase(self):
        """Run the introduction phase where each character introduces themselves."""
        self.interface.clear_screen()
        self.interface.display_title()
        print("\n===== CHARACTER INTRODUCTIONS =====\n")
        
        # Human player introduces themselves
        human_intro = self.interface.get_text_input(
            f"As {self.human_character.name}, introduce yourself to the group (1-2 sentences):"
        )
        self.human_character.introduction = human_intro
        
        # AI players introduce themselves
        print("\nOther characters are introducing themselves...")
        
        for ai_player in self.ai_players:
            # Generate introduction
            introduction = self._generate_introduction(ai_player)
            ai_player.character.introduction = introduction
            
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 2.0))
        
        # Display all introductions
        self.interface.display_introductions(self.characters)
        
        input("\nPress Enter to begin the interrogation rounds...")
    
    def run_interrogation_round(self, round_num):
        """Run a single round of interrogations."""
        self.interface.clear_screen()
        self.interface.display_title()
        print(f"\n===== INTERROGATION ROUND {round_num}/{self.num_rounds} =====\n")
        
        # Store interrogation data for this round
        interrogation_data = []
        
        # Determine interrogation order (random)
        interrogation_order = list(self.characters)
        random.shuffle(interrogation_order)
        
        # Each character takes a turn interrogating another character
        for interrogator in interrogation_order:
            # Get already interrogated characters in this round
            interrogated_chars = [data['target'] for data in interrogation_data 
                                if data['interrogator'] == interrogator]
            
            # Choose target (human chooses if it's their turn)
            if interrogator == self.human_character:
                # Let human choose who to interrogate
                available_targets = [c for c in self.characters 
                                   if c != interrogator and c not in interrogated_chars]
                
                if not available_targets:
                    continue
                    
                target_idx = self.interface.get_interrogation_target(
                    interrogator.name, [c.name for c in available_targets]
                )
                target = available_targets[target_idx]
                
                # Let human create question
                question = self.interface.get_interrogation_question(
                    interrogator.name, target.name
                )
            else:
                # AI chooses who to interrogate
                ai_player = next(ai for ai in self.ai_players if ai.character == interrogator)
                
                # Filter out already interrogated characters
                available_targets = [c for c in self.characters 
                                   if c != interrogator and c not in interrogated_chars]
                
                if not available_targets:
                    continue
                    
                target = self._choose_interrogation_target(ai_player, available_targets, round_num)
                
                # AI generates question
                question = self._generate_question(ai_player, target, round_num)
                
                # Simulate thinking time
                time.sleep(random.uniform(1.0, 2.0))
            
            # Display the question
            self.interface.display_interrogation_question(interrogator.name, target.name, question)
            
            # Get response (human or AI)
            if target == self.human_character:
                # Human responds to interrogation
                response = self.interface.get_interrogation_response(
                    target.name, interrogator.name, question
                )
            else:
                # AI responds to interrogation
                ai_target = next(ai for ai in self.ai_players if ai.character == target)
                response = self._generate_response(ai_target, question, interrogator)
                
                # Simulate thinking time
                time.sleep(random.uniform(1.0, 2.0))
            
            # Display the response
            self.interface.display_interrogation_response(target.name, response)
            
            # Store the interrogation data
            interrogation_data.append({
                'interrogator': interrogator,
                'target': target,
                'question': question,
                'response': response
            })
            
            # Pause between interrogations
            input("\nPress Enter to continue to the next interrogation...")
        
        # Store interrogation data for this round
        self.interrogation_history[round_num] = interrogation_data
    
    def run_suspicion_phase(self, round_num):
        """Run the suspicion phase after an interrogation round."""
        self.interface.clear_screen()
        self.interface.display_title()
        print(f"\n===== SUSPICIONS AFTER ROUND {round_num} =====\n")
        
        # Get human suspicion
        human_suspicion = self.interface.get_text_input(
            f"As {self.human_character.name}, express your suspicions about who might be human (1-2 sentences):"
        )
        self.human_character.add_suspicion(human_suspicion)
        
        # Get AI suspicions
        print("\nAI characters are forming their suspicions...")
        
        for ai_player in self.ai_players:
            # Generate suspicion based on interrogations
            suspicion = self._generate_suspicion(ai_player, round_num)
            ai_player.character.add_suspicion(suspicion)
            
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 2.0))
        
        # Display all suspicions
        self.interface.display_suspicions(self.characters, round_num - 1)
    
    def run_voting_phase(self):
        """Run the final voting phase."""
        # Display voting instructions
        self.interface.clear_screen()
        self.interface.display_title()
        print("\n===== FINAL VOTING PHASE =====")
        print("\nBased on all the interrogations and suspicions, each player will now vote on who they think is the human.")
        
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
            # Generate vote based on all interrogations and suspicions
            vote = self._generate_vote(ai_player)
            
            # Simulate thinking time
            time.sleep(random.uniform(1.0, 1.5))
        
        # Display votes and results
        human_won = self.interface.display_votes(self.characters, self.human_character)
        
        # Display game over screen
        self.interface.display_game_over(human_won)
        
        return human_won
    
    def _generate_introduction(self, ai_player):
        """Generate an introduction for an AI character."""
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game.
        
        {ai_player.character.get_prompt_description()}
        
        Introduce yourself to the group in 1-2 sentences. Stay true to your character's personality and speech style.
        Don't reveal that you're an AI - just introduce yourself naturally as your character would.
        """
        
        return ai_player._call_openai_api(prompt)
    
    def _choose_interrogation_target(self, ai_player, available_targets, round_num):
        """Choose which character to interrogate."""
        # If it's the first round, choose randomly
        if round_num == 1 or not self.interrogation_history:
            return random.choice(available_targets)
        
        # Otherwise, use AI to choose based on previous interactions
        prompt = self._create_target_selection_prompt(ai_player, available_targets, round_num)
        response = ai_player._call_openai_api(prompt)
        
        # Extract the character name from the response
        for target in available_targets:
            if target.name in response:
                return target
        
        # Default to random selection if no match found
        return random.choice(available_targets)
    
    def _create_target_selection_prompt(self, ai_player, available_targets, round_num):
        """Create prompt for selecting an interrogation target."""
        # Build history of previous interrogations
        history = ""
        for r in range(1, round_num):
            if r in self.interrogation_history:
                history += f"--- ROUND {r} INTERROGATIONS ---\n"
                for data in self.interrogation_history[r]:
                    history += f"{data['interrogator'].name} asked {data['target'].name}: \"{data['question']}\"\n"
                    history += f"{data['target'].name} responded: \"{data['response']}\"\n\n"
        
        # Build suspicion history
        suspicion_history = ""
        for char in self.characters:
            if char.suspicions:
                suspicion_history += f"{char.name}'s suspicions:\n"
                for r, suspicion in enumerate(char.suspicions):
                    suspicion_history += f"After round {r+1}: \"{suspicion}\"\n"
                suspicion_history += "\n"
        
        # Create the prompt
        target_names = [t.name for t in available_targets]
        return f"""
        You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
        
        {ai_player.character.get_prompt_description()}
        
        This is round {round_num} of the interrogation phase. You need to choose someone to interrogate.
        
        Previous interrogations:
        {history}
        
        Suspicions expressed so far:
        {suspicion_history}
        
        You can interrogate one of these characters: {', '.join(target_names)}
        
        Which character do you want to interrogate? 
        
        There is only one human so focus on identifying the "odd one out" from the group based on previous interactions.
        Look for patterns in how most characters respond, and identify which character breaks that pattern.
        Consider factors like response style, consistency, and uniqueness compared to the group.
        
        Respond with ONLY the character's name.
        """
    
    def _generate_question(self, ai_player, target, round_num):
        """Generate a targeted question for another character."""
        # Build history of previous interactions with this target
        history = ""
        for r in range(1, round_num):
            if r in self.interrogation_history:
                for data in self.interrogation_history[r]:
                    if data['target'] == target:
                        history += f"In round {r}, {data['interrogator'].name} asked: \"{data['question']}\"\n"
                        history += f"{target.name} responded: \"{data['response']}\"\n\n"
        
        # Create the prompt
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
        
        {ai_player.character.get_prompt_description()}
        
        You want to determine if {target.name} is the human or an AI.
        
        About {target.name}:
        {target.get_prompt_description()}
        
        Previous interactions with {target.name}:
        {history}
        
        Generate ONE specific question to ask {target.name} that might reveal whether they are the human or an AI.
        The question should be challenging but answerable in 1-2 sentences.
        Use your character's speech style.
        Make your question clever and designed to reveal if they break the pattern of the AI group.
        """
        
        return ai_player._call_openai_api(prompt)
    
    def _generate_response(self, ai_player, question, questioner):
        """Generate a response to an interrogation question."""
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
        
        {ai_player.character.get_prompt_description()}
        
        {questioner.name} has asked you the following question:
        "{question}"
        
        Respond to this question in 1-2 sentences, staying true to your character's personality and speech style.
        Remember that you are trying to appear as an AI character would, not revealing any human traits.
        """
        
        return ai_player._call_openai_api(prompt)
    
    def _generate_suspicion(self, ai_player, round_num):
        """Generate suspicions based on interrogations."""
        # Build history of all interrogations in this round
        round_history = ""
        if round_num in self.interrogation_history:
            for data in self.interrogation_history[round_num]:
                round_history += f"{data['interrogator'].name} asked {data['target'].name}: \"{data['question']}\"\n"
                round_history += f"{data['target'].name} responded: \"{data['response']}\"\n\n"
        
        # Create the prompt
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
        
        {ai_player.character.get_prompt_description()}
        
        This is round {round_num} of the game. You need to express your suspicions about who might be the human player.
        
        Interrogations from this round:
        {round_history}
        
        As {ai_player.character.name}, analyze the interactions and identify which character seems different from the others. This is likely the human.
        Look for patterns in how most characters respond, and identify which character breaks that pattern.
        Consider factors like response style, consistency with previous answers, and uniqueness compared to the group.
        
        Express your suspicions about who might be the human player in 1-2 sentences.
        Use your character's speech style. Name specifically who you are suspecting and why they stand out from the group.
        """
        
        return ai_player._call_openai_api(prompt)
    
    def _generate_vote(self, ai_player):
        """Generate final vote on who is the human."""
        # Build complete history of all interrogations
        full_history = ""
        for round_num in sorted(self.interrogation_history.keys()):
            full_history += f"--- ROUND {round_num} INTERROGATIONS ---\n"
            for data in self.interrogation_history[round_num]:
                full_history += f"{data['interrogator'].name} asked {data['target'].name}: \"{data['question']}\"\n"
                full_history += f"{data['target'].name} responded: \"{data['response']}\"\n\n"
        
        # Build suspicion history
        suspicion_history = ""
        for char in self.characters:
            if char.suspicions:
                suspicion_history += f"{char.name}'s suspicions:\n"
                for r, suspicion in enumerate(char.suspicions):
                    suspicion_history += f"After round {r+1}: \"{suspicion}\"\n"
                suspicion_history += "\n"
        
        # Create the prompt
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
        Your goal is to identify the human based on their responses throughout the game.
        
        {ai_player.character.get_prompt_description()}
        
        Here is the complete game history:
        
        INTERROGATIONS:
        {full_history}
        
        SUSPICIONS:
        {suspicion_history}
        
        Analyze all interactions and suspicions to identify which character is the "odd one out" from the group. This is likely the human.
        Look for patterns that most characters follow and identify who breaks these patterns.
        Focus on identifying differences in response style, consistency, and uniqueness compared to the group.
        
        Based on your analysis of who stands out from the group, which character do you think is the human player?
        Respond with just the character's name that you're voting for.
        """
        
        vote = ai_player._call_openai_api(prompt)
        
        # Extract just the character name from the response
        for character in self.characters:
            if character.name.lower() in vote.lower():
                ai_player.character.set_vote(character.name)
                return character.name
        
        # If no clear match, use the first character mentioned
        ai_player.character.set_vote(self.characters[0].name)
        return self.characters[0].name
    
    def reset(self):
        """Reset the game state for a new game."""
        self.human_character = None
        self.ai_players = []
        self.current_round = 0
        self.interrogation_history = {}
        
        # Reset character states
        for character in self.characters:
            character.responses = []
            character.suspicions = []
            character.vote = None
            if hasattr(character, 'introduction'):
                delattr(character, 'introduction')
