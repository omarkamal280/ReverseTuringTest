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
        """
        prompt = self._create_vote_prompt(all_characters, all_questions)
        response = self._call_openai_api(prompt)
        
        # Extract the character name from the response
        for char in all_characters:
            if char.name.lower() in response.lower():
                return char.name
        
        # If no character name found, return a random one
        return random.choice([char.name for char in all_characters])
        
    def discuss(self, other_judges, all_characters, all_questions, max_rounds=3):
        """Discuss with other judges to try to reach a consensus."""
        # Initial votes from all judges
        judge_votes = {}
        for judge in [self] + other_judges:
            judge_votes[judge.name] = judge.generate_vote(all_characters, all_questions)
            
        # Check if there's already a consensus
        vote_counts = {}
        for vote in judge_votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
            
        # If all judges agree, no need for discussion
        if len(vote_counts) == 1:
            return list(judge_votes.values())[0], []
            
        # Start discussion
        discussion_history = []
        current_round = 1
        consensus_reached = False
        
        print(f"\n=== STARTING JUDGE DISCUSSION ===\n")
        print(f"Initial votes: {judge_votes}\n")
        
        while current_round <= max_rounds and not consensus_reached:
            print(f"\n--- DISCUSSION ROUND {current_round} ---")
            round_messages = []
            
            # Create the discussion prompt
            discussion_prompt = self._create_discussion_prompt(
                judge_votes, discussion_history, all_characters, all_questions, current_round
            )
            
            # Each judge contributes to the discussion
            for judge in [self] + other_judges:
                print(f"Getting response from Judge {judge.name}...")
                judge_message = judge._call_openai_api(discussion_prompt)
                
                # Validate and clean up the judge's message
                # Remove any instances where the judge included their own name
                for name in ["Holmes:", "Watson:", "Poirot:"]:
                    if name in judge_message:
                        judge_message = judge_message.replace(name, "")
                
                # If the message is too long, truncate it
                if len(judge_message) > 300:
                    judge_message = judge_message[:297] + "..."
                
                print(f"Judge {judge.name}: {judge_message}")
                round_messages.append({"judge": judge.name, "message": judge_message})
                discussion_prompt += f"\n{judge.name}: {judge_message}"
            
            # Add this round to the discussion history
            discussion_history.append(round_messages)
            print(f"Added round {current_round} to discussion history. Current history length: {len(discussion_history)}")
            
            # Update votes based on the discussion
            new_votes = {}
            for judge in [self] + other_judges:
                vote_prompt = self._create_post_discussion_vote_prompt(
                    discussion_history, judge_votes, all_characters, judge.name
                )
                response = judge._call_openai_api(vote_prompt)
                
                # Extract the character name from the response
                new_vote = None
                # Clean up the response to just get the name
                clean_response = response.strip().lower()
                
                # Try to match exact character names
                for char in all_characters:
                    if char.name.lower() == clean_response or f"{char.name.lower()}." == clean_response:
                        new_vote = char.name
                        break
                
                # If no exact match, try to find the name in the response
                if not new_vote:
                    for char in all_characters:
                        if char.name.lower() in clean_response:
                            new_vote = char.name
                            break
                
                # Log the vote extraction
                print(f"Judge {judge.name} response: '{response}' -> Extracted vote: {new_vote or 'None'}")
                
                if not new_vote:
                    new_vote = judge_votes[judge.name]  # Keep previous vote if no clear answer
                    print(f"No clear vote extracted, keeping previous vote: {new_vote}")
                    
                new_votes[judge.name] = new_vote
            
            # Update judge votes
            judge_votes = new_votes
            
            # Check if consensus is reached
            vote_counts = {}
            for vote in judge_votes.values():
                vote_counts[vote] = vote_counts.get(vote, 0) + 1
                
            if len(vote_counts) == 1:
                consensus_reached = True
                
            current_round += 1
        
        # Determine final verdict (majority vote)
        final_votes = list(judge_votes.values())
        vote_counts = {}
        for vote in final_votes:
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
            
        # Find the character with the most votes
        max_votes = 0
        final_verdict = None
        for character, count in vote_counts.items():
            if count > max_votes:
                max_votes = count
                final_verdict = character
                
        return final_verdict, discussion_history
    
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
Focus on identifying the "odd one out" rather than looking for specific human characteristics as you see this as misleading due to AI tools becoming more powerful.

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
3. You realize AI is becoming more powerful and advanced, so you must be careful in your analysis.

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
Avoid focusing solely on "human-like" characteristics, as this can be misleading with today's AI becoming more complex.

Based on your analysis of who stands out from the group, which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
        else:  # mixed approach
            prompt = f"""You are Judge {self.name}, an expert at identifying humans in a game where one player is human and the rest are AI.

Here is the complete game history:
{game_history}

Using a balanced approach that considers both human traits and pattern-breaking behavior:
1. Analyze which character showed human traits.
2. Identify which character was the "odd one out" in terms of response patterns.


Based on your comprehensive analysis, which character do you think is the human player?
Respond with just the character's name that you're voting for.
"""
        
        return prompt
    
    def _create_discussion_prompt(self, judge_votes, discussion_history, all_characters, all_questions, current_round):
        """Create prompt for judges to discuss their votes."""
        # Create a summary of the game
        game_summary = ""
        for round_num in range(len(all_questions)):
            game_summary += f"--- ROUND {round_num+1} ---\n"
            game_summary += f"Question: {all_questions[round_num].text}\n\n"
            
            for char in all_characters:
                if round_num < len(char.responses):
                    game_summary += f"{char.name}'s response: \"{char.responses[round_num]}\"\n"
            game_summary += "\n"
        
        # Create a summary of current votes
        votes_summary = "Current votes:\n"
        for judge_name, vote in judge_votes.items():
            votes_summary += f"{judge_name} votes for: {vote}\n"
        
        # Create a summary of previous discussion rounds
        discussion_summary = ""
        for round_idx, round_messages in enumerate(discussion_history):
            discussion_summary += f"\n--- DISCUSSION ROUND {round_idx + 1} ---\n"
            for message in round_messages:
                discussion_summary += f"{message['judge']}: {message['message']}\n"
        
        # Create the prompt
        prompt = f"""You are Judge {self.name} participating in a panel discussion with other judges to determine who is the human player in a game.

Game summary:
{game_summary}

{votes_summary}

{discussion_summary}

--- DISCUSSION ROUND {current_round} ---
It's now your turn to speak. Discuss your reasoning for your vote and respond to points raised by other judges.

IMPORTANT INSTRUCTIONS:
1. Speak ONLY as Judge {self.name}. Do NOT simulate dialogue from other judges or characters.
2. Do NOT include other names like "Holmes:", "Watson:", "Poirot:", etc. in your response.
3. Do NOT create fictional dialogue or conversations within your response.
4. Simply state your own opinion and reasoning directly.
5. Keep your response concise (2-3 sentences).
6. If other judges have already spoken in this round, MAKE SURE to respond to their points with your own perspective.
7. Your perspective should be UNIQUE and different from other judges - do not simply repeat what they said.
8. If you disagree with other judges, explain why. If you agree, add new insights.
"""

        # Add role-specific instructions based on the judge's approach
        if self.approach == 'human_traits':
            prompt += """
As Judge Holmes, you focus on identifying human traits in responses. Look for emotional depth, personal anecdotes, humor, or unique perspectives that suggest human thinking.
"""
        elif self.approach == 'odd_one_out':
            prompt += """
As Judge Watson, you focus on identifying pattern breakers. Look for responses that stand out from the group in terms of style, structure, or content that break AI patterns.
"""
        else:  # mixed approach
            prompt += """
As Judge Poirot, you use a balanced approach that considers both human traits and pattern-breaking behavior. You should weigh both perspectives in your analysis.
"""
            
        prompt += """

Your response should be a single, direct statement of your own thoughts that contributes new information to the discussion.
"""
        
        return prompt
    
    def _create_post_discussion_vote_prompt(self, discussion_history, previous_votes, all_characters, judge_name):
        """Create prompt for judges to vote after discussion."""
        # Create a summary of the discussion
        discussion_summary = ""
        for round_idx, round_messages in enumerate(discussion_history):
            discussion_summary += f"\n--- DISCUSSION ROUND {round_idx + 1} ---\n"
            for message in round_messages:
                discussion_summary += f"{message['judge']}: {message['message']}\n"
        
        # Create the prompt
        prompt = f"""You are Judge {judge_name} who previously voted for {previous_votes[judge_name]} as the human player.

After discussing with other judges:
{discussion_summary}

IMPORTANT INSTRUCTIONS:
1. Based on this discussion, which character do you now believe is the HUMAN player?
2. Respond with ONLY the character's name - no explanation, no dialogue, no additional text.
3. Your entire response should be a single name like "Alex" or "Jordan".
4. Do NOT include any other text, quotes, or punctuation in your response.
5. Your response must be exactly one of these character names: {', '.join([char.name for char in all_characters])}

Your complete response (just the name):
"""
        
        return prompt
    
    def _call_openai_api(self, prompt):
        """Call OpenAI API with the given prompt."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
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
