from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uuid
import requests
from typing import List, Optional
import json
import random
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from fastapi.middleware.cors import CORSMiddleware

nltk.download('vader_lexicon', quiet=True)

app = FastAPI()

# deal with CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}

sia = SentimentIntensityAnalyzer()

# Prompts specifying the player's objective
prompts_list = [
    "Sell me this pen.",
    "Convince me to buy your company.",
    "Persuade me to invest in your startup.",
    "Sell a cutting-edge AI software to a cautious CEO.",
    "Convince me to buy your revolutionary new product."
]

# define classes to store game state
class GameState(BaseModel):
    """
    stores session id, game progress, history, prompt, context
    """
    game_id: str
    progress: int
    chat_history: List[str]
    prompt: str
    context: str

class PlayerMessage(BaseModel):
    game_id: str
    message: str

class AIResponse(BaseModel):
    ai_message: str
    progress: int
    game_over: bool

# initialize game
@app.post("/start_game")
def start_game():
    game_id = str(uuid.uuid4())
    progress = 0
    chat_history = []

    # Randomly select a prompt from the list
    prompt = random.choice(prompts_list)

    context = "You are a potential customer with specific concerns."

    games[game_id] = GameState(
        game_id=game_id,
        progress=progress,
        chat_history=chat_history,
        prompt=prompt,
        context=context
    )
    return {"game_id": game_id, "prompt": prompt}

# continue playing the game
@app.post("/play", response_model=AIResponse)
def play(player_message: PlayerMessage):
    game_id = player_message.game_id
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]
    message = player_message.message

    game.chat_history.append(f"Player: {message}")
    sentiment_prompt = f"Think of yourself as the opposite side of the business negotiation. When you hear '{message}' from the other party, do you find them reasonable? Do you find them trustworthy? Do you find them likable? Please give a combined reaction to this message. e.g., if you find them strongly reasonable, trustworthy or likable, act happy. If not, act sad or angry."
    ai_sentiment_response = send_to_llm(sentiment_prompt)
    print(ai_sentiment_response)
    sentiment_score = get_sentiment_score(ai_sentiment_response)
    scaled_sentiment = int(sentiment_score * 10)
    game.progress += scaled_sentiment
    llm_prompt = prepare_llm_prompt(game, sentiment_score, message)
    print(llm_prompt)
    ai_response = send_to_llm(llm_prompt)
    print(ai_response)
    game.chat_history.append(f"AI: {ai_response}")

    # Check if progress >= 100
    if game.progress >= 100:
        congrats_prompt = "You have been convinced and decided to make the purchase. Please generate a congratulatory message to the salesperson."
        congrats_message = send_to_llm(congrats_prompt)
        game.chat_history.append(f"AI: {congrats_message}")
        return AIResponse(ai_message=congrats_message, progress=game.progress, game_over=True)

    else:
        return AIResponse(ai_message=ai_response, progress=game.progress, game_over=False)

def send_to_llm(prompt: str) -> str:
    """
    send_to_llm: sends a request to the LLM and generates a response
    """
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "llama3:8b",
        "prompt": prompt
    }
    response = requests.post(url, json=data, stream=True)
    if response.status_code == 200:
        generated_text = ""
        for line in response.iter_lines():
            if line:
                data_line = line.decode('utf-8')
                print(data_line)
                if data_line:
                    try:
                        data_json = json.loads(data_line)
                        print(data_json)
                        generated_text += data_json.get('response', '')
                    except json.JSONDecodeError:
                        continue
        return generated_text.strip()
    else:
        raise HTTPException(status_code=500, detail="Error communicating with LLM")

def get_sentiment_score(text: str) -> float:
    """
    get_sentiment_score: scores the player conversation using Vader
    """
    sentiment = sia.polarity_scores(text)
    compound_score = sentiment['compound']  # Compound score ranges from -1 to 1
    return compound_score

def prepare_llm_prompt(game: GameState, sentiment_score: float, player_message: str) -> str:
    """
    prepare_llm_prompt: prompt engineering to make sure the LLM generates responses relevant to the conversation
    """
    # Decide on the LLM's mood based on sentiment score
    if sentiment_score > 0:
        mood = "You are feeling positive about the negotiation."
    else:
        mood = "You are feeling negative about the negotiation."

    llm_prompt = f"""
                {game.context}
                {mood}
                The player is trying to {game.prompt}
                Here is the conversation so far:
                {chr(10).join(game.chat_history)}
                Respond accordingly.
                """
    return llm_prompt

