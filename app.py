from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from game_logic import initialize_game, progress_game
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb://localhost:27017/")
db = client['game_db']
games_collection = db['games']

class MessageInput(BaseModel):
    game_id: str
    player_message: str

@app.post("/start_game")
async def start_game():
    # Start a new game
    game_data = initialize_game()
    game_id = games_collection.insert_one(game_data).inserted_id
    return {"game_id": str(game_id), "message": game_data["ai_message"], "progress": game_data["progress"]}

@app.post("/send_message")
async def send_message(input_data: MessageInput):
    game_id = input_data.game_id
    player_message = input_data.player_message

    # Fetch the game state from the database
    game_data = games_collection.find_one({"_id": game_id})
    if not game_data:
        raise HTTPException(status_code=404, detail="Game not found")

    # Progress the game with the player's message
    updated_game_data = progress_game(game_data, player_message)

    # Update the game state in the database
    games_collection.update_one({"_id": game_id}, {"$set": updated_game_data})

    return {
        "progress": updated_game_data["progress"],
        "ai_message": updated_game_data["ai_message"],
        "game_over": updated_game_data["progress"] >= 100
    }
