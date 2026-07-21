SET NOCOUNT ON;
GO

IF DB_ID('ML_HUB_DEMO') IS NULL
BEGIN
    CREATE DATABASE ML_HUB_DEMO;
END
GO

USE ML_HUB_DEMO;
GO

IF OBJECT_ID('dbo.FactCustomerLending','U') IS NOT NULL DROP TABLE dbo.FactCustomerLending;
IF OBJECT_ID('dbo.FactFraudSignal','U') IS NOT NULL DROP TABLE dbo.FactFraudSignal;
IF OBJECT_ID('dbo.FactCustomerRecommendation','U') IS NOT NULL DROP TABLE dbo.FactCustomerRecommendation;
IF OBJECT_ID('dbo.FactCustomerCLV','U') IS NOT NULL DROP TABLE dbo.FactCustomerCLV;
IF OBJECT_ID('dbo.FactCustomerSegmentScore','U') IS NOT NULL DROP TABLE dbo.FactCustomerSegmentScore;
IF OBJECT_ID('dbo.FactCustomerEngagement','U') IS NOT NULL DROP TABLE dbo.FactCustomerEngagement;
IF OBJECT_ID('dbo.FactCustomerAccount','U') IS NOT NULL DROP TABLE dbo.FactCustomerAccount;
IF OBJECT_ID('dbo.DimCustomer','U') IS NOT NULL DROP TABLE dbo.DimCustomer;
IF OBJECT_ID('dbo.DimRMO','U') IS NOT NULL DROP TABLE dbo.DimRMO;
IF OBJECT_ID('dbo.DimBranch','U') IS NOT NULL DROP TABLE dbo.DimBranch;
IF OBJECT_ID('dbo.DimProduct','U') IS NOT NULL DROP TABLE dbo.DimProduct;
GO

CREATE TABLE dbo.DimBranch (
    BranchId INT IDENTITY(1,1) PRIMARY KEY,
    BranchCode NVARCHAR(10) NOT NULL UNIQUE,
    BranchName NVARCHAR(100) NOT NULL,
    Region NVARCHAR(50) NOT NULL,
    City NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.DimRMO (
    RmoId INT IDENTITY(1,1) PRIMARY KEY,
    RmoCode NVARCHAR(10) NOT NULL UNIQUE,
    RmoName NVARCHAR(100) NOT NULL,
    Team NVARCHAR(50) NOT NULL,
    Region NVARCHAR(50) NOT NULL,
    JoinDate DATE NOT NULL
);

CREATE TABLE dbo.DimProduct (
    ProductId INT IDENTITY(1,1) PRIMARY KEY,
    ProductCode NVARCHAR(20) NOT NULL UNIQUE,
    ProductName NVARCHAR(150) NOT NULL,
    ProductCategory NVARCHAR(50) NOT NULL,
    ProductFamily NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.DimCustomer (
    CustomerId INT IDENTITY(1,1) PRIMARY KEY,
    CIF NVARCHAR(12) NOT NULL UNIQUE,
    CustomerName NVARCHAR(150) NOT NULL,
    CustomerType NVARCHAR(20) NOT NULL,
    Segment NVARCHAR(30) NOT NULL,
    Gender NVARCHAR(10) NOT NULL,
    Age INT NOT NULL,
    Region NVARCHAR(50) NOT NULL,
    BranchId INT NULL,
    PrimaryRmoId INT NULL,
    CreatedDate DATE NOT NULL,
    CustomerStatus NVARCHAR(20) NOT NULL,
    CONSTRAINT FK_DimCustomer_DimBranch FOREIGN KEY (BranchId) REFERENCES dbo.DimBranch(BranchId),
    CONSTRAINT FK_DimCustomer_DimRMO FOREIGN KEY (PrimaryRmoId) REFERENCES dbo.DimRMO(RmoId)
);

CREATE TABLE dbo.FactCustomerAccount (
    AccountId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    AccountNumber NVARCHAR(20) NOT NULL UNIQUE,
    AccountType NVARCHAR(30) NOT NULL,
    Balance DECIMAL(15,2) NOT NULL,
    AccountStatus NVARCHAR(20) NOT NULL,
    OpenDate DATE NOT NULL,
    ProductId INT NOT NULL,
    CONSTRAINT FK_FactCustomerAccount_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId),
    CONSTRAINT FK_FactCustomerAccount_DimProduct FOREIGN KEY (ProductId) REFERENCES dbo.DimProduct(ProductId)
);

CREATE TABLE dbo.FactCustomerSegmentScore (
    CustomerId INT NOT NULL,
    ModelName NVARCHAR(100) NOT NULL,
    Score DECIMAL(8,4) NOT NULL,
    ModelDate DATE NOT NULL,
    PredictedChurn BIT NOT NULL,
    SegmentName NVARCHAR(50) NOT NULL,
    RiskBand NVARCHAR(20) NOT NULL,
    Explanation NVARCHAR(250) NOT NULL,
    CONSTRAINT PK_FactCustomerSegmentScore PRIMARY KEY (CustomerId, ModelName, ModelDate),
    CONSTRAINT FK_FactCustomerSegmentScore_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId)
);

CREATE TABLE dbo.FactCustomerCLV (
    CustomerId INT NOT NULL,
    CLVScore DECIMAL(12,2) NOT NULL,
    CLVBand NVARCHAR(20) NOT NULL,
    CLVSegment NVARCHAR(30) NOT NULL,
    ModelDate DATE NOT NULL,
    CONSTRAINT PK_FactCustomerCLV PRIMARY KEY (CustomerId, ModelDate),
    CONSTRAINT FK_FactCustomerCLV_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId)
);

CREATE TABLE dbo.FactCustomerRecommendation (
    RecommendationId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    RecommendationType NVARCHAR(60) NOT NULL,
    ProductId INT NOT NULL,
    Score DECIMAL(8,4) NOT NULL,
    RecommendationDate DATE NOT NULL,
    Channel NVARCHAR(30) NOT NULL,
    PriorityScore DECIMAL(8,4) NOT NULL,
    CONSTRAINT FK_FactCustomerRecommendation_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId),
    CONSTRAINT FK_FactCustomerRecommendation_DimProduct FOREIGN KEY (ProductId) REFERENCES dbo.DimProduct(ProductId)
);

CREATE TABLE dbo.FactFraudSignal (
    CustomerId INT NOT NULL,
    FraudRiskScore DECIMAL(8,4) NOT NULL,
    FraudFlag BIT NOT NULL,
    AlertLevel NVARCHAR(20) NOT NULL,
    ModelDate DATE NOT NULL,
    CONSTRAINT PK_FactFraudSignal PRIMARY KEY (CustomerId, ModelDate),
    CONSTRAINT FK_FactFraudSignal_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId)
);

CREATE TABLE dbo.FactCustomerLending (
    CustomerId INT NOT NULL,
    LendingModelScore DECIMAL(8,4) NOT NULL,
    Eligible BIT NOT NULL,
    ApprovedLimit DECIMAL(12,2) NOT NULL,
    ModelDate DATE NOT NULL,
    CONSTRAINT PK_FactCustomerLending PRIMARY KEY (CustomerId, ModelDate),
    CONSTRAINT FK_FactCustomerLending_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId)
);

CREATE TABLE dbo.FactCustomerEngagement (
    EngagementId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    EngagementDate DATE NOT NULL,
    Channel NVARCHAR(30) NOT NULL,
    EventType NVARCHAR(60) NOT NULL,
    EventValue DECIMAL(12,2) NOT NULL,
    ContactOutcome NVARCHAR(40) NOT NULL,
    CONSTRAINT FK_FactCustomerEngagement_DimCustomer FOREIGN KEY (CustomerId) REFERENCES dbo.DimCustomer(CustomerId)
);

CREATE INDEX IX_DimCustomer_Type_Segment ON dbo.DimCustomer(CustomerType, Segment);
CREATE INDEX IX_DimCustomer_Branch ON dbo.DimCustomer(BranchId);
CREATE INDEX IX_DimCustomer_RMO ON dbo.DimCustomer(PrimaryRmoId);
CREATE INDEX IX_FactCustomerAccount_Customer ON dbo.FactCustomerAccount(CustomerId);
CREATE INDEX IX_FactCustomerSegmentScore_Risk ON dbo.FactCustomerSegmentScore(PredictedChurn, RiskBand);
CREATE INDEX IX_FactCustomerRecommendation_Customer ON dbo.FactCustomerRecommendation(CustomerId);
CREATE INDEX IX_FactCustomerEngagement_Customer ON dbo.FactCustomerEngagement(CustomerId);
GO

PRINT 'Schema created successfully.';
GO

INSERT INTO dbo.DimBranch (BranchCode, BranchName, Region, City) VALUES
('LAG001','Lagos Island','Lagos','Lagos'),
('LAG002','Victoria Island','Lagos','Lagos'),
('LAG003','Ikeja','Lagos','Lagos'),
('PHC001','Port Harcourt','Rivers','Port Harcourt'),
('ABJ001','Garki','Abuja','Abuja'),
('KDG001','Kano','Kano','Kano'),
('ENU001','Enugu','Enugu','Enugu'),
('IBD001','Ikeja GRA','Lagos','Lagos'),
('RIV001','Trans Amadi','Rivers','Port Harcourt'),
('KAD001','Kaduna','Kaduna','Kaduna'),
('BEN001','GRA Benin','Edo','Benin City'),
('ONI001','Onitsha','Anambra','Onitsha'),
('ABA001','Aba','Abia','Aba'),
('JOS001','Jos','Plateau','Jos'),
('MIN001','Mina','Niger','Minna'),
('OWE001','Owerri','Imo','Owerri'),
('ILO001','Ilo','Ogun','Abeokuta'),
('YOL001','Yola','Adamawa','Yola'),
('AKW001','Akwa','Akwa Ibom','Uyo'),
('LOS001','Lekki','Lagos','Lagos'),
('KAD002','Kafanchan','Kaduna','Kaduna'),
('RIV002','Mile 3','Rivers','Port Harcourt'),
('ABJ002','Wuse','Abuja','Abuja'),
('LAG004','Surulere','Lagos','Lagos'),
('NSE001','Nsukka','Enugu','Nsukka'),
('CAL001','Calabar','Cross River','Calabar'),
('MAK001','Makurdi','Benue','Makurdi'),
('JAL001','Jalingo','Taraba','Jalingo'),
('ZAR001','Zaria','Kaduna','Zaria');
GO

;WITH n AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM n WHERE n < 200
)
INSERT INTO dbo.DimRMO (RmoCode, RmoName, Team, Region, JoinDate)
SELECT
    CONCAT('RMO', RIGHT('000' + CAST(n AS NVARCHAR(3)), 3)),
    CONCAT('Relationship Manager ', n),
    CASE
        WHEN n % 4 = 0 THEN 'Corporate'
        WHEN n % 4 = 1 THEN 'Retail'
        WHEN n % 4 = 2 THEN 'SME'
        ELSE 'Priority'
    END,
    CASE n % 6
        WHEN 0 THEN 'Lagos'
        WHEN 1 THEN 'Abuja'
        WHEN 2 THEN 'Port Harcourt'
        WHEN 3 THEN 'Kano'
        WHEN 4 THEN 'Enugu'
        ELSE 'Kaduna'
    END,
    DATEADD(MONTH, -((n % 60)), CAST(GETDATE() AS DATE))
FROM n
OPTION (MAXRECURSION 0);
GO

INSERT INTO dbo.DimProduct (ProductCode, ProductName, ProductCategory, ProductFamily) VALUES
('SAV001','Classic Savings','Deposit','Savings'),
('SAV002','Salary Current Account','Deposit','Current Accounts'),
('CRD001','Platinum Credit Card','Credit','Cards'),
('LON001','SME Working Capital Loan','Lending','SME Loans'),
('LON002','Retail Personal Loan','Lending','Retail Loans'),
('INV001','Treasury Fixed Deposit','Investment','Fixed Deposit'),
('INS001','Life Insurance Cover','Insurance','Protection'),
('DIG001','Mobile Banking Premium','Digital','Digital Services');
GO

;WITH n AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM n WHERE n < 100000
)
INSERT INTO dbo.DimCustomer (
    CIF, CustomerName, CustomerType, Segment, Gender, Age, Region, BranchId, PrimaryRmoId, CreatedDate, CustomerStatus
)
SELECT
    CASE
        WHEN n % 3 = 0 THEN CONCAT('C', RIGHT('000000000' + CAST(n AS NVARCHAR(9)), 9))
        WHEN n % 3 = 1 THEN CONCAT('R', RIGHT('000000000' + CAST(n AS NVARCHAR(9)), 9))
        ELSE CONCAT('S', RIGHT('000000000' + CAST(n AS NVARCHAR(9)), 9))
    END,
    CONCAT('Customer ', n),
    CASE
        WHEN n % 3 = 0 THEN 'Corporate'
        WHEN n % 3 = 1 THEN 'Retail'
        ELSE 'SME'
    END,
    CASE
        WHEN n % 3 = 0 THEN CASE WHEN n % 4 = 0 THEN 'Large Corporate' WHEN n % 4 = 1 THEN 'Mid Corporate' ELSE 'SME Corporate' END
        WHEN n % 3 = 1 THEN CASE WHEN n % 4 = 0 THEN 'Mass Retail' WHEN n % 4 = 1 THEN 'Premium Retail' ELSE 'Youth Retail' END
        ELSE CASE WHEN n % 4 = 0 THEN 'Growth SME' WHEN n % 4 = 1 THEN 'Manufacturing SME' ELSE 'Service SME' END
    END,
    CASE WHEN n % 2 = 0 THEN 'Female' ELSE 'Male' END,
    22 + ((n + 7) % 45),
    CASE n % 8
        WHEN 0 THEN 'Lagos'
        WHEN 1 THEN 'Abuja'
        WHEN 2 THEN 'Port Harcourt'
        WHEN 3 THEN 'Kano'
        WHEN 4 THEN 'Enugu'
        WHEN 5 THEN 'Kaduna'
        WHEN 6 THEN 'Ibadan'
        ELSE 'Benin'
    END,
    ((n - 1) % 30) + 1,
    ((n - 1) % 200) + 1,
    DATEADD(DAY, -((n % 1800)), CAST(GETDATE() AS DATE)),
    CASE WHEN n % 10 = 0 THEN 'Dormant' ELSE 'Active' END
FROM n
OPTION (MAXRECURSION 0);
GO

INSERT INTO dbo.FactCustomerAccount (
    CustomerId, AccountNumber, AccountType, Balance, AccountStatus, OpenDate, ProductId
)
SELECT
    c.CustomerId,
    CONCAT('ACC', RIGHT('0000000000' + CAST(c.CustomerId AS NVARCHAR(10)), 10)),
    CASE
        WHEN c.CustomerType = 'Corporate' THEN 'Current Account'
        WHEN c.CustomerType = 'Retail' THEN 'Savings Account'
        ELSE 'SME Current Account'
    END,
    ROUND(50000 + ((c.CustomerId % 5000) * 125.5), 2),
    CASE WHEN c.CustomerStatus = 'Dormant' THEN 'Dormant' ELSE 'Active' END,
    DATEADD(DAY, -((c.CustomerId % 1800)), CAST(GETDATE() AS DATE)),
    CASE
        WHEN c.CustomerType = 'Corporate' THEN 2
        WHEN c.CustomerType = 'Retail' THEN 1
        ELSE 4
    END
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactCustomerSegmentScore (
    CustomerId, ModelName, Score, ModelDate, PredictedChurn, SegmentName, RiskBand, Explanation
)
SELECT
    c.CustomerId,
    'Churn_Model',
    ROUND(0.12 + ((c.CustomerId % 800) / 1000.0), 4),
    CAST(GETDATE() AS DATE),
    CASE WHEN ROUND(0.12 + ((c.CustomerId % 800) / 1000.0), 4) > 0.70 THEN 1 ELSE 0 END,
    c.Segment,
    CASE
        WHEN ROUND(0.12 + ((c.CustomerId % 800) / 1000.0), 4) > 0.80 THEN 'High'
        WHEN ROUND(0.12 + ((c.CustomerId % 800) / 1000.0), 4) > 0.50 THEN 'Medium'
        ELSE 'Low'
    END,
    'Customer activity and product utilization trend'
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactCustomerCLV (
    CustomerId, CLVScore, CLVBand, CLVSegment, ModelDate
)
SELECT
    c.CustomerId,
    ROUND(1500 + ((c.CustomerId % 250000) * 1.75), 2),
    CASE
        WHEN ((c.CustomerId % 250000) * 1.75) > 180000 THEN 'High'
        WHEN ((c.CustomerId % 250000) * 1.75) > 90000 THEN 'Medium'
        ELSE 'Low'
    END,
    CASE
        WHEN c.CustomerType = 'Corporate' THEN 'Corporate Value'
        WHEN c.CustomerType = 'Retail' THEN 'Retail Value'
        ELSE 'SME Value'
    END,
    CAST(GETDATE() AS DATE)
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactCustomerRecommendation (
    CustomerId, RecommendationType, ProductId, Score, RecommendationDate, Channel, PriorityScore
)
SELECT
    c.CustomerId,
    CASE WHEN c.CustomerType = 'Retail' THEN 'Next_Best_Product' ELSE 'Cross_Sell' END,
    CASE
        WHEN c.CustomerType = 'Corporate' THEN 3
        WHEN c.CustomerType = 'Retail' THEN 4
        ELSE 5
    END,
    ROUND(0.45 + ((c.CustomerId % 300) / 1000.0), 4),
    CAST(GETDATE() AS DATE),
    CASE WHEN c.CustomerId % 3 = 0 THEN 'Email' WHEN c.CustomerId % 3 = 1 THEN 'SMS' ELSE 'Mobile App' END,
    ROUND(0.55 + ((c.CustomerId % 200) / 1000.0), 4)
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactFraudSignal (
    CustomerId, FraudRiskScore, FraudFlag, AlertLevel, ModelDate
)
SELECT
    c.CustomerId,
    ROUND(0.01 + ((c.CustomerId % 500) / 1000.0), 4),
    CASE WHEN ((c.CustomerId % 500) / 1000.0) > 0.35 THEN 1 ELSE 0 END,
    CASE
        WHEN ((c.CustomerId % 500) / 1000.0) > 0.35 THEN 'High'
        WHEN ((c.CustomerId % 500) / 1000.0) > 0.20 THEN 'Medium'
        ELSE 'Low'
    END,
    CAST(GETDATE() AS DATE)
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactCustomerLending (
    CustomerId, LendingModelScore, Eligible, ApprovedLimit, ModelDate
)
SELECT
    c.CustomerId,
    ROUND(0.30 + ((c.CustomerId % 400) / 1000.0), 4),
    CASE WHEN ((c.CustomerId % 400) / 1000.0) > 0.55 THEN 1 ELSE 0 END,
    ROUND(100000 + ((c.CustomerId % 10000) * 250.0), 2),
    CAST(GETDATE() AS DATE)
FROM dbo.DimCustomer AS c;
GO

INSERT INTO dbo.FactCustomerEngagement (
    CustomerId, EngagementDate, Channel, EventType, EventValue, ContactOutcome
)
SELECT
    c.CustomerId,
    DATEADD(DAY, -((c.CustomerId % 60)), CAST(GETDATE() AS DATE)),
    CASE WHEN c.CustomerId % 3 = 0 THEN 'Call' WHEN c.CustomerId % 3 = 1 THEN 'Email' ELSE 'SMS' END,
    CASE WHEN c.CustomerId % 4 = 0 THEN 'Product Inquiry' WHEN c.CustomerId % 4 = 1 THEN 'Retention Call' ELSE 'Cross Sell' END,
    ROUND(1000 + ((c.CustomerId % 1000) * 2.5), 2),
    CASE WHEN c.CustomerId % 5 = 0 THEN 'Converted' WHEN c.CustomerId % 5 = 1 THEN 'Follow Up' ELSE 'Engaged' END
FROM dbo.DimCustomer AS c;
GO

PRINT '100,000 customer warehouse demo data loaded successfully.';
GO
