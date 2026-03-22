# DATN Architecture - Multi-tenant SaaS Platform

## System Overview

Hệ thống Data Warehouse + BI dạng **SaaS Multi-tenant**:
- **Admin Portal**: Quản lý tenants, users, upload, ETL
- **User Portal**: Xem dashboard, upload file
- **Per-tenant isolation**: Mỗi tenant = 1 database riêng
- **Superset embedded**: BI charts nhúng trong React

## Architecture

```
                    INTERNET
                       │
         ┌─────────────┴─────────────┐
         │                             │
    Admin Portal                  User Portal
    (React, :3000/admin)        (React, :3000/user)
         │                             │
         └──────────────┬────────────┘
                        │
                  FastAPI Backend
                   (:8000/api)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   TenantDB_001    TenantDB_002    TenantDB_003
   (SQL Server)    (SQL Server)    (SQL Server)
        │               │               │
        ▼               ▼               ▼
   Superset      Superset       Superset
   (per-tenant   (same Superset instance,
    DB)           switch DB via URL)
```

## Components

### 1. FastAPI Backend (:8000)
- JWT authentication
- Multi-database tenant isolation
- Tenant management (SuperAdmin)
- User management (Admin)
- File upload service
- ETL trigger
- Superset guest token generator
- Stats/KPIs API

### 2. React Frontend (:3000)
- Login page
- Admin Portal: Dashboard, Tenants, Users, ETLRuns, EmbeddedCharts
- User Portal: Dashboard, Upload, Reports
- Superset charts embedded via guest token

### 3. SQL Server
- 1 container = N databases (per tenant)
- DWH_Master: metadata (Tenants, Users, Subscriptions)
- DWH_TenantXXX: data warehouse per tenant

### 4. Superset
- 1 instance
- Guest token per tenant
- Switch database via URL parameter

### 5. ETL Pipeline
- Per-tenant execution
- Reads from: data/sources/{tenant_id}/
- Writes to: DWH_TenantXXX

## User Roles

| Role | Quyền |
|------|--------|
| SuperAdmin | Quản lý tenants, tạo user, upload file, chạy ETL, xem log |
| TenantAdmin | Quản lý user trong tenant, upload file, chạy ETL |
| User | Upload file, xem dashboard (Superset embed) |

## Database Schema

### DWH_Master (metadata DB)
```sql
CREATE TABLE Tenants (
    TenantId       VARCHAR(50) PRIMARY KEY,
    TenantName     NVARCHAR(200) NOT NULL,
    DatabaseName   VARCHAR(100) NOT NULL UNIQUE,
    Plan           VARCHAR(20) DEFAULT 'trial',
    IsActive       BIT DEFAULT 1,
    CreatedAt      DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE Users (
    UserId         INT IDENTITY PRIMARY KEY,
    TenantId      VARCHAR(50) NOT NULL,
    Username      VARCHAR(100) NOT NULL,
    PasswordHash  VARCHAR(255) NOT NULL,
    Role          VARCHAR(20) NOT NULL, -- SuperAdmin, TenantAdmin, User
    IsActive      BIT DEFAULT 1,
    CreatedAt     DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (TenantId) REFERENCES Tenants(TenantId)
);
```

### DWH_TenantXXX (per tenant)
- Giống hệt schema hiện tại: STG_*, Dim*, Fact*, DM_*

## API Endpoints

### Auth
```
POST /api/auth/login    - Login → JWT token
POST /api/auth/logout   - Logout
GET  /api/auth/me       - Current user info
```

### SuperAdmin
```
GET    /api/admin/tenants          - List tenants
POST   /api/admin/tenants          - Create tenant + DB
DELETE /api/admin/tenants/{id}     - Delete tenant

GET    /api/admin/users             - List all users
POST   /api/admin/users             - Create user
PUT    /api/admin/users/{id}       - Update user
DELETE /api/admin/users/{id}       - Delete user
```

### Tenant Admin
```
GET    /api/tenant/users            - Users in tenant
POST   /api/tenant/users           - Create user in tenant
DELETE /api/tenant/users/{id}     - Delete user in tenant
```

### Upload
```
POST /api/upload                   - Upload file
GET  /api/upload                   - List uploaded files
```

### ETL
```
POST /api/etl/run                  - Trigger ETL
GET  /api/etl/status               - ETL status
GET  /api/etl/history              - ETL history
```

### Embed & Stats
```
GET /api/embed/guest-token         - Superset guest token
GET /api/embed/dashboards          - Dashboard list
GET /api/stats                     - KPIs
```

## Docker Services

| Service | Image | Port | Mô tả |
|---------|-------|------|--------|
| mssql | mssql/server:2022 | 1433 | SQL Server (N databases) |
| postgres_meta | postgres:15 | 5432 | Metadata DB |
| redis | redis:7-alpine | 6379 | Cache |
| superset | apache/superset:3.1.1 | 8088 | BI (embedded) |
| backend | datn/backend | 8000 | FastAPI |
| frontend | datn/frontend | 80 | React SPA |

## Data Flow

### New Tenant Onboarding
```
1. SuperAdmin → POST /api/admin/tenants
   → Backend creates DWH_TenantXXX database
   → Runs init SQL scripts
   → Creates TenantAdmin user
   → Returns tenant credentials
```

### ETL Per Tenant
```
1. User uploads file → /data/sources/{tenant_id}/
2. POST /api/etl/run → Backend runs ETL subprocess
3. ETL reads from data/sources/{tenant_id}/
4. ETL writes to DWH_TenantXXX
5. Superset embeds charts from DWH_TenantXXX
```

### Superset Embedding
```
1. Frontend → GET /api/embed/guest-token?dashboard=1
2. Backend → Creates Superset guest token for DWH_TenantXXX
3. Frontend → Renders <iframe src="superset...?guest_token=xxx">
```

## Security

- JWT tokens (access + refresh)
- Tenant isolation at database level
- Row-level security via TenantId
- Password hashed with bcrypt
- Superset guest tokens (short-lived, scoped per DB)
- HTTPS recommended in production
