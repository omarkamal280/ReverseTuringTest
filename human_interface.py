"""
Human interface for the Reverse Turing Test game.
"""
import os
import sys
import pygame
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

class TerminalInterface:
    """Simple terminal-based interface for the game."""
    
    def __init__(self):
        """Initialize the terminal interface."""
        self.input_buffer = ""
        self.game_mode = "standard"
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_title(self):
        """Display the game title."""
        self.clear_screen()
        print(Fore.CYAN + Style.BRIGHT + """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║             R E V E R S E   T U R I N G   T E S T             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)
    
    def display_menu(self, title, options):
        """
        Display a menu with options.
        
        Args:
            title (str): Menu title
            options (list): List of option strings
        
        Returns:
            int: Selected option index
        """
        self.display_title()
        print(Fore.YELLOW + f"\n{title}\n" + Style.RESET_ALL)
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(options):
                    return choice - 1
                print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)
    
    def get_text_input(self, prompt):
        """
        Get text input from the user.
        
        Args:
            prompt (str): Input prompt
        
        Returns:
            str: User input
        """
        print(Fore.GREEN + prompt + Style.RESET_ALL)
        return input("> ")
    
    def display_character_selection(self, characters):
        """
        Display character selection screen.
        
        Args:
            characters (list): List of Character objects
        
        Returns:
            int: Selected character index
        """
        options = []
        for char in characters:
            options.append(f"{char.name} - {char.profile}")
        
        self.display_title()
        print(Fore.YELLOW + "\nChoose your character:\n" + Style.RESET_ALL)
        
        for i, char in enumerate(characters):
            print(f"{i+1}. {Fore.CYAN}{char.name}{Style.RESET_ALL} - {char.profile}")
            print(f"   {Fore.WHITE}Personality:{Style.RESET_ALL} {char.personality}")
            print(f"   {Fore.WHITE}Background:{Style.RESET_ALL} {char.background}")
            print(f"   {Fore.WHITE}Speech Style:{Style.RESET_ALL} {char.speech_style}")
            print()
        
        while True:
            try:
                choice = int(input("Enter your choice (number): "))
                if 1 <= choice <= len(characters):
                    return choice - 1
                print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)
    
    def display_question(self, question, round_num, total_rounds):
        """
        Display a question to the player.
        
        Args:
            question (Question): Question object
            round_num (int): Current round number
            total_rounds (int): Total number of rounds
        """
        print(f"\n{Fore.YELLOW}Round {round_num}/{total_rounds}: {question.category}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{question.text}{Style.RESET_ALL}\n")
    
    def display_responses(self, characters, round_num):
        """
        Display all character responses for a round.
        
        Args:
            characters (list): List of Character objects
            round_num (int): Round number (0-indexed)
        """
        print(f"\n{Fore.YELLOW}All Responses:{Style.RESET_ALL}\n")
        
        for char in characters:
            if round_num < len(char.responses):
                print(f"{Fore.CYAN}{char.name}:{Style.RESET_ALL} \"{char.responses[round_num]}\"")
                print()
    
    def display_suspicions(self, characters, round_num):
        """
        Display all character suspicions for a round.
        
        Args:
            characters (list): List of Character objects
            round_num (int): Round number (0-indexed)
        """
        print(f"\n{Fore.YELLOW}Suspicions:{Style.RESET_ALL}\n")
        
        for char in characters:
            if round_num < len(char.suspicions):
                print(f"{Fore.CYAN}{char.name}:{Style.RESET_ALL} \"{char.suspicions[round_num]}\"")
                print()
    
    def display_votes(self, characters, human_character):
        """
        Display final votes.
        
        Args:
            characters (list): List of Character objects
            human_character (Character): The human player's character
        
        Returns:
            bool: True if human won, False if human lost
        """
        # This method is kept for compatibility with the interrogation mode
        # Standard mode now uses judge votes which are displayed directly in run_voting_phase
        self.display_title()
        print(f"\n{Fore.YELLOW}Final Votes:{Style.RESET_ALL}\n")
        
        votes = {}
        for char in characters:
            if char.vote:
                if char.vote not in votes:
                    votes[char.vote] = 0
                votes[char.vote] += 1
                print(f"{Fore.CYAN}{char.name}{Style.RESET_ALL} votes for: {char.vote}")
        
        print(f"\n{Fore.YELLOW}Vote Tally:{Style.RESET_ALL}")
        for name, count in votes.items():
            print(f"{name}: {count} vote(s)")
        
        # Determine the character with the most votes
        most_votes = 0
        voted_character = None
        for name, count in votes.items():
            if count > most_votes:
                most_votes = count
                voted_character = name
        
        print(f"\n{Fore.YELLOW}The group has voted that {voted_character} is the human!{Style.RESET_ALL}")
        
        # Determine if human won or lost
        human_won = (voted_character != human_character.name)
        
        if human_won:
            print(f"\n{Fore.GREEN}Congratulations! You successfully disguised yourself as an AI.{Style.RESET_ALL}")
            print(f"The AI players thought {voted_character} was the human, but it was actually you, {human_character.name}!")
        else:
            print(f"\n{Fore.RED}You've been discovered! The AI players correctly identified you as the human.{Style.RESET_ALL}")
        
        return human_won
        
    def display_judge_analysis(self, judge_name, suspicion):
        """Display a judge's analysis of the responses.
        
        Args:
            judge_name (str): Name of the judge
            suspicion (str): Judge's suspicion statement
        """
        print(f"\n{Fore.MAGENTA}Judge {judge_name}:{Style.RESET_ALL} \"{suspicion}\"")
    
    def display_game_over(self, human_won):
        """
        Display game over screen.
        
        Args:
            human_won (bool): Whether the human player won
        """
        input("\nPress Enter to continue...")
        self.display_title()
        
        if human_won:
            print(f"\n{Fore.GREEN}GAME OVER - YOU WIN!{Style.RESET_ALL}")
            if self.game_mode == "standard":
                print("\nYou successfully disguised yourself as an AI and fooled the judges.")
            else:
                print("\nYou successfully disguised yourself as an AI and fooled the other players.")
        else:
            print(f"\n{Fore.RED}GAME OVER - YOU LOSE!{Style.RESET_ALL}")
            if self.game_mode == "standard":
                print("\nThe judges saw through your disguise and identified you as the human.")
            else:
                print("\nThe AI players saw through your disguise and identified you as the human.")
        
        print("\nThanks for playing the Reverse Turing Test!")
        input("\nPress Enter to exit...")
        
    # Interrogation Mode Methods
    
    def display_interrogation_mode_intro(self):
        """Display introduction to interrogation mode."""
        self.clear_screen()
        print(Fore.CYAN + Style.BRIGHT + """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       I N T E R R O G A T I O N    M O D E                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)
        
        print("In this mode, characters will introduce themselves and then take turns")
        print("interrogating each other to determine who is the human player.")
        print("\nThe game consists of:")
        print("1. Character introductions")
        print("2. Multiple rounds of interrogations")
        print("3. Suspicion statements after each round")
        print("4. Final voting")
        print("\nYour goal is to blend in as an AI character and avoid being identified as the human.")
    
    def display_introductions(self, characters):
        """Display all character introductions."""
        self.clear_screen()
        print(f"\n{Fore.YELLOW}Character Introductions:{Style.RESET_ALL}\n")
        
        for char in characters:
            if hasattr(char, 'introduction'):
                print(f"{Fore.CYAN}{char.name}:{Style.RESET_ALL} \"{char.introduction}\"")
                print()
    
    def get_interrogation_target(self, interrogator_name, available_targets):
        """Let human player choose who to interrogate."""
        print(f"\n{Fore.YELLOW}As {interrogator_name}, choose a character to interrogate:{Style.RESET_ALL}\n")
        
        for i, target in enumerate(available_targets, 1):
            print(f"{i}. {target}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(available_targets):
                    return choice - 1
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
    
    def get_interrogation_question(self, interrogator_name, target_name):
        """Let human player create an interrogation question."""
        print(f"\n{Fore.YELLOW}As {interrogator_name}, create a question to ask {target_name}:{Style.RESET_ALL}")
        print("Make your question challenging but answerable in 1-2 sentences.")
        return input("> ")
    
    def display_interrogation_question(self, interrogator_name, target_name, question):
        """Display an interrogation question."""
        print(f"\n{Fore.CYAN}{interrogator_name} asks {target_name}:{Style.RESET_ALL}")
        print(f"\"{question}\"")
    
    def get_interrogation_response(self, responder_name, interrogator_name, question):
        """Let human player respond to an interrogation."""
        print(f"\n{Fore.YELLOW}As {responder_name}, respond to {interrogator_name}'s question:{Style.RESET_ALL}")
        print("Remember to stay in character and try to appear as an AI would.")
        return input("> ")
    
    def display_interrogation_response(self, responder_name, response):
        """Display a response to an interrogation."""
        print(f"\n{Fore.CYAN}{responder_name} responds:{Style.RESET_ALL}")
        print(f"\"{response}\"")
    
    def display_interrogation_analysis(self, analyzer_name, analysis):
        """Display an analysis of an interrogation."""
        print(f"\n{Fore.CYAN}{analyzer_name}'s analysis:{Style.RESET_ALL}")
        print(f"\"{analysis}\"")


class GraphicalInterface:
    """Pygame-based graphical interface for the game."""
    
    def __init__(self, width=800, height=600):
        """
        Initialize the graphical interface.
        
        Args:
            width (int): Window width
            height (int): Window height
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Reverse Turing Test")
        
        # Define colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 120, 255)
        self.DARK_BLUE = (0, 80, 160)
        self.RED = (255, 100, 100)
        self.GREEN = (100, 255, 100)
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.heading_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Text input variables
        self.input_text = ""
        self.input_active = False
    
    def draw_text(self, text, font, color, x, y, align="left"):
        """Draw text on the screen with alignment options."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "center":
            text_rect.center = (x, y)
        elif align == "right":
            text_rect.right = x
            text_rect.top = y
        else:  # left align
            text_rect.left = x
            text_rect.top = y
            
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_button(self, text, x, y, width, height, inactive_color, active_color):
        """Draw a button and return if it was clicked."""
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        # Check if mouse is over button
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            pygame.draw.rect(self.screen, active_color, (x, y, width, height))
            
            # Check for click
            if pygame.mouse.get_pressed()[0]:
                clicked = True
                # Add a small delay to prevent multiple clicks
                pygame.time.delay(300)
        else:
            pygame.draw.rect(self.screen, inactive_color, (x, y, width, height))
        
        # Draw button text
        text_rect = self.draw_text(text, self.text_font, self.WHITE, x + width/2, y + height/2, align="center")
        
        return clicked
    
    def draw_input_box(self, x, y, width, height, text=""):
        """Draw a text input box and handle input events."""
        # Draw the input box
        color = self.BLUE if self.input_active else self.GRAY
        pygame.draw.rect(self.screen, color, (x, y, width, height), 2)
        
        # Render the text
        text_surface = self.text_font.render(text, True, self.BLACK)
        
        # Blit the text
        self.screen.blit(text_surface, (x + 5, y + 5))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the user clicked on the input box
                if x <= event.pos[0] <= x + width and y <= event.pos[1] <= y + height:
                    self.input_active = True
                else:
                    self.input_active = False
            
            if event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_RETURN:
                    temp = text
                    self.input_text = ""
                    return temp
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        
        return None
    
    def display_title_screen(self):
        """Display the title screen and wait for user to start."""
        self.screen.fill(self.WHITE)
        
        # Draw title
        self.draw_text("REVERSE TURING TEST", self.title_font, self.BLUE, self.width/2, 100, align="center")
        self.draw_text("Can you disguise yourself as an AI?", self.heading_font, self.BLACK, self.width/2, 150, align="center")
        
        # Draw start button
        start_clicked = self.draw_button("Start Game", self.width/2 - 100, 300, 200, 50, self.BLUE, self.DARK_BLUE)
        
        # Draw exit button
        exit_clicked = self.draw_button("Exit", self.width/2 - 100, 400, 200, 50, self.RED, (200, 0, 0))
        
        pygame.display.flip()
        
        if exit_clicked:
            pygame.quit()
            sys.exit()
        
        return start_clicked
    
    # Additional methods for the graphical interface would be implemented here
    # For brevity, I'm not implementing the full graphical interface
    # The terminal interface will be used as the primary interface for now
