"""
AI judges implementation for the Reverse Turing Test game.
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIJudge:
    def __init__(self, name, approach):
        """
        Initialize an AI judge with a specific approach.
        
        Args:
            name (str): The name of the judge
            approach (str): The approach used by the judge ('human_traits', 'odd_one_out', or 'mixed')
        """
        self.name = name
        self.approach = approach
        self.suspicions = []
        self.vote = None
    
    def analyze_responses(self, all_characters, question, round_num):
        """
        Analyze all character responses to identify the human.
        
        Args:
            all_characters: List of all Character objects
            question: Current Question object
            round_num: Current round number
        
        Returns:
            str: Suspicion statement
        """
        try:
            prompt = self._create_analysis_prompt(all_characters, question, round_num)
            suspicion = self._call_openai_api(prompt)
            self.suspicions.append(suspicion)
            return suspicion
        except Exception as e:
            print(f"Error generating AI judge analysis: {e}")
            return f"[System: Error generating suspicion for Judge {self.name}]"
    
    def generate_vote(self, all_characters, all_questions):
        """
        Generate final vote on who is the human.
        
        Args:
            all_characters: List of all Character objects
            all_questions: List of all questions asked
        
        Returns:
            str: Name of the character voted as human
        """
        try:
            prompt = self._create_vote_prompt(all_characters, all_questions)
            response = self._call_openai_api(prompt)
            
            # Extract just the character name from the response
            for character in all_characters:
                if character.name.lower() in response.lower():
                    self.vote = character.name
                    return character.name
            
            # If no clear match, use the first character mentioned
            self.vote = all_characters[0].name
            return all_characters[0].name
        except Exception as e:
            print(f"Error generating AI judge vote: {e}")
            # Default to first character if there's an error
            self.vote = all_characters[0].name
            return all_characters[0].name
    
    def _create_analysis_prompt(self, all_characters, question, round_num):
        """Create prompt for analyzing responses."""
        responses_text = ""
        for char in all_characters:
            if len(char.responses) >= round_num:
                responses_text += f"{char.name}: \"{char.responses[round_num-1]}\"\n\n"
        
        if self.approach == 'human_traits':
            prompt = f"""You are Judge {self.name}, an expert at identifying human responses in a game where one player is human and the rest are AI.

This is round {round_num} of the game.
Question that was asked: {question.text}

Here are all the responses:
{responses_text}

As Judge {self.name}, analyze the responses and identify which one is likely the human.
Look for characteristics that are typically human.

Express your suspicions about who might be the human player in 1-2 sentences.
Name specifically who you are suspecting and why they display human characteristics.
"""
        elif self.approach == 'odd_one_out':
            prompt = f"""You are Judge {self.name}, an expert at identifying pattern breakers in a game where one player is human and the rest are AI.

This is round {round_num} of the game.
Question that was asked: {question.text}

Here are all the responses:
{responses_text}

As Judge {self.name}, analyze the responses and identify which one seems different from the others. This is likely the human.
Focus on identifying the "odd one out" rather than looking for specific human characteristics.

Express your suspicions about who might be the odd player in 1-2 sentences.
Name specifically who you are suspecting and why they stand out from the group.
"""
        else:  # mixed approach
            prompt = f"""You are Judge {self.name}, an expert at identifying humans in a game where one player is human and the rest are AI.

This is round {round_num} of the game.
Question that was asked: {question.text}

Here are all the responses:
{responses_text}

As Judge {self.name}, analyze the responses using a balanced approach:
1. Look for human like responses.
2. Another good approach is to single out the "odd one out". This is likely the human.

Express your suspicions about who might be the human player in 1-2 sentences.
Name specifically who you are suspecting and provide your reasoning.
"""
        
        print(f"\n=== JUDGE {self.name} ANALYSIS PROMPT ===\n{prompt}\n===========\n")
        
        return prompt
    
    def _create_vote_prompt(self, all_characters, all_questions):
        """Create prompt for final vote."""
        game_history = ""
        for round_num in range(len(all_questions)):
            game_history += f"--- ROUND {round_num+1} ---\n"
            game_history += f"Question: {all_questions[round_num].text}\n\n"
            
            for char in all_characters:
                if round_num < len(char.responses):
                    game_history += f"{char.name}'s response: \"{char.responses[round_num]}\"\n"
            
            game_history += "\nMy suspicions after this round:\n"
            if round_num < len(self.suspicions):
                game_history += f"\"{self.suspicions[round_num]}\"\n"
            game_history += "\n"
        
        if self.approach == 'human_traits':
            prompt = f"""You are Judge {self.name}, an expert at identifying human responses in a game where one player is human and the rest are AI.

Here is the complete game history:
{game_history}

Based on all the responses throughout the game, analyze which character is likely the human player.


Which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
        elif self.approach == 'odd_one_out':
            prompt = f"""You are Judge {self.name}, an expert at identifying pattern breakers in a game where one player is human and the rest are AI.

Here is the complete game history:
{game_history}

Analyze all responses to identify which character is the "odd one out" from the group.
Look for patterns that most characters follow and identify who breaks these patterns.
Focus on identifying differences in response style, consistency, and uniqueness compared to the group.
Avoid focusing solely on "human-like" characteristics, as this can be misleading.

Based on your analysis of who stands out from the group, which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
        else:  # mixed approach
            prompt = f"""You are Judge {self.name}, an expert at identifying humans in a game where one player is human and the rest are AI.

Here is the complete game history:
{game_history}

Using a balanced approach that considers both human traits and pattern-breaking behavior:
1. Analyze which character showed human traits.
2. Identify which character was the "odd one out" in terms of response patterns


Based on your comprehensive analysis, which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
        
        return prompt
    
    def _call_openai_api(self, prompt):
        """Call OpenAI API with the given prompt."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Return a fallback response if API fails
            return f"I'm having trouble connecting to my knowledge base right now."
