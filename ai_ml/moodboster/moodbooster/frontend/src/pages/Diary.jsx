import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMood } from '../contexts/MoodContext';
import { externalAPI } from '../services/api';
import { 
  Send, 
  Mic, 
  MicOff, 
  Loader2, 
  Heart, 
  Music, 
  Video, 
  Quote,
  ThumbsUp,
  ThumbsDown,
  RefreshCw
} from 'lucide-react';
import DiaryInput from '../components/DiaryInput';
import ResponseCard from '../components/ResponseCard';
import MoodDisplay from '../components/MoodDisplay';

const Diary = () => {
  const { 
    currentMood, 
    isAnalyzing, 
    error, 
    analyzeMood, 
    getCompleteAnalysis,
    clearError 
  } = useMood();
  
  const [diaryText, setDiaryText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [content, setContent] = useState(null);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleSubmit = async (text) => {
    if (!text || text.trim().length < 10) {
      return;
    }

    setDiaryText(text);
    setAnalysisResult(null);
    setContent(null);
    setFeedback(null);
    clearError();

    try {
      // Get complete analysis (mood + context + decision + content)
      const result = await getCompleteAnalysis(text);
      
      if (result) {
        setAnalysisResult(result);
        
        // If we have a response plan, load the content
        if (result.response_plan) {
          await loadContent(result.mood_analysis.mood);
        }
      }
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  };

  const loadContent = async (mood) => {
    setIsLoadingContent(true);
    
    try {
      const response = await externalAPI.getUnifiedContent(
        mood, 
        ['quote', 'music', 'video'], 
        3
      );
      
      if (response.success) {
        setContent(response.data);
      }
    } catch (err) {
      console.error('Content loading failed:', err);
    } finally {
      setIsLoadingContent(false);
    }
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    // Here you would typically send feedback to the backend
    console.log('Feedback:', type);
  };

  const handleTryAgain = () => {
    if (currentMood) {
      loadContent(currentMood.mood);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            How are you feeling today?
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Share your thoughts and let us help brighten your day
          </p>
        </div>

        {/* Diary Input */}
        <div className="mb-8">
          <DiaryInput 
            onSubmit={handleSubmit}
            isAnalyzing={isAnalyzing}
            error={error}
          />
        </div>

        {/* Analysis Results */}
        <AnimatePresence>
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8"
            >
              <MoodDisplay 
                moodAnalysis={analysisResult.mood_analysis}
                contextAnalysis={analysisResult.context_analysis}
                themeAnalysis={analysisResult.theme_analysis}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content Recommendations */}
        <AnimatePresence>
          {(content || isLoadingContent) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8"
            >
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Here's something for you
                  </h2>
                  <button
                    onClick={handleTryAgain}
                    disabled={isLoadingContent}
                    className="flex items-center space-x-2 px-4 py-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${isLoadingContent ? 'animate-spin' : ''}`} />
                    <span>Try something else</span>
                  </button>
                </div>

                {isLoadingContent ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
                    <span className="ml-3 text-gray-600 dark:text-gray-300">
                      Finding the perfect content for you...
                    </span>
                  </div>
                ) : content ? (
                  <div className="space-y-6">
                    {/* Quotes */}
                    {content.content?.quote?.items && content.content.quote.items.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                          <Quote className="w-5 h-5 mr-2 text-secondary-500" />
                          Inspirational Quotes
                        </h3>
                        <div className="grid gap-4">
                          {content.content.quote.items.map((quote, index) => (
                            <ResponseCard
                              key={index}
                              type="quote"
                              data={quote}
                              onFeedback={handleFeedback}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Music */}
                    {content.content?.music?.items && content.content.music.items.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                          <Music className="w-5 h-5 mr-2 text-primary-500" />
                          Music Recommendations
                        </h3>
                        <div className="grid gap-4">
                          {content.content.music.items.map((track, index) => (
                            <ResponseCard
                              key={index}
                              type="music"
                              data={track}
                              onFeedback={handleFeedback}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Videos */}
                    {content.content?.video?.items && content.content.video.items.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                          <Video className="w-5 h-5 mr-2 text-red-500" />
                          Video Content
                        </h3>
                        <div className="grid gap-4">
                          {content.content.video.items.map((video, index) => (
                            <ResponseCard
                              key={index}
                              type="video"
                              data={video}
                              onFeedback={handleFeedback}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : null}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feedback Section */}
        {feedback && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-8"
          >
            <div className="flex items-center">
              <Heart className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-700 dark:text-green-300">
                Thank you for your feedback! We'll use this to improve your experience.
              </span>
            </div>
          </motion.div>
        )}

        {/* Call to Action */}
        {!analysisResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Ready to get started?
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Write about your day, your feelings, or anything on your mind. 
                Our AI will analyze your mood and provide personalized support.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => document.getElementById('diary-textarea')?.focus()}
                  className="inline-flex items-center px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors"
                >
                  Start Writing
                </button>
                <button
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                  className="inline-flex items-center px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  Learn More
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Diary;
