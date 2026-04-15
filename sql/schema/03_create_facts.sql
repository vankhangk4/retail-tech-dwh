-- ============================================================
-- FILE: sql/schema/03_create_facts.sql
-- Mô tả: Tạo các bảng Fact (Star Schema) có TenantID
-- ============================================================

-- 4.4.1. FactSales — Sự kiện Bán hàng (Grain: 1 dòng = 1 sản phẩm / 1 hóa đơn)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactSales')
BEGIN
    CREATE TABLE FactSales (
        SalesKey            BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID            VARCHAR(20)   NOT NULL,          -- FK → Tenants [MỚI]
        DateKey            INT           NOT NULL,           -- FK → DimDate
        ProductKey         INT           NOT NULL,           -- FK → DimProduct
        CustomerKey        INT           NOT NULL,           -- FK → DimCustomer (-1 = Unknown)
        StoreKey           INT           NOT NULL,           -- FK → DimStore
        EmployeeKey        INT           NOT NULL,           -- FK → DimEmployee (-1 = Unknown)
        InvoiceNumber      VARCHAR(50)   NOT NULL,           -- Số hóa đơn (Degenerate Dimension)
        Quantity           SMALLINT      NOT NULL,           -- CHECK > 0
        UnitPrice          DECIMAL(18,2) NOT NULL,
        DiscountAmount     DECIMAL(18,2) NOT NULL DEFAULT 0,
        GrossSalesAmount   DECIMAL(18,2) NOT NULL,           -- Qty × UnitPrice
        NetSalesAmount     DECIMAL(18,2) NOT NULL,           -- Gross - Discount
        CostAmount        DECIMAL(18,2) NOT NULL,           -- Qty × UnitCostPrice
        GrossProfitAmount DECIMAL(18,2) NOT NULL,           -- Net - Cost
        TaxAmount         DECIMAL(18,2) NOT NULL DEFAULT 0, -- Thuế VAT
        PaymentMethodKey  INT           NULL,               -- FK → DimPaymentMethod
        SalesChannel      VARCHAR(20)   NOT NULL DEFAULT 'InStore',
        ReturnFlag        BIT           NOT NULL DEFAULT 0,  -- 1 = Hoàn trả
        LoadDatetime      DATETIME2     NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_FactSales_Tenant   FOREIGN KEY (TenantID)   REFERENCES Tenants(TenantID),
        CONSTRAINT FK_FactSales_Date     FOREIGN KEY (DateKey)     REFERENCES DimDate(DateKey),
        CONSTRAINT FK_FactSales_Product  FOREIGN KEY (ProductKey)  REFERENCES DimProduct(ProductKey),
        CONSTRAINT FK_FactSales_Customer FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
        CONSTRAINT FK_FactSales_Store    FOREIGN KEY (StoreKey)    REFERENCES DimStore(StoreKey),
        CONSTRAINT FK_FactSales_Employee FOREIGN KEY (EmployeeKey) REFERENCES DimEmployee(EmployeeKey),
        CONSTRAINT FK_FactSales_Payment   FOREIGN KEY (PaymentMethodKey) REFERENCES DimPaymentMethod(PaymentMethodKey),
        CONSTRAINT CHK_Quantity CHECK (Quantity > 0)
    );
    PRINT 'Created: FactSales';
END

-- 4.4.2. FactInventory — Sự kiện Tồn kho (Grain: 1 sản phẩm / 1 cửa hàng / 1 ngày)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactInventory')
BEGIN
    CREATE TABLE FactInventory (
        InventoryKey       BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID          VARCHAR(20)   NOT NULL,           -- FK → Tenants [MỚI]
        DateKey           INT           NOT NULL,            -- FK → DimDate — Ngày chụp ảnh tồn kho
        ProductKey        INT           NOT NULL,            -- FK → DimProduct
        StoreKey          INT           NOT NULL,            -- FK → DimStore
        SupplierKey       INT           NULL,                -- FK → DimSupplier
        OpeningStock      INT           NOT NULL DEFAULT 0,   -- Tồn đầu ngày
        ClosingStock      INT           NOT NULL DEFAULT 0,   -- Tồn cuối ngày
        StockReceived     INT           NOT NULL DEFAULT 0,   -- Nhập trong ngày
        StockSold         INT           NOT NULL DEFAULT 0,   -- Bán trong ngày
        StockAdjusted     INT           NOT NULL DEFAULT 0,   -- Điều chỉnh (mất mát, hỏng)
        ReorderPoint      INT           NULL,                -- Mức tồn tối thiểu
        UnitCost          DECIMAL(18,2) NOT NULL,
        TotalInventoryValue DECIMAL(18,2) NOT NULL,         -- ClosingStock × UnitCost
        LoadDatetime      DATETIME2     NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_FactInventory_Tenant  FOREIGN KEY (TenantID)  REFERENCES Tenants(TenantID),
        CONSTRAINT FK_FactInventory_Date    FOREIGN KEY (DateKey)    REFERENCES DimDate(DateKey),
        CONSTRAINT FK_FactInventory_Product FOREIGN KEY (ProductKey) REFERENCES DimProduct(ProductKey),
        CONSTRAINT FK_FactInventory_Store   FOREIGN KEY (StoreKey)   REFERENCES DimStore(StoreKey),
        CONSTRAINT FK_FactInventory_Supplier FOREIGN KEY (SupplierKey) REFERENCES DimSupplier(SupplierKey)
    );
    PRINT 'Created: FactInventory';
END

-- 4.4.3. FactPurchase — Sự kiện Nhập hàng
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactPurchase')
BEGIN
    CREATE TABLE FactPurchase (
        PurchaseKey         BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID           VARCHAR(20)   NOT NULL,           -- FK → Tenants [MỚI]
        DateKey            INT           NOT NULL,            -- FK → DimDate — Ngày nhập hàng
        ProductKey         INT           NOT NULL,            -- FK → DimProduct
        SupplierKey        INT           NOT NULL,            -- FK → DimSupplier
        StoreKey           INT           NOT NULL,            -- FK → DimStore — Kho nhận hàng
        PurchaseOrderNo    VARCHAR(50)   NOT NULL,            -- Số phiếu đặt hàng (DD)
        QuantityOrdered    INT           NOT NULL,
        QuantityReceived   INT           NOT NULL,
        UnitPurchasePrice  DECIMAL(18,2) NOT NULL,
        TotalPurchaseAmount DECIMAL(18,2) NOT NULL,
        LeadTime_Days      SMALLINT      NULL,                -- Thời gian giao hàng thực tế
        LoadDatetime       DATETIME2     NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_FactPurchase_Tenant  FOREIGN KEY (TenantID)  REFERENCES Tenants(TenantID),
        CONSTRAINT FK_FactPurchase_Date    FOREIGN KEY (DateKey)    REFERENCES DimDate(DateKey),
        CONSTRAINT FK_FactPurchase_Product FOREIGN KEY (ProductKey) REFERENCES DimProduct(ProductKey),
        CONSTRAINT FK_FactPurchase_Supplier FOREIGN KEY (SupplierKey) REFERENCES DimSupplier(SupplierKey),
        CONSTRAINT FK_FactPurchase_Store   FOREIGN KEY (StoreKey)   REFERENCES DimStore(StoreKey)
    );
    PRINT 'Created: FactPurchase';
END

PRINT 'Done: 03_create_facts.sql';
