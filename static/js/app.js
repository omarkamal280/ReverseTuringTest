/**
 * Reverse Turing Test Game - Client-side JavaScript
 */

// Game state
const gameState = {
    gameId: null,
    characters: [],
    selectedCharacterIndex: null,
    humanCharacter: null,
    currentRound: 0,
    totalRounds: 5,
    currentQuestion: null,
    responses: {},
    suspicions: {},
    votes: {},
    gameOver: false,
    humanWon: null
};

// DOM Elements
const screens = {
    title: document.getElementById('title-screen'),
    characterSelect: document.getElementById('character-select-screen'),
    question: document.getElementById('question-screen'),
    responses: document.getElementById('responses-screen'),
    suspicions: document.getElementById('suspicions-screen'),
    voting: document.getElementById('voting-screen'),
    results: document.getElementById('results-screen')
};

const loadingOverlay = document.getElementById('loading-overlay');

// Character avatar colors
const avatarColors = {
    'Dr. Alex Morgan': 'avatar-tech',
    'Riley Jordan': 'avatar-creative',
    'Sam Taylor': 'avatar-logical',
    'Jamie Wilson': 'avatar-gamer',
    'Professor Pat Chen': 'avatar-academic'
};

// Helper Functions
function showScreen(screenId) {
    // Hide all screens
    Object.values(screens).forEach(screen => {
        screen.classList.add('d-none');
    });
    
    // Show the requested screen
    screens[screenId].classList.remove('d-none');
    
    // Scroll to top
    window.scrollTo(0, 0);
}

function showLoading(message = 'Loading...') {
    loadingOverlay.querySelector('.loading-text').textContent = message;
    loadingOverlay.classList.remove('d-none');
}

function hideLoading() {
    loadingOverlay.classList.add('d-none');
}

function getInitials(name) {
    return name.split(' ').map(part => part[0]).join('');
}

function createCharacterAvatar(name, size = 60) {
    const avatar = document.createElement('div');
    avatar.className = `avatar ${avatarColors[name] || 'avatar-tech'}`;
    avatar.style.width = `${size}px`;
    avatar.style.height = `${size}px`;
    avatar.textContent = getInitials(name);
    return avatar;
}

function createMessageBubble(characterName, message, isSuspicion = false) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isSuspicion ? 'suspicion-bubble' : ''}`;
    
    // Create avatar
    const avatar = createCharacterAvatar(characterName, 40);
    
    // Create message content
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const sender = document.createElement('div');
    sender.className = 'message-sender';
    sender.textContent = characterName;
    
    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = message;
    
    content.appendChild(sender);
    content.appendChild(text);
    
    bubble.appendChild(avatar);
    bubble.appendChild(content);
    
    return bubble;
}

// API Functions
async function startGame() {
    try {
        showLoading('Starting new game...');
        
        const response = await fetch('/api/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to start game');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.gameId = data.game_id;
        gameState.characters = data.characters;
        
        // Show character selection screen
        displayCharacterSelection();
        
        hideLoading();
        showScreen('characterSelect');
    } catch (error) {
        console.error('Error starting game:', error);
        hideLoading();
        alert('Failed to start game. Please try again.');
    }
}

async function selectCharacter() {
    if (gameState.selectedCharacterIndex === null) {
        alert('Please select a character first.');
        return;
    }
    
    try {
        showLoading('Setting up game...');
        
        const response = await fetch('/api/select_character', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                character_index: gameState.selectedCharacterIndex
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to select character');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.currentRound = data.round;
        gameState.currentQuestion = data.question;
        gameState.humanCharacter = data.character;
        
        // Show question screen
        displayQuestion();
        
        hideLoading();
        showScreen('question');
    } catch (error) {
        console.error('Error selecting character:', error);
        hideLoading();
        alert('Failed to select character. Please try again.');
    }
}

async function submitResponse() {
    const responseInput = document.getElementById('response-input');
    const response = responseInput.value.trim();
    
    if (!response) {
        alert('Please enter a response.');
        return;
    }
    
    try {
        showLoading('AI characters are thinking...');
        
        const apiResponse = await fetch('/api/submit_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                response: response
            })
        });
        
        if (!apiResponse.ok) {
            throw new Error('Failed to submit response');
        }
        
        const data = await apiResponse.json();
        
        // Update game state
        gameState.responses = data.responses;
        
        // Show responses screen
        displayResponses();
        
        hideLoading();
        showScreen('responses');
    } catch (error) {
        console.error('Error submitting response:', error);
        hideLoading();
        alert('Failed to submit response. Please try again.');
    }
}

async function submitSuspicion() {
    const suspicionInput = document.getElementById('suspicion-input');
    const suspicion = suspicionInput.value.trim();
    
    if (!suspicion) {
        alert('Please enter your suspicions.');
        return;
    }
    
    try {
        showLoading('AI characters are analyzing...');
        
        const response = await fetch('/api/submit_suspicion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                suspicion: suspicion
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit suspicion');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.suspicions = data.suspicions;
        
        // Display suspicions
        displaySuspicions();
        
        // Check next action
        if (data.next_action === 'voting') {
            // Prepare for voting
            document.getElementById('continue-button').textContent = 'Continue to Voting';
            document.getElementById('continue-button').onclick = () => {
                displayVoting();
                showScreen('voting');
            };
        } else {
            // Prepare for next round
            gameState.currentRound = data.next_round;
            gameState.currentQuestion = data.next_question;
            
            document.getElementById('continue-button').textContent = 'Continue to Next Round';
            document.getElementById('continue-button').onclick = () => {
                displayQuestion();
                showScreen('question');
            };
        }
        
        hideLoading();
        
        // Show suspicions list
        document.getElementById('suspicion-input-container').classList.add('d-none');
        document.getElementById('suspicions-list-container').classList.remove('d-none');
    } catch (error) {
        console.error('Error submitting suspicion:', error);
        hideLoading();
        alert('Failed to submit suspicion. Please try again.');
    }
}

async function submitVote(votedCharacterName) {
    try {
        showLoading('Collecting votes...');
        
        const response = await fetch('/api/submit_vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                vote: votedCharacterName
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit vote');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.votes = data.votes;
        gameState.votedCharacter = data.voted_character;
        gameState.humanWon = data.human_won;
        gameState.gameOver = true;
        
        // Show results screen
        displayResults();
        
        hideLoading();
        showScreen('results');
    } catch (error) {
        console.error('Error submitting vote:', error);
        hideLoading();
        alert('Failed to submit vote. Please try again.');
    }
}

async function resetGame() {
    try {
        showLoading('Resetting game...');
        
        if (gameState.gameId) {
            await fetch('/api/reset_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_id: gameState.gameId
                })
            });
        }
        
        // Reset game state
        Object.assign(gameState, {
            gameId: null,
            characters: [],
            selectedCharacterIndex: null,
            humanCharacter: null,
            currentRound: 0,
            totalRounds: 5,
            currentQuestion: null,
            responses: {},
            suspicions: {},
            votes: {},
            gameOver: false,
            humanWon: null
        });
        
        // Start a new game
        startGame();
    } catch (error) {
        console.error('Error resetting game:', error);
        hideLoading();
        alert('Failed to reset game. Please try again.');
    }
}

// Display Functions
function displayCharacterSelection() {
    const characterList = document.getElementById('character-list');
    characterList.innerHTML = '';
    
    gameState.characters.forEach((character, index) => {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.dataset.index = index;
        
        // Create avatar
        const avatar = createCharacterAvatar(character.name);
        
        // Create character info
        const info = document.createElement('div');
        info.className = 'character-info';
        
        const name = document.createElement('div');
        name.className = 'character-name';
        name.textContent = character.name;
        
        const profile = document.createElement('div');
        profile.className = 'character-profile';
        profile.textContent = character.profile;
        
        const details = document.createElement('div');
        details.className = 'character-details';
        
        const personality = document.createElement('div');
        personality.innerHTML = `<span class="character-detail-label">Personality:</span> ${character.personality}`;
        
        const background = document.createElement('div');
        background.innerHTML = `<span class="character-detail-label">Background:</span> ${character.background}`;
        
        const speechStyle = document.createElement('div');
        speechStyle.innerHTML = `<span class="character-detail-label">Speech Style:</span> ${character.speech_style}`;
        
        details.appendChild(personality);
        details.appendChild(background);
        details.appendChild(speechStyle);
        
        info.appendChild(name);
        info.appendChild(profile);
        info.appendChild(details);
        
        card.appendChild(avatar);
        card.appendChild(info);
        
        // Add click event
        card.addEventListener('click', () => {
            // Remove selected class from all cards
            document.querySelectorAll('.character-card').forEach(c => {
                c.classList.remove('selected');
            });
            
            // Add selected class to clicked card
            card.classList.add('selected');
            
            // Update selected character index
            gameState.selectedCharacterIndex = index;
        });
        
        characterList.appendChild(card);
    });
}

function displayQuestion() {
    // Update round title
    document.getElementById('round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds}`;
    
    // Update question
    document.getElementById('question-category').textContent = `Category: ${gameState.currentQuestion.category}`;
    document.getElementById('question-text').textContent = gameState.currentQuestion.text;
    
    // Update character info
    const characterAvatar = document.getElementById('character-avatar');
    characterAvatar.innerHTML = '';
    characterAvatar.appendChild(createCharacterAvatar(gameState.humanCharacter.name));
    
    document.getElementById('character-name').textContent = `You are ${gameState.humanCharacter.name}`;
    
    // Clear response input
    document.getElementById('response-input').value = '';
}

function displayResponses() {
    // Update round title
    document.getElementById('responses-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - All Responses`;
    
    // Update question
    document.getElementById('responses-question-text').textContent = gameState.currentQuestion.text;
    
    // Display responses
    const responsesList = document.getElementById('responses-list');
    responsesList.innerHTML = '';
    
    gameState.responses.forEach(response => {
        const bubble = createMessageBubble(response.character_name, response.response);
        responsesList.appendChild(bubble);
    });
}

function displaySuspicions() {
    // Update round title
    document.getElementById('suspicions-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Suspicions`;
    
    // Display suspicions
    const suspicionsList = document.getElementById('suspicions-list');
    suspicionsList.innerHTML = '';
    
    gameState.suspicions.forEach(suspicion => {
        const bubble = createMessageBubble(suspicion.character_name, suspicion.suspicion, true);
        suspicionsList.appendChild(bubble);
    });
}

function displayVoting() {
    const votingOptions = document.getElementById('voting-options');
    votingOptions.innerHTML = '';
    
    // Filter out human character
    const otherCharacters = gameState.characters.filter(
        character => character.name !== gameState.humanCharacter.name
    );
    
    otherCharacters.forEach(character => {
        const option = document.createElement('div');
        option.className = 'voting-option';
        
        // Create avatar
        const avatar = createCharacterAvatar(character.name, 40);
        
        // Create option content
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const name = document.createElement('div');
        name.className = 'message-sender';
        name.textContent = character.name;
        
        content.appendChild(name);
        
        option.appendChild(avatar);
        option.appendChild(content);
        
        // Add click event
        option.addEventListener('click', () => {
            submitVote(character.name);
        });
        
        votingOptions.appendChild(option);
    });
}

function displayResults() {
    // Display votes
    const votesList = document.getElementById('votes-list');
    votesList.innerHTML = '';
    
    gameState.characters.forEach(character => {
        if (character.vote) {
            const li = document.createElement('li');
            li.textContent = `${character.name} voted for: ${character.vote}`;
            votesList.appendChild(li);
        }
    });
    
    // Display vote tally
    const voteTally = document.getElementById('vote-tally');
    voteTally.innerHTML = '';
    
    Object.entries(gameState.votes).forEach(([name, voters]) => {
        const li = document.createElement('li');
        li.textContent = `${name}: ${voters.length} vote(s)`;
        voteTally.appendChild(li);
    });
    
    // Display result announcement
    const resultAnnouncement = document.getElementById('result-announcement');
    resultAnnouncement.innerHTML = '';
    
    const resultHeader = document.createElement('h3');
    resultHeader.textContent = `The group has voted that ${gameState.votedCharacter} is the human!`;
    
    const resultMessage = document.createElement('p');
    
    if (gameState.humanWon) {
        resultAnnouncement.className = 'result-announcement win-message';
        resultMessage.textContent = `Congratulations! You successfully disguised yourself as an AI. The AI players thought ${gameState.votedCharacter} was the human, but it was actually you, ${gameState.humanCharacter.name}!`;
    } else {
        resultAnnouncement.className = 'result-announcement lose-message';
        resultMessage.textContent = `You've been discovered! The AI players correctly identified you as the human.`;
    }
    
    resultAnnouncement.appendChild(resultHeader);
    resultAnnouncement.appendChild(resultMessage);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Title Screen
    document.getElementById('start-button').addEventListener('click', startGame);
    
    // Character Selection Screen
    document.getElementById('select-character-button').addEventListener('click', selectCharacter);
    
    // Question Screen
    document.getElementById('submit-response-button').addEventListener('click', submitResponse);
    
    // Responses Screen
    document.getElementById('continue-to-suspicions-button').addEventListener('click', () => {
        // Reset suspicion input
        document.getElementById('suspicion-input').value = '';
        document.getElementById('suspicion-input-container').classList.remove('d-none');
        document.getElementById('suspicions-list-container').classList.add('d-none');
        
        showScreen('suspicions');
    });
    
    // Suspicions Screen
    document.getElementById('submit-suspicion-button').addEventListener('click', submitSuspicion);
    
    // Results Screen
    document.getElementById('play-again-button').addEventListener('click', resetGame);
    document.getElementById('exit-button').addEventListener('click', () => {
        showScreen('title');
    });
});
