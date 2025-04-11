"""
Asset management for the Reverse Turing Test game.
"""
import os
import pygame

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
LIGHT_BLUE = (100, 180, 255)
DARK_BLUE = (0, 80, 160)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
PURPLE = (180, 100, 255)

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Font sizes
TITLE_SIZE = 36
HEADING_SIZE = 24
TEXT_SIZE = 18
SMALL_SIZE = 14

class Assets:
    """Asset manager for the game."""
    
    def __init__(self):
        """Initialize assets."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reverse Turing Test")
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", TITLE_SIZE, bold=True)
        self.heading_font = pygame.font.SysFont("Arial", HEADING_SIZE, bold=True)
        self.text_font = pygame.font.SysFont("Arial", TEXT_SIZE)
        self.small_font = pygame.font.SysFont("Arial", SMALL_SIZE)
        
        # Create character avatars (colored circles with initials)
        self.avatars = self._create_avatars()
        
        # Load or create background
        self.background = self._create_background()
    
    def _create_avatars(self):
        """Create avatar images for characters."""
        avatars = {}
        colors = [BLUE, GREEN, RED, YELLOW, PURPLE]
        
        from character import get_character_profiles
        characters = get_character_profiles()
        
        for i, character in enumerate(characters):
            # Create a surface for the avatar
            avatar = pygame.Surface((60, 60), pygame.SRCALPHA)
            
            # Draw circle with character color
            pygame.draw.circle(avatar, colors[i % len(colors)], (30, 30), 30)
            
            # Get character initials
            name_parts = character.name.split()
            initials = "".join([part[0] for part in name_parts if part[0].isupper()])
            
            # Draw initials
            text = self.heading_font.render(initials, True, WHITE)
            text_rect = text.get_rect(center=(30, 30))
            avatar.blit(text, text_rect)
            
            avatars[character.name] = avatar
        
        return avatars
    
    def _create_background(self):
        """Create a background for the game."""
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)
        
        # Add some subtle grid lines
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(background, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(background, LIGHT_GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # Add a header area
        pygame.draw.rect(background, LIGHT_BLUE, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.line(background, DARK_BLUE, (0, 80), (SCREEN_WIDTH, 80), 2)
        
        return background
    
    def draw_text(self, text, font, color, x, y, align="left", max_width=None):
        """
        Draw text on the screen with alignment options and optional wrapping.
        
        Args:
            text (str): Text to draw
            font: Pygame font object
            color: RGB color tuple
            x (int): X coordinate
            y (int): Y coordinate
            align (str): Text alignment ('left', 'center', 'right')
            max_width (int): Maximum width for text wrapping
        
        Returns:
            int: Y coordinate of the bottom of the text
        """
        if max_width:
            return self.draw_wrapped_text(text, font, color, x, y, max_width, align)
        
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
        return text_rect.bottom
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width, align="left"):
        """
        Draw text wrapped to a maximum width.
        
        Args:
            text (str): Text to draw
            font: Pygame font object
            color: RGB color tuple
            x (int): X coordinate
            y (int): Y coordinate
            max_width (int): Maximum width for wrapping
            align (str): Text alignment ('left', 'center', 'right')
        
        Returns:
            int: Y coordinate of the bottom of the text
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test width with current word added
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Start a new line if current line has content
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If a single word is too long, force it on its own line
                    lines.append(word)
                    current_line = []
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        current_y = y
        for line in lines:
            current_y = self.draw_text(line, font, color, x, current_y, align)
            current_y += font.get_linesize()
        
        return current_y
    
    def draw_button(self, text, x, y, width, height, inactive_color, active_color, text_color=WHITE, border_radius=5):
        """
        Draw a button and return if it was clicked.
        
        Args:
            text (str): Button text
            x, y (int): Button position
            width, height (int): Button dimensions
            inactive_color: Color when not hovered
            active_color: Color when hovered
            text_color: Text color
            border_radius (int): Corner radius
        
        Returns:
            bool: True if button was clicked
        """
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        # Check if mouse is over button
        button_rect = pygame.Rect(x, y, width, height)
        hover = button_rect.collidepoint(mouse_pos)
        
        # Draw the button
        color = active_color if hover else inactive_color
        pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)
        
        # Draw button text
        text_surf = self.text_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        # Check for click
        if hover and pygame.mouse.get_pressed()[0]:
            clicked = True
            # Add a small delay to prevent multiple clicks
            pygame.time.delay(200)
        
        return clicked
    
    def draw_input_box(self, x, y, width, height, text, active):
        """
        Draw a text input box.
        
        Args:
            x, y (int): Box position
            width, height (int): Box dimensions
            text (str): Current text
            active (bool): Whether box is active
        
        Returns:
            pygame.Rect: Box rectangle
        """
        # Draw the input box
        color = BLUE if active else GRAY
        box_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, WHITE, box_rect)
        pygame.draw.rect(self.screen, color, box_rect, 2)
        
        # Render the text
        text_surf = self.text_font.render(text, True, BLACK)
        
        # Create a smaller rect for the text to enable scrolling for long text
        text_rect = pygame.Rect(x + 5, y + 5, width - 10, height - 10)
        
        # Blit the text
        self.screen.blit(text_surf, text_rect)
        
        return box_rect
    
    def draw_character_card(self, character, x, y, width, height, selected=False):
        """
        Draw a character card.
        
        Args:
            character: Character object
            x, y (int): Card position
            width, height (int): Card dimensions
            selected (bool): Whether card is selected
        
        Returns:
            pygame.Rect: Card rectangle
        """
        # Draw card background
        card_rect = pygame.Rect(x, y, width, height)
        border_color = BLUE if selected else GRAY
        
        pygame.draw.rect(self.screen, WHITE, card_rect)
        pygame.draw.rect(self.screen, border_color, card_rect, 3 if selected else 1)
        
        # Draw avatar
        avatar = self.avatars.get(character.name)
        if avatar:
            self.screen.blit(avatar, (x + 10, y + 10))
        
        # Draw character info
        text_x = x + 80
        text_y = y + 10
        
        # Name and profile
        text_y = self.draw_text(character.name, self.heading_font, BLUE, text_x, text_y)
        text_y = self.draw_text(character.profile, self.text_font, BLACK, text_x, text_y + 5)
        
        # Personality, background, speech style
        text_y += 10
        text_y = self.draw_text("Personality:", self.small_font, DARK_GRAY, text_x, text_y)
        text_y = self.draw_wrapped_text(character.personality, self.small_font, BLACK, 
                                      text_x + 10, text_y, width - 100)
        
        text_y += 5
        text_y = self.draw_text("Background:", self.small_font, DARK_GRAY, text_x, text_y)
        text_y = self.draw_wrapped_text(character.background, self.small_font, BLACK, 
                                      text_x + 10, text_y, width - 100)
        
        text_y += 5
        text_y = self.draw_text("Speech Style:", self.small_font, DARK_GRAY, text_x, text_y)
        text_y = self.draw_wrapped_text(character.speech_style, self.small_font, BLACK, 
                                      text_x + 10, text_y, width - 100)
        
        return card_rect
    
    def draw_message_bubble(self, character_name, message, x, y, width, is_suspicion=False):
        """
        Draw a message bubble for character responses.
        
        Args:
            character_name (str): Name of the character
            message (str): Message content
            x, y (int): Bubble position
            width (int): Bubble width
            is_suspicion (bool): Whether this is a suspicion message
        
        Returns:
            int: Y coordinate of the bottom of the bubble
        """
        # Get avatar
        avatar = self.avatars.get(character_name)
        
        # Calculate padding and spacing
        padding = 10
        avatar_size = 40 if avatar else 0
        
        # Draw the message text to calculate height
        text_width = width - avatar_size - (padding * 3)
        
        # Create a temporary surface to measure text height
        temp_surf = pygame.Surface((text_width, 1000), pygame.SRCALPHA)
        temp_y = self.draw_wrapped_text(message, self.text_font, BLACK, 0, 0, text_width, "left")
        
        # Calculate bubble height
        bubble_height = max(avatar_size + (padding * 2), temp_y + (padding * 2))
        
        # Draw bubble background
        bubble_color = LIGHT_GRAY
        if is_suspicion:
            bubble_color = (255, 240, 200)  # Light yellow for suspicions
            
        bubble_rect = pygame.Rect(x, y, width, bubble_height)
        pygame.draw.rect(self.screen, bubble_color, bubble_rect, border_radius=10)
        
        # Draw avatar
        if avatar:
            # Scale down avatar for messages
            scaled_avatar = pygame.transform.scale(avatar, (avatar_size, avatar_size))
            self.screen.blit(scaled_avatar, (x + padding, y + padding))
        
        # Draw character name
        name_y = y + padding
        self.draw_text(character_name, self.text_font, BLUE, 
                     x + avatar_size + (padding * 2), name_y)
        
        # Draw message
        message_y = name_y + self.text_font.get_linesize() + 5
        self.draw_wrapped_text(message, self.text_font, BLACK, 
                             x + avatar_size + (padding * 2), message_y, text_width)
        
        return y + bubble_height
