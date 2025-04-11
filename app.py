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

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Game state
game_states = {}

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """Initialize a new game."""
    # Generate a unique game ID
    game_id = str(random.randint(10000, 99999))
    
    # Initialize game state
    characters = get_character_profiles()
    question_bank = get_question_bank()
    game_questions = select_game_questions(question_bank, 5)
    
    # Store game state
    game_states[game_id] = {
        'characters': characters,
        'game_questions': game_questions,
        'current_round': 0,
        'human_character': None,
        'ai_players': [],
        'responses': {},
        'suspicions': {},
        'votes': {},
        'game_over': False,
        'human_won': None
    }
    
    # Return game information
    return jsonify({
        'game_id': game_id,
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
    
    # Return first question
    current_question = game_state['game_questions'][0]
    return jsonify({
        'round': 1,
        'question': {
            'text': current_question.text,
            'category': current_question.category
        },
        'character': {
            'name': game_state['human_character'].name,
            'profile': game_state['human_character'].profile
        }
    })

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
    
    # Generate AI suspicions
    current_question = game_state['game_questions'][current_round - 1]
    for ai_player in game_state['ai_players']:
        ai_player.analyze_responses(
            game_state['characters'],
            current_question,
            current_round
        )
    
    # Collect all suspicions
    all_suspicions = []
    for character in game_state['characters']:
        if current_round <= len(character.suspicions):
            all_suspicions.append({
                'character_name': character.name,
                'suspicion': character.suspicions[current_round - 1]
            })
    
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

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
