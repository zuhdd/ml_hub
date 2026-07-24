# ML Hub Demo Data Dictionary

## Overview

This data dictionary describes the warehouse tables created by the SQL script in [sql/ml_hub_warehouse.sql](sql/ml_hub_warehouse.sql).

## Dimension Tables

### DimBranch

| Column | Type | Description |
|---|---|---|
| BranchId | INT | Surrogate key for the branch |
| BranchCode | NVARCHAR(10) | Business code for the branch |
| BranchName | NVARCHAR(100) | Branch name |
| Region | NVARCHAR(50) | Region where the branch is located |
| City | NVARCHAR(50) | City where the branch is located |

### DimRMO

| Column | Type | Description |
|---|---|---|
| RmoId | INT | Surrogate key for the relationship manager |
| RmoCode | NVARCHAR(10) | Business code for the RMO |
| RmoName | NVARCHAR(100) | Full name of the relationship manager |
| Team | NVARCHAR(50) | Team or specialization such as Retail, Corporate, SME |
| Region | NVARCHAR(50) | Region covered by the RMO |
| JoinDate | DATE | Date the RMO joined the bank |

### DimProduct

| Column | Type | Description |
|---|---|---|
| ProductId | INT | Surrogate key for the product |
| ProductCode | NVARCHAR(20) | Business code for the product |
| ProductName | NVARCHAR(150) | Product name |
| ProductCategory | NVARCHAR(50) | Broad product category |
| ProductFamily | NVARCHAR(50) | Product family or grouping |

### DimCustomer

| Column | Type | Description |
|---|---|---|
| CustomerId | INT | Surrogate key for the customer |
| CIF | NVARCHAR(12) | Customer Identification File number |
| CustomerName | NVARCHAR(150) | Customer name |
| CustomerType | NVARCHAR(20) | Customer type such as Retail, Corporate, or SME |
| Segment | NVARCHAR(30) | Business segment assigned to the customer |
| Gender | NVARCHAR(10) | Gender |
| Age | INT | Customer age |
| Region | NVARCHAR(50) | Customer region |
| BranchId | INT | Branch associated with the customer |
| PrimaryRmoId | INT | Primary relationship manager assigned to the customer |
| CreatedDate | DATE | Date the customer record was created |
| CustomerStatus | NVARCHAR(20) | Status such as Active or Dormant |

## Fact Tables

### FactCustomerAccount

| Column | Type | Description |
|---|---|---|
| AccountId | INT | Surrogate key for the account |
| CustomerId | INT | Foreign key to DimCustomer |
| AccountNumber | NVARCHAR(20) | Account number |
| AccountType | NVARCHAR(30) | Type of account |
| Balance | DECIMAL(15,2) | Current account balance |
| AccountStatus | NVARCHAR(20) | Account status |
| OpenDate | DATE | Account opening date |
| ProductId | INT | Foreign key to DimProduct |

### FactCustomerSegmentScore

| Column | Type | Description |
|---|---|---|
| CustomerId | INT | Foreign key to DimCustomer |
| ModelName | NVARCHAR(100) | Name of the scoring model |
| Score | DECIMAL(8,4) | Model score |
| ModelDate | DATE | Date the score was generated |
| PredictedChurn | BIT | Indicator of churn risk |
| SegmentName | NVARCHAR(50) | Segment associated with the score |
| RiskBand | NVARCHAR(20) | Risk category such as Low, Medium, or High |
| Explanation | NVARCHAR(250) | Model explanation text |

### FactCustomerCLV

| Column | Type | Description |
|---|---|---|
| CustomerId | INT | Foreign key to DimCustomer |
| CLVScore | DECIMAL(12,2) | Customer lifetime value score, normalized 0-100 |
| CLVBand | NVARCHAR(20) | CLV band such as Low, Medium, or High |
| CLVSegment | NVARCHAR(30) | CLV segment grouping |
| ModelDate | DATE | Date the CLV score was generated |

### FactCustomerRecommendation

| Column | Type | Description |
|---|---|---|
| RecommendationId | INT | Surrogate key for the recommendation |
| CustomerId | INT | Foreign key to DimCustomer |
| RecommendationType | NVARCHAR(60) | Type of recommendation |
| ProductId | INT | Product linked to the recommendation |
| Score | DECIMAL(8,4) | Recommendation score |
| RecommendationDate | DATE | Date the recommendation was generated |
| Channel | NVARCHAR(30) | Channel used for recommendation delivery |
| PriorityScore | DECIMAL(8,4) | Priority score for the recommendation |

### FactFraudSignal

| Column | Type | Description |
|---|---|---|
| CustomerId | INT | Foreign key to DimCustomer |
| FraudRiskScore | DECIMAL(8,4) | Fraud risk score |
| FraudFlag | BIT | Fraud alert flag |
| AlertLevel | NVARCHAR(20) | Alert severity |
| ModelDate | DATE | Date the fraud score was generated |

### FactCustomerLending

| Column | Type | Description |
|---|---|---|
| CustomerId | INT | Foreign key to DimCustomer |
| LendingModelScore | DECIMAL(8,4) | Lending score |
| Eligible | BIT | Lending eligibility flag (should we offer this customer a loan) |
| ApprovedLimit | DECIMAL(12,2) | Approved lending limit |
| DefaultRiskScore | DECIMAL(8,4) | Risk of default if this customer is lent to (independent of Eligible) |
| Defaulted | BIT | Default outcome flag - synthetic ground truth for a default-risk classifier, ~12% positive rate |
| ModelDate | DATE | Date the lending score was generated |

### FactCustomerEngagement

| Column | Type | Description |
|---|---|---|---|
| EngagementId | INT | Surrogate key for the engagement event |
| CustomerId | INT | Foreign key to DimCustomer |
| EngagementDate | DATE | Date of the engagement event |
| Channel | NVARCHAR(30) | Engagement channel |
| EventType | NVARCHAR(60) | Type of engagement event |
| EventValue | DECIMAL(12,2) | Value associated with the engagement |
| ContactOutcome | NVARCHAR(40) | Outcome of the contact |

## Suggested Starter Queries

### 1. High churn risk customers

```sql
SELECT TOP 20
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    s.Score,
    s.RiskBand
FROM dbo.FactCustomerSegmentScore s
JOIN dbo.DimCustomer c ON c.CustomerId = s.CustomerId
WHERE s.PredictedChurn = 1
ORDER BY s.Score DESC;
```

### 2. High CLV customers by segment

```sql
SELECT TOP 20
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    clv.CLVScore,
    clv.CLVBand
FROM dbo.FactCustomerCLV clv
JOIN dbo.DimCustomer c ON c.CustomerId = clv.CustomerId
ORDER BY clv.CLVScore DESC;
```

### 3. Customers managed by each RMO

```sql
SELECT
    r.RmoName,
    COUNT(*) AS CustomerCount
FROM dbo.DimCustomer c
JOIN dbo.DimRMO r ON r.RmoId = c.PrimaryRmoId
GROUP BY r.RmoName
ORDER BY CustomerCount DESC;
```
