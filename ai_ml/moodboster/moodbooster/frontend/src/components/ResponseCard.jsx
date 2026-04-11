import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Quote, 
  Music, 
  Video, 
  Play, 
  ExternalLink, 
  ThumbsUp, 
  ThumbsDown,
  Heart,
  Share2,
  Copy
} from 'lucide-react';

const ResponseCard = ({ type, data, onFeedback }) => {
  const [isLiked, setIsLiked] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  const handleFeedback = (feedbackType) => {
    setIsLiked(feedbackType);
    onFeedback?.(feedbackType);
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: data.title || 'MoodBooster Content',
          text: data.text || data.description || '',
          url: data.url || window.location.href
        });
      } catch (err) {
        console.error('Failed to share:', err);
      }
    } else {
      // Fallback to copying URL
      handleCopy(data.url || window.location.href);
    }
  };

  const renderQuote = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-secondary-50 to-primary-50 dark:from-secondary-900/20 dark:to-primary-900/20 border border-secondary-200 dark:border-secondary-800 rounded-xl p-6"
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-secondary-100 dark:bg-secondary-900/30 rounded-full flex items-center justify-center">
            <Quote className="w-6 h-6 text-secondary-600 dark:text-secondary-400" />
          </div>
        </div>
        <div className="flex-1">
          <blockquote className="text-lg font-medium text-gray-900 dark:text-white mb-4 leading-relaxed">
            "{data.text}"
          </blockquote>
          <div className="flex items-center justify-between">
            <cite className="text-sm text-gray-600 dark:text-gray-400">
              — {data.author || 'Anonymous'}
            </cite>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleCopy(data.text)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                title="Copy quote"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={handleShare}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                title="Share quote"
              >
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderMusic = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border border-primary-200 dark:border-primary-800 rounded-xl p-6"
    >
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            {data.album_image ? (
              <img 
                src={data.album_image} 
                alt={data.album}
                className="w-full h-full rounded-lg object-cover"
              />
            ) : (
              <Music className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            )}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
            {data.name}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
            {data.artist}
          </p>
          {data.album && (
            <p className="text-xs text-gray-500 dark:text-gray-500 truncate">
              {data.album}
            </p>
          )}
          <div className="flex items-center space-x-4 mt-2">
            <span className="text-xs text-gray-500 dark:text-gray-500">
              {data.duration || 'Unknown duration'}
            </span>
            {data.popularity && (
              <span className="text-xs text-gray-500 dark:text-gray-500">
                {data.popularity}% popular
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {data.preview_url && (
            <button
              onClick={() => new Audio(data.preview_url).play()}
              className="p-2 bg-primary-500 hover:bg-primary-600 text-white rounded-full transition-colors"
              title="Play preview"
            >
              <Play className="w-4 h-4" />
            </button>
          )}
          {data.spotify_url && (
            <a
              href={data.spotify_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              title="Open in Spotify"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );

  const renderVideo = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-24 h-16 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center overflow-hidden">
            {data.thumbnail ? (
              <img 
                src={data.thumbnail} 
                alt={data.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <Video className="w-8 h-8 text-red-600 dark:text-red-400" />
            )}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
            {data.title}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {data.channel_title}
          </p>
          {data.description && (
            <p className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
              {data.description}
            </p>
          )}
          <div className="flex items-center space-x-4 mt-2">
            <span className="text-xs text-gray-500 dark:text-gray-500">
              {data.duration || 'Unknown duration'}
            </span>
            {data.view_count && (
              <span className="text-xs text-gray-500 dark:text-gray-500">
                {data.view_count.toLocaleString()} views
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <a
            href={data.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
            title="Watch video"
          >
            <Play className="w-4 h-4" />
          </a>
          <button
            onClick={handleShare}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="Share video"
          >
            <Share2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );

  const renderContent = () => {
    switch (type) {
      case 'quote':
        return renderQuote();
      case 'music':
        return renderMusic();
      case 'video':
        return renderVideo();
      default:
        return null;
    }
  };

  return (
    <div className="relative">
      {renderContent()}
      
      {/* Feedback Buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="flex items-center justify-center space-x-4 mt-4"
      >
        <button
          onClick={() => handleFeedback('positive')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            isLiked === 'positive'
              ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              : 'bg-gray-100 text-gray-600 hover:bg-green-100 hover:text-green-700 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-green-900/20 dark:hover:text-green-400'
          }`}
        >
          <ThumbsUp className="w-4 h-4" />
          <span className="text-sm font-medium">Helpful</span>
        </button>
        
        <button
          onClick={() => handleFeedback('negative')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            isLiked === 'negative'
              ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
              : 'bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-700 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-red-900/20 dark:hover:text-red-400'
          }`}
        >
          <ThumbsDown className="w-4 h-4" />
          <span className="text-sm font-medium">Not helpful</span>
        </button>
      </motion.div>

      {/* Feedback Confirmation */}
      {isLiked && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full p-1"
        >
          <Heart className="w-4 h-4" />
        </motion.div>
      )}

      {/* Copy Confirmation */}
      {isCopied && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded"
        >
          Copied!
        </motion.div>
      )}
    </div>
  );
};

export default ResponseCard;
