import React, { useEffect, useState, useRef } from "react";
import { format } from "date-fns";
import { getAllReviews, postReview } from "../services/api";

export default function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);
  const [submitting, setSubmitting] = useState(false);
  const evtSourceRef = useRef(null);
  const lastIdRef = useRef(0);

  const user = JSON.parse(localStorage.getItem("user") || localStorage.getItem("heartshield_user") || "null");

  const loadReviews = async () => {
    try {
      const res = await getAllReviews();
      if (res.success) {
        const revs = res.reviews || [];
        setReviews(revs);
        if (revs.length) lastIdRef.current = Math.max(...revs.map(r => r.id));
      }
    } catch (error) {
      console.error("Error loading reviews:", error);
    }
  };

  useEffect(() => {
    // Load reviews using the available API method
    (async () => {
      await loadReviews();
    })();
    
    // Open SSE stream for real-time updates
    const lastSeen = lastIdRef.current || 0;
    const es = new EventSource(`/api/reviews/stream?last_id=${lastSeen}`);
    evtSourceRef.current = es;

    es.onmessage = (e) => {
      try {
        const obj = JSON.parse(e.data);
        if (obj && obj.review) {
          setReviews(prev => [...prev, obj.review]);
          lastIdRef.current = Math.max(lastIdRef.current, obj.review.id);
        }
      } catch (error) {
        console.error("Error parsing review stream:", error);
      }
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      alert("Please login to submit a review.");
      return;
    }
    if (!comment.trim()) {
      alert("Please add a comment.");
      return;
    }

    setSubmitting(true);

    const payload = {
      user_id: user.id,
      username: user.username,
      rating,
      comment: comment.trim()
    };

    // Optimistic update
    const optimisticReview = {
      id: Date.now() * -1, // Temporary negative ID
      user_id: payload.user_id,
      username: payload.username,
      rating: payload.rating,
      comment: payload.comment,
      created_at: new Date().toISOString()
    };
    
    setReviews(prev => [...prev, optimisticReview]);
    setComment("");

    try {
      const res = await postReview(payload);

      if (res.success && res.review) {
        // Replace optimistic entry with real review from server
        setReviews(prev => prev.map(r => 
          r.id === optimisticReview.id ? res.review : r
        ));
      } else {
        // Remove optimistic review if submission failed
        setReviews(prev => prev.filter(r => r.id !== optimisticReview.id));
        alert(res.error || "Unable to submit review");
      }
    } catch {
      // Remove optimistic review on network error
      setReviews(prev => prev.filter(r => r.id !== optimisticReview.id));
      alert("Network error submitting review");
    }
    
    setSubmitting(false);
  };

  // Calculate average rating
  const avgRating = reviews.length 
    ? (reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length).toFixed(1)
    : "—";

  const handleLogout = () => {
    localStorage.removeItem("heartshield_user");
    window.location.href = "/login";
  };

  return (
    <div className="reviews-page">
      <div className="navbar">
        <h2>HeartShield</h2>
        <div className="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/history">History</a>
          <a href="/profile">Profile</a>
          <a href="/chatbot">Chat</a>
          <a href="/reviews">Reviews</a>
          <button 
            className="btn-cta logout-btn" 
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="app-container">
        <h1 className="page-title">User Reviews</h1>

        {/* Review form */}
        <div className="review-form-card">
          <h3>Leave a Review</h3>
          <textarea
            className="review-textarea"
            placeholder="Share your experience with HeartShield..."
            rows="4"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
          
          <div className="rating-selector">
            <label>Rating</label>
            <select 
              value={rating} 
              onChange={(e) => setRating(Number(e.target.value))}
              className="rating-select"
            >
              <option value={5}>5 - Excellent</option>
              <option value={4}>4 - Very Good</option>
              <option value={3}>3 - Good</option>
              <option value={2}>2 - Fair</option>
              <option value={1}>1 - Poor</option>
            </select>
          </div>

          <button 
            className="submit-review-btn" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? "Submitting..." : "Submit Review"}
          </button>
        </div>

        {/* Stats section */}
        <div className="reviews-stats">
          <div className="average-rating">{avgRating} / 5</div>
          <div className="review-count">{reviews.length} review(s)</div>
        </div>

        {/* Reviews display */}
        {reviews.length === 0 ? (
          <div className="no-reviews">
            No reviews yet — be the first to post!
          </div>
        ) : (
          <div className="reviews-grid">
            {reviews.slice().reverse().map(review => (
              <div key={review.id} className={`review-card rating-${review.rating || 0}`}>
                <div className="review-meta">
                  {review.username || "Anonymous"} • {review.created_at 
                    ? format(new Date(review.created_at), "dd MMM yyyy HH:mm") 
                    : "just now"}
                </div>
                <div className="review-comment">
                  {review.comment}
                </div>
                {review.rating && (
                  <div className="review-rating">
                    Rating: {review.rating}/5
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx>{`
        .reviews-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #eeeff3ff 0%, #764ba2 100%);
        }

        .navbar {
          background: rgba(247, 9, 9, 0.8);
          padding: 15px 30px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: white;
        }

        .navbar h2 {
          margin: 0;
          font-size: 1.8rem;
        }

        .nav-links {
          display: flex;
          gap: 20px;
          align-items: center;
        }

        .nav-links a {
          color: white;
          text-decoration: none;
          transition: opacity 0.3s;
        }

        .nav-links a:hover {
          opacity: 0.8;
        }

        .logout-btn {
          background: #1b1919ff;
          color: white;
          padding: 8px 16px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          transition: background 0.3s;
        }

        .logout-btn:hover {
          background: #c0392b;
        }

        .app-container {
          max-width: 1000px;
          margin: 30px auto;
          padding: 0 20px;
        }

        .page-title {
          color: white;
          text-align: center;
          margin-bottom: 40px;
          font-size: 2.5rem;
        }

        .review-form-card {
          background: white;
          padding: 30px;
          border-radius: 15px;
          margin-bottom: 40px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .review-form-card h3 {
          color: #010a13ff;
          margin-top: 0;
        }

        .review-textarea {
          width: 100%;
          padding: 12px;
          border: 2px solid #0a86deff;
          border-radius: 8px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
          box-sizing: border-box;
        }

        .review-textarea:focus {
          outline: none;
          border-color: #e5e6ecff;
        }

        .rating-selector {
          margin: 20px 0;
        }

        .rating-selector label {
          display: block;
          color: #156bc1ff;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .rating-select {
          width: 100%;
          padding: 10px;
          border: 2px solid #e1e8ed;
          border-radius: 8px;
          font-size: 1rem;
          cursor: pointer;
          box-sizing: border-box;
        }

        .rating-select:focus {
          outline: none;
          border-color: #667eea;
        }

        .submit-review-btn {
          width: 100%;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 12px;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          margin-top: 15px;
        }

        .submit-review-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .submit-review-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .reviews-stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 40px;
        }

        .average-rating {
          background: white;
          padding: 30px;
          border-radius: 15px;
          text-align: center;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
          font-size: 3rem;
          font-weight: bold;
          color: #667eea;
        }

        .review-count {
          background: white;
          padding: 30px;
          border-radius: 15px;
          text-align: center;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
          font-size: 1.5rem;
          color: #2c3e50;
        }

        .no-reviews {
          background: white;
          padding: 40px;
          border-radius: 15px;
          text-align: center;
          color: #2ba4adff;
          font-size: 1.2rem;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .reviews-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
        }

        .review-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s, box-shadow 0.3s;
          border-left: 5px solid #1f3bb8ff;
        }

        .review-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }

        .review-card.rating-5 {
          border-left-color: #27ae60;
          background: linear-gradient(135deg, rgba(39, 174, 96, 0.05), white);
        }

        .review-card.rating-4 {
          border-left-color: #3498db;
          background: linear-gradient(135deg, rgba(52, 152, 219, 0.05), white);
        }

        .review-card.rating-3 {
          border-left-color: #f39c12;
          background: linear-gradient(135deg, rgba(243, 156, 18, 0.05), white);
        }

        .review-card.rating-2 {
          border-left-color: #e67e22;
          background: linear-gradient(135deg, rgba(230, 126, 34, 0.05), white);
        }

        .review-card.rating-1 {
          border-left-color: #e74c3c;
          background: linear-gradient(135deg, rgba(231, 76, 60, 0.05), white);
        }

        .review-meta {
          font-size: 0.9rem;
          color: #7f8c8d;
          margin-bottom: 12px;
          font-weight: 500;
        }

        .review-comment {
          color: #2c3e50;
          font-size: 1rem;
          line-height: 1.6;
          margin-bottom: 15px;
          word-wrap: break-word;
        }

        .review-rating {
          color: #667eea;
          font-weight: 600;
          font-size: 0.95rem;
        }
      `}</style>
    </div>
  );
}