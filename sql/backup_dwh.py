#!/usr/bin/env python3
# ============================================================
# FILE: sql/backup_dwh.py
# Mô tả: Python backup script cho SQL Server DWH Multi-Tenant
# Chạy theo schedule (full/diff/log) - có thể dùng cron hoặc APScheduler
# ============================================================

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ---- Configuration ----
MSSQL_SERVER = os.environ.get('MSSQL_SERVER', 'localhost')
MSSQL_USER = os.environ.get('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', '')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')

BACKUP_DIR = Path(os.environ.get('BACKUP_DIR', '/backups/dwh'))
ARCHIVE_DIR = BACKUP_DIR / 'archive'
LOG_FILE = BACKUP_DIR / 'backup.log'

RETENTION_DAYS = {
    'full': 28,
    'differential': 7,
    'log': 2
}

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ---- Backup Functions ----

def backup_full() -> bool:
    """Execute FULL backup of DWH database."""
    logger.info('=' * 60)
    logger.info('FULL BACKUP START')
    logger.info('=' * 60)

    backup_file = BACKUP_DIR / f'dwh_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak'

    cmd = (
        f"sqlcmd -S {MSSQL_SERVER} -U {MSSQL_USER} -P {MSSQL_PASSWORD} "
        f"-Q \"BACKUP DATABASE [{MSSQL_DATABASE}] TO DISK='{backup_file}' "
        f"WITH INIT, COMPRESSION;\""
    )

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)

        if result.returncode == 0:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(f'✓ FULL backup completed: {backup_file.name} ({size_mb:.2f} MB)')
            return True
        else:
            logger.error(f'✗ FULL backup FAILED: {result.stderr}')
            return False
    except Exception as e:
        logger.error(f'✗ FULL backup error: {e}')
        return False


def backup_differential() -> bool:
    """Execute DIFFERENTIAL backup of DWH database."""
    logger.info('=' * 60)
    logger.info('DIFFERENTIAL BACKUP START')
    logger.info('=' * 60)

    backup_file = BACKUP_DIR / f'dwh_diff_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak'

    cmd = (
        f"sqlcmd -S {MSSQL_SERVER} -U {MSSQL_USER} -P {MSSQL_PASSWORD} "
        f"-Q \"BACKUP DATABASE [{MSSQL_DATABASE}] TO DISK='{backup_file}' "
        f"WITH DIFFERENTIAL, INIT, COMPRESSION;\""
    )

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1800)

        if result.returncode == 0:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(f'✓ DIFFERENTIAL backup completed: {backup_file.name} ({size_mb:.2f} MB)')
            return True
        else:
            logger.error(f'✗ DIFFERENTIAL backup FAILED: {result.stderr}')
            return False
    except Exception as e:
        logger.error(f'✗ DIFFERENTIAL backup error: {e}')
        return False


def backup_transaction_log() -> bool:
    """Execute TRANSACTION LOG backup of DWH database."""
    logger.info('=' * 60)
    logger.info('TRANSACTION LOG BACKUP START')
    logger.info('=' * 60)

    backup_file = BACKUP_DIR / f'dwh_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.trn'

    cmd = (
        f"sqlcmd -S {MSSQL_SERVER} -U {MSSQL_USER} -P {MSSQL_PASSWORD} "
        f"-Q \"BACKUP LOG [{MSSQL_DATABASE}] TO DISK='{backup_file}' "
        f"WITH INIT, COMPRESSION;\""
    )

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)

        if result.returncode == 0:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(f'✓ TRANSACTION LOG backup completed: {backup_file.name} ({size_mb:.2f} MB)')
            return True
        else:
            logger.warning(f'⚠ TRANSACTION LOG backup FAILED: {result.stderr}')
            logger.warning('  Note: DB may not be in FULL recovery mode')
            return False
    except Exception as e:
        logger.error(f'✗ TRANSACTION LOG backup error: {e}')
        return False


def cleanup_old_backups():
    """Remove old backups beyond retention period."""
    logger.info('=' * 60)
    logger.info('CLEANUP OLD BACKUPS START')
    logger.info('=' * 60)

    backup_types = {
        'dwh_full_*.bak': RETENTION_DAYS['full'],
        'dwh_diff_*.bak': RETENTION_DAYS['differential'],
        'dwh_log_*.trn': RETENTION_DAYS['log']
    }

    for pattern, days in backup_types.items():
        cutoff_date = datetime.now() - timedelta(days=days)
        files_deleted = 0

        for backup_file in BACKUP_DIR.glob(pattern):
            file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    backup_file.unlink()
                    files_deleted += 1
                except Exception as e:
                    logger.warning(f'Failed to delete {backup_file.name}: {e}')

        logger.info(f'✓ Removed {files_deleted} {pattern} backups older than {days} days')


def archive_backups():
    """Archive old backups to separate directory."""
    logger.info('=' * 60)
    logger.info('ARCHIVE BACKUPS START')
    logger.info('=' * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Archive FULL backups, keep latest 4 in main dir
    full_backups = sorted(BACKUP_DIR.glob('dwh_full_*.bak'), reverse=True)
    for backup_file in full_backups[4:]:  # All except latest 4
        try:
            new_path = ARCHIVE_DIR / backup_file.name
            backup_file.rename(new_path)
            logger.info(f'✓ Archived {backup_file.name}')
        except Exception as e:
            logger.warning(f'Failed to archive {backup_file.name}: {e}')

    logger.info('✓ Archive operation completed')


def verify_connectivity() -> bool:
    """Verify connection to SQL Server."""
    logger.info('Verifying SQL Server connectivity...')

    cmd = (
        f"sqlcmd -S {MSSQL_SERVER} -U {MSSQL_USER} -P {MSSQL_PASSWORD} "
        f"-Q \"SELECT 1;\""
    )

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logger.info('✓ SQL Server is accessible')
            return True
        else:
            logger.error(f'✗ SQL Server connection failed: {result.stderr}')
            return False
    except Exception as e:
        logger.error(f'✗ SQL Server connection error: {e}')
        return False


# ---- Main ----

def main(backup_type: str = 'auto'):
    """
    Execute backup based on type or current day of week (auto mode).

    Args:
        backup_type: 'full', 'differential', 'log', or 'auto' (based on day)
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    logger.info('=' * 60)
    logger.info('DWH Backup Script Started')
    logger.info(f'Database: {MSSQL_DATABASE} @ {MSSQL_SERVER}')
    logger.info(f'Backup Dir: {BACKUP_DIR}')
    logger.info('=' * 60)

    # Verify connectivity
    if not verify_connectivity():
        logger.error('FATAL: Cannot connect to SQL Server')
        return 1

    # Determine backup type
    if backup_type == 'auto':
        day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
        if day_of_week == 6:  # Sunday
            backup_type = 'full'
        elif day_of_week in [0, 3]:  # Monday & Thursday
            backup_type = 'differential'
        else:
            backup_type = 'log'

    logger.info(f'Backup type: {backup_type}')

    # Execute backup
    success = True
    if backup_type == 'full':
        success = backup_full()
    elif backup_type == 'differential':
        success = backup_differential()
    elif backup_type == 'log':
        success = backup_transaction_log()
    else:
        logger.error(f'Unknown backup type: {backup_type}')
        return 1

    # Cleanup and archive
    if success:
        cleanup_old_backups()
        archive_backups()

    logger.info('=' * 60)
    logger.info('DWH Backup Script Completed')
    logger.info('=' * 60)

    return 0 if success else 1


if __name__ == '__main__':
    backup_type = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    sys.exit(main(backup_type))
