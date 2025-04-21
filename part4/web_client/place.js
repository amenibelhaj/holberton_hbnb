// Utility functions
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  
  function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id'); // expects ?id=PLACE_ID
  }
  
  // Fetch place details based on placeId
  async function fetchPlaceDetails(placeId) {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`);
      const data = await response.json();
  
      if (!data) {
        document.getElementById('place-details').innerHTML = '<p>Place not found.</p>';
        return;
      }
  
      // Update place title and details dynamically
      document.querySelector('.place-details h1').textContent = data.title || 'Place Details';
      document.querySelector('#place-details').innerHTML = `
        <h1>${data.title || 'Unnamed Place'}</h1>
        <p><strong>Host:</strong> ${data.owner?.name || 'Unknown'}</p>
        <p><strong>Price per night:</strong> $${data.price_per_night}</p>
        <p><strong>Description:</strong> ${data.description}</p>
        <div class="amenities">${(data.amenities || []).map(a => `<span class="amenity-tag">${a}</span>`).join('')}</div>
      `;
      
      // Optionally, show the Add Review section
      document.getElementById('add-review').style.display = 'block';
  
    } catch (err) {
      console.error('Error fetching place:', err);
      document.getElementById('place-details').innerHTML = '<p>Failed to load place details.</p>';
    }
  }
  
  // Fetch reviews for the place
  async function fetchReviews(placeId) {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}/reviews`);
      const reviews = await response.json();
      displayReviews(reviews);
    } catch (err) {
      console.error('Error fetching reviews:', err);
    }
  }
  
  // Display reviews dynamically
  function displayReviews(reviews) {
    const container = document.getElementById('reviews-container');
    container.innerHTML = '';
  
    if (!reviews || reviews.length === 0) {
      container.innerHTML = `<p>No reviews yet.</p>`;
      return;
    }
  
    reviews.forEach(review => {
      const reviewEl = document.createElement('div');
      reviewEl.className = 'review';
      reviewEl.innerHTML = `
        <div class="review-header">
          <span class="review-author">${review.author || 'Anonymous'}</span>
          <span class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
        </div>
        <p class="review-content">${review.text}</p>
      `;
      container.appendChild(reviewEl);
    });
  }
  
  // Submit a new review
  async function handleReviewSubmit(event, placeId) {
    event.preventDefault();
  
    const reviewText = document.getElementById('review-text').value;
    const token = getCookie('token'); // Get token from cookie
  
    if (!token) {
      alert('You must be logged in to submit a review.');
      return;
    }
  
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ text: reviewText, rating: 5 }), // Example review data
      });
  
      if (response.ok) {
        const data = await response.json();
        alert('Review submitted successfully!');
        fetchReviews(placeId); // Reload reviews
      } else {
        const errorData = await response.json();
        alert('Failed to submit review: ' + (errorData.message || response.statusText));
      }
    } catch (err) {
      console.error('Error submitting review:', err);
      alert('Something went wrong while submitting your review.');
    }
  }
  
  // Initialization - get place details and reviews
  document.addEventListener('DOMContentLoaded', () => {
    const placeId = getPlaceIdFromURL();
    if (!placeId) return;
  
    fetchPlaceDetails(placeId);
    fetchReviews(placeId);
  
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
      reviewForm.addEventListener('submit', (event) => handleReviewSubmit(event, placeId));
    }
  });
  