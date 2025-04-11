# Reverse Turing Test Game

A game where a human player tries to disguise themselves as an AI while AI agents try to identify the human among them.

## Game Concept
- The human player selects one of 5 character profiles
- 4 AI players assume the remaining character profiles
- 5 rounds of questions are asked to all characters
- After each round, all players express their suspicions
- At the end, all players vote on who they think is the human
- If the human is identified, they lose; if not, they win

## Setup
1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the game in one of the following modes:

   **Terminal Mode**:
   ```
   python main.py --terminal
   ```

   **Pygame GUI Mode**:
   ```
   python main.py
   ```

   **Web Interface Mode**:
   ```
   flask run
   ```
   Then open http://127.0.0.1:5000 in your browser

## Game Controls
- Terminal Mode: Follow text prompts and type responses
- Pygame GUI: Use the mouse to select options and navigate menus
- Web Interface: Click buttons and use text inputs to interact

## Requirements
- Python 3.8+
- OpenAI API key
- Flask (for web interface)

## Technical Implementation

### Project Structure
```
gameProject/
├── .env                # Environment variables (API keys)
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
├── app.py              # Flask application for web interface
├── assets.py           # Asset management for Pygame interface
├── ai_player.py        # AI player implementation
├── character.py        # Character profiles and management
├── game_engine.py      # Core game logic
├── gui.py              # Pygame graphical interface
├── human_interface.py  # Terminal interface
├── main.py             # Entry point for terminal/Pygame modes
├── questions.py        # Question bank and selection
├── requirements.txt    # Project dependencies
├── static/             # Static files for web interface
│   ├── css/            # CSS stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Image assets
└── templates/          # HTML templates for web interface
```

### Core Components

#### Character System
- `character.py` defines the `Character` class and 5 distinct character profiles
- Each character has a name, profile, personality, background, and speech style
- Characters store their responses, suspicions, and final vote

#### Question System
- `questions.py` contains a diverse bank of questions across different categories
- Categories include ethical dilemmas, creative scenarios, logical puzzles, emotional situations, and opinions
- Questions are selected to ensure diversity across categories

#### AI Player Implementation
- `ai_player.py` handles AI character responses and analysis
- Uses OpenAI API to generate responses based on character profiles
- Analyzes all responses to identify potential human players
- Generates suspicion statements and final votes

#### Game Engine
- `game_engine.py` manages the overall game flow
- Handles character selection, question rounds, and voting
- Determines game outcome based on votes
- Supports both terminal and graphical interfaces

#### User Interfaces

**Terminal Interface**
- `human_interface.py` provides a text-based interface
- Uses colorama for enhanced terminal output
- Simple navigation through numbered options

**Pygame Interface**
- `gui.py` and `assets.py` implement a graphical interface
- Character avatars, message bubbles, and interactive elements
- Mouse-based navigation and input

**Web Interface**
- `app.py` implements a Flask web application
- RESTful API endpoints for game actions
- Frontend in HTML/CSS/JavaScript with responsive design
- Uses Bootstrap for layout and styling

### OpenAI API Integration

#### Prompt Engineering
The game uses carefully crafted prompts to generate appropriate AI responses:

1. **Character Response Prompt**:
```
You are roleplaying as a character in a game. Respond to the question as this character would.

{character_description}

This is round {round_num} of the game.

Question: {question_text}

Provide a response (2-3 sentences) that reflects your character's personality and speech style.
```

2. **Analysis Prompt**:
```
You are roleplaying as a character in a game where one player is human and the rest are AI. 
Your goal is to identify the human based on their responses.

{character_description}

This is round {round_num} of the game.
Question that was asked: {question_text}

Here are all the responses:
{responses_text}

As {character_name}, express your suspicions about who might be the human player in 1-2 sentences.
Use your character's speech style. Don't directly accuse anyone yet, just share your thoughts.
```

3. **Voting Prompt**:
```
You are roleplaying as a character in a game where one player is human and the rest are AI.
Your goal is to identify the human based on their responses throughout the game.

{character_description}

Here is the complete game history:
{game_history}

Based on all the responses and suspicions, which character do you think is the human player?
Respond with just the character's name that you're voting for.
```

### Data Flow

1. **Game Initialization**:
   - Load character profiles and question bank
   - Player selects character
   - AI players are created for remaining characters
   - Questions are selected for the game

2. **Question Round**:
   - Question is presented to all characters
   - Human player provides response for their character
   - AI responses are generated via OpenAI API
   - All responses are displayed

3. **Suspicion Phase**:
   - Human player expresses suspicions
   - AI suspicions are generated via OpenAI API
   - All suspicions are displayed

4. **Voting Phase**:
   - Human player votes for a character
   - AI votes are generated via OpenAI API
   - Votes are tallied

5. **Result Determination**:
   - If most votes are for the human player's character, human loses
   - If most votes are for another character, human wins

### API Usage Optimization

- Responses are limited to 150 tokens to control API costs
- Character profiles are included in prompts to maintain consistency
- Error handling ensures graceful degradation if API calls fail

## Extending the Game

### Adding New Characters
Add new character profiles to the `get_character_profiles()` function in `character.py`.

### Adding New Questions
Add new questions to the `get_question_bank()` function in `questions.py`.

### Customizing AI Behavior
Modify the prompt templates in `ai_player.py` to change how AI characters respond and analyze.
