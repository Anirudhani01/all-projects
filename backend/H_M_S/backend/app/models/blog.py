"""
Blog model for hospital achievements and news
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class BlogPost(Base):
    """Blog post model for hospital achievements and news"""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), index=True)
    featured_image = Column(String(255))
    is_published = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title}', category='{self.category}', published={self.is_published})>"
