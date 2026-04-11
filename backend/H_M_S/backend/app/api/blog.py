"""
Blog API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import BlogPost
from ..schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostResponse, BlogPostList

router = APIRouter()


@router.get("/", response_model=BlogPostList)
async def get_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None),
    published_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get blog posts with optional filtering"""
    
    query = db.query(BlogPost)
    
    # Apply filters
    if published_only:
        query = query.filter(BlogPost.is_published == True)
    
    if category:
        query = query.filter(BlogPost.category.ilike(f"%{category}%"))
    
    if search:
        query = query.filter(
            BlogPost.title.ilike(f"%{search}%") | 
            BlogPost.content.ilike(f"%{search}%")
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    posts = query.order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()
    
    return BlogPostList(
        posts=posts,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific blog post by ID"""
    
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return post


@router.post("/", response_model=BlogPostResponse)
async def create_blog_post(post: BlogPostCreate, db: Session = Depends(get_db)):
    """Create a new blog post (Admin only)"""
    
    # Check if post with same title already exists
    existing_post = db.query(BlogPost).filter(BlogPost.title == post.title).first()
    if existing_post:
        raise HTTPException(status_code=400, detail="Blog post with this title already exists")
    
    # Create new blog post
    db_post = BlogPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post


@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: int,
    post: BlogPostUpdate,
    db: Session = Depends(get_db)
):
    """Update a blog post (Admin only)"""
    
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Update only provided fields
    update_data = post.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    
    return db_post


@router.delete("/{post_id}")
async def delete_blog_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a blog post (Admin only)"""
    
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    db.delete(db_post)
    db.commit()
    
    return {"message": "Blog post deleted successfully"}


@router.get("/categories/list", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """Get list of all blog post categories"""
    
    categories = db.query(BlogPost.category).filter(
        BlogPost.is_published == True,
        BlogPost.category.isnot(None)
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]


@router.get("/featured/latest", response_model=List[BlogPostResponse])
async def get_featured_posts(
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get latest featured blog posts"""
    
    posts = db.query(BlogPost).filter(
        BlogPost.is_published == True
    ).order_by(BlogPost.created_at.desc()).limit(limit).all()
    
    return posts
