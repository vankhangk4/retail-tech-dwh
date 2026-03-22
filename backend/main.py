from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from api.routes import auth, tenants, users, upload, etl, embed, stats

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init master DB tables + create SuperAdmin
    from app.init_db import init_db, init_superadmin
    try:
        init_db()
        init_superadmin()
    except Exception as e:
        print(f"Warning: startup init failed (may already exist): {e}")
    yield


app = FastAPI(
    title="DATN SaaS Platform API",
    description="Multi-tenant Data Warehouse & BI Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - cho phép frontend truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(upload.router)
app.include_router(etl.router)
app.include_router(embed.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {
        "name": "DATN SaaS Platform",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
