// src/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [ownerId, setOwnerId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (ownerId === 'anirudh' && password === 'password123') {
      navigate('/dashboard');
    } else {
      setError('Invalid credentials');
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '0.375rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', width: '24rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', textAlign: 'center' }}>Owner Login</h1>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>Owner ID</label>
            <input
              type="text"
              value={ownerId}
              onChange={(e) => setOwnerId(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}
              required
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}
              required
            />
          </div>
          {error && <p style={{ color: '#ef4444', fontSize: '0.875rem', marginBottom: '1rem' }}>{error}</p>}
          <button
            type="submit"
            style={{ width: '100%', backgroundColor: '#3b82f6', color: 'white', padding: '0.5rem', borderRadius: '0.25rem' }}
            onMouseOver={(e) => (e.target.style.backgroundColor = '#2563eb')}
            onMouseOut={(e) => (e.target.style.backgroundColor = '#3b82f6')}
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;