/**
 * Reverse Turing Test Game - Client-side JavaScript
 */

// Game state
const gameState = {
    gameId: null,
    gameMode: 'standard', // 'standard' or 'interrogation'
    characters: [],
    selectedCharacterIndex: null,
    humanCharacter: null,
    currentRound: 0,
    totalRounds: 5,
    currentQuestion: null,
    responses: {},
    suspicions: {},
    judgeSuspicions: {},  // New: suspicions from AI judges in standard mode
    votes: {},
    judgeVotes: {},       // New: votes from AI judges in standard mode
    gameOver: false,
    humanWon: null,
    // Interrogation mode specific
    introductions: [],
    interrogations: {},
    interrogationOrder: [],
    currentInterrogator: null,
    currentTarget: null,
    currentInterrogationQuestion: null
};

// DOM Elements
const screens = {
    title: document.getElementById('title-screen'),
    characterSelect: document.getElementById('character-select-screen'),
    question: document.getElementById('question-screen'),
    responses: document.getElementById('responses-screen'),
    suspicions: document.getElementById('suspicions-screen'),
    voting: document.getElementById('voting-screen'),
    results: document.getElementById('results-screen'),
    // Interrogation mode screens
    introduction: document.getElementById('introduction-screen'),
    introductionsDisplay: document.getElementById('introductions-display-screen'),
    interrogation: document.getElementById('interrogation-screen'),
    interrogationResponse: document.getElementById('interrogation-response-screen'),
    interrogationSummary: document.getElementById('interrogation-summary-screen'),
    interrogationSuspicions: document.getElementById('interrogation-suspicions-screen')
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
    
    // Show conversation history tab for gameplay screens
    const gameplayScreens = ['question', 'responses', 'suspicions', 'voting', 'introduction', 'introductionsDisplay', 'interrogation', 'interrogationResponse', 'interrogationSummary', 'interrogationSuspicions'];
    
    if (gameplayScreens.includes(screenId) && gameState.gameId) {
        document.getElementById('conversation-history-tab').classList.remove('d-none');
        
        // Auto-refresh conversation history if enabled
        if (document.getElementById('auto-refresh-history').checked) {
            fetchConversationHistory();
        }
    } else {
        document.getElementById('conversation-history-tab').classList.add('d-none');
    }
    
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

function createMessageBubble(characterName, message, isSuspicion = false, extraClass = '') {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isSuspicion ? 'suspicion-bubble' : ''} ${extraClass}`;
    
    // Check if this is a judge message
    const isJudge = characterName.startsWith('Judge ');
    
    // Create avatar (different styling for judges)
    let avatar;
    if (isJudge) {
        avatar = document.createElement('div');
        avatar.className = 'avatar avatar-judge';
        avatar.style.width = '40px';
        avatar.style.height = '40px';
        avatar.textContent = characterName.replace('Judge ', '').charAt(0);
    } else {
        avatar = createCharacterAvatar(characterName, 40);
    }
    
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
        
        // Get selected game mode
        const gameModeRadios = document.getElementsByName('gameMode');
        let selectedMode = 'standard';
        for (const radio of gameModeRadios) {
            if (radio.checked) {
                selectedMode = radio.value;
                break;
            }
        }
        
        gameState.gameMode = selectedMode;
        
        const response = await fetch('/api/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_mode: selectedMode
            })
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
        gameState.humanCharacter = data.character;
        
        // Handle based on game mode
        if (gameState.gameMode === 'standard') {
            gameState.currentQuestion = data.question;
            // Show question screen
            displayQuestion();
            hideLoading();
            showScreen('question');
        } else if (gameState.gameMode === 'interrogation') {
            // Show introduction screen
            displayIntroductionScreen();
            hideLoading();
            showScreen('introduction');
        }
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
        
        // Handle judge suspicions in standard mode
        if (gameState.gameMode === 'standard' && data.judge_suspicions) {
            gameState.judgeSuspicions = data.judge_suspicions;
        }
        
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
        gameState.humanWon = data.human_won;
        gameState.gameOver = true;
        gameState.votedCharacter = data.voted_character;
        
        // Handle different game modes
        if (gameState.gameMode === 'standard') {
            // Standard mode: Judge votes
            if (data.judge_votes) {
                gameState.judgeVotes = data.judge_votes;
            }
            if (data.vote_counts) {
                gameState.voteCounts = data.vote_counts;
            }
        } else {
            // Interrogation mode: Character votes
            gameState.votes = data.votes;
        }
        
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
    
    // Handle different display based on game mode
    if (gameState.gameMode === 'standard') {
        // Show standard mode suspicions container, hide interrogation mode container
        document.getElementById('standard-mode-suspicions').classList.remove('d-none');
        document.getElementById('interrogation-mode-suspicions').classList.add('d-none');
        
        // Display human suspicion
        const humanSuspicionContainer = document.getElementById('human-suspicion');
        humanSuspicionContainer.innerHTML = '';
        
        // Find the human suspicion in the suspicions array
        const humanSuspicion = gameState.suspicions.find(s => s.character_name === gameState.humanCharacter.name);
        if (humanSuspicion) {
            const bubble = createMessageBubble(humanSuspicion.character_name, humanSuspicion.suspicion, true);
            humanSuspicionContainer.appendChild(bubble);
        }
        
        // Display judge suspicions
        const judgeSuspicionsContainer = document.getElementById('judge-suspicions');
        judgeSuspicionsContainer.innerHTML = '';
        
        if (gameState.judgeSuspicions && gameState.judgeSuspicions.length > 0) {
            gameState.judgeSuspicions.forEach(judge => {
                const bubble = createMessageBubble(`Judge ${judge.judge_name}`, judge.suspicion, true, 'judge-message');
                judgeSuspicionsContainer.appendChild(bubble);
            });
        }
    } else {
        // Show interrogation mode suspicions container, hide standard mode container
        document.getElementById('standard-mode-suspicions').classList.add('d-none');
        document.getElementById('interrogation-mode-suspicions').classList.remove('d-none');
        
        // Display all character suspicions for interrogation mode
        const suspicionsList = document.getElementById('suspicions-list');
        suspicionsList.innerHTML = '';
        
        gameState.suspicions.forEach(suspicion => {
            const bubble = createMessageBubble(suspicion.character_name, suspicion.suspicion, true);
            suspicionsList.appendChild(bubble);
        });
    }
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
    // Handle different display based on game mode
    if (gameState.gameMode === 'standard') {
        // Show standard mode results, hide interrogation mode results
        document.getElementById('standard-mode-results').classList.remove('d-none');
        document.getElementById('interrogation-mode-results').classList.add('d-none');
        
        // Display judge votes
        const judgeVotesList = document.getElementById('judge-votes-list');
        judgeVotesList.innerHTML = '';
        
        if (gameState.judgeVotes) {
            Object.entries(gameState.judgeVotes).forEach(([judgeName, vote]) => {
                const li = document.createElement('li');
                li.textContent = `Judge ${judgeName} voted for: ${vote}`;
                judgeVotesList.appendChild(li);
            });
        }
        
        // Display judge vote tally
        const judgeVoteTally = document.getElementById('judge-vote-tally');
        judgeVoteTally.innerHTML = '';
        
        if (gameState.voteCounts) {
            Object.entries(gameState.voteCounts).forEach(([name, count]) => {
                const li = document.createElement('li');
                li.textContent = `${name}: ${count} vote(s)`;
                judgeVoteTally.appendChild(li);
            });
        }
        
        // Display result announcement
        const resultAnnouncement = document.getElementById('judge-result-announcement');
        resultAnnouncement.innerHTML = '';
        
        const announcement = document.createElement('p');
        announcement.className = 'result-text';
        
        if (gameState.humanWon) {
            announcement.className += ' success';
            announcement.textContent = `Congratulations! You successfully disguised yourself as an AI. The judges thought ${gameState.votedCharacter} was the human, but it was actually you, ${gameState.humanCharacter.name}!`;
        } else {
            announcement.className += ' failure';
            announcement.textContent = `You've been discovered! The judges correctly identified you as the human.`;
        }
        
        resultAnnouncement.appendChild(announcement);
    } else {
        // Show interrogation mode results, hide standard mode results
        document.getElementById('standard-mode-results').classList.add('d-none');
        document.getElementById('interrogation-mode-results').classList.remove('d-none');
        
        // Display character votes
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
        
        const announcement = document.createElement('p');
        announcement.className = 'result-text';
        
        if (gameState.humanWon) {
            announcement.className += ' success';
            announcement.textContent = `Congratulations! You successfully disguised yourself as an AI. The group thought ${gameState.votedCharacter} was the human, but it was actually you, ${gameState.humanCharacter.name}!`;
        } else {
            announcement.className += ' failure';
            announcement.textContent = `You've been discovered! The group correctly identified you as the human.`;
        }
        
        resultAnnouncement.appendChild(announcement);
    }
}

// Interrogation Mode Functions
async function displayIntroductionScreen() {
    // Display character info
    const characterAvatar = document.getElementById('intro-character-avatar');
    characterAvatar.className = `avatar ${avatarColors[gameState.humanCharacter.name] || 'avatar-tech'}`;
    characterAvatar.textContent = getInitials(gameState.humanCharacter.name);
    
    document.getElementById('intro-character-name').textContent = gameState.humanCharacter.name;
}

async function submitIntroduction() {
    const introductionInput = document.getElementById('introduction-input');
    const introduction = introductionInput.value.trim();
    
    if (!introduction) {
        alert('Please enter an introduction.');
        return;
    }
    
    try {
        showLoading('AI characters are introducing themselves...');
        
        const response = await fetch('/api/submit_introduction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                introduction: introduction
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit introduction');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.introductions = data.introductions;
        
        // Display all introductions
        displayAllIntroductions();
        
        hideLoading();
        showScreen('introductionsDisplay');
    } catch (error) {
        console.error('Error submitting introduction:', error);
        hideLoading();
        alert('Failed to submit introduction. Please try again.');
    }
}

function displayAllIntroductions() {
    const introductionsList = document.getElementById('introductions-list');
    introductionsList.innerHTML = '';
    
    gameState.introductions.forEach(intro => {
        const bubble = createMessageBubble(intro.character_name, intro.introduction);
        introductionsList.appendChild(bubble);
    });
}

async function startInterrogationRound() {
    try {
        showLoading('Starting interrogation round...');
        
        const response = await fetch('/api/start_interrogation_round', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start interrogation round');
        }
        
        const data = await response.json();
        
        // Update game state
        gameState.currentRound = data.round;
        gameState.totalRounds = data.total_rounds;
        gameState.interrogationOrder = data.interrogation_order;
        
        // Get the first interrogation turn
        await getNextInterrogationTurn();
        
        hideLoading();
    } catch (error) {
        console.error('Error starting interrogation round:', error);
        hideLoading();
        alert('Failed to start interrogation round. Please try again.');
    }
}

async function getNextInterrogationTurn() {
    try {
        showLoading('Getting next interrogation turn...');
        
        const response = await fetch('/api/get_interrogation_turn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get interrogation turn');
        }
        
        const data = await response.json();
        
        // Check if round is complete
        if (data.round_complete) {
            // Show round summary
            displayInterrogationSummary();
            hideLoading();
            showScreen('interrogationSummary');
            return;
        }
        
        // Update game state
        gameState.currentInterrogator = data.interrogator;
        
        // Update UI
        document.getElementById('interrogation-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Interrogation`;
        document.getElementById('current-interrogator').textContent = data.interrogator;
        
        // Show appropriate controls based on whose turn it is
        if (data.is_human_turn) {
            // Human's turn to interrogate
            document.getElementById('human-interrogation-controls').classList.remove('d-none');
            document.getElementById('ai-interrogation-display').classList.add('d-none');
            
            // Display target options
            displayInterrogationTargets(data.available_targets);
        } else {
            // AI's turn to interrogate
            document.getElementById('human-interrogation-controls').classList.add('d-none');
            document.getElementById('ai-interrogation-display').classList.remove('d-none');
            
            // Display AI's choice
            document.getElementById('ai-target-name').textContent = data.ai_target;
            document.getElementById('ai-question-text').textContent = data.ai_question;
            
            // Store AI's question and target
            gameState.currentTarget = data.ai_target;
            gameState.currentInterrogationQuestion = data.ai_question;
        }
        
        hideLoading();
        showScreen('interrogation');
    } catch (error) {
        console.error('Error getting interrogation turn:', error);
        hideLoading();
        alert('Failed to get interrogation turn. Please try again.');
    }
}

function displayInterrogationTargets(targets) {
    const targetsContainer = document.getElementById('interrogation-targets');
    targetsContainer.innerHTML = '';
    
    targets.forEach(targetName => {
        const targetCard = document.createElement('div');
        targetCard.className = 'character-card';
        targetCard.dataset.name = targetName;
        
        const avatar = createCharacterAvatar(targetName);
        const name = document.createElement('p');
        name.textContent = targetName;
        
        targetCard.appendChild(avatar);
        targetCard.appendChild(name);
        
        targetCard.addEventListener('click', () => {
            // Remove selection from all cards
            document.querySelectorAll('.character-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Add selection to this card
            targetCard.classList.add('selected');
            
            // Store selected target
            gameState.currentTarget = targetName;
        });
        
        targetsContainer.appendChild(targetCard);
    });
}

async function submitInterrogation() {
    if (!gameState.currentTarget) {
        alert('Please select a character to interrogate.');
        return;
    }
    
    const questionInput = document.getElementById('interrogation-question-input');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question.');
        return;
    }
    
    try {
        showLoading('Submitting interrogation...');
        
        const response = await fetch('/api/submit_interrogation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                target: gameState.currentTarget,
                question: question
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit interrogation');
        }
        
        const data = await response.json();
        
        // Store the question for later
        gameState.currentInterrogationQuestion = question;
        
        // If target is human, show response screen
        if (data.is_human_target) {
            hideLoading();
            // We'll handle this in the next turn
            getNextInterrogationTurn();
        } else {
            // Show AI response
            document.getElementById('response-interrogator').textContent = gameState.currentInterrogator;
            document.getElementById('response-question').textContent = question;
            document.getElementById('response-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Response`;
            
            document.getElementById('human-response-controls').classList.add('d-none');
            document.getElementById('ai-response-display').classList.remove('d-none');
            document.getElementById('ai-response-text').textContent = data.interrogation.response;
            
            hideLoading();
            showScreen('interrogationResponse');
        }
    } catch (error) {
        console.error('Error submitting interrogation:', error);
        hideLoading();
        alert('Failed to submit interrogation. Please try again.');
    }
}

async function continueAfterAIInterrogation() {
    try {
        showLoading('Submitting AI interrogation...');
        
        const response = await fetch('/api/submit_interrogation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId,
                target: gameState.currentTarget,
                question: gameState.currentInterrogationQuestion
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit AI interrogation');
        }
        
        const data = await response.json();
        
        // If target is human, show response screen
        if (data.is_human_target) {
            // Show response screen for human to respond
            document.getElementById('response-interrogator').textContent = gameState.currentInterrogator;
            document.getElementById('response-question').textContent = gameState.currentInterrogationQuestion;
            document.getElementById('response-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Response`;
            
            document.getElementById('human-response-controls').classList.remove('d-none');
            document.getElementById('ai-response-display').classList.add('d-none');
            document.getElementById('interrogation-response-input').value = '';
            
            hideLoading();
            showScreen('interrogationResponse');
        } else {
            // Show AI response
            document.getElementById('response-interrogator').textContent = gameState.currentInterrogator;
            document.getElementById('response-question').textContent = gameState.currentInterrogationQuestion;
            document.getElementById('response-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Response`;
            
            document.getElementById('human-response-controls').classList.add('d-none');
            document.getElementById('ai-response-display').classList.remove('d-none');
            document.getElementById('ai-response-text').textContent = data.interrogation.response;
            
            hideLoading();
            showScreen('interrogationResponse');
        }
    } catch (error) {
        console.error('Error submitting AI interrogation:', error);
        hideLoading();
        alert('Failed to submit AI interrogation. Please try again.');
    }
}

async function submitInterrogationResponse() {
    const responseInput = document.getElementById('interrogation-response-input');
    const response = responseInput.value.trim();
    
    if (!response) {
        alert('Please enter a response.');
        return;
    }
    
    try {
        showLoading('Submitting response...');
        
        const apiResponse = await fetch('/api/submit_interrogation_response', {
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
        
        // Get next interrogation turn
        await getNextInterrogationTurn();
        
        hideLoading();
    } catch (error) {
        console.error('Error submitting response:', error);
        hideLoading();
        alert('Failed to submit response. Please try again.');
    }
}

function displayInterrogationSummary() {
    document.getElementById('summary-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Summary`;
    
    // We would need to fetch the interrogation data for this round
    // For now, just show a placeholder message
    const summaryContainer = document.getElementById('interrogation-summary');
    summaryContainer.innerHTML = '<p>All interrogations for this round are complete. Continue to see suspicions.</p>';
}

async function submitInterrogationSuspicion() {
    const suspicionInput = document.getElementById('interrogation-suspicion-input');
    const suspicion = suspicionInput.value.trim();
    
    if (!suspicion) {
        alert('Please enter your suspicions.');
        return;
    }
    
    try {
        showLoading('AI characters are thinking...');
        
        const response = await fetch('/api/submit_interrogation_suspicion', {
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
        
        // Hide input container and show suspicions list
        document.getElementById('interrogation-suspicion-input-container').classList.add('d-none');
        document.getElementById('interrogation-suspicions-list-container').classList.remove('d-none');
        
        // Display all suspicions
        const suspicionsList = document.getElementById('interrogation-suspicions-list');
        suspicionsList.innerHTML = '';
        
        data.suspicions.forEach(suspicionData => {
            const bubble = createMessageBubble(suspicionData.character_name, suspicionData.suspicion, true);
            suspicionsList.appendChild(bubble);
        });
        
        // Store next action
        gameState.nextAction = data.next_action;
        gameState.nextRound = data.next_round;
        
        hideLoading();
    } catch (error) {
        console.error('Error submitting suspicion:', error);
        hideLoading();
        alert('Failed to submit suspicion. Please try again.');
    }
}

function handleAfterInterrogationSuspicions() {
    if (gameState.nextAction === 'next_round') {
        // Start next round
        startInterrogationRound();
    } else if (gameState.nextAction === 'voting') {
        // Show voting screen
        displayVoting();
        showScreen('voting');
    }
}

// Conversation History Functions
async function fetchConversationHistory() {
    try {
        if (!gameState.gameId) return;
        
        const response = await fetch('/api/get_conversation_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameState.gameId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch conversation history');
        }
        
        const data = await response.json();
        displayConversationHistory(data.conversation_history);
    } catch (error) {
        console.error('Error fetching conversation history:', error);
    }
}

function displayConversationHistory(history) {
    const historyContent = document.getElementById('conversation-history-content');
    historyContent.innerHTML = '';
    
    if (!history || history.length === 0) {
        historyContent.innerHTML = '<p class="text-muted">No conversation history yet.</p>';
        return;
    }
    
    // Group by rounds
    let currentRound = -1;
    
    history.forEach(item => {
        // Add round separator if needed
        if (item.round !== currentRound) {
            currentRound = item.round;
            const roundHeader = document.createElement('div');
            roundHeader.className = 'round-separator my-3';
            
            let roundTitle;
            if (currentRound === 0) {
                roundTitle = 'Introductions';
            } else {
                roundTitle = `Round ${currentRound}`;
            }
            
            roundHeader.innerHTML = `<h6 class="text-center border-bottom pb-2">${roundTitle}</h6>`;
            historyContent.appendChild(roundHeader);
        }
        
        // Create message element based on type
        const messageEl = document.createElement('div');
        messageEl.className = 'history-message mb-2';
        
        let messageContent = '';
        
        switch (item.type) {
            case 'introduction':
                messageContent = `<strong>${item.character}</strong> introduced: "${item.content}"`;
                messageEl.classList.add('introduction-message');
                break;
                
            case 'question':
                messageContent = `<strong>${item.character}</strong> asked <strong>${item.target}</strong>: "${item.content}"`;
                messageEl.classList.add('question-message');
                break;
                
            case 'response':
                messageContent = `<strong>${item.character}</strong> responded to <strong>${item.to}</strong>: "${item.content}"`;
                messageEl.classList.add('response-message');
                break;
                
            case 'suspicion':
                messageContent = `<strong>${item.character}'s suspicion</strong>: "${item.content}"`;
                messageEl.classList.add('suspicion-message');
                break;
        }
        
        messageEl.innerHTML = messageContent;
        historyContent.appendChild(messageEl);
    });
    
    // Scroll to bottom
    historyContent.scrollTop = historyContent.scrollHeight;
}

function toggleConversationHistory() {
    const panel = document.getElementById('conversation-history-panel');
    const icon = document.getElementById('conversation-history-icon');
    
    if (panel.classList.contains('d-none')) {
        // Show panel
        panel.classList.remove('d-none');
        icon.textContent = '❌';
        fetchConversationHistory();
    } else {
        // Hide panel
        panel.classList.add('d-none');
        icon.textContent = '📜';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Title Screen
    document.getElementById('start-button').addEventListener('click', startGame);
    
    // Game mode selection
    const gameModeRadios = document.getElementsByName('gameMode');
    for (const radio of gameModeRadios) {
        radio.addEventListener('change', updateModeDescription);
    }
    
    // Conversation History
    document.getElementById('toggle-conversation-history').addEventListener('click', toggleConversationHistory);
    document.getElementById('close-conversation-history').addEventListener('click', () => {
        document.getElementById('conversation-history-panel').classList.add('d-none');
        document.getElementById('conversation-history-icon').textContent = '📜';
    });
    document.getElementById('refresh-conversation-history').addEventListener('click', fetchConversationHistory);
    
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
    
    // Interrogation Mode
    // Introduction Screen
    document.getElementById('submit-introduction-button').addEventListener('click', submitIntroduction);
    
    // Introductions Display Screen
    document.getElementById('start-interrogation-button').addEventListener('click', startInterrogationRound);
    
    // Interrogation Screen
    document.getElementById('submit-interrogation-button').addEventListener('click', submitInterrogation);
    document.getElementById('continue-ai-interrogation-button').addEventListener('click', continueAfterAIInterrogation);
    
    // Interrogation Response Screen
    document.getElementById('submit-response-to-interrogation-button').addEventListener('click', submitInterrogationResponse);
    document.getElementById('continue-after-response-button').addEventListener('click', getNextInterrogationTurn);
    
    // Interrogation Summary Screen
    document.getElementById('continue-to-interrogation-suspicions-button').addEventListener('click', () => {
        showScreen('interrogationSuspicions');
        document.getElementById('interrogation-suspicions-round-title').textContent = `Round ${gameState.currentRound}/${gameState.totalRounds} - Suspicions`;
    });
    
    // Interrogation Suspicions Screen
    document.getElementById('submit-interrogation-suspicion-button').addEventListener('click', submitInterrogationSuspicion);
    document.getElementById('continue-after-interrogation-suspicions-button').addEventListener('click', handleAfterInterrogationSuspicions);
    
    // Results Screen
    document.getElementById('play-again-button').addEventListener('click', resetGame);
    document.getElementById('exit-button').addEventListener('click', () => {
        showScreen('title');
    });
});

function updateModeDescription() {
    const modeDescription = document.getElementById('mode-description');
    const selectedMode = document.querySelector('input[name="gameMode"]:checked').value;
    
    if (selectedMode === 'standard') {
        modeDescription.innerHTML = '<p><strong>Standard Mode:</strong> Answer preset questions over 5 rounds.</p>';
    } else {
        modeDescription.innerHTML = '<p><strong>Interrogation Mode:</strong> Characters introduce themselves and directly question each other.</p>';
    }
}
