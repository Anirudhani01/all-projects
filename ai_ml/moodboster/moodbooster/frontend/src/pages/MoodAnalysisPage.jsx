import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const MoodAnalysisPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [mood, setMood] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState('')

  useEffect(() => {
    // Simulate mood analysis
    const analyzeMood = async () => {
      setLoading(true)
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock mood analysis (in real app, this would come from backend)
      const moods = ['happy', 'sad', 'angry', 'stressed', 'neutral']
      const randomMood = moods[Math.floor(Math.random() * moods.length)]
      
      setMood(randomMood)
      setAnalysis(`Based on your entry, I can sense you're feeling ${randomMood}. Let me help you with some personalized content to boost your mood!`)
      setLoading(false)
    }

    if (location.state?.entry) {
      analyzeMood()
    } else {
      navigate('/diary')
    }
  }, [location.state, navigate])

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

  const handleGetBooster = () => {
    navigate('/booster', { state: { mood, entry: location.state.entry } })
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
          <p className="text-lg text-gray-600">Analyzing your mood...</p>
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
            Mood Analysis Complete!
          </h1>
        </div>

        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className={`mood-card ${getMoodColor(mood)} text-center mb-8`}
        >
          <div className="text-8xl mb-4">{getMoodEmoji(mood)}</div>
          <h2 className="text-3xl font-handwritten text-white mb-4 capitalize">
            You're feeling {mood}
          </h2>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            {analysis}
          </p>
        </motion.div>

        <div className="flex justify-center space-x-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/diary')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            Write Another Entry
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleGetBooster}
            className="bg-primary-200 hover:bg-primary-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            Get My Booster ✨
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}

export default MoodAnalysisPage
