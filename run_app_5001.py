
from web_app import app
import os

if __name__ == '__main__':
    print("Starting web app on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
