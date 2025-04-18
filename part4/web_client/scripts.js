// This file contains JavaScript functionality for the pages.

document.addEventListener('DOMContentLoaded', () => {
    // Get the current page URL to determine what functionality is needed
    const pageUrl = window.location.pathname;
    
    // Handle functionality for List of Places page (index.html)
    if (pageUrl.includes('index.html')) {
        loadPlaces();
        setupPriceFilter();
    }

    // Handle functionality for Login page (login.html)
    if (pageUrl.includes('login.html')) {
        setupLoginForm();
    }

    // Handle functionality for Place Details page (place.html)
    if (pageUrl.includes('place.html')) {
        const placeId = new URLSearchParams(window.location.search).get('id');
        if (placeId) {
            loadPlaceDetails(placeId);
            loadReviews(placeId);
        }
    }

    // Handle functionality for Add Review page (add_review.html)
    if (pageUrl.includes('add_review.html')) {
        setupReviewForm();
    }
});

// Function to load places dynamically in index.html
function loadPlaces() {
    const placesList = document.getElementById('places-list');

    fetch('https://your-api-endpoint.com/places') // Replace with your API endpoint
        .then(response => response.json())
        .then(places => {
            places.forEach(place => {
                const placeCard = document.createElement('div');
                placeCard.classList.add('place-card');
                placeCard.innerHTML = `
                    <h3>${place.name}</h3>
                    <p><strong>Price per night:</strong> $${place.price_per_night}</p>
                    <button class="details-button" data-id="${place.id}">View Details</button>
                `;
                placesList.appendChild(placeCard);
            });

            // Add event listener for the "View Details" buttons
            document.querySelectorAll('.details-button').forEach(button => {
                button.addEventListener('click', (event) => {
                    const placeId = event.target.dataset.id;
                    window.location.href = `place.html?id=${placeId}`;
                });
            });
        })
        .catch(error => console.error('Error loading places:', error));
}

// Function to set up the price filter in index.html
function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');

    priceFilter.addEventListener('change', (event) => {
        const maxPrice = event.target.value;
        filterPlacesByPrice(maxPrice);
    });
}

// Function to filter places by price range (in index.html)
function filterPlacesByPrice(maxPrice) {
    const placeCards = document.querySelectorAll('.place-card');
    placeCards.forEach(card => {
        const price = parseInt(card.querySelector('p').textContent.replace(/[^\d]/g, '')); // Extract price
        if (price > maxPrice) {
            card.style.display = 'none';
        } else {
            card.style.display = 'block';
        }
    });
}

// Function to set up login form (login.html)
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        loginUser(email, password);
    });
}

// Function to login user
function loginUser(email, password) {
    fetch('https://your-api-endpoint.com/login', { // Replace with your API endpoint
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                localStorage.setItem('auth_token', data.token);
                window.location.href = 'index.html'; // Redirect to the homepage
            } else {
                alert('Login failed');
            }
        })
        .catch(error => console.error('Error logging in:', error));
}

// Function to load place details (place.html)
function loadPlaceDetails(placeId) {
    const placeDetailsSection = document.getElementById('place-details');

    fetch(`https://your-api-endpoint.com/places/${placeId}`) // Replace with your API endpoint
        .then(response => response.json())
        .then(place => {
            placeDetailsSection.innerHTML = `
                <h1>${place.name}</h1>
                <p><strong>Host:</strong> ${place.host}</p>
                <p><strong>Price:</strong> $${place.price_per_night}/night</p>
                <p><strong>Description:</strong> ${place.description}</p>
                <p><strong>Amenities:</strong> ${place.amenities.join(', ')}</p>
            `;
        })
        .catch(error => console.error('Error loading place details:', error));
}

// Function to load reviews for a place (place.html)
function loadReviews(placeId) {
    const reviewsSection = document.getElementById('reviews');

    fetch(`https://your-api-endpoint.com/places/${placeId}/reviews`) // Replace with your API endpoint
        .then(response => response.json())
        .then(reviews => {
            reviews.forEach(review => {
                const reviewCard = document.createElement('div');
                reviewCard.classList.add('review-card');
                reviewCard.innerHTML = `
                    <p><strong>${review.user_name}</strong> (${review.rating} stars)</p>
                    <p>${review.comment}</p>
                `;
                reviewsSection.appendChild(reviewCard);
            });
        })
        .catch(error => console.error('Error loading reviews:', error));
}

// Function to set up the review form (add_review.html)
function setupReviewForm() {
    const reviewForm = document.getElementById('review-form');

    reviewForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const reviewText = document.getElementById('review-text').value;
        const rating = document.getElementById('rating').value;

        addReview(reviewText, rating);
    });
}

// Function to submit a review (add_review.html)
function addReview(reviewText, rating) {
    const placeId = new URLSearchParams(window.location.search).get('id');
    const token = localStorage.getItem('auth_token');

    if (!token) {
        alert('You need to be logged in to add a review.');
        return;
    }

    fetch(`https://your-api-endpoint.com/places/${placeId}/reviews`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ review: reviewText, rating })
    })
        .then(response => response.json())
        .then(review => {
            alert('Review submitted successfully!');
            window.location.href = `place.html?id=${placeId}`; // Redirect to the place details page
        })
        .catch(error => console.error('Error submitting review:', error));
}
