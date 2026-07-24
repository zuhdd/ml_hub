from db import run_query

HIGH_CHURN_RISK_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    s.Score,
    s.RiskBand
FROM dbo.FactCustomerSegmentScore s
JOIN dbo.DimCustomer c ON c.CustomerId = s.CustomerId
WHERE s.PredictedChurn = 1 AND c.PrimaryRmoId = %s
ORDER BY s.Score DESC;
"""

HIGH_CHURN_RISK_ALL_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    s.Score,
    s.RiskBand
FROM dbo.FactCustomerSegmentScore s
JOIN dbo.DimCustomer c ON c.CustomerId = s.CustomerId
WHERE s.PredictedChurn = 1
ORDER BY s.Score DESC;
"""

HIGH_CLV_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    clv.CLVScore,
    clv.CLVBand
FROM dbo.FactCustomerCLV clv
JOIN dbo.DimCustomer c ON c.CustomerId = clv.CustomerId
WHERE c.PrimaryRmoId = %s
ORDER BY clv.CLVScore DESC;
"""

HIGH_CLV_ALL_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    clv.CLVScore,
    clv.CLVBand
FROM dbo.FactCustomerCLV clv
JOIN dbo.DimCustomer c ON c.CustomerId = clv.CustomerId
ORDER BY clv.CLVScore DESC;
"""

MY_CUSTOMER_COUNT_SQL = """
SELECT
    r.RmoName,
    COUNT(*) AS CustomerCount
FROM dbo.DimCustomer c
JOIN dbo.DimRMO r ON r.RmoId = c.PrimaryRmoId
WHERE c.PrimaryRmoId = %s
GROUP BY r.RmoName;
"""

TOP_RECOMMENDATIONS_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    r.RecommendationType,
    p.ProductName,
    r.Score,
    r.Channel,
    r.PriorityScore
FROM dbo.FactCustomerRecommendation r
JOIN dbo.DimCustomer c ON c.CustomerId = r.CustomerId
JOIN dbo.DimProduct p ON p.ProductId = r.ProductId
WHERE c.PrimaryRmoId = %s
ORDER BY r.PriorityScore DESC;
"""

TOP_RECOMMENDATIONS_BY_TYPE_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    r.RecommendationType,
    p.ProductName,
    r.Score,
    r.Channel,
    r.PriorityScore
FROM dbo.FactCustomerRecommendation r
JOIN dbo.DimCustomer c ON c.CustomerId = r.CustomerId
JOIN dbo.DimProduct p ON p.ProductId = r.ProductId
WHERE c.PrimaryRmoId = %s AND c.CustomerType = %s
ORDER BY r.PriorityScore DESC;
"""

TOP_RECOMMENDATIONS_ALL_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    r.RecommendationType,
    p.ProductName,
    r.Score,
    r.Channel,
    r.PriorityScore
FROM dbo.FactCustomerRecommendation r
JOIN dbo.DimCustomer c ON c.CustomerId = r.CustomerId
JOIN dbo.DimProduct p ON p.ProductId = r.ProductId
ORDER BY r.PriorityScore DESC;
"""

TOP_RECOMMENDATIONS_ALL_BY_TYPE_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    r.RecommendationType,
    p.ProductName,
    r.Score,
    r.Channel,
    r.PriorityScore
FROM dbo.FactCustomerRecommendation r
JOIN dbo.DimCustomer c ON c.CustomerId = r.CustomerId
JOIN dbo.DimProduct p ON p.ProductId = r.ProductId
WHERE c.CustomerType = %s
ORDER BY r.PriorityScore DESC;
"""

LENDING_ELIGIBLE_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    l.LendingModelScore,
    l.Eligible,
    l.ApprovedLimit
FROM dbo.FactCustomerLending l
JOIN dbo.DimCustomer c ON c.CustomerId = l.CustomerId
WHERE l.Eligible = 1 AND c.PrimaryRmoId = %s
ORDER BY l.ApprovedLimit DESC;
"""

LENDING_ELIGIBLE_BY_TYPE_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    l.LendingModelScore,
    l.Eligible,
    l.ApprovedLimit
FROM dbo.FactCustomerLending l
JOIN dbo.DimCustomer c ON c.CustomerId = l.CustomerId
WHERE l.Eligible = 1 AND c.PrimaryRmoId = %s AND c.CustomerType = %s
ORDER BY l.ApprovedLimit DESC;
"""

LENDING_ELIGIBLE_ALL_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    l.LendingModelScore,
    l.Eligible,
    l.ApprovedLimit
FROM dbo.FactCustomerLending l
JOIN dbo.DimCustomer c ON c.CustomerId = l.CustomerId
WHERE l.Eligible = 1
ORDER BY l.ApprovedLimit DESC;
"""

LENDING_ELIGIBLE_ALL_BY_TYPE_SQL = """
SELECT TOP (%d)
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    l.LendingModelScore,
    l.Eligible,
    l.ApprovedLimit
FROM dbo.FactCustomerLending l
JOIN dbo.DimCustomer c ON c.CustomerId = l.CustomerId
WHERE l.Eligible = 1 AND c.CustomerType = %s
ORDER BY l.ApprovedLimit DESC;
"""

CUSTOMER_BY_CIF_SQL = """
SELECT
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    c.CustomerStatus,
    s.Score AS ChurnScore,
    s.RiskBand,
    clv.CLVScore,
    clv.CLVBand,
    f.FraudRiskScore,
    f.AlertLevel,
    l.LendingModelScore,
    l.Eligible AS LendingEligible
FROM dbo.DimCustomer c
LEFT JOIN dbo.FactCustomerSegmentScore s ON s.CustomerId = c.CustomerId
LEFT JOIN dbo.FactCustomerCLV clv ON clv.CustomerId = c.CustomerId
LEFT JOIN dbo.FactFraudSignal f ON f.CustomerId = c.CustomerId
LEFT JOIN dbo.FactCustomerLending l ON l.CustomerId = c.CustomerId
WHERE c.CIF = %s AND c.PrimaryRmoId = %s;
"""

CUSTOMER_BY_CIF_ALL_SQL = """
SELECT
    c.CIF,
    c.CustomerName,
    c.CustomerType,
    c.Segment,
    c.CustomerStatus,
    s.Score AS ChurnScore,
    s.RiskBand,
    clv.CLVScore,
    clv.CLVBand,
    f.FraudRiskScore,
    f.AlertLevel,
    l.LendingModelScore,
    l.Eligible AS LendingEligible
FROM dbo.DimCustomer c
LEFT JOIN dbo.FactCustomerSegmentScore s ON s.CustomerId = c.CustomerId
LEFT JOIN dbo.FactCustomerCLV clv ON clv.CustomerId = c.CustomerId
LEFT JOIN dbo.FactFraudSignal f ON f.CustomerId = c.CustomerId
LEFT JOIN dbo.FactCustomerLending l ON l.CustomerId = c.CustomerId
WHERE c.CIF = %s;
"""

RMO_BY_CODE_SQL = """
SELECT RmoId, RmoCode, RmoName, Team, Region
FROM dbo.DimRMO
WHERE RmoCode = %s;
"""

ALL_RMOS_SQL = """
SELECT
    r.RmoId,
    r.RmoCode,
    r.RmoName,
    r.Team,
    r.Region,
    COUNT(c.CustomerId) AS CustomerCount
FROM dbo.DimRMO r
LEFT JOIN dbo.DimCustomer c ON c.PrimaryRmoId = r.RmoId
GROUP BY r.RmoId, r.RmoCode, r.RmoName, r.Team, r.Region
ORDER BY r.RmoId;
"""


def high_churn_risk(limit: int, rmo_id: int | None = None):
    if rmo_id is not None:
        return run_query(HIGH_CHURN_RISK_SQL, (limit, rmo_id))
    return run_query(HIGH_CHURN_RISK_ALL_SQL, (limit,))


def high_clv(limit: int, rmo_id: int | None = None):
    if rmo_id is not None:
        return run_query(HIGH_CLV_SQL, (limit, rmo_id))
    return run_query(HIGH_CLV_ALL_SQL, (limit,))


def my_customer_count(rmo_id: int | None = None):
    if rmo_id is not None:
        rows = run_query(MY_CUSTOMER_COUNT_SQL, (rmo_id,))
        return rows[0] if rows else {"RmoName": None, "CustomerCount": 0}
    total = run_query("SELECT COUNT(*) AS CustomerCount FROM dbo.DimCustomer;")
    return {"RmoName": "All RMOs (bank-wide)", "CustomerCount": total[0]["CustomerCount"]}


def top_recommendations(limit: int, rmo_id: int | None = None, customer_type: str | None = None):
    if rmo_id is not None and customer_type:
        return run_query(TOP_RECOMMENDATIONS_BY_TYPE_SQL, (limit, rmo_id, customer_type))
    if rmo_id is not None:
        return run_query(TOP_RECOMMENDATIONS_SQL, (limit, rmo_id))
    if customer_type:
        return run_query(TOP_RECOMMENDATIONS_ALL_BY_TYPE_SQL, (limit, customer_type))
    return run_query(TOP_RECOMMENDATIONS_ALL_SQL, (limit,))


def lending_eligible(limit: int, rmo_id: int | None = None, customer_type: str | None = None):
    if rmo_id is not None and customer_type:
        return run_query(LENDING_ELIGIBLE_BY_TYPE_SQL, (limit, rmo_id, customer_type))
    if rmo_id is not None:
        return run_query(LENDING_ELIGIBLE_SQL, (limit, rmo_id))
    if customer_type:
        return run_query(LENDING_ELIGIBLE_ALL_BY_TYPE_SQL, (limit, customer_type))
    return run_query(LENDING_ELIGIBLE_ALL_SQL, (limit,))


def customer_by_cif(cif: str, rmo_id: int | None = None):
    if rmo_id is not None:
        rows = run_query(CUSTOMER_BY_CIF_SQL, (cif, rmo_id))
    else:
        rows = run_query(CUSTOMER_BY_CIF_ALL_SQL, (cif,))
    return rows[0] if rows else None


def rmo_by_code(rmo_code: str):
    rows = run_query(RMO_BY_CODE_SQL, (rmo_code,))
    return rows[0] if rows else None


def all_rmos():
    return run_query(ALL_RMOS_SQL)
