#!/usr/bin/env python3
"""Simple HTTP server to serve the frontend"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 3000
FRONTEND_DIR = "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def serve_frontend():
    """Start the frontend server"""
    print("🌐 Starting Frontend Server...")
    print(f"📁 Serving from: {os.path.abspath(FRONTEND_DIR)}")
    print(f"🔗 Server URL: http://localhost:{PORT}")
    print("\n📋 Available Pages:")
    print("   👥 Patient Frontend:")
    print(f"      • Landing Page: http://localhost:{PORT}/patient/index.html")
    print(f"      • Doctors: http://localhost:{PORT}/patient/doctors.html")
    print(f"      • Book Appointment: http://localhost:{PORT}/patient/book.html")
    print(f"      • Blog: http://localhost:{PORT}/patient/blog.html")
    print(f"      • Contact: http://localhost:{PORT}/patient/contact.html")
    print("\n   🔧 Admin Frontend:")
    print(f"      • Admin Login: http://localhost:{PORT}/admin/login.html")
    print(f"      • Admin Dashboard: http://localhost:{PORT}/admin/dashboard.html")
    print(f"      • Doctor Management: http://localhost:{PORT}/admin/pages/doctors.html")
    print("\n🚀 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Please try a different port.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    serve_frontend()
