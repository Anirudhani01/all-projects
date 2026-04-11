// src/OwnerDashboard.jsx
import React, { useState } from 'react';

function OwnerDashboard() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleAsk = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/nlp-query/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
      <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '1rem' }}>Owner Chatbot Dashboard</h1>
      <form onSubmit={handleAsk} style={{ width: '100%', maxWidth: '36rem' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.25rem', marginBottom: '1rem' }}
          placeholder="Ask something like 'What is the total revenue?'"
          required
        />
        <button
          type="submit"
          style={{ backgroundColor: '#3b82f6', color: 'white', padding: '0.5rem 1.5rem', borderRadius: '0.25rem', width: '100%' }}
          onMouseOver={(e) => (e.target.style.backgroundColor = '#2563eb')}
          onMouseOut={(e) => (e.target.style.backgroundColor = '#3b82f6')}
        >
          Ask
        </button>
      </form>

      {answer && (
        <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: 'white', borderRadius: '0.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', width: '100%', maxWidth: '36rem' }}>
          <p style={{ fontSize: '1.125rem', fontWeight: '500' }}>Answer:</p>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default OwnerDashboard;