# ecommerce-retention-sql
View the Interactive Tableau Dashboard:
https://public.tableau.com/app/profile/sravya.kodavatiganti/viz/Ecommerce_Customer_Retention/E-CommerceCustomerRetentionCohorts#1
 Executive Summary
In e-commerce, **Customer Retention** is often more important than Acquisition. A 5% increase in retention can increase profits by 25-95%.

This project analyzes 500,000+ transaction rows from a UK-based online retailer to identify Cohort Retention Rates. By grouping customers based on their first purchase month (Cohorts), we track how their purchasing behavior changes over time.

Key Findings:
Identified a 15% drop in retention for customers acquired during the holiday season (Q4) compared to Q1.
The average "Month 1" retention rate across all cohorts is ~20%, indicating a need for stronger post-purchase engagement campaigns.

---

Technical Implementation

1. Data Extraction & Cleaning (Python + DuckDB)
Instead of using Excel, I built a reproducible SQL Pipeline using Python and DuckDB to process the raw CSV data.
Removed Cancellations: Filtered out transactions starting with 'C'
Data Parsing:Standardized Date formats and Customer IDs.

2. Advanced SQL Logic (The "Hard" Part)
I used Common Table Expressions (CTEs) and Window Functions to calculate retention. The logic follows these steps:
1.  Cohort Identification: Find the first purchase month for every unique CustomerID.
2.  Activity Tracking: Join transaction logs to the cohort date.
3.  Date Math: Calculate the `month_diff` between the cohort start and the current purchase.
4.  Aggregation: Count active users per cohort, per month.

3. Visualization (Tableau)
Designed a Cohort Heatmap to visualize the density of customer activity.
Color Psychology: Used Orange-Blue diverging scales (Blue = High Retention) to instantly highlight drop-off points.
LOD Calculations: Ensured percentages were calculated against the starting cohort size, not the total population.

---
SQL Logic Snippet
Here is the core SQL logic used to normalize the purchase dates into months (Month 0, 1, 2...):
WITH cohorts AS (
    SELECT 
        CustomerID,
        MIN(date_trunc('month', InvoiceDate)) AS cohort_month
    FROM clean_data
    GROUP BY CustomerID
),
activities AS (
    SELECT 
        c.CustomerID,
        c.cohort_month,
        -- Calculate the difference in months
        date_diff('month', c.cohort_month, date_trunc('month', d.InvoiceDate)) AS month_number
    FROM clean_data d
    JOIN cohorts c ON d.CustomerID = c.CustomerID
)
SELECT 
    cohort_month,
    month_number,
    COUNT(DISTINCT CustomerID) as active_users
FROM activities
GROUP BY 1, 2
ORDER BY 1, 2;

How to Run This Project
1. Clone the Repository
git clone https://github.com/yourusername/ecommerce-retention-sql.git
cd ecommerce-retention-sql
2. Install Dependencies
pip install pandas duckdb
3. Run the SQL Pipeline
This script downloads the raw data, runs the SQL transformation, and outputs a clean CSV.
python run_cohort_sql.py
4. Visualize
Open the resulting tableau_ready_cohorts.csv in Tableau or Power BI.

