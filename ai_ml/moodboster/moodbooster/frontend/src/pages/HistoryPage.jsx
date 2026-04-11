import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const HistoryPage = () => {
  const navigate = useNavigate()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock data for now - in real app, fetch from API
    const mockEntries = [
      {
        id: 1,
        text: "Had a great day at work! Got promoted and celebrated with friends.",
        mood: "happy",
        confidence: 0.95,
        created_at: "2024-09-15T10:30:00Z"
      },
      {
        id: 2,
        text: "Feeling a bit overwhelmed with all the tasks I need to complete this week.",
        mood: "stressed",
        confidence: 0.87,
        created_at: "2024-09-14T15:45:00Z"
      },
      {
        id: 3,
        text: "Had an argument with my partner and feeling really upset about it.",
        mood: "sad",
        confidence: 0.92,
        created_at: "2024-09-13T20:15:00Z"
      }
    ]
    
    setTimeout(() => {
      setEntries(mockEntries)
      setLoading(false)
    }, 1000)
  }, [])

  const getMoodEmoji = (mood) => {
    const emojis = {
      happy: '😀',
      sad: '😔',
      angry: '😡',
      stressed: '😟',
      neutral: '😐'
    }
    return emojis[mood] || '😐'
  }

  const getMoodColor = (mood) => {
    const colors = {
      happy: 'mood-happy',
      sad: 'mood-sad',
      angry: 'mood-angry',
      stressed: 'mood-stressed',
      neutral: 'mood-neutral'
    }
    return colors[mood] || 'mood-neutral'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen diary-paper flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-300 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading your mood history...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen diary-paper p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-handwritten text-primary-300 mb-4">
            Your Mood Journey
          </h1>
          <p className="text-lg text-gray-600">
            A timeline of your emotional experiences
          </p>
        </div>

        {entries.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="text-6xl mb-4">📝</div>
            <h2 className="text-2xl font-handwritten text-gray-600 mb-4">
              No entries yet
            </h2>
            <p className="text-gray-500 mb-6">
              Start your mood journey by writing your first diary entry
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/diary')}
              className="bg-primary-200 hover:bg-primary-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
            >
              Write First Entry
            </motion.button>
          </motion.div>
        ) : (
          <div className="space-y-6">
            {entries.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className={`mood-card ${getMoodColor(entry.mood)}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{getMoodEmoji(entry.mood)}</span>
                    <div>
                      <h3 className="text-xl font-handwritten text-white capitalize">
                        {entry.mood} mood
                      </h3>
                      <p className="text-white/80 text-sm">
                        {formatDate(entry.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-white/80 text-sm">
                      {Math.round(entry.confidence * 100)}% confidence
                    </div>
                  </div>
                </div>
                
                <p className="text-white/90 text-lg leading-relaxed">
                  {entry.text}
                </p>
              </motion.div>
            ))}
          </div>
        )}

        <div className="flex justify-center mt-8">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/diary')}
            className="bg-primary-200 hover:bg-primary-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            Write New Entry
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}

export default HistoryPage
