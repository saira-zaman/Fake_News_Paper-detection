"""
Vercel API wrapper for Flask app
This ensures compatibility with Vercel's serverless environment
"""
from app import app

# Export app for Vercel
__all__ = ['app']
