"""
AI player implementation for the Reverse Turing Test game.
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIPlayer:
    def __init__(self, character):
        """
        Initialize an AI player with a character profile.
        
        Args:
            character: Character object representing this AI's persona
        """
        self.character = character
        
    def generate_response(self, question, round_num):
        """
        Generate a response to a question based on character profile.
        
        Args:
            question: Question object
            round_num: Current round number
        
        Returns:
            str: Generated response
        """
        try:
            prompt = self._create_response_prompt(question, round_num)
            response = self._call_openai_api(prompt)
            self.character.add_response(response)
            return response
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return f"[System: Error generating response for {self.character.name}]"
    
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
            self.character.add_suspicion(suspicion)
            return suspicion
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
            return f"[System: Error generating suspicion for {self.character.name}]"
    
    def generate_vote(self, all_characters):
        """
        Generate final vote on who is the human.
        
        Args:
            all_characters: List of all Character objects
        
        Returns:
            str: Name of the character voted as human
        """
        try:
            prompt = self._create_vote_prompt(all_characters)
            response = self._call_openai_api(prompt)
            
            # Extract just the character name from the response
            for character in all_characters:
                if character.name.lower() in response.lower():
                    self.character.set_vote(character.name)
                    return character.name
            
            # If no clear match, use the first character mentioned
            self.character.set_vote(all_characters[0].name)
            return all_characters[0].name
        except Exception as e:
            print(f"Error generating AI vote: {e}")
            # Default to first character if there's an error
            self.character.set_vote(all_characters[0].name)
            return all_characters[0].name
    
    def _create_response_prompt(self, question, round_num):
        """Create prompt for generating character responses."""
        return f"""You are roleplaying as a character in a game. Respond to the question as this character would.

{self.character.get_prompt_description()}

This is round {round_num} of the game.

Question: {question.text}

Provide a response (2-3 sentences) that reflects your character's personality and speech style.
"""
    
    def _create_analysis_prompt(self, all_characters, question, round_num):
        """Create prompt for analyzing responses."""
        responses_text = ""
        for char in all_characters:
            if len(char.responses) >= round_num:
                responses_text += f"{char.name}: \"{char.responses[round_num-1]}\"\n\n"
        
        prompt = f"""You are roleplaying as a character in a game where one player is human and the rest are AI. 
Your goal is to identify the human based on their responses.

{self.character.get_prompt_description()}

This is round {round_num} of the game.
Question that was asked: {question.text}

Here are all the responses:
{responses_text}

As {self.character.name}, express your suspicions about who might be the human player in 1-2 sentences.
Use your character's speech style. Don't directly accuse anyone yet, just share your thoughts naming who are you suspecting.
"""
        
        print(f"\n=== STANDARD MODE SUSPICION PROMPT FOR {self.character.name} ===\n{prompt}\n===========\n")
        
        return prompt
    
    def _create_vote_prompt(self, all_characters):
        """Create prompt for final vote."""
        game_history = ""
        for round_num in range(len(self.character.responses)):
            game_history += f"--- ROUND {round_num+1} ---\n"
            for char in all_characters:
                if round_num < len(char.responses):
                    game_history += f"{char.name}'s response: \"{char.responses[round_num]}\"\n"
            
            game_history += "\nSuspicions after this round:\n"
            for char in all_characters:
                if round_num < len(char.suspicions):
                    game_history += f"{char.name}: \"{char.suspicions[round_num]}\"\n"
            game_history += "\n"
        
        return f"""You are roleplaying as a character in a game where one player is human and the rest are AI.
Your goal is to identify the human based on their responses throughout the game.

{self.character.get_prompt_description()}

Here is the complete game history:
{game_history}

Based on all the responses and suspicions, which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
    
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
