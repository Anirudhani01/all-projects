import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useMood } from '../contexts/MoodContext';
import { analyticsAPI } from '../services/api';
import { 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Trash2, 
  Eye,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import { Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Profile = () => {
  const { moodHistory, clearMoodHistory } = useMood();
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [viewMode, setViewMode] = useState('chart'); // 'chart' or 'list'

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      // For now, we'll use the mood history from context
      // In a real app, you'd fetch from the backend
      const mockUserId = 'user-123';
      const response = await analyticsAPI.getMoodAnalytics(mockUserId, selectedPeriod);
      
      if (response.success) {
        setAnalytics(response.data);
      } else {
        // Fallback to local data
        setAnalytics(generateLocalAnalytics());
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setAnalytics(generateLocalAnalytics());
    } finally {
      setIsLoading(false);
    }
  };

  const generateLocalAnalytics = () => {
    if (moodHistory.length === 0) {
      return {
        moodDistribution: {},
        moodTrends: [],
        totalEntries: 0,
        averageConfidence: 0
      };
    }

    // Calculate mood distribution
    const moodCounts = moodHistory.reduce((acc, entry) => {
      acc[entry.mood] = (acc[entry.mood] || 0) + 1;
      return acc;
    }, {});

    const totalEntries = moodHistory.length;
    const moodDistribution = Object.entries(moodCounts).reduce((acc, [mood, count]) => {
      acc[mood] = (count / totalEntries) * 100;
      return acc;
    }, {});

    // Calculate average confidence
    const averageConfidence = moodHistory.reduce((sum, entry) => sum + entry.confidence, 0) / totalEntries;

    // Generate trend data (last 7 days)
    const trendData = generateTrendData();

    return {
      moodDistribution,
      moodTrends: trendData,
      totalEntries,
      averageConfidence
    };
  };

  const generateTrendData = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - i);
      return date.toISOString().split('T')[0];
    }).reverse();

    return last7Days.map(date => {
      const dayEntries = moodHistory.filter(entry => 
        entry.timestamp.startsWith(date)
      );
      
      if (dayEntries.length === 0) {
        return { date, mood: 'neutral', confidence: 0.5 };
      }

      // Get the most recent entry for the day
      const latestEntry = dayEntries[dayEntries.length - 1];
      return {
        date,
        mood: latestEntry.mood,
        confidence: latestEntry.confidence
      };
    });
  };

  const getMoodColor = (mood) => {
    const colors = {
      happy: '#4CAF50',
      sad: '#2196F3',
      angry: '#F44336',
      stressed: '#FF9800',
      neutral: '#9E9E9E'
    };
    return colors[mood] || colors.neutral;
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

  const pieChartData = {
    labels: Object.keys(analytics?.moodDistribution || {}),
    datasets: [
      {
        data: Object.values(analytics?.moodDistribution || {}),
        backgroundColor: Object.keys(analytics?.moodDistribution || {}).map(getMoodColor),
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  const barChartData = {
    labels: analytics?.moodTrends?.map(entry => 
      new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short' })
    ) || [],
    datasets: [
      {
        label: 'Confidence',
        data: analytics?.moodTrends?.map(entry => entry.confidence * 100) || [],
        backgroundColor: analytics?.moodTrends?.map(entry => 
          getMoodColor(entry.mood) + '80'
        ) || [],
        borderColor: analytics?.moodTrends?.map(entry => getMoodColor(entry.mood)) || [],
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20
        }
      }
    }
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Your Mood Profile
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Track your emotional journey and discover patterns
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                <Activity className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Entries</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics?.totalEntries || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center">
              <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <BarChart3 className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Confidence</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round((analytics?.averageConfidence || 0) * 100)}%
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">This Week</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {moodHistory.filter(entry => {
                    const entryDate = new Date(entry.timestamp);
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return entryDate >= weekAgo;
                  }).length}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <PieChart className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Most Common</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {Object.keys(analytics?.moodDistribution || {}).length > 0 
                    ? Object.entries(analytics.moodDistribution).reduce((a, b) => 
                        analytics.moodDistribution[a[0]] > analytics.moodDistribution[b[0]] ? a : b
                      )[0]
                    : 'N/A'
                  }
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Mood Distribution Pie Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
              Mood Distribution
            </h3>
            {Object.keys(analytics?.moodDistribution || {}).length > 0 ? (
              <div className="h-64">
                <Pie data={pieChartData} options={chartOptions} />
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <PieChart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No mood data available</p>
                </div>
              </div>
            )}
          </motion.div>

          {/* Mood Trends Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
              Weekly Trends
            </h3>
            {analytics?.moodTrends?.length > 0 ? (
              <div className="h-64">
                <Bar data={barChartData} options={barChartOptions} />
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No trend data available</p>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Recent Entries */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Recent Entries
            </h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode(viewMode === 'chart' ? 'list' : 'chart')}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                title="Toggle view"
              >
                {viewMode === 'chart' ? <Eye className="w-4 h-4" /> : <BarChart3 className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {moodHistory.length > 0 ? (
            <div className="space-y-4">
              {moodHistory.slice(0, 10).map((entry, index) => (
                <div
                  key={entry.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${getMoodColor(entry.mood)}`}></div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1)}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {new Date(entry.timestamp).toLocaleDateString()} at{' '}
                        {new Date(entry.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {Math.round(entry.confidence * 100)}% confidence
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {entry.keywords?.slice(0, 3).join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No entries yet</p>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                Start writing in your diary to see your mood history here
              </p>
            </div>
          )}
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 flex justify-center"
        >
          <button
            onClick={clearMoodHistory}
            className="flex items-center space-x-2 px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear History</span>
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default Profile;
