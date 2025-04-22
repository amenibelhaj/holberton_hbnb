document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const logoutLink = document.getElementById('logout-link');
    const loginLink = document.getElementById('login-link');
    const placeDetailsSection = document.getElementById('place-details');
    const addReviewForm = document.getElementById('review-form');
    const placesList = document.querySelector('.places-grid');
    const priceFilter = document.getElementById('max-price');
  
    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);
        });
    } else {
        checkAuthentication();
        
        // Only run these if on the index page
        if (placesList) {
            populatePriceFilter();
            setupPriceFilter();
        }
        
        // Only fetch place details if on the place details page
        if (placeDetailsSection) {
            fetchPlaceDetails();
        }
    }
  
    // Logout handler
    if (logoutLink) {
        logoutLink.addEventListener('click', async (e) => {
            e.preventDefault();
            await logoutUser();
            window.location.href = 'index.html';
        });
    }
  
    // Fetch place details - only runs on place.html
    async function fetchPlaceDetails() {
        const placeId = getPlaceIdFromURL();
        if (!placeId) {
            console.error('Place ID not found in URL');
            return;
        }
  
        try {
            const token = getCookie('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, { headers });
  
            if (response.ok) {
                const placeData = await response.json();
                displayPlaceDetails(placeData);
            } else {
                console.error('Failed to fetch place details', await response.json());
            }
        } catch (error) {
            console.error('Error fetching place details:', error);
        }
    }
  
    // Improved place details display
    async function displayPlaceDetails(placeData) {
        if (!placeDetailsSection) return;
  
        const place = placeData.place || {};
        const amenities = placeData.associated_amenities || [];
        console.log('Amenities Data:', amenities);
  
        placeDetailsSection.innerHTML = `
            <h2>${place.title || 'Place Name Not Available'}</h2>
            <p><strong>Description:</strong> ${place.description || 'Not available'}</p>
            <p><strong>Price per night:</strong> ${place.price ? `$${place.price}` : 'Not available'}</p>
            <p><strong>Amenities:</strong> ${await fetchAmenityNames(amenities)}</p>
            <h3>Reviews</h3>
            <ul>
                ${place.reviews && place.reviews.length 
                    ? place.reviews.map(review => `
                        <li>
                            <p><strong>${review.user || 'Anonymous'}</strong>: ${review.comment || 'No comment'}</p>
                        </li>`).join('')
                    : '<li>No reviews available</li>'}
            </ul>
        `;
  
        if (addReviewForm) {
            addReviewForm.style.display = getCookie('token') ? 'block' : 'none';
        }
    }
  
    // Fetch amenity names from the IDs array
    async function fetchAmenityNames(ids) {
        if (ids.length === 0) {
            return 'No amenities available';
        }
  
        const names = await Promise.all(ids.map(async (id) => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/api/v1/amenities/${id}`);
                if (response.ok) {
                    const data = await response.json();
                    return data.name;
                }
            } catch (error) {
                console.error('Error fetching amenity:', error);
            }
            return null;
        }));
        return names.filter(name => name).join(', ') || 'No amenities available';
    }
  
    // Authentication functions
    async function loginUser(email, password) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
  
            if (response.ok) {
                const data = await response.json();
                document.cookie = `token=${data.access_token}; path=/`;
                window.location.href = 'index.html';
            } else {
                const errorData = await response.json();
                alert('Login failed: ' + (errorData.message || response.statusText));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    }
  
    function logoutUser() {
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
  
    function checkAuthentication() {
        const token = getCookie('token');
        if (loginLink) loginLink.style.display = token ? 'none' : 'block';
        if (logoutLink) logoutLink.style.display = token ? 'block' : 'none';
        
        // Only fetch places if on index page and authenticated
        if (token && placesList) {
            fetchPlaces(token);
        }
    }
  
    // Places listing functions
    async function fetchPlaces(token) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
  
            if (response.ok) {
                displayPlaces(await response.json());
            } else {
                console.error('Failed to fetch places');
            }
        } catch (error) {
            console.error('Error fetching places:', error);
        }
    }
  
    function displayPlaces(places) {
        if (!placesList) return;
        
        placesList.innerHTML = places.map(place => `
            <div class="place-card" data-price="${place.price}">
                <h2>${place.title}</h2>
                <p class="price">Price per night: $${place.price}</p>
                <a href="place.html?id=${place.id}" class="details-button">View Details</a>
            </div>
        `).join('');
    }
  
    // Price filter functions
    function populatePriceFilter() {
        if (!priceFilter) return;
        
        priceFilter.innerHTML = ['All', '50', '100', '150', '200', '250', '300']
            .map(price => `<option value="${price}">${price === 'All' ? 'All' : `$${price}`}</option>`)
            .join('');
    }
  
    function setupPriceFilter() {
        if (!priceFilter) return;
        
        priceFilter.addEventListener('change', () => {
            const selectedPrice = priceFilter.value;
            document.querySelectorAll('.place-card').forEach(card => {
                card.style.display = (selectedPrice === 'All' || parseFloat(card.dataset.price) <= selectedPrice) 
                    ? 'block' 
                    : 'none';
            });
        });
    }
  
    // Review submission logic
    const reviewForm = document.getElementById('review-form');
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();
  
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Get the review text and rating from the form
            const reviewText = document.getElementById('review-text').value;
            const rating = document.getElementById('rating').value;
  
            // Debug log
            console.log('Place ID:', placeId);
            console.log('Review Text:', reviewText);
            console.log('Rating:', rating);
            
            if (!placeId) {
                console.error('Place ID is missing or invalid');
                alert('Invalid Place ID');
                return;
            }
            
            await submitReview(token, placeId, reviewText, rating);
        });
    }
  
    // Function to extract place ID from the URL query parameters
function getPlaceIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('id');
    console.log('Full URL:', window.location.href); // Debug log
    console.log('Extracted placeId from URL:', placeId); // Debug log
    return placeId;
}

    // Function to submit the review
    async function submitReview(token, placeId, reviewText, rating) {
        const url = `http://127.0.0.1:5000/api/v1/reviews/places/${placeId}/reviews`;
  
        const reviewData = {
            text: reviewText,
            rating: rating,
            place_id: placeId
        };
    
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(reviewData),
            });
    
            if (response.ok) {
                const responseData = await response.json();
                console.log('Review submitted:', responseData);
                alert('Review submitted successfully!');
                
            } else {
                const errorData = await response.json();
                console.error('Error submitting review:', errorData);
                alert(`Failed to submit review: ${errorData.message || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred while submitting the review.');
        }
    }
  });
  