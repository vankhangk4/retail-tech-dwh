# ============================================================
# FILE: api/upload.py
# Mô tả: Upload file + trigger ETL cho tenant (tách riêng)
# ============================================================

import os
import re
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import jwt
import pymssql as mssql
import pydantic
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, BackgroundTasks

# ---- Configuration ----
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'changeme-minimum-32-chars!!')
ALGORITHM = 'HS256'

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'

ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}
MAX_FILE_SIZE_MB = 50
LANDING_DIR_NAME = '1_landing'
ARCHIVE_DIR_NAME = '2_archive'
ERROR_DIR_NAME = '3_error'

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api', tags=['Upload'])


# ============================================================
# Helpers
# ============================================================

def get_mssql_conn():
    return mssql.connect(
        server=os.environ.get('MSSQL_SERVER', 'localhost'),
        user=os.environ.get('MSSQL_USER', 'sa'),
        password=os.environ.get('MSSQL_PASSWORD', ''),
        database=os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')
    )


def require_auth(authorization: str = Header(...)):
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Token khong hop le')


def validate_tenant(tenant_id: str) -> dict:
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT TenantID, TenantName, FilePath, IsActive, ExpiresAt FROM Tenants WHERE TenantID = %s',
        (tenant_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, detail=f'Tenant "{tenant_id}" khong ton tai')
    if not row['IsActive']:
        raise HTTPException(400, detail=f'Tenant "{tenant_id}" khong con hoat dong')
    # Check tenant expiration
    if row['ExpiresAt']:
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc)
        exp_utc = row['ExpiresAt']
        if exp_utc.tzinfo is None:
            exp_utc = exp_utc.replace(tzinfo=timezone.utc)
        if now_utc > exp_utc:
            raise HTTPException(403, detail=f'Tenant "{tenant_id}" da het han vao {exp_utc.strftime("%d/%m/%Y %H:%M")} — khong the truy cap')
    return row


def ensure_tenant_stage_dirs(tenant_id: str) -> dict[str, Path]:
    tenant_root = DATA_ROOT / tenant_id
    stage_dirs = {
        'root': tenant_root,
        'landing': tenant_root / LANDING_DIR_NAME,
        'archive': tenant_root / ARCHIVE_DIR_NAME,
        'error': tenant_root / ERROR_DIR_NAME,
        'logs': tenant_root / 'logs',
    }
    for path in stage_dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return stage_dirs


def get_tenant_data_dir(tenant_id: str) -> Path:
    """Return the only directory ETL should scan for new, unprocessed files."""
    return ensure_tenant_stage_dirs(tenant_id)['landing']


def ensure_tenant_access(payload: dict, tenant_id: str) -> None:
    """Superadmin được thao tác mọi tenant; các role khác chỉ được đúng tenant trong JWT."""
    if payload.get('role') == 'superadmin':
        return
    if payload.get('tenant_id') != tenant_id:
        raise HTTPException(403, detail='Chi duoc thao tac tren tenant cua minh')


def detect_file_type(filename: str) -> Optional[str]:
    fname = filename.upper()
    if 'BAOCAODOANHTHU' in fname or 'DOANHTHU' in fname:
        return 'sales'
    if 'QUANLYKHO' in fname or 'TONKHO' in fname or 'KHO' in fname:
        return 'inventory'
    if 'DANHMUCSANPHAM' in fname or 'SANPHAM' in fname:
        return 'product'
    if 'DANHMUCKHACHHANG' in fname or 'KHACHHANG' in fname:
        return 'customer'
    if 'PHIEUNHAPHANG' in fname or 'NHAPHANG' in fname:
        return 'purchase'
    if 'NCC' in fname or 'NHACUNGCAP' in fname or 'SUPPLIER' in fname:
        return 'supplier'
    if filename.lower().endswith('.csv'):
        return 'csv'
    return None


async def save_upload_file(upload_file: UploadFile, dest_path: Path) -> int:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    file_size = 0
    with open(dest_path, 'wb') as f:
        while chunk := upload_file.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                f.close()
                dest_path.unlink(missing_ok=True)
                raise HTTPException(413, detail=f'File vuot qua {MAX_FILE_SIZE_MB}MB')
            f.write(chunk)
    return file_size


def run_etl_for_tenant_sync(tenant_id: str) -> dict:
    script_path = PROJECT_ROOT / 'etl' / 'orchestrator' / 'main_etl.py'
    env = {
        **os.environ,
        'MSSQL_SERVER': os.environ.get('MSSQL_SERVER', 'localhost'),
        'MSSQL_USER': os.environ.get('MSSQL_USER', 'sa'),
        'MSSQL_PASSWORD': os.environ.get('MSSQL_PASSWORD', ''),
        'MSSQL_DATABASE': os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant'),
    }
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--tenant', tenant_id],
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout[-2000:] if result.stdout else '',
            'stderr': result.stderr[-500:] if result.stderr else '',
        }
    except subprocess.TimeoutExpired:
        return {'exit_code': -1, 'stdout': '', 'stderr': 'ETL timed out (>5 min)'}
    except Exception as e:
        return {'exit_code': -1, 'stdout': '', 'stderr': str(e)}


def run_etl_background(tenant_id: str):
    logger.info(f'[ETL-BG] Starting ETL for tenant={tenant_id}')
    result = run_etl_for_tenant_sync(tenant_id)
    if result['exit_code'] == 0:
        logger.info(f'[ETL-BG] ETL SUCCESS for {tenant_id}')
    else:
        logger.error(f'[ETL-BG] ETL FAILED for {tenant_id}: {result["stderr"]}')


# ============================================================
# Pydantic Models
# ============================================================

class FileUploadResult(pydantic.BaseModel):
    filename: str
    file_type: Optional[str]
    file_size_bytes: int
    saved_path: str
    success: bool
    error: Optional[str] = None


class UploadResponse(pydantic.BaseModel):
    success: bool
    tenant_id: str
    uploaded_files: list[FileUploadResult]
    total_files: int
    successful_uploads: int
    message: str


class ETLTriggerResponse(pydantic.BaseModel):
    success: bool
    tenant_id: str
    exit_code: int
    message: str
    stdout: str | None = None
    stderr: str | None = None


class FileListItem(pydantic.BaseModel):
    filename: str
    file_type: str
    size_bytes: int
    uploaded_at: str


class FileListResponse(pydantic.BaseModel):
    tenant_id: str
    files: list[FileListItem]


# ============================================================
# Endpoints
# ============================================================

@router.post('/upload/{tenant_id}', response_model=UploadResponse)
async def upload_files(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
    files: list[UploadFile] = File(...),
):
    """
    Upload NHIEU FILE cung luc cho tenant.
    File duoc luu vao: data/{tenant_id}/1_landing/
    KHONG tu dong trigger ETL — dung endpoint /upload/{tenant_id}/etl rieng.
    """
    payload = require_auth(authorization)

    ensure_tenant_access(payload, tenant_id)

    validate_tenant(tenant_id)

    if not files:
        raise HTTPException(400, detail='Khong co file nao duoc chon')

    results = []
    successful = 0
    data_dir = get_tenant_data_dir(tenant_id)

    for upload_file in files:
        if not upload_file.filename:
            continue

        ext = Path(upload_file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            results.append(FileUploadResult(
                filename=upload_file.filename,
                file_type=None,
                file_size_bytes=0,
                saved_path='',
                success=False,
                error=f'Dinh dang khong ho tro: {ext}',
            ))
            continue

        file_type = detect_file_type(upload_file.filename)
        if not file_type:
            results.append(FileUploadResult(
                filename=upload_file.filename,
                file_type=None,
                file_size_bytes=0,
                saved_path='',
                success=False,
                error='Khong nhan dien duoc loai file. Dat ten theo quy uoc.',
            ))
            continue

        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', upload_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stem = Path(safe_name).stem
        saved_name = f"{stem}_{timestamp}{ext}"
        saved_path = data_dir / saved_name

        try:
            file_size = await save_upload_file(upload_file, saved_path)
            results.append(FileUploadResult(
                filename=saved_name,
                file_type=file_type,
                file_size_bytes=file_size,
                saved_path=str(saved_path),
                success=True,
            ))
            successful += 1
            logger.info(
                f'[UPLOAD] tenant={tenant_id} file={saved_name} '
                f'type={file_type} size={file_size} by={payload.get("username")}'
            )
        except HTTPException:
            raise
        except Exception as e:
            results.append(FileUploadResult(
                filename=upload_file.filename,
                file_type=file_type,
                file_size_bytes=0,
                saved_path='',
                success=False,
                error=str(e),
            ))

    return UploadResponse(
        success=successful > 0,
        tenant_id=tenant_id,
        uploaded_files=results,
        total_files=len(files),
        successful_uploads=successful,
        message=f'Da upload {successful}/{len(files)} file thanh cong.',
    )


@router.post('/upload/{tenant_id}/etl', response_model=ETLTriggerResponse)
async def trigger_etl(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
):
    """Trigger ETL cho tenant — nap du lieu tu file da upload vao Data Warehouse."""
    payload = require_auth(authorization)

    ensure_tenant_access(payload, tenant_id)

    validate_tenant(tenant_id)

    background_tasks.add_task(run_etl_background, tenant_id)

    logger.info(f'[ETL] Triggered for tenant={tenant_id} by={payload.get("username")}')

    return ETLTriggerResponse(
        success=True,
        tenant_id=tenant_id,
        exit_code=-1,
        message=f'ETL da duoc kich hoat cho tenant {tenant_id}. '
                f'Kiem tra trang ETL Logs de xem ket qua.',
    )


@router.get('/upload/{tenant_id}/etl/status')
def get_etl_status(
    tenant_id: str,
    authorization: str = Header(...),
):
    """Lay trang thai cuoi cua ETL chay cho tenant."""
    payload = require_auth(authorization)

    ensure_tenant_access(payload, tenant_id)

    validate_tenant(tenant_id)

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        'SELECT TOP 3 LogID, TenantID, TableName, StepName, RowsProcessed, '
        'RowsInserted, RowsUpdated, RowsRejected, DurationSec, '
        'Status, ErrorMessage, CreatedAt '
        'FROM ETLLogs WHERE TenantID = %s ORDER BY CreatedAt DESC',
        (tenant_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return {
        'tenant_id': tenant_id,
        'recent_logs': [
            {
                'log_id': r['LogID'],
                'source_table': r['TableName'],
                'step_name': r['StepName'],
                'rows_extracted': r['RowsProcessed'],
                'rows_inserted': r['RowsInserted'],
                'rows_rejected': r['RowsRejected'],
                'duration_seconds': r['DurationSec'],
                'status': r['Status'],
                'start_time': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
                'error_message': r['ErrorMessage'],
            }
            for r in rows
        ]
    }


@router.get('/upload/{tenant_id}/files', response_model=FileListResponse)
def list_uploaded_files(
    tenant_id: str,
    authorization: str = Header(...),
):
    """Danh sach file moi dang cho xu ly ETL trong 1_landing."""
    payload = require_auth(authorization)

    ensure_tenant_access(payload, tenant_id)

    validate_tenant(tenant_id)

    data_dir = get_tenant_data_dir(tenant_id)
    files = []
    for f in sorted(data_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            files.append(FileListItem(
                filename=f.name,
                file_type=detect_file_type(f.name) or 'unknown',
                size_bytes=f.stat().st_size,
                uploaded_at=mtime.isoformat(),
            ))

    return FileListResponse(tenant_id=tenant_id, files=files)


@router.delete('/upload/{tenant_id}/files/{filename}')
def delete_uploaded_file(
    tenant_id: str,
    filename: str,
    authorization: str = Header(...),
):
    """Xoa file da upload (Admin only)."""
    payload = require_auth(authorization)
    if payload.get('role') not in ('admin', 'superadmin'):
        raise HTTPException(403, detail='Chi admin moi co quyen xoa file')
    ensure_tenant_access(payload, tenant_id)

    validate_tenant(tenant_id)

    data_dir = get_tenant_data_dir(tenant_id)
    file_path = data_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, detail=f'File "{filename}" khong ton tai')

    file_path.unlink()
    logger.info(f'[UPLOAD] Deleted {tenant_id}/{filename} by {payload.get("username")}')

    return {'success': True, 'message': f'Da xoa file "{filename}"'}
