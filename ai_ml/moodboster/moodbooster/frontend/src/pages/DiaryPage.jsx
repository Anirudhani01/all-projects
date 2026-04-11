import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const DiaryPage = () => {
  const [entry, setEntry] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (entry.trim()) {
      setIsTyping(true)
      // Simulate processing delay
      setTimeout(() => {
        navigate('/mood-analysis', { state: { entry } })
      }, 1000)
    }
  }

  const handleTextChange = (e) => {
    setEntry(e.target.value)
    setIsTyping(e.target.value.length > 0)
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-dark">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-1/4 left-1/4 w-64 h-64 bg-accent-500/10 rounded-full blur-3xl"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ 
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-neon-purple/10 rounded-full blur-2xl"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.5, 0.2]
          }}
          transition={{ 
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>

      <div className="relative z-10 min-h-screen diary-paper p-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-5xl mx-auto"
        >
          {/* Header Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-center mb-12"
          >
            <motion.h1
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-5xl md:text-6xl lg:text-7xl font-handwritten text-dark-50 mb-6 glow-text"
            >
              How was your day?
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="text-xl md:text-2xl text-dark-300 font-light"
            >
              Share your thoughts and feelings with me
            </motion.p>
            
            {/* Decorative Line */}
            <motion.div
              className="w-24 h-1 bg-gradient-to-r from-accent-500 to-neon-purple mx-auto rounded-full mt-4"
              initial={{ width: 0 }}
              animate={{ width: "6rem" }}
              transition={{ delay: 0.8, duration: 1, ease: "easeOut" }}
            />
          </motion.div>

          {/* Diary Form */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="glass-card rounded-2xl p-8 md:p-12 relative overflow-hidden"
          >
            {/* Shimmer Effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
              initial={{ x: "-100%" }}
              animate={{ x: "100%" }}
              transition={{ duration: 3, repeat: Infinity, repeatDelay: 5 }}
            />
            
            <form onSubmit={handleSubmit} className="relative z-10">
              <div className="mb-8">
                <label className="block text-dark-200 text-lg font-medium mb-4">
                  What's on your mind today?
                </label>
                <div className="relative">
                  <textarea
                    value={entry}
                    onChange={handleTextChange}
                    placeholder="Tell me about your day... What made you happy, sad, excited, or worried? Share whatever is on your mind."
                    className="input-field w-full h-80 resize-none text-lg leading-relaxed"
                    required
                  />
                  
                  {/* Character Counter */}
                  <div className="absolute bottom-3 right-3 text-dark-400 text-sm">
                    {entry.length}/2000
                  </div>
                  
                  {/* Typing Indicator */}
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="absolute top-3 right-3 flex items-center space-x-1 text-accent-400"
                    >
                      <motion.div
                        className="w-2 h-2 bg-accent-400 rounded-full"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      />
                      <motion.div
                        className="w-2 h-2 bg-accent-400 rounded-full"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                      />
                      <motion.div
                        className="w-2 h-2 bg-accent-400 rounded-full"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                      />
                    </motion.div>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
                <motion.button
                  type="button"
                  onClick={() => navigate('/')}
                  whileHover={{ scale: 1.05, x: -5 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-ghost flex items-center space-x-2"
                >
                  <span>←</span>
                  <span>Back to Home</span>
                </motion.button>
                
                <motion.button
                  type="submit"
                  disabled={!entry.trim()}
                  whileHover={{ 
                    scale: 1.05,
                    boxShadow: "0 0 30px rgba(14, 165, 233, 0.4)"
                  }}
                  whileTap={{ scale: 0.95 }}
                  className={`btn-primary flex items-center space-x-3 px-8 py-4 text-lg ${
                    !entry.trim() 
                      ? 'opacity-50 cursor-not-allowed' 
                      : 'hover:shadow-glow'
                  }`}
                >
                  <span>Analyze My Mood</span>
                  <motion.span
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    🧠
                  </motion.span>
                </motion.button>
              </div>
            </form>
          </motion.div>

          {/* Tips Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
            className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {[
              {
                icon: "💭",
                title: "Be Honest",
                description: "Share your true feelings without judgment"
              },
              {
                icon: "📝",
                title: "Be Detailed",
                description: "The more you share, the better the analysis"
              },
              {
                icon: "🌟",
                title: "Be Open",
                description: "Let us help you understand your emotions"
              }
            ].map((tip, index) => (
              <motion.div
                key={tip.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 + index * 0.1, duration: 0.5 }}
                whileHover={{ scale: 1.02, y: -2 }}
                className="glass-card-dark p-6 rounded-xl text-center"
              >
                <div className="text-3xl mb-3">{tip.icon}</div>
                <h3 className="text-dark-200 font-semibold mb-2">{tip.title}</h3>
                <p className="text-dark-400 text-sm">{tip.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default DiaryPage
