import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const BoosterPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { mood, entry } = location.state || {}

  const getBoosterContent = (mood) => {
    const boosters = {
      happy: {
        title: "Keep the Joy Going! 🎉",
        content: "You're radiating positivity! Here's something to amplify that happiness:",
        type: "game",
        action: "Play a fun memory game to keep your spirits high!"
      },
      sad: {
        title: "Gentle Comfort 💙",
        content: "I understand you're going through a tough time. Here's something gentle to help:",
        type: "story",
        action: "Read a comforting story about hope and healing."
      },
      angry: {
        title: "Release & Relax 🔥",
        content: "It's okay to feel angry. Let's channel that energy positively:",
        type: "meditation",
        action: "Try this breathing exercise to help you feel calmer."
      },
      stressed: {
        title: "Find Your Calm 🌸",
        content: "Stress can be overwhelming. Let's help you find some peace:",
        type: "meditation",
        action: "Practice this mindfulness exercise."
      },
      neutral: {
        title: "Mindful Moment 🌱",
        content: "Sometimes a neutral mood is perfect for reflection:",
        type: "activity",
        action: "Try this gratitude exercise to brighten your perspective."
      }
    }
    return boosters[mood] || boosters.neutral
  }

  const booster = getBoosterContent(mood)

  const handleTryAnother = () => {
    navigate('/diary')
  }

  const handleViewHistory = () => {
    navigate('/history')
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
            Your Personal Booster
          </h1>
        </div>

        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="bg-white rounded-lg shadow-lg p-8 mb-8"
        >
          <h2 className="text-3xl font-handwritten text-primary-300 mb-4">
            {booster.title}
          </h2>
          
          <p className="text-lg text-gray-700 mb-6">
            {booster.content}
          </p>

          <div className="bg-primary-50 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              {booster.action}
            </h3>
            
            {booster.type === 'game' && (
              <div className="text-center">
                <div className="text-6xl mb-4">🎮</div>
                <p className="text-gray-600">Click the stars to collect them!</p>
                <div className="flex justify-center space-x-2 mt-4">
                  {[...Array(5)].map((_, i) => (
                    <motion.button
                      key={i}
                      whileHover={{ scale: 1.2, rotate: 360 }}
                      whileTap={{ scale: 0.8 }}
                      className="text-4xl"
                    >
                      ⭐
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
            
            {booster.type === 'story' && (
              <div className="text-center">
                <div className="text-6xl mb-4">📖</div>
                <p className="text-gray-600 italic">
                  "Even in the darkest moments, there's always a glimmer of hope. 
                  Like a small candle in the night, it may seem fragile, but it has 
                  the power to light up the entire room. You are stronger than you know."
                </p>
              </div>
            )}
            
            {booster.type === 'meditation' && (
              <div className="text-center">
                <div className="text-6xl mb-4">🧘‍♀️</div>
                <p className="text-gray-600 mb-4">Breathe in for 4 counts, hold for 4, breathe out for 6.</p>
                <div className="w-16 h-16 bg-primary-200 rounded-full mx-auto animate-pulse"></div>
              </div>
            )}
            
            {booster.type === 'activity' && (
              <div className="text-center">
                <div className="text-6xl mb-4">✨</div>
                <p className="text-gray-600 mb-4">Write down three things you're grateful for today:</p>
                <div className="space-y-2">
                  <input type="text" placeholder="1. " className="w-full p-2 border rounded" />
                  <input type="text" placeholder="2. " className="w-full p-2 border rounded" />
                  <input type="text" placeholder="3. " className="w-full p-2 border rounded" />
                </div>
              </div>
            )}
          </div>
        </motion.div>

        <div className="flex justify-center space-x-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleTryAnother}
            className="bg-primary-200 hover:bg-primary-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            Write Another Entry
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleViewHistory}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            View My History
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}

export default BoosterPage
