# ERD — Data Warehouse Multi-Tenant Schema

**Dự án:** DWH Multi-Tenant cho Chuỗi Bán lẻ Thiết bị Công nghệ  
**Cập nhật:** 2026-05-08

---

## Sơ đồ quan hệ (Text ERD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TENANT MANAGEMENT                                  │
├──────────────────────┐   ┌──────────────────────────────────────────────────┤
│ Tenants              │   │ AppUsers                                          │
│──────────────────────│   │──────────────────────────────────────────────────│
│ PK TenantID  VARCHAR │◄──┤ PK UserID       INT IDENTITY                     │
│    TenantName        │   │    Username     VARCHAR(100) UNIQUE               │
│    FilePath          │   │    PasswordHash VARCHAR(255)                      │
│    IsActive          │   │ FK TenantID     VARCHAR → Tenants.TenantID (NULL) │
│    ExpiresAt         │   │    Role         VARCHAR (superadmin/admin/viewer)  │
│    CreatedAt         │   │    IsActive     BIT                               │
│    Description       │   │    DisplayName  VARCHAR(100)                      │
└──────────────────────┘   │    Email        VARCHAR(200)                      │
                           │    Phone        VARCHAR(20)                       │
                           │    AvatarData   NVARCHAR(MAX)                     │
                           │    CreatedAt    DATETIME                          │
                           └──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DIMENSION TABLES (Shared & Per-Tenant)              │
├──────────────────┐  ┌──────────────────┐  ┌───────────────────────────────┐
│ DimDate          │  │ DimProduct (SCD2)│  │ DimCustomer (SCD2)            │
│──────────────────│  │──────────────────│  │───────────────────────────────│
│ PK DateKey INT   │  │ PK ProductKey    │  │ PK CustomerKey INT            │
│    FullDate      │  │    ProductID     │  │    CustomerID                 │
│    Year          │  │    ProductName   │  │ FK TenantID → Tenants         │
│    Quarter       │  │    CategoryName  │  │    HoTen                      │
│    Month         │  │    SubCategory   │  │    GioiTinh                   │
│    Week          │  │    Brand         │  │    NgaySinh                   │
│    DayOfWeek     │  │    CostPrice     │  │    ThanhPho                   │
│    IsWeekend     │  │    ListPrice     │  │    LoaiKH                     │
│    IsHoliday     │  │    Unit          │  │    DiemTichLuy                │
│    Season        │  │    WarrantyMonths│  │    IsCurrent BIT              │
└──────────────────┘  │    IsCurrent BIT │  │    ValidFrom / ValidTo        │
                      │    ValidFrom     │  └───────────────────────────────┘
                      │    ValidTo       │
                      └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ DimStore         │  │ DimEmployee      │  │ DimSupplier      │
│──────────────────│  │──────────────────│  │──────────────────│
│ PK StoreKey INT  │  │ PK EmployeeKey   │  │ PK SupplierKey   │
│    StoreID       │  │    EmployeeID    │  │    SupplierID    │
│ FK TenantID      │  │ FK TenantID      │  │    SupplierName  │
│    StoreName     │  │    HoTen         │  │    ContactName   │
│    City          │  │    ChucVu        │  │    Phone         │
│    Province      │  │    CaLam         │  │    Email         │
│    StoreType     │  │    NgayVaoLam    │  │    Address       │
│    OpenDate      │  │    IsActive BIT  │  │    IsActive BIT  │
│    IsActive BIT  │  └──────────────────┘  └──────────────────┘
└──────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           FACT TABLES                                         │
├────────────────────────────────────────────────────────────────────────────── │
│ FactSales                                                                    │
│──────────────────────────────────────────────────────────────────────────────│
│ PK SalesKey      BIGINT IDENTITY                                             │
│ FK TenantID      → Tenants.TenantID                                          │
│ FK DateKey       → DimDate.DateKey                                           │
│ FK ProductKey    → DimProduct.ProductKey                                     │
│ FK CustomerKey   → DimCustomer.CustomerKey                                   │
│ FK StoreKey      → DimStore.StoreKey                                         │
│ FK EmployeeKey   → DimEmployee.EmployeeKey                                   │
│ FK PaymentKey    → DimPaymentMethod.PaymentKey                               │
│    MaHoaDon      VARCHAR(50)                                                 │
│    Quantity      INT                                                         │
│    UnitPrice     DECIMAL(18,2)                                               │
│    Discount      DECIMAL(18,2)                                               │
│    GrossSalesAmount DECIMAL(18,2)                                            │
│    NetSalesAmount   DECIMAL(18,2)                                            │
│    SalesChannel  VARCHAR(20)   -- InStore / Online                           │
│    IsReturn      BIT                                                         │
│    CreatedAt     DATETIME                                                    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ FactInventory                                                                │
│──────────────────────────────────────────────────────────────────────────────│
│ PK InventoryKey  BIGINT IDENTITY                                             │
│ FK TenantID      → Tenants                                                   │
│ FK DateKey       → DimDate                                                   │
│ FK ProductKey    → DimProduct                                                │
│ FK StoreKey      → DimStore                                                  │
│    StockBegin    INT                                                         │
│    StockEnd      INT                                                         │
│    StockReceived INT                                                         │
│    StockSold     INT                                                         │
│    StockAdjust   INT                                                         │
│    CostPrice     DECIMAL(18,2)                                               │
│    TotalValue    DECIMAL(18,2)                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ FactPurchase                                                                 │
│──────────────────────────────────────────────────────────────────────────────│
│ PK PurchaseKey   BIGINT IDENTITY                                             │
│ FK TenantID      → Tenants                                                   │
│ FK DateKey       → DimDate (ngày đặt)                                        │
│ FK ProductKey    → DimProduct                                                │
│ FK StoreKey      → DimStore                                                  │
│ FK SupplierKey   → DimSupplier                                               │
│    SoPhieuDat    VARCHAR(50)                                                 │
│    QuantityOrdered INT                                                       │
│    QuantityReceived INT                                                      │
│    UnitCost      DECIMAL(18,2)                                               │
│    TotalCost     DECIMAL(18,2)                                               │
│    ReceivedDate  DATE                                                        │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                        DATA MART TABLES / VIEWS                              │
├──────────────────────┬────────────────────────┬────────────────────────────── │
│ DM_SalesSummary      │ DM_CustomerRFM          │ DM_InventoryAlert            │
│──────────────────────│────────────────────────│──────────────────────────────│
│ FK TenantID          │ FK TenantID             │ FK TenantID                  │
│    SalesYear         │    CustomerID           │    ProductID                 │
│    SalesMonth        │    Recency_Days INT      │    StoreID                  │
│    StoreID           │    Frequency   INT      │    CurrentStock              │
│    CategoryName      │    Monetary    DECIMAL  │    ReorderPoint              │
│    TotalRevenue      │    Segment VARCHAR      │    AlertType VARCHAR          │
│    TotalProfit       │      (Champion/         │      (OutOfStock/            │
│    TotalOrders       │       Loyal/            │       LowStock/              │
│    AvgOrderValue     │       AtRisk/...)        │       Overstocked)           │
│    UpdatedAt         │    UpdatedAt            │    UpdatedAt                 │
└──────────────────────┴────────────────────────┴──────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                        ETL CONTROL TABLES                                    │
├──────────────────────┬────────────────────────────────────────────────────── │
│ ETL_Watermark        │ ETLLogs                                               │
│──────────────────────│────────────────────────────────────────────────────── │
│ PK WatermarkID       │ PK LogID          BIGINT IDENTITY                     │
│ FK TenantID          │ FK TenantID                                           │
│    TableName         │    ProcessType    VARCHAR (extract/transform/load)     │
│    LastProcessedAt   │    RowsProcessed  INT                                 │
│    Status VARCHAR    │    RowsError      INT                                 │
│      PENDING/RUNNING/│    RunStatus      VARCHAR (SUCCESS/FAILED/WARNING)    │
│      SUCCESS/FAILED  │    StartTime      DATETIME                            │
└──────────────────────│    EndTime        DATETIME                            │
                       │    ErrorMessage   NVARCHAR(MAX)                       │
                       └────────────────────────────────────────────────────── │

┌──────────────────────────────────────────────────────────────────────────────┐
│                        STAGING TABLES                                        │
│ STG_SalesRaw · STG_InventoryRaw · STG_PurchaseRaw                           │
│ STG_ProductRaw · STG_CustomerRaw                                             │
│ STG_ErrorLog (TenantID, TableName, RowData, ErrorType, CreatedAt)           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Quan hệ chính

| Từ bảng | → | Đến bảng | Loại | Ghi chú |
|---------|---|----------|------|---------|
| AppUsers | FK | Tenants | N:1 | Mỗi user thuộc 1 tenant (NULL = SuperAdmin) |
| FactSales | FK | Tenants | N:1 | Row-Level Security theo TenantID |
| FactSales | FK | DimDate | N:1 | Ngày bán |
| FactSales | FK | DimProduct | N:1 | SCD Type 2 |
| FactSales | FK | DimCustomer | N:1 | SCD Type 2, per-tenant |
| FactSales | FK | DimStore | N:1 | Per-tenant |
| FactSales | FK | DimEmployee | N:1 | Per-tenant |
| FactInventory | FK | Tenants, DimDate, DimProduct, DimStore | N:1 | — |
| FactPurchase | FK | Tenants, DimDate, DimProduct, DimStore, DimSupplier | N:1 | — |
| ETL_Watermark | FK | Tenants | N:1 | Mỗi tenant có watermark riêng |
| ETLLogs | FK | Tenants | N:1 | Log mỗi ETL run |

---

## Indexes quan trọng

| Index | Bảng | Cột | Mục đích |
|-------|------|-----|---------|
| IX_FactSales_TenantID | FactSales | TenantID | RLS filter |
| IX_FactSales_TenantDate | FactSales | (TenantID, DateKey) | Dashboard query |
| IX_FactInventory_Tenant | FactInventory | TenantID | RLS filter |
| IX_DM_Sales_Tenant_Date | DM_SalesSummary | (TenantID, SalesYear, SalesMonth) | Aggregation |
| UQ_DimProduct_Current | DimProduct | (ProductID, IsCurrent) | SCD2 lookup |
| IX_AppUsers_Username | AppUsers | Username | Login lookup |
| IX_ETL_Watermark | ETL_Watermark | (TenantID, TableName) | Watermark lookup |

---

## SCD Type 2 — DimProduct & DimCustomer

```
ProductKey  ProductID  TenantID   IsCurrent  ValidFrom    ValidTo
──────────  ─────────  ─────────  ─────────  ──────────   ──────────
1           SP001      STORE_HN   0          2023-01-01   2024-06-01   ← lịch sử
2           SP001      STORE_HN   1          2024-06-01   NULL         ← hiện tại
3           SP002      STORE_HN   1          2023-01-01   NULL         ← hiện tại
```

---

## RLS View

```sql
-- sql/views/v_FactSales_ByTenant.sql
CREATE VIEW v_FactSales_ByTenant AS
SELECT * FROM FactSales
WHERE TenantID = CAST(SESSION_CONTEXT(N'tenant_id') AS VARCHAR(50))
   OR SESSION_CONTEXT(N'tenant_id') IS NULL;  -- NULL = SuperAdmin
```
