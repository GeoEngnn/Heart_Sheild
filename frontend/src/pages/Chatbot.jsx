import React, { useEffect, useRef, useState } from "react";
import Header from "../components/Header";
import { sendMessage } from "../services/api";
import { useParams } from "react-router-dom";

export default function Chatbot() {
  const { userId: routeUserId } = useParams();
  const [user, setUser] = useState(null);

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I'm your HeartShield assistant. Ask me anything about improving BP, cholesterol, glucose, or general health."
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    // FIXED: Use correct localStorage key
    const stored = localStorage.getItem("heartshield_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  // auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const text = input.trim();
    setInput("");

    // add user message
    setMessages((prev) => [...prev, { sender: "me", text }]);
    setLoading(true);

    try {
      const res = await sendMessage(text, routeUserId || user?.id);

      if (res.success) {
        const reply = res.reply || "I'm here to help!";
        setMessages((prev) => [...prev, { sender: "bot", text: reply }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: "Sorry, I couldn't understand. Try again?" },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Server error. Please check backend." },
      ]);
    }

    setLoading(false);
  };

  const handleKey = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="chatbot-page">
      <Header />
      <div className="app-container">
        <h2 className="page-title">Health Assistant Chat</h2>

        <div className="chat-container">
          <div className="chat-box">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message-bubble ${msg.sender === "me" ? "user-message" : "bot-message"}`}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div className="message-bubble bot-message typing-indicator">
                Typing...
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-container">
            <input
              type="text"
              placeholder="Type your message..."
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
            />
            <button className="send-button" onClick={handleSend}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}