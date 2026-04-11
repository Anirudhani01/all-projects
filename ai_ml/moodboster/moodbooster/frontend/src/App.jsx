import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { MoodProvider } from './contexts/MoodContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Diary from './pages/Diary';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <MoodProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/diary" element={<Diary />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
      </MoodProvider>
    </ThemeProvider>
  );
}

export default App;