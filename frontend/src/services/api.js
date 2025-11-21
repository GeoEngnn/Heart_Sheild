const BASE_URL = "http://localhost:5000";



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

/* ✅ Correct endpoint for status */
export async function getUserStatus(userId) {
  const res = await fetch(`${BASE_URL}/api/status/${userId}`);
  return res.json();
}

/* ✅ Correct endpoint for history */
export async function getUserHistory(userId) {
  const res = await fetch(`${BASE_URL}/api/history/${userId}`);
  return res.json();
}

/* ✅ Chatbot API */
export async function sendMessage(message, userId) {
  const res = await fetch(`${BASE_URL}/api/chatbot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, userId }),
  });

  return res.json();
}
