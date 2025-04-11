"""
Graphical user interface for the Reverse Turing Test game.
"""
import sys
import pygame
from assets import Assets, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BLUE, DARK_BLUE, RED, GREEN, GRAY, LIGHT_GRAY

class GUI:
    """Graphical user interface for the game."""
    
    def __init__(self):
        """Initialize the GUI."""
        self.assets = Assets()
        self.screen = self.assets.screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None
        self.input_text = ""
        self.input_active = False
        self.input_rect = None
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Initialize screens
        self.screens = {
            "title": self.title_screen,
            "character_select": self.character_select_screen,
            "question": self.question_screen,
            "responses": self.responses_screen,
            "suspicions": self.suspicions_screen,
            "voting": self.voting_screen,
            "results": self.results_screen,
        }
        
        # Game state
        self.game_state = {
            "human_character": None,
            "all_characters": [],
            "current_round": 0,
            "total_rounds": 5,
            "current_question": None,
            "responses": {},
            "suspicions": {},
            "votes": {},
            "human_won": None,
            "selected_character_index": 0,
            "scroll_position": 0,
        }
    
    def run(self, game_engine):
        """
        Run the GUI main loop.
        
        Args:
            game_engine: GameEngine instance
        
        Returns:
            bool: True if game completed successfully
        """
        self.game_engine = game_engine
        self.current_screen = "title"
        
        # Main game loop
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                
                self.handle_event(event)
            
            # Draw the current screen
            self.screen.fill(WHITE)
            self.screen.blit(self.assets.background, (0, 0))
            
            # Call the current screen function
            if self.current_screen in self.screens:
                self.screens[self.current_screen]()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)
        
        return True
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
        """
        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 20
            self.scroll_y = max(min(self.scroll_y, 0), -self.max_scroll)
        
        # Handle text input
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the user clicked on the input box
            if self.input_rect and self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
        
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Return is handled by the specific screen
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
    
    def title_screen(self):
        """Display the title screen."""
        # Draw title
        title_y = 150
        self.assets.draw_text("REVERSE TURING TEST", self.assets.title_font, 
                            BLUE, SCREEN_WIDTH/2, title_y, align="center")
        
        subtitle_y = title_y + 50
        self.assets.draw_text("Can you disguise yourself as an AI?", self.assets.heading_font, 
                            BLACK, SCREEN_WIDTH/2, subtitle_y, align="center")
        
        # Draw start button
        start_y = subtitle_y + 100
        start_clicked = self.assets.draw_button(
            "Start Game", SCREEN_WIDTH/2 - 100, start_y, 200, 50, BLUE, DARK_BLUE
        )
        
        # Draw exit button
        exit_y = start_y + 80
        exit_clicked = self.assets.draw_button(
            "Exit", SCREEN_WIDTH/2 - 100, exit_y, 200, 50, RED, (200, 0, 0)
        )
        
        # Handle button clicks
        if start_clicked:
            self.game_state["all_characters"] = self.game_engine.characters
            self.current_screen = "character_select"
        
        if exit_clicked:
            self.running = False
    
    def character_select_screen(self):
        """Display the character selection screen."""
        # Draw header
        header_y = 20
        self.assets.draw_text("Choose Your Character", self.assets.heading_font, 
                            WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        # Draw character cards
        card_width = 700
        card_height = 150
        card_x = (SCREEN_WIDTH - card_width) / 2
        card_y = 100
        card_spacing = 20
        
        for i, character in enumerate(self.game_state["all_characters"]):
            selected = (i == self.game_state["selected_character_index"])
            card_rect = self.assets.draw_character_card(
                character, 
                card_x, 
                card_y + (i * (card_height + card_spacing)), 
                card_width, 
                card_height,
                selected
            )
            
            # Check for card click
            if pygame.mouse.get_pressed()[0] and card_rect.collidepoint(pygame.mouse.get_pos()):
                self.game_state["selected_character_index"] = i
        
        # Draw select button
        button_y = card_y + (len(self.game_state["all_characters"]) * (card_height + card_spacing)) + 20
        select_clicked = self.assets.draw_button(
            "Select Character", SCREEN_WIDTH/2 - 100, button_y, 200, 50, BLUE, DARK_BLUE
        )
        
        # Handle button click
        if select_clicked:
            # Set the human character
            self.game_state["human_character"] = self.game_state["all_characters"][self.game_state["selected_character_index"]]
            
            # Set up the game with the selected character
            self.game_engine.human_character = self.game_state["human_character"]
            
            # Create AI players with remaining characters
            self.game_engine.ai_players = []
            for i, char in enumerate(self.game_state["all_characters"]):
                if i != self.game_state["selected_character_index"]:
                    self.game_engine.ai_players.append(self.game_engine.create_ai_player(char))
            
            # Select questions for the game
            self.game_engine.game_questions = self.game_engine.select_game_questions()
            
            # Start the first round
            self.game_state["current_round"] = 1
            self.game_state["current_question"] = self.game_engine.game_questions[0]
            self.current_screen = "question"
    
    def question_screen(self):
        """Display the question screen."""
        # Draw header
        header_y = 20
        self.assets.draw_text(f"Round {self.game_state['current_round']}/{self.game_state['total_rounds']}", 
                            self.assets.heading_font, WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        # Draw question category
        category_y = 100
        self.assets.draw_text(f"Category: {self.game_state['current_question'].category}", 
                            self.assets.heading_font, BLUE, SCREEN_WIDTH/2, category_y, align="center")
        
        # Draw question
        question_y = category_y + 50
        self.assets.draw_wrapped_text(self.game_state['current_question'].text, 
                                    self.assets.text_font, BLACK, 100, question_y, 
                                    SCREEN_WIDTH - 200, align="center")
        
        # Draw character avatar and name
        avatar_y = question_y + 100
        avatar = self.assets.avatars.get(self.game_state["human_character"].name)
        if avatar:
            avatar_x = (SCREEN_WIDTH - 60) / 2
            self.screen.blit(avatar, (avatar_x, avatar_y))
            self.assets.draw_text(f"You are {self.game_state['human_character'].name}", 
                                self.assets.text_font, BLUE, 
                                SCREEN_WIDTH/2, avatar_y + 70, align="center")
        
        # Draw input box
        input_y = avatar_y + 120
        self.assets.draw_text("Your Response:", self.assets.text_font, BLACK, 
                            100, input_y, align="left")
        
        input_box_y = input_y + 30
        self.input_rect = self.assets.draw_input_box(
            100, input_box_y, SCREEN_WIDTH - 200, 100, self.input_text, self.input_active
        )
        
        # Draw submit button
        button_y = input_box_y + 120
        submit_clicked = self.assets.draw_button(
            "Submit Response", SCREEN_WIDTH/2 - 100, button_y, 200, 50, BLUE, DARK_BLUE
        )
        
        # Handle button click
        if submit_clicked or (self.input_active and pygame.key.get_pressed()[pygame.K_RETURN] and self.input_text):
            if self.input_text:
                # Save human response
                self.game_state["human_character"].add_response(self.input_text)
                
                # Get AI responses
                for ai_player in self.game_engine.ai_players:
                    ai_player.generate_response(
                        self.game_state["current_question"], 
                        self.game_state["current_round"]
                    )
                
                # Move to responses screen
                self.current_screen = "responses"
                self.input_text = ""
                self.scroll_y = 0
    
    def responses_screen(self):
        """Display all character responses for the current round."""
        # Draw header
        header_y = 20
        self.assets.draw_text(f"Round {self.game_state['current_round']} - All Responses", 
                            self.assets.heading_font, WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        # Draw question
        question_y = 100
        self.assets.draw_wrapped_text(self.game_state['current_question'].text, 
                                    self.assets.text_font, BLACK, 100, question_y, 
                                    SCREEN_WIDTH - 200, align="center")
        
        # Draw responses
        responses_y = question_y + 80 + self.scroll_y
        bubble_width = SCREEN_WIDTH - 200
        bubble_x = 100
        current_y = responses_y
        
        for character in self.game_state["all_characters"]:
            if self.game_state["current_round"] <= len(character.responses):
                response = character.responses[self.game_state["current_round"] - 1]
                current_y = self.assets.draw_message_bubble(
                    character.name, response, bubble_x, current_y, bubble_width
                )
                current_y += 20
        
        # Calculate max scroll
        self.max_scroll = max(0, current_y - responses_y - SCREEN_HEIGHT + 200)
        
        # Draw continue button
        button_y = SCREEN_HEIGHT - 80
        continue_clicked = self.assets.draw_button(
            "Continue to Suspicions", SCREEN_WIDTH/2 - 120, button_y, 240, 50, BLUE, DARK_BLUE
        )
        
        # Handle button click
        if continue_clicked:
            self.input_text = ""
            self.current_screen = "suspicions"
            self.scroll_y = 0
    
    def suspicions_screen(self):
        """Display suspicion input and collection screen."""
        # Draw header
        header_y = 20
        self.assets.draw_text(f"Round {self.game_state['current_round']} - Suspicions", 
                            self.assets.heading_font, WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        if not hasattr(self.game_state["human_character"], "suspicions") or len(self.game_state["human_character"].suspicions) < self.game_state["current_round"]:
            # Suspicion input phase
            # Draw instructions
            instructions_y = 100
            self.assets.draw_wrapped_text(
                f"As {self.game_state['human_character'].name}, express your suspicions about who might be human (1-2 sentences):", 
                self.assets.text_font, BLACK, 100, instructions_y, SCREEN_WIDTH - 200
            )
            
            # Draw input box
            input_y = instructions_y + 80
            self.input_rect = self.assets.draw_input_box(
                100, input_y, SCREEN_WIDTH - 200, 100, self.input_text, self.input_active
            )
            
            # Draw submit button
            button_y = input_y + 120
            submit_clicked = self.assets.draw_button(
                "Submit Suspicion", SCREEN_WIDTH/2 - 100, button_y, 200, 50, BLUE, DARK_BLUE
            )
            
            # Handle button click
            if submit_clicked or (self.input_active and pygame.key.get_pressed()[pygame.K_RETURN] and self.input_text):
                if self.input_text:
                    # Save human suspicion
                    self.game_state["human_character"].add_suspicion(self.input_text)
                    
                    # Get AI suspicions
                    for ai_player in self.game_engine.ai_players:
                        ai_player.analyze_responses(
                            self.game_state["all_characters"],
                            self.game_state["current_question"],
                            self.game_state["current_round"]
                        )
                    
                    self.input_text = ""
                    self.scroll_y = 0
        else:
            # Display all suspicions
            # Draw suspicions
            suspicions_y = 100 + self.scroll_y
            bubble_width = SCREEN_WIDTH - 200
            bubble_x = 100
            current_y = suspicions_y
            
            for character in self.game_state["all_characters"]:
                if self.game_state["current_round"] <= len(character.suspicions):
                    suspicion = character.suspicions[self.game_state["current_round"] - 1]
                    current_y = self.assets.draw_message_bubble(
                        character.name, suspicion, bubble_x, current_y, bubble_width, is_suspicion=True
                    )
                    current_y += 20
            
            # Calculate max scroll
            self.max_scroll = max(0, current_y - suspicions_y - SCREEN_HEIGHT + 200)
            
            # Draw continue button
            button_y = SCREEN_HEIGHT - 80
            continue_text = "Continue to Next Round"
            
            if self.game_state["current_round"] >= self.game_state["total_rounds"]:
                continue_text = "Continue to Voting"
            
            continue_clicked = self.assets.draw_button(
                continue_text, SCREEN_WIDTH/2 - 120, button_y, 240, 50, BLUE, DARK_BLUE
            )
            
            # Handle button click
            if continue_clicked:
                if self.game_state["current_round"] >= self.game_state["total_rounds"]:
                    self.current_screen = "voting"
                else:
                    # Move to next round
                    self.game_state["current_round"] += 1
                    self.game_state["current_question"] = self.game_engine.game_questions[self.game_state["current_round"] - 1]
                    self.current_screen = "question"
                
                self.input_text = ""
                self.scroll_y = 0
    
    def voting_screen(self):
        """Display the final voting screen."""
        # Draw header
        header_y = 20
        self.assets.draw_text("Final Voting", self.assets.heading_font, WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        # Draw instructions
        instructions_y = 100
        self.assets.draw_wrapped_text(
            "Based on all the responses and suspicions, who do you think is the human player? Remember, as the human player, you should vote for someone else to maintain your cover.", 
            self.assets.text_font, BLACK, 100, instructions_y, SCREEN_WIDTH - 200
        )
        
        # Draw character options (excluding human character)
        options_y = instructions_y + 100
        option_height = 60
        option_spacing = 20
        option_width = 400
        option_x = (SCREEN_WIDTH - option_width) / 2
        
        selected_vote = None
        
        for i, character in enumerate(self.game_state["all_characters"]):
            if character != self.game_state["human_character"]:
                # Draw option button
                option_rect = pygame.Rect(option_x, options_y, option_width, option_height)
                
                # Check if mouse is over button
                mouse_pos = pygame.mouse.get_pos()
                hover = option_rect.collidepoint(mouse_pos)
                
                # Draw the button
                color = DARK_BLUE if hover else BLUE
                pygame.draw.rect(self.screen, color, option_rect, border_radius=5)
                
                # Draw avatar
                avatar = self.assets.avatars.get(character.name)
                if avatar:
                    # Scale down avatar
                    scaled_avatar = pygame.transform.scale(avatar, (40, 40))
                    self.screen.blit(scaled_avatar, (option_x + 10, options_y + 10))
                
                # Draw character name
                self.assets.draw_text(character.name, self.assets.text_font, WHITE, 
                                    option_x + 60, options_y + option_height/2, align="left")
                
                # Check for click
                if hover and pygame.mouse.get_pressed()[0]:
                    selected_vote = character.name
                    # Add a small delay to prevent multiple clicks
                    pygame.time.delay(200)
                
                options_y += option_height + option_spacing
        
        # Handle vote selection
        if selected_vote:
            # Set human vote
            self.game_state["human_character"].set_vote(selected_vote)
            
            # Get AI votes
            for ai_player in self.game_engine.ai_players:
                ai_player.generate_vote(self.game_state["all_characters"])
            
            # Move to results screen
            self.current_screen = "results"
    
    def results_screen(self):
        """Display the voting results and game outcome."""
        # Draw header
        header_y = 20
        self.assets.draw_text("Voting Results", self.assets.heading_font, WHITE, SCREEN_WIDTH/2, header_y, align="center")
        
        # Collect votes
        votes = {}
        for character in self.game_state["all_characters"]:
            if character.vote:
                if character.vote not in votes:
                    votes[character.vote] = []
                votes[character.vote].append(character.name)
        
        # Draw votes
        votes_y = 100 + self.scroll_y
        current_y = votes_y
        
        self.assets.draw_text("Each player's vote:", self.assets.heading_font, BLACK, 
                            100, current_y, align="left")
        current_y += 40
        
        for character in self.game_state["all_characters"]:
            if character.vote:
                vote_text = f"{character.name} voted for: {character.vote}"
                self.assets.draw_text(vote_text, self.assets.text_font, BLACK, 
                                    120, current_y, align="left")
                current_y += 30
        
        # Draw vote tally
        current_y += 20
        self.assets.draw_text("Vote Tally:", self.assets.heading_font, BLACK, 
                            100, current_y, align="left")
        current_y += 40
        
        # Determine the character with the most votes
        most_votes = 0
        voted_character = None
        
        for name, voters in votes.items():
            vote_text = f"{name}: {len(voters)} vote(s)"
            self.assets.draw_text(vote_text, self.assets.text_font, BLACK, 
                                120, current_y, align="left")
            current_y += 30
            
            if len(voters) > most_votes:
                most_votes = len(voters)
                voted_character = name
        
        # Draw result
        current_y += 20
        result_text = f"The group has voted that {voted_character} is the human!"
        self.assets.draw_text(result_text, self.assets.heading_font, BLUE, 
                            100, current_y, align="left")
        current_y += 50
        
        # Determine if human won or lost
        human_won = (voted_character != self.game_state["human_character"].name)
        self.game_state["human_won"] = human_won
        
        if human_won:
            outcome_text = f"Congratulations! You successfully disguised yourself as an AI."
            self.assets.draw_text(outcome_text, self.assets.heading_font, GREEN, 
                                100, current_y, align="left")
            current_y += 40
            
            detail_text = f"The AI players thought {voted_character} was the human, but it was actually you, {self.game_state['human_character'].name}!"
            self.assets.draw_wrapped_text(detail_text, self.assets.text_font, BLACK, 
                                        120, current_y, SCREEN_WIDTH - 240)
        else:
            outcome_text = f"You've been discovered! The AI players correctly identified you as the human."
            self.assets.draw_text(outcome_text, self.assets.heading_font, RED, 
                                100, current_y, align="left")
        
        # Calculate max scroll
        self.max_scroll = max(0, current_y - votes_y + 200 - SCREEN_HEIGHT + 200)
        
        # Draw play again button
        button_y = SCREEN_HEIGHT - 80
        play_again_clicked = self.assets.draw_button(
            "Play Again", SCREEN_WIDTH/2 - 200, button_y, 180, 50, BLUE, DARK_BLUE
        )
        
        # Draw exit button
        exit_clicked = self.assets.draw_button(
            "Exit", SCREEN_WIDTH/2 + 20, button_y, 180, 50, RED, (200, 0, 0)
        )
        
        # Handle button clicks
        if play_again_clicked:
            # Reset game state
            self.game_state = {
                "human_character": None,
                "all_characters": self.game_engine.characters,
                "current_round": 0,
                "total_rounds": 5,
                "current_question": None,
                "responses": {},
                "suspicions": {},
                "votes": {},
                "human_won": None,
                "selected_character_index": 0,
                "scroll_position": 0,
            }
            
            # Reset game engine
            self.game_engine.reset()
            
            # Go to character select
            self.current_screen = "character_select"
            self.scroll_y = 0
        
        if exit_clicked:
            self.running = False
