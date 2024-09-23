# AceNegotiator: Persuade the AI

## Overview

This is an interactive game designed to simulate a business negotiation in a beautiful chat app interface. The player is given a prompt (e.g., "Sell me this pen" or "Sell me your company"), and their goal is to convince the AI to "buy" the item or idea by making persuasive arguments. The game provides real-time feedback, using a large language model (LLM) to simulate the AI's responses and track progress based on sentiment analysis.

## How to Play

1. **Game Start**: 
   - Upon starting a round, the game randomly selects one of the prepared negotiation prompts (e.g., "Sell me this pen").
   - The prompt is displayed at the top of the chat window.
   
2. **Making a Move**:
   - The player enters a message in the chat box, attempting to convince the AI to "buy" the item in question.
   - After sending the message, the AI (powered by **Ollama tiny dolphin 1.1B**) will respond, offering feedback on the player's argument.
   
3. **Game Progress**:
   - Each response from the AI includes an internal sentiment analysis of the player's message. A numeric value between **-10 and +10** is generated:
     - **+10**: Extremely positive response
     - **0**: Neutral response
     - **-10**: Extremely negative response
   - This value is added to the game state variable called `progress`.
   - If `progress` reaches or surpasses **100**, the player wins.

4. **AI Responses**:
   - The AI's behavior adapts based on the numeric sentiment score:
     - **Low scores** result in negative, critical, or untrusting responses.
     - **High scores** yield more positive, enthusiastic, and trusting replies.
   - Each message builds on the context of the ongoing conversation, the player's progress, and the AI's financial "situation."

5. **Winning**:
   - Once `progress` hits **100 or more**, the AI will congratulate the player, and the round ends.

## Technology Stack

- **Large Language Model (LLM)**: The game uses **Ollama tiny dolphin 1.1B** for generating AI responses.
- **Sentiment Analysis**: The game performs basic sentiment classification (positive vs negative) on the AI's response. You can use lightweight sentiment analysis tools like:
  - **VADER**: A simple and efficient sentiment analysis tool suitable for short texts.

## How the AI Works

- Each player message is sent to the LLM for feedback, using prompt engineering to simulate a business negotiation. We provide the following context:
  - The **prompt** (e.g., "Sell me this pen").
  - The **chat history**.
  - The AI's **financial situation** (affecting its willingness to "buy").
  - The current **progress score**, affecting whether the AI reacts negatively or positively.
  
- The AI evaluates the player's message on whether it finds them **reasonable**, **trustworthy**, and **likable**:
  - A template is used to prompt the AI:  
    *"Think of yourself as the opposite side of the business negotiation. When you hear 'xxxxx' from the other party, do you find them reasonable? Do you trust them? Do you find them likable? Please give a combined reaction to this message."*
  
- Sentiment analysis is then performed on the AI's response to generate the numeric score that determines progress.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TomShu01/AceNegotiator.git
   cd chat-game
   ```

2. **Install Dependencies**:
   - Install the required Python libraries:
     ```bash
     pip install ollama nltk
     ```

3. **Run the Game**:
   ```bash
   python game.py
   ```

## Customization

- You can add new prompts by editing the `prompts.json` file.
- Adjust the scoring system or sentiment analysis model by modifying `sentiment_analysis.py`.

## Future Enhancements

- Additional prompts and negotiation scenarios.
- More advanced sentiment analysis with finer granularity (e.g., considering more specific emotions like excitement, doubt, or urgency).
- A scoring leaderboard for tracking persuasive abilities across rounds.