import { createContext, useContext, useState, useCallback } from 'react';
import { moodAPI } from '../services/api';

const MoodContext = createContext();

export const useMood = () => {
  const context = useContext(MoodContext);
  if (!context) {
    throw new Error('useMood must be used within a MoodProvider');
  }
  return context;
};

export const MoodProvider = ({ children }) => {
  const [currentMood, setCurrentMood] = useState(null);
  const [moodHistory, setMoodHistory] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const analyzeMood = useCallback(async (text) => {
    if (!text || text.trim().length < 10) {
      setError('Please write at least 10 characters');
      return null;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await moodAPI.analyzeMood(text);
      
      if (response.success) {
        const moodData = response.data;
        setCurrentMood(moodData);
        
        // Add to history
        const newEntry = {
          id: Date.now(),
          text: text,
          mood: moodData.mood,
          confidence: moodData.confidence,
          timestamp: new Date().toISOString(),
          emotions: moodData.emotions,
          keywords: moodData.keywords
        };
        
        setMoodHistory(prev => [newEntry, ...prev.slice(0, 49)]); // Keep last 50 entries
        return moodData;
      } else {
        setError(response.message || 'Failed to analyze mood');
        return null;
      }
    } catch (err) {
      console.error('Mood analysis error:', err);
      setError('Something went wrong. Please try again.');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const getEnrichedMood = useCallback(async (text) => {
    if (!text || text.trim().length < 10) {
      setError('Please write at least 10 characters');
      return null;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await moodAPI.getEnrichedMood(text);
      
      if (response.success) {
        return response.data;
      } else {
        setError(response.message || 'Failed to get enriched mood analysis');
        return null;
      }
    } catch (err) {
      console.error('Enriched mood analysis error:', err);
      setError('Something went wrong. Please try again.');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const getCompleteAnalysis = useCallback(async (text) => {
    if (!text || text.trim().length < 10) {
      setError('Please write at least 10 characters');
      return null;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await moodAPI.getCompleteAnalysis(text);
      
      if (response.success) {
        return response.data;
      } else {
        setError(response.message || 'Failed to get complete analysis');
        return null;
      }
    } catch (err) {
      console.error('Complete analysis error:', err);
      setError('Something went wrong. Please try again.');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearMoodHistory = useCallback(() => {
    setMoodHistory([]);
  }, []);

  const value = {
    currentMood,
    moodHistory,
    isAnalyzing,
    error,
    analyzeMood,
    getEnrichedMood,
    getCompleteAnalysis,
    clearError,
    clearMoodHistory
  };

  return (
    <MoodContext.Provider value={value}>
      {children}
    </MoodContext.Provider>
  );
};
