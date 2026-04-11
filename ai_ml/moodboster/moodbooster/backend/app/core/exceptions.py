# Custom exceptions for the application

class MoodBoosterException(Exception):
    """Base exception for MoodBooster application"""
    pass

class MoodAnalysisError(MoodBoosterException):
    """Exception raised when mood analysis fails"""
    pass

class BoosterNotFoundError(MoodBoosterException):
    """Exception raised when booster is not found"""
    pass

class DatabaseError(MoodBoosterException):
    """Exception raised when database operations fail"""
    pass
