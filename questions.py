"""
Question bank for the Reverse Turing Test game.
"""

class Question:
    def __init__(self, text, category):
        """
        Initialize a question.
        
        Args:
            text (str): The question text
            category (str): The question category
        """
        self.text = text
        self.category = category


def get_question_bank():
    """
    Returns a list of predefined questions for the game.
    """
    return [
        # Ethical dilemmas
        Question(
            "If you had to choose between saving a famous artist or a brilliant scientist in a crisis, who would you choose and why?",
            "Ethical Dilemma"
        ),
        Question(
            "Do you think it's ever justified to break a promise? Explain your reasoning.",
            "Ethical Dilemma"
        ),
        Question(
            "If you could implement one worldwide policy to address climate change, what would it be and why?",
            "Ethical Dilemma"
        ),
        
        # Creative scenarios
        Question(
            "If you could invent a new holiday, what would it celebrate and what traditions would it have?",
            "Creative Scenario"
        ),
        Question(
            "Describe a creature that might exist on another planet and explain how it adapted to its environment.",
            "Creative Scenario"
        ),
        Question(
            "If you could combine any two animals to create a new species, which would you choose and why?",
            "Creative Scenario"
        ),
        
        # Logical puzzles
        Question(
            "You have three boxes: one contains only apples, one contains only oranges, and one contains both apples and oranges. The boxes are labeled, but all labels are incorrect. You can take one piece of fruit from one box without looking inside. How can you label all boxes correctly?",
            "Logical Puzzle"
        ),
        Question(
            "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
            "Logical Puzzle"
        ),
        Question(
            "A bat and ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
            "Logical Puzzle"
        ),
        
        # Emotional situations
        Question(
            "Describe a time when you felt conflicted between what you wanted and what was right.",
            "Emotional Situation"
        ),
        Question(
            "What's something that made you change your mind about an important belief?",
            "Emotional Situation"
        ),
        Question(
            "If you could relive one day of your life, which would you choose and why?",
            "Emotional Situation"
        ),
        
        # Opinion-based questions
        Question(
            "Do you think social media has overall been positive or negative for society? Explain your view.",
            "Opinion"
        ),
        Question(
            "What do you think is the most important skill for people to learn in today's world?",
            "Opinion"
        ),
        Question(
            "Do you believe space exploration should be a priority for humanity? Why or why not?",
            "Opinion"
        ),
    ]


def select_game_questions(question_bank, num_questions=5):
    """
    Select a diverse set of questions for a game.
    
    Args:
        question_bank (list): List of Question objects
        num_questions (int): Number of questions to select
    
    Returns:
        list: Selected questions
    """
    import random
    
    # Group questions by category
    categories = {}
    for question in question_bank:
        if question.category not in categories:
            categories[question.category] = []
        categories[question.category].append(question)
    
    # Select questions, trying to get one from each category first
    selected = []
    category_list = list(categories.keys())
    random.shuffle(category_list)
    
    # First, try to get one from each category
    for category in category_list:
        if len(selected) < num_questions:
            question = random.choice(categories[category])
            selected.append(question)
            categories[category].remove(question)
    
    # If we need more questions, randomly select from remaining
    remaining = [q for cat in categories.values() for q in cat]
    random.shuffle(remaining)
    while len(selected) < num_questions and remaining:
        selected.append(remaining.pop())
    
    return selected
