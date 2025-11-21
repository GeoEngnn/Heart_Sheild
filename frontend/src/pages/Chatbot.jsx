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
    // FIXED correct localStorage key
    const stored = localStorage.getItem("user");
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
    <div style={styles.container}>
      <Header />
      <h2 style={styles.title}>Health Assistant Chat</h2>

      <div style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...styles.bubble,
              ...(msg.sender === "me" ? styles.me : styles.bot),
            }}
          >
            {msg.text}
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.bubble, ...styles.bot }}>Typing...</div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div style={styles.inputRow}>
        <input
          type="text"
          placeholder="Type your message..."
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
        />
        <button style={styles.sendBtn} onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { padding: "20px", maxWidth: "900px", margin: "0 auto" },
  title: { fontSize: "22px", fontWeight: "bold", marginBottom: "15px" },
  chatBox: {
    height: "60vh",
    background: "#fff",
    borderRadius: "10px",
    padding: "15px",
    overflowY: "auto",
    boxShadow: "0 0 12px rgba(0,0,0,0.1)",
  },
  bubble: {
    maxWidth: "80%",
    padding: "10px",
    marginBottom: "12px",
    borderRadius: "10px",
    fontSize: "15px",
    lineHeight: "1.4",
  },
  me: {
    background: "#4A4AE1",
    color: "#fff",
    marginLeft: "auto",
  },
  bot: {
    background: "#f1f1f1",
    color: "#333",
    marginRight: "auto",
  },
  inputRow: {
    display: "flex",
    marginTop: "15px",
    gap: "10px",
  },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "15px",
  },
  sendBtn: {
    padding: "12px 20px",
    background: "#4A4AE1",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
};
