# ============================================================
# FILE: api/main.py
# Mô tả: FastAPI Auth Gateway — Main Application
# ============================================================

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from api.auth import router as auth_router, run_bootstrap
from api.management import router as management_router
from api.upload import router as upload_router

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ---- FastAPI App ----
app = FastAPI(
    title='DWH Auth Gateway',
    description='API xác thực đa tenant cho Data Warehouse Multi-Tenant',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

# ---- Middleware ----
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Thay bằng domain thực tế khi production
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ---- Health check endpoint ----
@app.get('/health', tags=['Health'])
def health_check():
    """Health check endpoint cho monitoring."""
    return {
        'status': 'healthy',
        'service': 'DWH Auth Gateway',
        'version': '1.0.0'
    }

# ---- Include routers ----
app.include_router(auth_router)
app.include_router(management_router)
app.include_router(upload_router)

# ---- Exception handlers ----

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Xử lý exception chung — không leak thông tin lỗi."""
    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'detail': 'Loi he thong, vui long thu lai sau'}
    )


@app.on_event('startup')
async def startup_event():
    logger.info('DWH Auth Gateway started successfully')
    logger.info(f'JWT Algorithm: HS256, Access Token TTL: 8h')
    # Chạy bootstrap users vào MSSQL sau khi DB sẵn sàng
    run_bootstrap()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info('DWH Auth Gateway shutting down')


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(
        'api.main:app',
        host='0.0.0.0',
        port=port,
        reload=True,
        log_level='info'
    )