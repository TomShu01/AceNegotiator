import requests
import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict

import nltk
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

OLLAMA_API_URL = "http://localhost:11434/api/v1/generate"

PROMPTS = [
    "Sell me a vacuum cleaner.",
    "Convince me to invest in your startup.",
    "Why should I buy your e-book?",
]

def initialize_game() -> Dict:
    """
    Initialize a new game with a random prompt and starting progress.
    """
    prompt = random.choice(PROMPTS)
    context = "I am financially tight, so I'm unlikely to buy things I don't need."
    initial_ai_message = generate_ai_response(f"Your task is to sell me {prompt}. I'm hesitant.")
    
    return {
        "prompt": prompt,
        "context": context,
        "progress": 0,
        "chat_history": [initial_ai_message],
        "ai_message": initial_ai_message
    }

def progress_game(game_data: Dict, player_message: str) -> Dict:
    """
    Progress the game by sending the player's message to the AI and analyzing its response.
    """
    ai_response = generate_ai_response(
        f"You are hesitant to buy. Respond to this attempt to sell: '{player_message}'. Context: {game_data['context']}."
    )

    sentiment_score = perform_sentiment_analysis(ai_response)

    game_data["progress"] += sentiment_score
    game_data["chat_history"].append({"player": player_message, "ai": ai_response})
    game_data["ai_message"] = ai_response

    return game_data

def generate_ai_response(prompt: str) -> str:
    """
    Send a request to the Ollama LLM to generate a response.
    """
    payload = {
        "model": "llama3:8b",
        "prompt": prompt,
    }
    # tiny_dolphin
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return "Error in LLM response"

def perform_sentiment_analysis(ai_response: str) -> int:
    """
    Perform sentiment analysis on the AI's response and return a score from -10 to 10.
    """
    sentiment = sid.polarity_scores(ai_response)
    compound_score = sentiment['compound']

    return int(compound_score * 10)
