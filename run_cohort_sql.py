import duckdb

print(" Running SQL on 'raw_retail_data.csv'...")

# 1. Connect to temporary database
con = duckdb.connect(database=':memory:')

# 2. SQL Query: Load CSV, Clean Data, and Calculate Cohorts
# We use DuckDB's SQL dialect (very similar to Postgres)
sql_query = """
    -- A. Load and Clean Data
    WITH clean_data AS (
        SELECT 
            "Customer ID" AS CustomerID,
            "InvoiceDate" AS InvoiceDate,
            "Invoice" AS InvoiceNo
        FROM read_csv_auto('raw_retail_data.csv') 
        WHERE "Customer ID" IS NOT NULL
        AND "Invoice" NOT LIKE 'C%' -- Exclude cancellations
    ),

    -- B. Find First Purchase Month (Cohort)
    cohorts AS (
        SELECT 
            CustomerID,
            MIN(date_trunc('month', InvoiceDate)) AS cohort_month
        FROM clean_data
        GROUP BY CustomerID
    ),

    -- C. Calculate Activities
    activities AS (
        SELECT 
            c.CustomerID,
            c.cohort_month,
            date_diff('month', c.cohort_month, date_trunc('month', d.InvoiceDate)) AS month_number
        FROM clean_data d
        JOIN cohorts c ON d.CustomerID = c.CustomerID
    ),

    -- D. Pivot Data for Tableau (Wide Format is okay for Heatmaps, but Tall is better. 
    -- We will output Tall format for Tableau)
    cohort_sizes AS (
        SELECT cohort_month, COUNT(DISTINCT CustomerID) as start_count
        FROM cohorts
        GROUP BY cohort_month
    )

    SELECT 
        a.cohort_month,
        s.start_count,
        a.month_number,
        COUNT(DISTINCT a.CustomerID) AS active_users,
        ROUND(COUNT(DISTINCT a.CustomerID) * 100.0 / s.start_count, 1) AS retention_rate
    FROM activities a
    JOIN cohort_sizes s ON a.cohort_month = s.cohort_month
    GROUP BY a.cohort_month, s.start_count, a.month_number
    HAVING a.month_number <= 12 -- Keep only first year
    ORDER BY a.cohort_month, a.month_number;
"""

# 3. Execute and Save to CSV for Tableau
df = con.execute(sql_query).df()
df.to_csv("tableau_ready_cohorts.csv", index=False)
print("SQL Analysis Complete. File 'tableau_ready_cohorts.csv' created.")