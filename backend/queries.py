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
ORDER BY clv.CLVScore DESC;
"""

RMO_CUSTOMER_COUNTS_SQL = """
SELECT
    r.RmoName,
    COUNT(*) AS CustomerCount
FROM dbo.DimCustomer c
JOIN dbo.DimRMO r ON r.RmoId = c.PrimaryRmoId
GROUP BY r.RmoName
ORDER BY CustomerCount DESC;
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
WHERE c.CIF = %s;
"""


def high_churn_risk(limit: int):
    return run_query(HIGH_CHURN_RISK_SQL, (limit,))


def high_clv(limit: int):
    return run_query(HIGH_CLV_SQL, (limit,))


def rmo_customer_counts():
    return run_query(RMO_CUSTOMER_COUNTS_SQL)


def customer_by_cif(cif: str):
    rows = run_query(CUSTOMER_BY_CIF_SQL, (cif,))
    return rows[0] if rows else None
