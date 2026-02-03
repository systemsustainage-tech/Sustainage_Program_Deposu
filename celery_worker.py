import os
import sys

# Add current directory and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.celery_app import celery
# Import tasks to ensure they are registered
import backend.modules.advanced_reporting.tasks

if __name__ == '__main__':
    # On Windows, we might need pool='solo' for development
    argv = [
        'worker',
        '--loglevel=INFO',
    ]
    if os.name == 'nt':
        argv.extend(['--pool=solo'])
        
    celery.worker_main(argv)
