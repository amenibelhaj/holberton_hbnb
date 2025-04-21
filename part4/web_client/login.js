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
  
  document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
  });
  