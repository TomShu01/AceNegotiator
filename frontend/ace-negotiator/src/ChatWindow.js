import React, { useState, useRef } from 'react';
import './ChatWindow.css';

function ChatWindow({ gameId, setGameOver, gameOver }) {
  const [messages, setMessages] = useState([]);
  const messageInputRef = useRef(null);
  const chatWindowRef = useRef(null);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (gameOver) return;

    const message = messageInputRef.current.value.trim();
    if (!message) return;

    appendMessage('player', message);
    messageInputRef.current.value = '';

    const response = await fetch('/play', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, message: message }),
    });
    const data = await response.json();

    appendMessage('ai', data.ai_message);

    // Check if the game is over
    if (data.game_over) {
      setGameOver(true);
      alert('Congratulations! You have convinced the AI.');
    }
  };

  const appendMessage = (sender, text) => {
    setMessages((prevMessages) => [...prevMessages, { sender, text }]);
    scrollToBottom();
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatWindowRef.current) {
        chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
      }
    }, 100);
  };

  return (
    <>
      <div className="chat-window" ref={chatWindowRef}>
        {messages.map((msg, index) => (
          <div className={`message ${msg.sender}`} key={index}>
            <div className="text">{msg.text}</div>
          </div>
        ))}
      </div>
      <form className="message-form" onSubmit={sendMessage}>
        <input
          type="text"
          placeholder="Type your message..."
          ref={messageInputRef}
          autoComplete="off"
          required
          disabled={gameOver}
        />
        <button type="submit" disabled={gameOver}>Send</button>
      </form>
    </>
  );
}

export default ChatWindow;
