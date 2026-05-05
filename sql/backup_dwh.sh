#!/bin/bash
# ============================================================
# FILE: sql/backup_dwh.sh
# Mô tả: Backup script cho SQL Server DWH Multi-Tenant
# Chạy hàng tuần (Full), hàng ngày (Differential), mỗi 4h (Log)
# ============================================================

set -e

# ---- Configuration ----
MSSQL_SERVER=${MSSQL_SERVER:-"localhost"}
MSSQL_USER=${MSSQL_USER:-"sa"}
MSSQL_PASSWORD=${MSSQL_PASSWORD:-""}
MSSQL_DATABASE=${MSSQL_DATABASE:-"DWH_MultiTenant"}

BACKUP_DIR=${BACKUP_DIR:-"/backups/dwh"}
ARCHIVE_DIR=${ARCHIVE_DIR:-"/backups/dwh/archive"}
LOG_FILE="${BACKUP_DIR}/backup.log"

RETENTION_DAYS_FULL=28
RETENTION_DAYS_DIFF=7
RETENTION_DAYS_LOG=2

# ---- Setup ----
mkdir -p "$BACKUP_DIR" "$ARCHIVE_DIR"

log_msg() {
    local msg="$1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $msg" | tee -a "$LOG_FILE"
}

# ---- Backup Functions ----

backup_full() {
    log_msg "=== FULL BACKUP START ==="
    local backup_file="${BACKUP_DIR}/dwh_full_$(date +'%Y%m%d_%H%M%S').bak"

    sqlcmd -S "$MSSQL_SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" \
        -Q "BACKUP DATABASE [$MSSQL_DATABASE] TO DISK='$backup_file' WITH INIT, COMPRESSION;" \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_msg "✓ FULL backup completed: $(basename $backup_file)"
        log_msg "  File size: $(du -h "$backup_file" | cut -f1)"
    else
        log_msg "✗ FULL backup FAILED"
        return 1
    fi
}

backup_differential() {
    log_msg "=== DIFFERENTIAL BACKUP START ==="
    local backup_file="${BACKUP_DIR}/dwh_diff_$(date +'%Y%m%d_%H%M%S').bak"

    sqlcmd -S "$MSSQL_SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" \
        -Q "BACKUP DATABASE [$MSSQL_DATABASE] TO DISK='$backup_file' WITH DIFFERENTIAL, INIT, COMPRESSION;" \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_msg "✓ DIFFERENTIAL backup completed: $(basename $backup_file)"
        log_msg "  File size: $(du -h "$backup_file" | cut -f1)"
    else
        log_msg "✗ DIFFERENTIAL backup FAILED"
        return 1
    fi
}

backup_transaction_log() {
    log_msg "=== TRANSACTION LOG BACKUP START ==="
    local backup_file="${BACKUP_DIR}/dwh_log_$(date +'%Y%m%d_%H%M%S').trn"

    sqlcmd -S "$MSSQL_SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" \
        -Q "BACKUP LOG [$MSSQL_DATABASE] TO DISK='$backup_file' WITH INIT, COMPRESSION;" \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_msg "✓ TRANSACTION LOG backup completed: $(basename $backup_file)"
        log_msg "  File size: $(du -h "$backup_file" | cut -f1)"
    else
        log_msg "✗ TRANSACTION LOG backup FAILED (DB may not be in FULL recovery mode)"
    fi
}

cleanup_old_backups() {
    log_msg "=== CLEANUP OLD BACKUPS START ==="

    # Remove old FULL backups (older than RETENTION_DAYS_FULL)
    find "$BACKUP_DIR" -name "dwh_full_*.bak" -type f -mtime +$RETENTION_DAYS_FULL -delete
    log_msg "✓ Removed FULL backups older than $RETENTION_DAYS_FULL days"

    # Remove old DIFFERENTIAL backups (older than RETENTION_DAYS_DIFF)
    find "$BACKUP_DIR" -name "dwh_diff_*.bak" -type f -mtime +$RETENTION_DAYS_DIFF -delete
    log_msg "✓ Removed DIFFERENTIAL backups older than $RETENTION_DAYS_DIFF days"

    # Remove old LOG backups (older than RETENTION_DAYS_LOG)
    find "$BACKUP_DIR" -name "dwh_log_*.trn" -type f -mtime +$RETENTION_DAYS_LOG -delete
    log_msg "✓ Removed TRANSACTION LOG backups older than $RETENTION_DAYS_LOG days"
}

archive_backups() {
    log_msg "=== ARCHIVE BACKUPS START ==="

    # Archive FULL backups to separate directory
    if [ "$(ls -A $BACKUP_DIR/dwh_full_*.bak 2>/dev/null)" ]; then
        cp "$BACKUP_DIR"/dwh_full_*.bak "$ARCHIVE_DIR/" 2>/dev/null || true
        log_msg "✓ Archived FULL backups"
    fi

    # Keep latest 4 FULL backups in main dir, archive rest
    local full_count=$(ls -1 "$BACKUP_DIR"/dwh_full_*.bak 2>/dev/null | wc -l)
    if [ "$full_count" -gt 4 ]; then
        ls -1t "$BACKUP_DIR"/dwh_full_*.bak | tail -n +5 | xargs -r mv -t "$ARCHIVE_DIR/"
        log_msg "✓ Moved excess FULL backups to archive (keeping latest 4)"
    fi
}

# ---- Main ----

log_msg "========================================"
log_msg "DWH Backup Script Started"
log_msg "Database: $MSSQL_DATABASE @ $MSSQL_SERVER"
log_msg "Backup Dir: $BACKUP_DIR"
log_msg "========================================"

# Check SQL Server connectivity
if ! sqlcmd -S "$MSSQL_SERVER" -U "$MSSQL_USER" -P "$MSSQL_PASSWORD" \
    -Q "SELECT 'SQL Server is accessible'" > /dev/null 2>&1; then
    log_msg "✗ FATAL: Cannot connect to SQL Server at $MSSQL_SERVER"
    exit 1
fi

# Determine backup type based on day of week
DAY_OF_WEEK=$(date +%w)  # 0=Sunday, 1=Monday, ..., 6=Saturday

if [ "$DAY_OF_WEEK" -eq 0 ]; then
    # Sunday: Full backup
    backup_full
elif [ "$DAY_OF_WEEK" -eq 1 ] || [ "$DAY_OF_WEEK" -eq 4 ]; then
    # Monday & Thursday: Differential + Transaction Log
    backup_differential
    backup_transaction_log
else
    # Other days: Transaction Log only
    backup_transaction_log
fi

cleanup_old_backups
archive_backups

log_msg "========================================"
log_msg "DWH Backup Script Completed"
log_msg "========================================"
log_msg ""

exit 0
