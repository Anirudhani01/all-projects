import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const SimpleHome = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1 style={{ color: 'blue', fontSize: '2rem' }}>MoodBooster - Simple Test</h1>
      <p>If you can see this, React Router is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
      <div style={{ marginTop: '20px' }}>
        <a href="/diary" style={{ margin: '10px', padding: '10px', background: 'lightblue', textDecoration: 'none' }}>Go to Diary</a>
        <a href="/profile" style={{ margin: '10px', padding: '10px', background: 'lightgreen', textDecoration: 'none' }}>Go to Profile</a>
      </div>
    </div>
  );
};

const SimpleDiary = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1 style={{ color: 'green', fontSize: '2rem' }}>Diary Page</h1>
      <p>This is the diary page!</p>
      <a href="/" style={{ margin: '10px', padding: '10px', background: 'lightblue', textDecoration: 'none' }}>Back to Home</a>
    </div>
  );
};

const SimpleProfile = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1 style={{ color: 'purple', fontSize: '2rem' }}>Profile Page</h1>
      <p>This is the profile page!</p>
      <a href="/" style={{ margin: '10px', padding: '10px', background: 'lightblue', textDecoration: 'none' }}>Back to Home</a>
    </div>
  );
};

const SimpleApp = () => {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<SimpleHome />} />
          <Route path="/diary" element={<SimpleDiary />} />
          <Route path="/profile" element={<SimpleProfile />} />
        </Routes>
      </div>
    </Router>
  );
};

export default SimpleApp;
