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
    </div>
  );
}