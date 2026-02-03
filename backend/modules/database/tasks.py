
import logging
from backend.celery_app import celery
from backend.modules.database.backup_recovery_manager import BackupRecoveryManager

@celery.task(name='tasks.run_scheduled_backup')
def run_scheduled_backup(backup_type='full', upload_to_cloud=True):
    """
    Celery task to run scheduled backups.
    """
    logging.info(f"Starting scheduled backup: type={backup_type}, cloud={upload_to_cloud}")
    try:
        manager = BackupRecoveryManager()
        success, message = manager.create_backup(
            backup_type=backup_type,
            created_by='system_scheduler',
            upload_to_cloud=upload_to_cloud
        )
        
        if success:
            logging.info(f"Scheduled backup completed successfully: {message}")
            return {"status": "success", "message": message}
        else:
            logging.error(f"Scheduled backup failed: {message}")
            return {"status": "failed", "message": message}
            
    except Exception as e:
        error_msg = f"Exception in scheduled backup: {str(e)}"
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}
