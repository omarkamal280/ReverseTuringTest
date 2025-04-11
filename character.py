"""
Character profiles and management for the Reverse Turing Test game.
"""

class Character:
    def __init__(self, name, profile, personality, background, speech_style):
        """
        Initialize a character with specific traits.
        
        Args:
            name (str): Character name
            profile (str): Short profile description
            personality (str): Personality traits
            background (str): Character background
            speech_style (str): Typical speech patterns
        """
        self.name = name
        self.profile = profile
        self.personality = personality
        self.background = background
        self.speech_style = speech_style
        self.responses = []
        self.suspicions = []
        self.vote = None
    
    def get_prompt_description(self):
        """
        Returns a description suitable for AI prompt context.
        """
        return (f"Character: {self.name}\n"
                f"Profile: {self.profile}\n"
                f"Personality: {self.personality}\n"
                f"Background: {self.background}\n"
                f"Speech Style: {self.speech_style}")
    
    def add_response(self, response):
        """Add a response to this character's history."""
        self.responses.append(response)
    
    def add_suspicion(self, suspicion):
        """Add a suspicion statement to this character's history."""
        self.suspicions.append(suspicion)
    
    def set_vote(self, character_name):
        """Set this character's vote for who they think is human."""
        self.vote = character_name


# Define the 5 character profiles
def get_character_profiles():
    """
    Returns a list of predefined character profiles.
    """
    return [
        Character(
            "Dr. Alex Morgan",
            "Tech Expert",
            "Analytical, precise, detail-oriented, and methodical",
            "Ph.D. in Computer Science with 15 years of experience in AI research",
            "Uses technical terminology, precise language, often references research papers and technical concepts"
        ),
        Character(
            "Riley Jordan",
            "Creative Artist",
            "Imaginative, emotional, expressive, and intuitive",
            "Multimedia artist with background in painting, digital art, and installation art",
            "Uses metaphors, descriptive language, references emotions and sensory experiences"
        ),
        Character(
            "Sam Taylor",
            "Logical Analyst",
            "Rational, structured, objective, and systematic",
            "Background in data analysis and strategic consulting",
            "Concise, factual statements, often lists points, avoids emotional language"
        ),
        Character(
            "Jamie Wilson",
            "Casual Gamer",
            "Relaxed, enthusiastic, playful, and sociable",
            "Avid video game player and online community member",
            "Informal language, uses gaming references, slang, and pop culture references"
        ),
        Character(
            "Professor Pat Chen",
            "Academic Scholar",
            "Thoughtful, nuanced, inquisitive, and thorough",
            "University professor specializing in philosophy and ethics",
            "Formal language, references theories and studies, poses questions, considers multiple perspectives"
        )
    ]
