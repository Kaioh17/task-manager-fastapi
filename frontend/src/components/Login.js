
import React, { useState } from 'react';

const API_URL = 'http://localhost:8000';

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      // Create URLSearchParams as expected by OAuth2PasswordRequestForm
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Store token (in a real app, you'd use localStorage)
      // For demo purposes, we'll call a callback function
      if (onLoginSuccess) {
        onLoginSuccess(data.access_token, {
          email: email,
          // You might want to fetch user details from another endpoint
        });
      }
      
      setEmail('');
      setPassword('');
      
    } catch (err) {
      console.error('Login error:', err);
      if (err.message.includes('429')) {
        setError('Too many login attempts. Please try again later.');
      } else if (err.message.includes('403')) {
        setError('Invalid email or password.');
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      maxWidth: '400px', 
      margin: '50px auto', 
      padding: '20px', 
      border: '1px solid #ddd', 
      borderRadius: '8px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h2 style={{ textAlign: 'center', color: '#333', marginBottom: '30px' }}>
        Task Manager Login
      </h2>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <input 
            type="email" 
            placeholder="Email Address" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required 
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
          />
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s'
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      {error && (
        <div style={{
          color: '#dc3545',
          marginTop: '15px',
          padding: '10px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          textAlign: 'center'
        }}>
          {error}
        </div>
      )}
    </div>
  );
}

// Example usage component
function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  const handleLoginSuccess = (accessToken, userInfo) => {
    setToken(accessToken);
    setUser(userInfo);
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
  };

  if (user && token) {
    return (
      <div style={{ 
        maxWidth: '600px', 
        margin: '50px auto', 
        padding: '20px',
        textAlign: 'center',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1>Welcome to Task Manager!</h1>
        <p>Successfully logged in as: {user.email}</p>
        <button 
          onClick={handleLogout}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
    );
  }

  return <Login onLoginSuccess={handleLoginSuccess} />;
}

export default App;