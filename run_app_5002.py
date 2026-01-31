from web_app import app
import os
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print("Starting web app on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)
