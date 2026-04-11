"""
Main FastAPI application for Hospital Management System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .config import settings
from .database import create_tables

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive Hospital Management System with patient and admin interfaces",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    create_tables()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} is starting up...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Hospital Management System is shutting down...")


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main landing page"""
    try:
        with open("frontend/patient/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Hospital Management System</title></head>
                <body>
                    <h1>🏥 Hospital Management System</h1>
                    <p>Welcome to the Hospital Management System!</p>
                    <p>API Documentation: <a href="/docs">/docs</a></p>
                    <p>ReDoc: <a href="/redoc">/redoc</a></p>
                </body>
            </html>
            """,
            status_code=200
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


# Include API routers
from .api import doctors, appointments, blog, contact, patients, auth

# Public API endpoints
app.include_router(doctors.router, prefix="/api/doctors", tags=["doctors"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Admin API endpoints
app.include_router(doctors.router, prefix="/api/admin/doctors", tags=["admin-doctors"])
app.include_router(appointments.router, prefix="/api/admin/appointments", tags=["admin-appointments"])
app.include_router(blog.router, prefix="/api/admin/blog", tags=["admin-blog"])
app.include_router(contact.router, prefix="/api/admin/contact", tags=["admin-contact"])
app.include_router(patients.router, prefix="/api/admin/patients", tags=["admin-patients"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
