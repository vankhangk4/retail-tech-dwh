import subprocess
import threading
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from models.master import User, ETLRun
from api.deps import get_db, get_current_active_user
from config import get_settings
from core.tenant import get_master_session

router = APIRouter(prefix="/api/etl", tags=["ETL"])
settings = get_settings()


def _run_etl_subprocess(tenant_id: str, run_id: int, db_name: str):
    """Chạy ETL subprocess cho tenant."""
    import time
    time.sleep(1)  # Small delay

    with get_master_session() as db:
        run = db.query(ETLRun).filter(ETLRun.RunId == run_id).first()
        if run:
            run.Status = "RUNNING"
            db.commit()

    try:
        result = subprocess.run(
            [
                "python3.10", "-m", "etl.main_etl",
                "--tenant", tenant_id,
                "--full",
            ],
            capture_output=True,
            text=True,
            cwd="/app",
            timeout=3600,
        )

        with get_master_session() as db:
            run = db.query(ETLRun).filter(ETLRun.RunId == run_id).first()
            if run:
                if result.returncode == 0:
                    run.Status = "SUCCESS"
                    run.CompletedAt = datetime.utcnow()
                    run.RowsProcessed = 0
                else:
                    run.Status = "FAILED"
                    run.CompletedAt = datetime.utcnow()
                    run.ErrorMessage = result.stderr[:1000]
                db.commit()
    except subprocess.TimeoutExpired:
        with get_master_session() as db:
            run = db.query(ETLRun).filter(ETLRun.RunId == run_id).first()
            if run:
                run.Status = "FAILED"
                run.CompletedAt = datetime.utcnow()
                run.ErrorMessage = "ETL timeout (>1h)"
                db.commit()
    except Exception as e:
        with get_master_session() as db:
            run = db.query(ETLRun).filter(ETLRun.RunId == run_id).first()
            if run:
                run.Status = "FAILED"
                run.CompletedAt = datetime.utcnow()
                run.ErrorMessage = str(e)[:1000]
                db.commit()


@router.post("/run")
async def trigger_etl(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    # Create ETL run record
    run = ETLRun(
        TenantId=tenant_id,
        TriggeredBy=current_user.UserId,
        Status="PENDING",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Run ETL in background
    db_name = f"DWH_{tenant_id}"
    background_tasks.add_task(_run_etl_subprocess, tenant_id, run.RunId, db_name)

    return {"run_id": run.RunId, "status": "PENDING", "message": "ETL đã được kích hoạt"}


@router.get("/status/{run_id}")
async def get_etl_status(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    run = db.query(ETLRun).filter(ETLRun.RunId == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run không tồn tại")
    if run.TenantId != current_user.TenantId and current_user.Role != "SuperAdmin":
        raise HTTPException(status_code=403, detail="Không có quyền xem")

    return {
        "run_id": run.RunId,
        "status": run.Status,
        "rows_processed": run.RowsProcessed,
        "error": run.ErrorMessage,
        "started_at": run.StartedAt,
        "completed_at": run.CompletedAt,
    }


@router.get("/history")
async def get_etl_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(ETLRun)
    if current_user.Role != "SuperAdmin":
        query = query.filter(ETLRun.TenantId == current_user.TenantId)

    runs = query.order_by(ETLRun.RunId.desc()).limit(50).all()
    return [
        {
            "run_id": r.RunId,
            "tenant_id": r.TenantId,
            "status": r.Status,
            "rows_processed": r.RowsProcessed,
            "error": r.ErrorMessage,
            "started_at": r.StartedAt,
            "completed_at": r.CompletedAt,
        }
        for r in runs
    ]
