import { motion } from 'framer-motion';
import { 
  Smile, 
  Frown, 
  Angry, 
  AlertTriangle, 
  Meh, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Brain,
  Target,
  Lightbulb
} from 'lucide-react';

const MoodDisplay = ({ moodAnalysis, contextAnalysis, themeAnalysis }) => {
  const getMoodIcon = (mood) => {
    const icons = {
      happy: Smile,
      sad: Frown,
      angry: Angry,
      stressed: AlertTriangle,
      neutral: Meh
    };
    return icons[mood] || Meh;
  };

  const getMoodColor = (mood) => {
    const colors = {
      happy: 'text-green-500 bg-green-100 dark:bg-green-900/20',
      sad: 'text-blue-500 bg-blue-100 dark:bg-blue-900/20',
      angry: 'text-red-500 bg-red-100 dark:bg-red-900/20',
      stressed: 'text-orange-500 bg-orange-100 dark:bg-orange-900/20',
      neutral: 'text-gray-500 bg-gray-100 dark:bg-gray-900/20'
    };
    return colors[mood] || colors.neutral;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400';
    if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'declining':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'stable':
        return <Minus className="w-4 h-4 text-gray-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  if (!moodAnalysis) return null;

  const { mood, confidence, emotions, keywords } = moodAnalysis;
  const MoodIcon = getMoodIcon(mood);
  const moodColorClass = getMoodColor(mood);

  return (
    <div className="space-y-6">
      {/* Main Mood Analysis */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Mood Analysis
          </h2>
          <div className={`px-3 py-1 rounded-full text-sm font-semibold ${moodColorClass}`}>
            {mood.charAt(0).toUpperCase() + mood.slice(1)}
          </div>
        </div>

        <div className="flex items-center space-x-4 mb-6">
          <div className={`p-4 rounded-full ${moodColorClass}`}>
            <MoodIcon className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                Confidence: {Math.round(confidence * 100)}%
              </span>
              <div className={`w-2 h-2 rounded-full ${getConfidenceColor(confidence).replace('text-', 'bg-')}`}></div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  confidence >= 0.8 ? 'bg-green-500' : confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${confidence * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Emotion Breakdown */}
        {emotions && Object.keys(emotions).length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Emotion Breakdown
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(emotions).map(([emotion, score]) => (
                <div key={emotion} className="text-center">
                  <div className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                  </div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {Math.round(score * 100)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Keywords */}
        {keywords && keywords.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Key Phrases
            </h3>
            <div className="flex flex-wrap gap-2">
              {keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Context Analysis */}
      {contextAnalysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
        >
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="w-6 h-6 text-primary-500" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Context Analysis
            </h2>
          </div>

          {contextAnalysis.mood_trend && (
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="font-semibold text-gray-900 dark:text-white">Mood Trend:</span>
                {getTrendIcon(contextAnalysis.mood_trend.trend_type)}
                <span className="text-gray-600 dark:text-gray-300">
                  {contextAnalysis.mood_trend.trend_type}
                </span>
              </div>
              {contextAnalysis.mood_trend.change_percentage && (
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  {contextAnalysis.mood_trend.change_percentage > 0 ? '+' : ''}
                  {contextAnalysis.mood_trend.change_percentage}% over the last {contextAnalysis.mood_trend.period_days} days
                </div>
              )}
            </div>
          )}

          {contextAnalysis.mood_patterns && contextAnalysis.mood_patterns.length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Patterns Detected:</h3>
              <div className="space-y-2">
                {contextAnalysis.mood_patterns.map((pattern, index) => (
                  <div key={index} className="text-sm text-gray-600 dark:text-gray-300">
                    • {pattern.description}
                    {pattern.intensity && (
                      <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        {Math.round(pattern.intensity * 100)}% intensity
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {contextAnalysis.mood_volatility && (
            <div className="text-sm text-gray-600 dark:text-gray-300">
              <span className="font-semibold">Mood Volatility:</span> {Math.round(contextAnalysis.mood_volatility * 100)}%
            </div>
          )}
        </motion.div>
      )}

      {/* Theme Analysis */}
      {themeAnalysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
        >
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-6 h-6 text-secondary-500" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Theme Analysis
            </h2>
          </div>

          {themeAnalysis.detected_themes && Object.keys(themeAnalysis.detected_themes).length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Detected Themes:</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(themeAnalysis.detected_themes).map(([theme, score]) => (
                  <span
                    key={theme}
                    className="px-3 py-1 bg-secondary-100 dark:bg-secondary-900/20 text-secondary-700 dark:text-secondary-300 rounded-full text-sm"
                  >
                    {theme} ({Math.round(score * 100)}%)
                  </span>
                ))}
              </div>
            </div>
          )}

          {themeAnalysis.emotional_triggers && Object.keys(themeAnalysis.emotional_triggers).length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Emotional Triggers:</h3>
              <div className="space-y-2">
                {Object.entries(themeAnalysis.emotional_triggers).map(([trigger, keywords]) => (
                  <div key={trigger} className="text-sm">
                    <span className="font-medium text-gray-900 dark:text-white">{trigger}:</span>
                    <span className="ml-2 text-gray-600 dark:text-gray-300">
                      {keywords.join(', ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {themeAnalysis.key_phrases && themeAnalysis.key_phrases.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Key Phrases:</h3>
              <div className="flex flex-wrap gap-2">
                {themeAnalysis.key_phrases.map((phrase, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                  >
                    {phrase}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default MoodDisplay;
