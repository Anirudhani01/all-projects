import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const SettingsPage = () => {
  const navigate = useNavigate()
  const [settings, setSettings] = useState({
    theme: 'light',
    notifications: true,
    voiceInput: true,
    animations: true,
    fontSize: 'medium'
  })

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSaveSettings = () => {
    // In real app, save to localStorage or send to backend
    localStorage.setItem('moodbooster-settings', JSON.stringify(settings))
    alert('Settings saved!')
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
            Settings
          </h1>
          <p className="text-lg text-gray-600">
            Customize your MoodBooster experience
          </p>
        </div>

        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="bg-white rounded-lg shadow-lg p-8 space-y-8"
        >
          {/* Theme Settings */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Appearance</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
                <select
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-200"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Size
                </label>
                <select
                  value={settings.fontSize}
                  onChange={(e) => handleSettingChange('fontSize', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-200"
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>
          </div>

          {/* Feature Settings */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Features</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Enable Notifications
                  </label>
                  <p className="text-xs text-gray-500">
                    Get reminders to write in your diary
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                  className="h-4 w-4 text-primary-300 focus:ring-primary-200 border-gray-300 rounded"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Voice Input
                  </label>
                  <p className="text-xs text-gray-500">
                    Speak your diary entries instead of typing
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.voiceInput}
                  onChange={(e) => handleSettingChange('voiceInput', e.target.checked)}
                  className="h-4 w-4 text-primary-300 focus:ring-primary-200 border-gray-300 rounded"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Animations
                  </label>
                  <p className="text-xs text-gray-500">
                    Enable smooth animations and transitions
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.animations}
                  onChange={(e) => handleSettingChange('animations', e.target.checked)}
                  className="h-4 w-4 text-primary-300 focus:ring-primary-200 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Data Settings */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Data & Privacy</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Export Data
                  </label>
                  <p className="text-xs text-gray-500">
                    Download your diary entries and mood data
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-full transition-all duration-300"
                >
                  Export
                </motion.button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Clear Data
                  </label>
                  <p className="text-xs text-gray-500">
                    Delete all your diary entries and settings
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-red-200 hover:bg-red-300 text-red-800 font-semibold py-2 px-4 rounded-full transition-all duration-300"
                >
                  Clear All
                </motion.button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-center pt-6">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSaveSettings}
              className="bg-primary-200 hover:bg-primary-300 text-gray-800 font-semibold py-3 px-8 rounded-full transition-all duration-300"
            >
              Save Settings
            </motion.button>
          </div>
        </motion.div>

        <div className="flex justify-center mt-8">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-full transition-all duration-300"
          >
            ← Back to Home
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}

export default SettingsPage
