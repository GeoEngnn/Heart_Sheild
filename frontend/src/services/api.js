const BASE_URL = "http://localhost:5000";

// User Authentication
export async function register(data) {
  const res = await fetch(`${BASE_URL}/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function login(data) {
  console.log('API: Sending login request to:', `${BASE_URL}/api/login`);
  console.log('API: Request data:', data);
  
  try {
    const res = await fetch(`${BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    
    console.log('API: Response status:', res.status);
    console.log('API: Response headers:', res.headers);
    
    const result = await res.json();
    console.log('API: Response data:', result);
    
    return result;
  } catch (error) {
    console.error('API: Fetch error:', error);
    throw error;
  }
}

// User Data
export async function getUserStatus(userId) {
  const res = await fetch(`${BASE_URL}/api/status/${userId}`);
  return res.json();
}

export async function getUserHistory(userId) {
  const res = await fetch(`${BASE_URL}/api/history/${userId}`);
  return res.json();
}

// Chatbot
export async function sendMessage(message, userId) {
  const res = await fetch(`${BASE_URL}/api/chatbot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, userId }),
  });
  return res.json();
}

// ===== REVIEW SYSTEM API =====

// Get all reviews
export async function getAllReviews() {
  const res = await fetch(`${BASE_URL}/api/reviews`);
  return res.json();
}

// Get reviews by specific user
export async function getReviewsByUser(userId) {
  const res = await fetch(`${BASE_URL}/api/reviews/${userId}`);
  return res.json();
}

// Submit a new review
export async function postReview({ user_id, username, rating, comment }) {
  const res = await fetch(`${BASE_URL}/api/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, username, rating, comment }),
  });
  return res.json();
}

// Get review statistics
export async function getReviewStats() {
  const res = await fetch(`${BASE_URL}/api/reviews/stats`);
  return res.json();
}

// Real-time SSE stream for live review updates
export function createReviewsEventSource(onMessage) {
  const es = new EventSource(`${BASE_URL}/api/reviews/stream`);
  es.onopen = () => console.log("SSE: connected to reviews stream");
  es.onerror = (e) => console.warn("SSE error", e);
  es.onmessage = (e) => {
    // e.data is a JSON string (or ping)
    try {
      const payload = JSON.parse(e.data);
      onMessage(payload);
    } catch {
      // ignore pings or non-json
      console.log("SSE: Received ping or non-JSON message");
    }
  };
  return es;
}

// Update user profile
export async function updateProfile(userId, data) {
  const res = await fetch(`${BASE_URL}/api/update-profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, ...data }),
  });
  return res.json();
}