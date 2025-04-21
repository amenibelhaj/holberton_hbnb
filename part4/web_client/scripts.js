/*********************
 * Utility Functions *
 *********************/

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  
  /********************
   * Authentication   *
   ********************/
  
  function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
  
    if (!token) {
      if (loginLink) loginLink.style.display = 'block';
      fetchPlaces(); // Public view
    } else {
      if (loginLink) loginLink.style.display = 'none';
      fetchPlaces(token); // Authenticated view
    }
  }
  
  /********************
   * Places Functions *
   ********************/
  
  async function fetchPlaces(token = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
  
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        method: 'GET',
        headers: headers
      });
  
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  
      const places = await response.json();
      displayPlaces(places);
    } catch (error) {
      console.error('Error fetching places:', error);
      const placesList = document.getElementById('places-list');
      if (placesList) {
        placesList.innerHTML = `
          <div class="error-message">
            Failed to load places. ${error.message || 'Please try again later.'}
          </div>
        `;
      }
    }
  }
  
  function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
  
    placesList.innerHTML = '';
  
    if (!places || places.length === 0) {
      placesList.innerHTML = `
        <div class="no-results">
          No places available at the moment.
        </div>
      `;
      return;
    }
  
    places.forEach(place => {
      const placeElement = document.createElement('div');
      placeElement.className = 'place-card';
      placeElement.dataset.price = place.price_per_night || place.price || 0;
  
      placeElement.innerHTML = `
        <div class="place-card-header">
          <h2 class="place-name">${place.title?.trim() || 'Unnamed Place'}</h2>
          <p class="place-price">Price per night: $${placeElement.dataset.price}</p>
        </div>
        
        ${place.description ? `<p class="place-description">${place.description}</p>` : ''}
        ${place.city ? `<p class="place-location">Location: ${place.city}${place.country ? `, ${place.country}` : ''}</p>` : ''}
        <div class="place-footer">
          <button class="btn view-details">View Details</button>
        </div>
        <div class="divider"></div>
      `;
  
      placesList.appendChild(placeElement);
    });
  }
  
  
  
  function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    if (!priceFilter) return;
  
    priceFilter.addEventListener('change', (event) => {
      const selectedPrice = event.target.value;
      const placeCards = document.querySelectorAll('.place-card');
  
      placeCards.forEach(card => {
        if (selectedPrice === 'all') {
          card.style.display = 'block';
        } else {
          const placePrice = parseFloat(card.dataset.price) || 0;
          const maxPrice = parseFloat(selectedPrice);
          card.style.display = placePrice <= maxPrice ? 'block' : 'none';
        }
      });
    });
  }
  
  /********************
   * Login Form       *
   ********************/
  
  async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
  
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
  
      if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.token}; path=/`;
        window.location.href = 'index.html';
      } else {
        const errorData = await response.json();
        alert('Login failed: ' + (errorData.message || response.statusText));
      }
    } catch (err) {
      console.error('Login error:', err);
      alert('Something went wrong while trying to log in.');
    }
  }
  
  /********************
   * Initialization   *
   ********************/
  
  document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('places-list')) {
      checkAuthentication();
      setupPriceFilter();
    }
  
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
  });
  