import { useState } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import { 
  Settings as SettingsIcon, 
  Moon, 
  Sun, 
  Bell, 
  Shield, 
  Database, 
  Download,
  Upload,
  Trash2,
  Info,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const Settings = () => {
  const { isDark, toggleTheme } = useTheme();
  const [notifications, setNotifications] = useState({
    dailyReminder: true,
    moodInsights: true,
    weeklyReport: false,
    newFeatures: true
  });
  const [privacy, setPrivacy] = useState({
    dataSharing: false,
    analytics: true,
    personalizedContent: true
  });
  const [showExportSuccess, setShowExportSuccess] = useState(false);
  const [showImportSuccess, setShowImportSuccess] = useState(false);

  const handleNotificationChange = (key) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handlePrivacyChange = (key) => {
    setPrivacy(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleExportData = () => {
    // In a real app, this would export user data
    const data = {
      settings: { notifications, privacy },
      theme: isDark ? 'dark' : 'light',
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `moodbooster-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setShowExportSuccess(true);
    setTimeout(() => setShowExportSuccess(false), 3000);
  };

  const handleImportData = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          // In a real app, this would import the data
          console.log('Imported data:', data);
          setShowImportSuccess(true);
          setTimeout(() => setShowImportSuccess(false), 3000);
        } catch (error) {
          console.error('Failed to import data:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleClearData = () => {
    if (window.confirm('Are you sure you want to clear all your data? This action cannot be undone.')) {
      // In a real app, this would clear user data
      console.log('Data cleared');
    }
  };

  const settingsSections = [
    {
      title: 'Appearance',
      icon: isDark ? Moon : Sun,
      items: [
        {
          key: 'theme',
          label: 'Dark Mode',
          description: 'Switch between light and dark themes',
          type: 'toggle',
          value: isDark,
          onChange: toggleTheme
        }
      ]
    },
    {
      title: 'Notifications',
      icon: Bell,
      items: [
        {
          key: 'dailyReminder',
          label: 'Daily Reminder',
          description: 'Get reminded to write in your diary',
          type: 'toggle',
          value: notifications.dailyReminder,
          onChange: () => handleNotificationChange('dailyReminder')
        },
        {
          key: 'moodInsights',
          label: 'Mood Insights',
          description: 'Receive insights about your mood patterns',
          type: 'toggle',
          value: notifications.moodInsights,
          onChange: () => handleNotificationChange('moodInsights')
        },
        {
          key: 'weeklyReport',
          label: 'Weekly Report',
          description: 'Get a weekly summary of your mood journey',
          type: 'toggle',
          value: notifications.weeklyReport,
          onChange: () => handleNotificationChange('weeklyReport')
        },
        {
          key: 'newFeatures',
          label: 'New Features',
          description: 'Be notified about new features and updates',
          type: 'toggle',
          value: notifications.newFeatures,
          onChange: () => handleNotificationChange('newFeatures')
        }
      ]
    },
    {
      title: 'Privacy & Data',
      icon: Shield,
      items: [
        {
          key: 'dataSharing',
          label: 'Data Sharing',
          description: 'Allow anonymous data sharing for research',
          type: 'toggle',
          value: privacy.dataSharing,
          onChange: () => handlePrivacyChange('dataSharing')
        },
        {
          key: 'analytics',
          label: 'Analytics',
          description: 'Help improve the app with usage analytics',
          type: 'toggle',
          value: privacy.analytics,
          onChange: () => handlePrivacyChange('analytics')
        },
        {
          key: 'personalizedContent',
          label: 'Personalized Content',
          description: 'Use your data to provide better recommendations',
          type: 'toggle',
          value: privacy.personalizedContent,
          onChange: () => handlePrivacyChange('personalizedContent')
        }
      ]
    },
    {
      title: 'Data Management',
      icon: Database,
      items: [
        {
          key: 'export',
          label: 'Export Data',
          description: 'Download your data as a JSON file',
          type: 'button',
          action: handleExportData,
          icon: Download
        },
        {
          key: 'import',
          label: 'Import Data',
          description: 'Import data from a JSON file',
          type: 'file',
          action: handleImportData,
          icon: Upload
        },
        {
          key: 'clear',
          label: 'Clear All Data',
          description: 'Permanently delete all your data',
          type: 'button',
          action: handleClearData,
          icon: Trash2,
          destructive: true
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Settings
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Customize your MoodBooster experience
          </p>
        </div>

        {/* Success Messages */}
        {showExportSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4"
          >
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-700 dark:text-green-300">
                Data exported successfully!
              </span>
            </div>
          </motion.div>
        )}

        {showImportSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4"
          >
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-700 dark:text-green-300">
                Data imported successfully!
              </span>
            </div>
          </motion.div>
        )}

        {/* Settings Sections */}
        <div className="space-y-8">
          {settingsSections.map((section, sectionIndex) => {
            const Icon = section.icon;
            return (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: sectionIndex * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
              >
                <div className="flex items-center mb-6">
                  <div className="p-3 bg-primary-100 dark:bg-primary-900/20 rounded-lg mr-4">
                    <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    {section.title}
                  </h2>
                </div>

                <div className="space-y-4">
                  {section.items.map((item, itemIndex) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                    >
                      <div className="flex-1">
                        <div className="flex items-center">
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                            {item.label}
                          </h3>
                          {item.destructive && (
                            <AlertCircle className="w-4 h-4 text-red-500 ml-2" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {item.description}
                        </p>
                      </div>

                      <div className="ml-4">
                        {item.type === 'toggle' && (
                          <button
                            onClick={item.onChange}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                              item.value
                                ? 'bg-primary-500'
                                : 'bg-gray-300 dark:bg-gray-600'
                            }`}
                          >
                            <span
                              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                item.value ? 'translate-x-6' : 'translate-x-1'
                              }`}
                            />
                          </button>
                        )}

                        {item.type === 'button' && (
                          <button
                            onClick={item.action}
                            className={`inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                              item.destructive
                                ? 'bg-red-500 hover:bg-red-600 text-white'
                                : 'bg-primary-500 hover:bg-primary-600 text-white'
                            }`}
                          >
                            {item.icon && <item.icon className="w-4 h-4 mr-2" />}
                            {item.label}
                          </button>
                        )}

                        {item.type === 'file' && (
                          <label className="inline-flex items-center px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium cursor-pointer transition-colors">
                            {item.icon && <item.icon className="w-4 h-4 mr-2" />}
                            {item.label}
                            <input
                              type="file"
                              accept=".json"
                              onChange={item.action}
                              className="hidden"
                            />
                          </label>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* App Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center mb-4">
            <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg mr-4">
              <Info className="w-6 h-6 text-gray-600 dark:text-gray-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              About MoodBooster
            </h2>
          </div>
          
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <p>Version: 1.0.0</p>
            <p>Build: 2024.09.16</p>
            <p>Made with ❤️ for your mental wellness</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Settings;
