import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, MicOff, Loader2, AlertCircle } from 'lucide-react';

const DiaryInput = ({ onSubmit, isAnalyzing, error }) => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const textareaRef = useRef(null);

  // Initialize speech recognition
  useState(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setText(prev => prev + (prev ? ' ' : '') + transcript);
        setIsRecording(false);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      setRecognition(recognition);
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim().length >= 10) {
      onSubmit(text.trim());
      setText('');
    }
  };

  const handleVoiceInput = () => {
    if (!recognition) {
      alert('Speech recognition is not supported in your browser');
      return;
    }

    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      recognition.start();
      setIsRecording(true);
    }
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const isSubmitDisabled = text.trim().length < 10 || isAnalyzing;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="diary-textarea" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Share your thoughts
          </label>
          <div className="relative">
            <textarea
              id="diary-textarea"
              ref={textareaRef}
              value={text}
              onChange={handleTextChange}
              placeholder="How was your day? What's on your mind? Share your thoughts and feelings..."
              className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              disabled={isAnalyzing}
            />
            <div className="absolute bottom-3 right-3 flex items-center space-x-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {text.length}/2000
              </span>
              <button
                type="button"
                onClick={handleVoiceInput}
                disabled={isAnalyzing || !recognition}
                className={`p-2 rounded-full transition-colors ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-500'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? (
                  <MicOff className="w-4 h-4" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3"
          >
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </motion.div>
        )}

        {/* Character Count Warning */}
        {text.length > 0 && text.length < 10 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-sm text-amber-600 dark:text-amber-400"
          >
            Please write at least 10 characters to get a meaningful analysis.
          </motion.div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSubmitDisabled}
            className={`inline-flex items-center px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
              isSubmitDisabled
                ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                : 'bg-primary-500 hover:bg-primary-600 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
            }`}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing your mood...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Analyze Mood
              </>
            )}
          </button>
        </div>
      </form>

      {/* Tips */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          💡 Tips for better mood analysis:
        </h4>
        <ul className="text-xs text-gray-600 dark:text-gray-300 space-y-1">
          <li>• Be specific about your feelings and experiences</li>
          <li>• Include context about what happened during your day</li>
          <li>• Mention any triggers or situations that affected your mood</li>
          <li>• The more detail you provide, the better our analysis will be</li>
        </ul>
      </div>
    </motion.div>
  );
};

export default DiaryInput;
