from web_app import app
import os
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print("Starting web app on port 5003...")
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False)
