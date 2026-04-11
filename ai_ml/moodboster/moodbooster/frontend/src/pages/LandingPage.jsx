import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const LandingPage = () => {
  const navigate = useNavigate()
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  const handleStartDiary = () => {
    navigate('/diary')
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-dark">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 w-20 h-20 bg-accent-500/20 rounded-full blur-xl"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ 
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute top-40 right-20 w-32 h-32 bg-neon-purple/20 rounded-full blur-2xl"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.5, 0.2]
          }}
          transition={{ 
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
        <motion.div
          className="absolute bottom-20 left-1/4 w-24 h-24 bg-neon-cyan/20 rounded-full blur-xl"
          animate={{ 
            scale: [1, 1.4, 1],
            opacity: [0.3, 0.7, 0.3]
          }}
          transition={{ 
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center diary-paper">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="text-center max-w-4xl mx-auto px-6"
        >
          {/* Main Title with Glow Effect */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            <h1 className="text-6xl md:text-8xl lg:text-9xl font-handwritten text-dark-50 mb-4 glow-text">
              MoodBooster
            </h1>
            <motion.div
              className="w-32 h-1 bg-gradient-to-r from-accent-500 to-neon-purple mx-auto rounded-full"
              initial={{ width: 0 }}
              animate={{ width: "8rem" }}
              transition={{ delay: 0.8, duration: 1, ease: "easeOut" }}
            />
          </motion.div>
          
          {/* Subtitle with Typewriter Effect */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mb-12"
          >
            <p className="text-xl md:text-2xl lg:text-3xl text-dark-200 mb-4 leading-relaxed font-light">
              Your personal diary companion that understands your emotions
            </p>
            <p className="text-lg md:text-xl text-dark-300 leading-relaxed">
              and provides personalized wellness boosters to brighten your day
            </p>
          </motion.div>
          
          {/* CTA Button with Enhanced Effects */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="mb-16"
          >
            <motion.button
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0 0 40px rgba(14, 165, 233, 0.6)"
              }}
              whileTap={{ scale: 0.95 }}
              onClick={handleStartDiary}
              className="btn-primary btn-neon text-xl px-12 py-4 relative group overflow-hidden"
            >
              <span className="relative z-10 flex items-center space-x-3">
                <span>Start My Diary</span>
                <motion.span
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  ✨
                </motion.span>
              </span>
              
              {/* Shimmer Effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                initial={{ x: "-100%" }}
                animate={{ x: "100%" }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              />
            </motion.button>
          </motion.div>
          
          {/* Feature Pills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.8 }}
            className="flex flex-wrap justify-center gap-4 mb-12"
          >
            {[
              { icon: "📝", text: "Smart Diary" },
              { icon: "🧠", text: "AI Analysis" },
              { icon: "💫", text: "Personal Boosters" },
              { icon: "📊", text: "Mood Tracking" }
            ].map((feature, index) => (
              <motion.div
                key={feature.text}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.4 + index * 0.1, duration: 0.5 }}
                whileHover={{ scale: 1.05, y: -2 }}
                className="glass-card px-4 py-2 rounded-full text-dark-200 text-sm font-medium"
              >
                <span className="mr-2">{feature.icon}</span>
                {feature.text}
              </motion.div>
            ))}
          </motion.div>
          
          {/* Floating Elements */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.8, duration: 1 }}
            className="flex justify-center space-x-8 text-dark-400"
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="text-sm"
            >
              Share your thoughts
            </motion.div>
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
              className="text-sm"
            >
              Get mood insights
            </motion.div>
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
              className="text-sm"
            >
              Receive boosters
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default LandingPage
