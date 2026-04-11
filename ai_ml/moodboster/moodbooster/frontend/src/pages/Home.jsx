import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Heart, Sparkles, ArrowRight } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: BookOpen,
      title: 'Smart Diary',
      description: 'Write your thoughts and get instant mood analysis with AI-powered insights.',
      color: 'text-primary-500'
    },
    {
      icon: Heart,
      title: 'Mood Support',
      description: 'Receive personalized content to lift your spirits when you need it most.',
      color: 'text-pink-500'
    },
    {
      icon: Sparkles,
      title: 'Personalized',
      description: 'Get music, quotes, videos, and activities tailored to your emotional state.',
      color: 'text-secondary-500'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <motion.div
            className="text-center"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.h1
              className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6"
              variants={itemVariants}
            >
              Write your thoughts,{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-secondary-500">
                lift your spirits
              </span>
            </motion.h1>
            
            <motion.p
              className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto"
              variants={itemVariants}
            >
              Your personal mood companion that understands your emotions and provides 
              personalized support through music, quotes, videos, and activities.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center"
              variants={itemVariants}
            >
              <Link
                to="/diary"
                className="inline-flex items-center px-8 py-4 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                Start Writing
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              
              <Link
                to="/profile"
                className="inline-flex items-center px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 transition-colors duration-200"
              >
                View Profile
              </Link>
            </motion.div>
          </motion.div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-20 h-20 bg-primary-200 dark:bg-primary-800 rounded-full opacity-20 animate-pulse-soft"></div>
          <div className="absolute top-40 right-20 w-16 h-16 bg-secondary-200 dark:bg-secondary-800 rounded-full opacity-20 animate-bounce-gentle"></div>
          <div className="absolute bottom-20 left-1/4 w-12 h-12 bg-primary-300 dark:bg-primary-700 rounded-full opacity-30 animate-pulse-soft"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How it works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Our AI-powered system analyzes your emotions and provides personalized support
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  className="text-center p-8 rounded-2xl bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-white dark:bg-gray-700 mb-6 ${feature.color}`}>
                    <Icon className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-500 to-secondary-500">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to start your journey?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Join thousands of users who have found emotional support through our platform
            </p>
            <Link
              to="/diary"
              className="inline-flex items-center px-8 py-4 bg-white text-primary-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              Get Started Now
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;
