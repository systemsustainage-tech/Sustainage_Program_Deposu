import os
from celery import Celery
from celery.schedules import crontab

def make_celery(app_name=__name__):
    # Redis URL - Default to localhost, but allow env override
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url
    )
    
    celery.conf.update(
        result_expires=3600,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        # Auto-discover tasks
        imports=(
            'backend.modules.database.tasks',
            'backend.modules.advanced_reporting.tasks',
        ),
        # Periodic tasks
        beat_schedule={
            'daily-full-backup-2am': {
                'task': 'tasks.run_scheduled_backup',
                'schedule': crontab(hour=2, minute=0),
                'kwargs': {'backup_type': 'full', 'upload_to_cloud': True},
            },
            'hourly-db-backup': {
                'task': 'tasks.run_scheduled_backup',
                'schedule': crontab(minute=0),
                'kwargs': {'backup_type': 'database_only', 'upload_to_cloud': True},
            },
        }
    )
    
    return celery

celery = make_celery()
