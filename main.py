#!/usr/bin/env python3
"""
Alpha Nex - AI Training Data Platform
Main application entry point for development server
"""
from app import app

if __name__ == '__main__':
    # Development server configuration
    app.run(host='0.0.0.0', port=5000, debug=True)
