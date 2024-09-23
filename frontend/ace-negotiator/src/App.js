import React, { useEffect, useState } from 'react';
import ChatWindow from './ChatWindow';
import './App.css';

function App() {
  const [gameId, setGameId] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    // Start a new game when the component mounts
    const startGame = async () => {
      const response = await fetch('/start_game', { method: 'POST' });
      const data = await response.json();
      setGameId(data.game_id);
      setPrompt(data.prompt);
    };
    startGame();
  }, []);

  return (
    <div className="container">
      <div className="prompt">{prompt}</div>
      {gameId && (
        <ChatWindow gameId={gameId} setGameOver={setGameOver} gameOver={gameOver} />
      )}
    </div>
  );
}

export default App;
