"""
Entry point for Vercel deployment
Imports the Flask app from api/main.py
"""

from api.main import app

# Vercel requires the app to be named 'app' or exported
if __name__ == "__main__":
    app.run()
