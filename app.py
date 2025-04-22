"""
Flask web application for the Reverse Turing Test game.
"""
import os
import json
import random
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO
from dotenv import load_dotenv
from character import get_character_profiles
from questions import get_question_bank, select_game_questions
from ai_player import AIPlayer
from ai_judge import AIJudge

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Game state
game_states = {}

# Game modes
GAME_MODE_STANDARD = 'standard'
GAME_MODE_INTERROGATION = 'interrogation'

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """Initialize a new game."""
    data = request.json
    game_mode = data.get('game_mode', GAME_MODE_STANDARD)
    
    # Generate a unique game ID
    game_id = str(random.randint(10000, 99999))
    
    # Initialize game state
    characters = get_character_profiles()
    
    # Create base game state
    game_state = {
        'characters': characters,
        'current_round': 0,
        'human_character': None,
        'ai_players': [],
        'ai_judges': [],
        'game_mode': game_mode,
        'suspicions': {},
        'judge_suspicions': {},
        'votes': {},
        'judge_votes': {},
        'game_over': False,
        'human_won': None
    }
    
    # Add mode-specific data
    if game_mode == GAME_MODE_STANDARD:
        question_bank = get_question_bank()
        game_questions = select_game_questions(question_bank, 2)
        game_state['game_questions'] = game_questions
        game_state['responses'] = {}
        
        # Create AI judges with different approaches
        game_state['ai_judges'] = [
            {'name': 'Holmes', 'approach': 'human_traits', 'object': AIJudge('Holmes', 'human_traits')},
            {'name': 'Watson', 'approach': 'odd_one_out', 'object': AIJudge('Watson', 'odd_one_out')},
            {'name': 'Poirot', 'approach': 'mixed', 'object': AIJudge('Poirot', 'mixed')}
        ]
    elif game_mode == GAME_MODE_INTERROGATION:
        game_state['introductions'] = {}
        game_state['interrogations'] = {}
        game_state['num_rounds'] = 3  # Default to 3 rounds for interrogation mode
    
    # Store game state
    game_states[game_id] = game_state
    
    # Return game information
    return jsonify({
        'game_id': game_id,
        'game_mode': game_mode,
        'characters': [
            {
                'name': char.name,
                'profile': char.profile,
                'personality': char.personality,
                'background': char.background,
                'speech_style': char.speech_style
            }
            for char in characters
        ]
    })

@app.route('/api/select_character', methods=['POST'])
def select_character():
    """Select a character for the human player."""
    data = request.json
    game_id = data.get('game_id')
    character_index = data.get('character_index')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if character_index is None or not isinstance(character_index, int):
        return jsonify({'error': 'Invalid character index'}), 400
    
    game_state = game_states[game_id]
    characters = game_state['characters']
    
    if character_index < 0 or character_index >= len(characters):
        return jsonify({'error': 'Character index out of range'}), 400
    
    # Set human character
    game_state['human_character'] = characters[character_index]
    
    # Create AI players for remaining characters
    game_state['ai_players'] = []
    for i, char in enumerate(characters):
        if i != character_index:
            game_state['ai_players'].append(AIPlayer(char))
    
    # Start first round
    game_state['current_round'] = 1
    
    # Prepare response based on game mode
    response_data = {
        'round': 1,
        'character': {
            'name': game_state['human_character'].name,
            'profile': game_state['human_character'].profile
        }
    }
    
    # Add mode-specific data
    if game_state['game_mode'] == GAME_MODE_STANDARD:
        current_question = game_state['game_questions'][0]
        response_data['question'] = {
            'text': current_question.text,
            'category': current_question.category
        }
    
    return jsonify(response_data)

@app.route('/api/submit_response', methods=['POST'])
def submit_response():
    """Submit the human player's response to a question."""
    data = request.json
    game_id = data.get('game_id')
    response = data.get('response')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not response:
        return jsonify({'error': 'Response cannot be empty'}), 400
    
    game_state = game_states[game_id]
    current_round = game_state['current_round']
    
    if current_round < 1 or current_round > len(game_state['game_questions']):
        return jsonify({'error': 'Invalid round'}), 400
    
    # Save human response
    human_character = game_state['human_character']
    human_character.add_response(response)
    
    # Generate AI responses
    current_question = game_state['game_questions'][current_round - 1]
    for ai_player in game_state['ai_players']:
        ai_player.generate_response(current_question, current_round)
    
    # Collect all responses
    all_responses = []
    for character in game_state['characters']:
        if current_round <= len(character.responses):
            all_responses.append({
                'character_name': character.name,
                'response': character.responses[current_round - 1]
            })
    
    return jsonify({
        'round': current_round,
        'responses': all_responses
    })

@app.route('/api/submit_suspicion', methods=['POST'])
def submit_suspicion():
    """Submit the human player's suspicion."""
    data = request.json
    game_id = data.get('game_id')
    suspicion = data.get('suspicion')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not suspicion:
        return jsonify({'error': 'Suspicion cannot be empty'}), 400
    
    game_state = game_states[game_id]
    current_round = game_state['current_round']
    
    if current_round < 1 or current_round > len(game_state['game_questions']):
        return jsonify({'error': 'Invalid round'}), 400
    
    # Save human suspicion
    human_character = game_state['human_character']
    human_character.add_suspicion(suspicion)
    
    # In standard mode, AI players don't generate suspicions anymore - only judges do
    current_question = game_state['game_questions'][current_round - 1]
    
    # Generate AI judge suspicions
    judge_suspicions = []
    if current_round not in game_state['judge_suspicions']:
        game_state['judge_suspicions'][current_round] = []
    
    for judge_data in game_state['ai_judges']:
        judge = judge_data['object']
        suspicion = judge.analyze_responses(
            game_state['characters'],
            current_question,
            current_round
        )
        judge_suspicions.append({
            'judge_name': judge.name,
            'approach': judge_data['approach'],
            'suspicion': suspicion
        })
        game_state['judge_suspicions'][current_round].append({
            'judge_name': judge.name,
            'suspicion': suspicion
        })
    
    # Collect human suspicion only
    all_suspicions = [{
        'character_name': game_state['human_character'].name,
        'suspicion': suspicion
    }]
    
    # Determine if we should move to the next round or to voting
    next_action = 'next_round'
    next_round = current_round + 1
    next_question = None
    
    if next_round > len(game_state['game_questions']):
        next_action = 'voting'
    else:
        game_state['current_round'] = next_round
        next_question = game_state['game_questions'][next_round - 1]
        next_question = {
            'text': next_question.text,
            'category': next_question.category
        }
    
    return jsonify({
        'round': current_round,
        'suspicions': all_suspicions,
        'judge_suspicions': judge_suspicions,
        'next_action': next_action,
        'next_round': next_round if next_action == 'next_round' else None,
        'next_question': next_question
    })

@app.route('/api/submit_vote', methods=['POST'])
def submit_vote():
    """Submit the human player's vote."""
    data = request.json
    game_id = data.get('game_id')
    vote = data.get('vote')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not vote:
        return jsonify({'error': 'Vote cannot be empty'}), 400
    
    game_state = game_states[game_id]
    
    # Different voting logic based on game mode
    if game_state['game_mode'] == GAME_MODE_STANDARD:
        # In standard mode, only judges vote (not AI players)
        # Save human vote for compatibility, but it won't be used in determining the winner
        human_character = game_state['human_character']
        human_character.set_vote(vote)
        
        # Generate AI judge votes
        judge_votes = {}
        for judge_data in game_state['ai_judges']:
            judge = judge_data['object']
            vote = judge.generate_vote(game_state['characters'], game_state['game_questions'])
            judge_votes[judge.name] = vote
        
        # Store judge votes in game state
        game_state['judge_votes'] = judge_votes
        
        # Determine the majority vote
        vote_counts = {}
        for vote in judge_votes.values():
            if vote not in vote_counts:
                vote_counts[vote] = 0
            vote_counts[vote] += 1
        
        most_votes = 0
        voted_character = None
        for name, count in vote_counts.items():
            if count > most_votes:
                most_votes = count
                voted_character = name
        
        # Determine if human won or lost
        human_won = (voted_character != human_character.name)
        game_state['human_won'] = human_won
        game_state['game_over'] = True
        
        return jsonify({
            'judge_votes': judge_votes,
            'vote_counts': vote_counts,
            'voted_character': voted_character,
            'human_character': human_character.name,
            'human_won': human_won
        })
    else:  # GAME_MODE_INTERROGATION
        # Original voting logic for interrogation mode
        # Save human vote
        human_character = game_state['human_character']
        human_character.set_vote(vote)
        
        # Generate AI votes
        for ai_player in game_state['ai_players']:
            ai_player.generate_vote(game_state['characters'])
        
        # Collect all votes
        all_votes = {}
        for character in game_state['characters']:
            if character.vote:
                if character.vote not in all_votes:
                    all_votes[character.vote] = []
                all_votes[character.vote].append(character.name)
        
        # Determine the character with the most votes
        most_votes = 0
        voted_character = None
        
        for name, voters in all_votes.items():
            if len(voters) > most_votes:
                most_votes = len(voters)
                voted_character = name
        
        # Determine if human won or lost
        human_won = (voted_character != human_character.name)
        game_state['human_won'] = human_won
        game_state['game_over'] = True
        
        return jsonify({
            'votes': {name: voters for name, voters in all_votes.items()},
            'voted_character': voted_character,
            'human_character': human_character.name,
            'human_won': human_won
        })

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    """Reset the game state for a new game."""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id and game_id in game_states:
        # Remove the game state
        del game_states[game_id]
    
    return jsonify({'success': True})

# Interrogation Mode API Endpoints

@app.route('/api/submit_introduction', methods=['POST'])
def submit_introduction():
    """Submit the human player's introduction."""
    data = request.json
    game_id = data.get('game_id')
    introduction = data.get('introduction')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not introduction:
        return jsonify({'error': 'Introduction cannot be empty'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    # Save human introduction
    human_character = game_state['human_character']
    human_character.introduction = introduction
    game_state['introductions'][human_character.name] = introduction
    
    # Generate AI introductions
    for ai_player in game_state['ai_players']:
        # Generate introduction
        prompt = f"""
        You are roleplaying as {ai_player.character.name} in a game.
        
        {ai_player.character.get_prompt_description()}
        
        Introduce yourself to the group in 1-2 sentences. Stay true to your character's personality and speech style.
        Don't reveal that you're an AI - just introduce yourself naturally as your character would.
        """
        
        introduction = ai_player._call_openai_api(prompt)
        ai_player.character.introduction = introduction
        game_state['introductions'][ai_player.character.name] = introduction
    
    # Collect all introductions
    all_introductions = []
    for character in game_state['characters']:
        if character.name in game_state['introductions']:
            all_introductions.append({
                'character_name': character.name,
                'introduction': game_state['introductions'][character.name]
            })
    
    return jsonify({
        'introductions': all_introductions
    })

@app.route('/api/start_interrogation_round', methods=['POST'])
def start_interrogation_round():
    """Start a new interrogation round."""
    data = request.json
    game_id = data.get('game_id')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    # Set round number (only increment if not the first interrogation round)
    if 'interrogation_started' not in game_state:
        # First interrogation round - keep current_round at 1
        current_round = 1
        game_state['current_round'] = 1
        game_state['interrogation_started'] = True
    else:
        # Subsequent rounds - increment
        current_round = game_state['current_round'] + 1
        game_state['current_round'] = current_round
    
    # Initialize round data
    if 'interrogation_order' not in game_state:
        # Determine interrogation order (random)
        game_state['interrogation_order'] = list(range(len(game_state['characters'])))
        random.shuffle(game_state['interrogation_order'])
    
    # Initialize round data
    if current_round not in game_state['interrogations']:
        game_state['interrogations'][current_round] = []
    
    # Return round information
    return jsonify({
        'round': current_round,
        'total_rounds': game_state['num_rounds'],
        'interrogation_order': [
            game_state['characters'][i].name for i in game_state['interrogation_order']
        ]
    })

@app.route('/api/get_interrogation_turn', methods=['POST'])
def get_interrogation_turn():
    """Get the next interrogation turn in the current round."""
    data = request.json
    game_id = data.get('game_id')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    current_round = game_state['current_round']
    round_interrogations = game_state['interrogations'].get(current_round, [])
    
    # Check if all interrogations for this round are complete
    if len(round_interrogations) >= len(game_state['characters']):
        return jsonify({
            'round_complete': True,
            'round': current_round
        })
    
    # Get the next interrogator
    interrogator_idx = game_state['interrogation_order'][len(round_interrogations)]
    interrogator = game_state['characters'][interrogator_idx]
    
    # Get available targets (all characters except the interrogator)
    available_targets = [char.name for char in game_state['characters'] 
                       if char.name != interrogator.name]
    
    # If this is the human's turn to interrogate
    is_human_turn = (interrogator == game_state['human_character'])
    
    # If it's an AI's turn, choose target and generate question
    ai_question = None
    ai_target = None
    
    if not is_human_turn and available_targets:
        # Find the AI player
        ai_player = next(ai for ai in game_state['ai_players'] 
                       if ai.character == interrogator)
        
        # Choose target
        target_name = _choose_ai_interrogation_target(ai_player, available_targets, game_state)
        ai_target = target_name
        
        # Generate question
        target_character = next(char for char in game_state['characters'] 
                             if char.name == target_name)
        ai_question = _generate_ai_question(ai_player, target_character, current_round, game_state)
    
    return jsonify({
        'round_complete': False,
        'round': current_round,
        'interrogator': interrogator.name,
        'is_human_turn': is_human_turn,
        'available_targets': available_targets,
        'ai_target': ai_target,
        'ai_question': ai_question
    })

@app.route('/api/submit_interrogation', methods=['POST'])
def submit_interrogation():
    """Submit an interrogation (question and target)."""
    data = request.json
    game_id = data.get('game_id')
    target_name = data.get('target')
    question = data.get('question')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not target_name or not question:
        return jsonify({'error': 'Target and question are required'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    current_round = game_state['current_round']
    round_interrogations = game_state['interrogations'].get(current_round, [])
    
    # Get the current interrogator
    interrogator_idx = game_state['interrogation_order'][len(round_interrogations)]
    interrogator = game_state['characters'][interrogator_idx]
    
    # Find target character
    target_character = next((char for char in game_state['characters'] 
                          if char.name == target_name), None)
    
    if not target_character:
        return jsonify({'error': 'Invalid target'}), 400
    
    # If target is human, we'll get their response later
    # If target is AI, generate response now
    response = None
    
    if target_character != game_state['human_character']:
        # Find AI player
        ai_target = next(ai for ai in game_state['ai_players'] 
                       if ai.character == target_character)
        
        # Generate response
        response = _generate_ai_response(ai_target, question, interrogator, game_state)
    
    # Store the interrogation
    interrogation_data = {
        'interrogator': interrogator.name,
        'target': target_name,
        'question': question,
        'response': response
    }
    
    game_state['interrogations'][current_round].append(interrogation_data)
    
    return jsonify({
        'interrogation': interrogation_data,
        'is_human_target': target_character == game_state['human_character']
    })

@app.route('/api/submit_interrogation_response', methods=['POST'])
def submit_interrogation_response():
    """Submit the human player's response to an interrogation."""
    data = request.json
    game_id = data.get('game_id')
    response = data.get('response')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not response:
        return jsonify({'error': 'Response cannot be empty'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    current_round = game_state['current_round']
    round_interrogations = game_state['interrogations'].get(current_round, [])
    
    # Find the last interrogation where human is the target and response is None
    for interrogation in reversed(round_interrogations):
        if interrogation['target'] == game_state['human_character'].name and not interrogation['response']:
            interrogation['response'] = response
            break
    
    return jsonify({
        'success': True
    })

@app.route('/api/submit_interrogation_suspicion', methods=['POST'])
def submit_interrogation_suspicion():
    """Submit suspicions after an interrogation round."""
    data = request.json
    game_id = data.get('game_id')
    suspicion = data.get('suspicion')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    if not suspicion:
        return jsonify({'error': 'Suspicion cannot be empty'}), 400
    
    game_state = game_states[game_id]
    
    if game_state['game_mode'] != GAME_MODE_INTERROGATION:
        return jsonify({'error': 'Not in interrogation mode'}), 400
    
    current_round = game_state['current_round']
    
    # Save human suspicion
    human_character = game_state['human_character']
    human_character.add_suspicion(suspicion)
    
    # Generate AI suspicions
    for ai_player in game_state['ai_players']:
        # Generate suspicion based on interrogations
        ai_suspicion = _generate_ai_suspicion(ai_player, current_round, game_state)
        ai_player.character.add_suspicion(ai_suspicion)
    
    # Collect all suspicions
    all_suspicions = []
    for character in game_state['characters']:
        # Check if the character has a suspicion for the current round
        if character.suspicions and len(character.suspicions) >= current_round:
            all_suspicions.append({
                'character_name': character.name,
                'suspicion': character.suspicions[current_round - 1]
            })
    
    # Determine if we should move to the next round or to voting
    next_action = 'next_round'
    next_round = current_round + 1
    
    if next_round > game_state['num_rounds']:
        next_action = 'voting'
    
    return jsonify({
        'round': current_round,
        'suspicions': all_suspicions,
        'next_action': next_action,
        'next_round': next_round if next_action == 'next_round' else None
    })

# Helper functions for interrogation mode

def _choose_ai_interrogation_target(ai_player, available_targets, game_state):
    """Choose which character an AI should interrogate."""
    # If only one target available, choose it
    if len(available_targets) == 1:
        return available_targets[0]
    
    # Build history with introductions and previous interrogations
    current_round = game_state['current_round']
    history = "--- CHARACTER INTRODUCTIONS ---\n"
    if 'introductions' in game_state:
        for char_name, intro in game_state['introductions'].items():
            history += f"{char_name} introduced themselves: \"{intro}\"\n\n"
    
    # Add previous interrogations to history
    for r in range(1, current_round):
        if r in game_state['interrogations']:
            history += f"--- ROUND {r} INTERROGATIONS ---\n"
            for data in game_state['interrogations'][r]:
                history += f"{data['interrogator']} asked {data['target']}: \"{data['question']}\"\n"
                history += f"{data['target']} responded: \"{data['response']}\"\n\n"
    
    # Build suspicion history
    suspicion_history = ""
    for char in game_state['characters']:
        if char.suspicions:
            suspicion_history += f"{char.name}'s suspicions:\n"
            for r, suspicion in enumerate(char.suspicions):
                suspicion_history += f"After round {r+1}: \"{suspicion}\"\n"
            suspicion_history += "\n"
    
    # Create the prompt
    prompt = f"""
    You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
    
    {ai_player.character.get_prompt_description()}
    
    This is round {current_round} of the interrogation phase. You need to choose someone to interrogate.
    
    Previous interrogations:
    {history}
    
    Suspicions expressed so far:
    {suspicion_history}
    
    You can interrogate one of these characters: {', '.join(available_targets)}
    
    Which character do you want to interrogate? 
    
    Focus on identifying the "odd one out" from the group based on previous interactions.
    Look for patterns in how most characters respond, and identify which character breaks that pattern.
    Consider factors like response style, consistency, and uniqueness compared to the group.
    
    Respond with ONLY the character's name.
    """
    
    response = ai_player._call_openai_api(prompt)
    
    # Extract the character name from the response
    for target in available_targets:
        if target in response:
            return target
    
    # Default to first available target if no match found
    return available_targets[0]

def _generate_ai_question(ai_player, target_character, round_num, game_state):
    """Generate a targeted question for another character."""
    # Build history of previous interactions with this target
    history = ""
    for r in range(1, round_num):
        if r in game_state['interrogations']:
            for data in game_state['interrogations'][r]:
                if data['target'] == target_character.name:
                    history += f"In round {r}, {data['interrogator']} asked: \"{data['question']}\"\n"
                    history += f"{target_character.name} responded: \"{data['response']}\"\n\n"
    
    # Create the prompt
    prompt = f"""
    You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
    
    {ai_player.character.get_prompt_description()}
    
    You want to determine if {target_character.name} is the human or an AI.
    
    
    Previous interactions with {target_character.name}:
    {history}
    
    Generate ONE specific question to ask {target_character.name} that might reveal whether they are the human or AI.
    The question should be challenging but answerable in 1-2 sentences.
    Make your question clever and designed to reveal if they break the pattern of the AI group.
    """
    
    return ai_player._call_openai_api(prompt)

def _generate_ai_response(ai_player, question, questioner, game_state):
    """Generate a response to an interrogation question."""
    prompt = f"""
    You are roleplaying as {ai_player.character.name} in a game where one player is human and the rest are AI.
    
    {ai_player.character.get_prompt_description()}
    
    {questioner.name} has asked you the following question:
    "{question}"
    
    Respond to this question in 1-2 sentences.
    """
    
    return ai_player._call_openai_api(prompt)

def _generate_ai_suspicion(ai_player, round_num, game_state):
    """Generate suspicions based on interrogations."""
    # Build history of all interrogations in this round
    round_history = ""
    if round_num in game_state['interrogations']:
        for data in game_state['interrogations'][round_num]:
            round_history += f"{data['interrogator']} asked {data['target']}: \"{data['question']}\"\n"
            round_history += f"{data['target']} responded: \"{data['response']}\"\n\n"
    
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
    print(prompt)
    return ai_player._call_openai_api(prompt)

@app.route('/api/get_conversation_history', methods=['POST'])
def get_conversation_history():
    """Get the full conversation history for a game."""
    data = request.json
    game_id = data.get('game_id')
    
    if not game_id or game_id not in game_states:
        return jsonify({'error': 'Invalid game ID'}), 400
    
    game_state = game_states[game_id]
    
    # Initialize conversation history
    conversation_history = []
    
    # Add introductions
    if 'introductions' in game_state:
        for char_name, intro in game_state['introductions'].items():
            conversation_history.append({
                'type': 'introduction',
                'character': char_name,
                'content': intro,
                'round': 0,
                'timestamp': None  # We could add timestamps if needed
            })
    
    # Add all interrogations from all rounds
    for round_num in sorted(game_state.get('interrogations', {}).keys()):
        for idx, interrogation in enumerate(game_state['interrogations'][round_num]):
            # Add the question
            conversation_history.append({
                'type': 'question',
                'character': interrogation['interrogator'],
                'target': interrogation['target'],
                'content': interrogation['question'],
                'round': round_num,
                'sequence': idx
            })
            
            # Add the response if it exists
            if interrogation['response']:
                conversation_history.append({
                    'type': 'response',
                    'character': interrogation['target'],
                    'to': interrogation['interrogator'],
                    'content': interrogation['response'],
                    'round': round_num,
                    'sequence': idx
                })
    
    # Add suspicions
    for round_num in range(1, game_state.get('current_round', 0) + 1):
        for character in game_state['characters']:
            if character.suspicions and len(character.suspicions) >= round_num:
                conversation_history.append({
                    'type': 'suspicion',
                    'character': character.name,
                    'content': character.suspicions[round_num - 1],
                    'round': round_num
                })
    
    return jsonify({
        'conversation_history': conversation_history
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
