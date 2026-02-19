-- ============================================================
--  Telecom Customer Churn Analysis — SQL Queries
--  Author  : Himanshu Kothari
--  Dataset : IBM Watson Telco Customer Churn (Kaggle)
--  Tool    : PostgreSQL / SQLite compatible
-- ============================================================

-- ── 0. CREATE TABLE ─────────────────────────────────────────
CREATE TABLE telco_churn (
    customerID        TEXT PRIMARY KEY,
    gender            TEXT,
    SeniorCitizen     INTEGER,
    Partner           TEXT,
    Dependents        TEXT,
    tenure            INTEGER,
    PhoneService      TEXT,
    MultipleLines     TEXT,
    InternetService   TEXT,
    OnlineSecurity    TEXT,
    OnlineBackup      TEXT,
    DeviceProtection  TEXT,
    TechSupport       TEXT,
    StreamingTV       TEXT,
    StreamingMovies   TEXT,
    Contract          TEXT,
    PaperlessBilling  TEXT,
    PaymentMethod     TEXT,
    MonthlyCharges    REAL,
    TotalCharges      REAL,
    Churn             TEXT
);


-- ── 1. OVERALL CHURN SNAPSHOT ────────────────────────────────
--  Business Question: What is our baseline churn rate?
SELECT
    COUNT(*)                                                AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)         AS churned,
    SUM(CASE WHEN Churn = 'No'  THEN 1 ELSE 0 END)         AS retained,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                           AS avg_monthly_charge,
    ROUND(AVG(tenure), 1)                                   AS avg_tenure_months
FROM telco_churn;


-- ── 2. CHURN RATE BY CONTRACT TYPE ───────────────────────────
--  Business Question: Which contract type is highest risk?
--  Insight: Month-to-month customers churn 6x more than two-year customers
SELECT
    Contract,
    COUNT(*)                                                        AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)                 AS churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                                   AS avg_monthly_charges
FROM telco_churn
GROUP BY Contract
ORDER BY churn_rate_pct DESC;


-- ── 3. HIGH-RISK CUSTOMER SEGMENT ────────────────────────────
--  Business Question: Who are the customers most likely to leave?
--  Segment: New month-to-month fiber customers paying high bills
SELECT
    customerID,
    tenure,
    MonthlyCharges,
    Contract,
    InternetService,
    PaymentMethod,
    'HIGH RISK' AS risk_flag
FROM telco_churn
WHERE Churn = 'No'                     -- currently retained
  AND Contract = 'Month-to-month'
  AND InternetService = 'Fiber optic'
  AND tenure < 12
  AND MonthlyCharges > 70
ORDER BY MonthlyCharges DESC
LIMIT 20;


-- ── 4. CHURN RATE BY INTERNET SERVICE ────────────────────────
--  Business Question: Is fiber optic a product quality issue?
SELECT
    InternetService,
    COUNT(*)                                                         AS customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                                    AS avg_monthly_charges,
    ROUND(AVG(tenure), 1)                                            AS avg_tenure_months
FROM telco_churn
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;


-- ── 5. REVENUE AT RISK ────────────────────────────────────────
--  Business Question: What is the monthly revenue impact of churn?
SELECT
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_lost,
    ROUND(SUM(CASE WHEN Churn = 'No'  THEN MonthlyCharges ELSE 0 END), 2) AS monthly_revenue_retained,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
          / SUM(MonthlyCharges), 2)                                        AS revenue_at_risk_pct
FROM telco_churn;


-- ── 6. TENURE COHORT ANALYSIS ─────────────────────────────────
--  Business Question: At what tenure stage is churn highest?
SELECT
    CASE
        WHEN tenure BETWEEN 0  AND 12 THEN '0–12 months  (New)'
        WHEN tenure BETWEEN 13 AND 24 THEN '13–24 months (Growing)'
        WHEN tenure BETWEEN 25 AND 48 THEN '25–48 months (Mature)'
        ELSE '48+ months  (Loyal)'
    END                                                                    AS tenure_cohort,
    COUNT(*)                                                               AS customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                                          AS avg_monthly_charges
FROM telco_churn
GROUP BY tenure_cohort
ORDER BY churn_rate_pct DESC;


-- ── 7. IMPACT OF ADD-ON SERVICES ON CHURN ─────────────────────
--  Business Question: Do value-added services reduce churn?
SELECT
    OnlineSecurity,
    TechSupport,
    COUNT(*)                                                               AS customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM telco_churn
WHERE OnlineSecurity != 'No internet service'
GROUP BY OnlineSecurity, TechSupport
ORDER BY churn_rate_pct DESC;


-- ── 8. PAYMENT METHOD vs CHURN ────────────────────────────────
--  Business Question: Does payment friction drive churn?
SELECT
    PaymentMethod,
    COUNT(*)                                                               AS customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                                          AS avg_bill
FROM telco_churn
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;
