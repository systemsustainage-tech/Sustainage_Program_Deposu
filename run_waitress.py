
from waitress import serve
from remote_web_app import app
import logging

# Configure logging to see what happens
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    print("Starting Waitress server on 0.0.0.0:8000 with 20 threads...")
    try:
        serve(app, host='0.0.0.0', port=8000, threads=20)
    except Exception as e:
        print(f"Waitress crashed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Waitress server stopped.")
