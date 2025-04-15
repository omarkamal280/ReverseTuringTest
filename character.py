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
    "Alex",
    "College Student",
    "Curious, laid-back, sometimes sarcastic",
    "Studying computer science, works part-time at a coffee shop, enjoys video games",
    "Uses casual language, occasionally makes jokes, asks straightforward questions"
),
Character(
    "Maya",
    "High School Teacher",
    "Patient, observant, encouraging",
    "Teaches history, coaches debate team, loves traveling during summer breaks",
    "Clear explanations, asks thoughtful questions, occasionally shares relevant personal stories"
),
Character(
    "Raj",
    "Food Blogger",
    "Enthusiastic, friendly, detail-oriented",
    "Reviews restaurants, shares recipes online, previously worked as a chef",
    "Descriptive language, asks about preferences, makes casual food references"
),
Character(
    "Taylor",
    "Fitness Instructor",
    "Energetic, motivational, straightforward",
    "Runs a small gym, competes in triathlons, advocates for balanced lifestyle",
    "Direct communication, encouraging tone, occasionally uses fitness metaphors"
),
Character(
    "Jordan",
    "Freelance Photographer",
    "Creative, observant, easygoing",
    "Specializes in nature photography, travels frequently, sells prints online",
    "Visual descriptions, notices details, relaxed conversational style"
)

    ]
