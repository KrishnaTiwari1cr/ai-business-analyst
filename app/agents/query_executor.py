import pandas as pd
from sqlalchemy import text

from app.database.connection import engine
from app.agents.sql_validator import validate_sql


# =========================================================
# EXECUTE SQL QUERY
# =========================================================

def execute_query(sql: str) -> pd.DataFrame:
    """
    Validate and execute a read-only SQL query.

    Returns:
        pandas.DataFrame containing the query results.
    """

    # -----------------------------------------------------
    # STEP 1: Validate SQL
    # -----------------------------------------------------

    is_valid, message = validate_sql(sql)

    if not is_valid:
        raise ValueError(
            f"SQL validation failed: {message}"
        )

    print("SQL validation passed.")


    # -----------------------------------------------------
    # STEP 2: Execute SQL
    # -----------------------------------------------------

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(sql)
            )

            # Convert result into Pandas DataFrame
            df = pd.DataFrame(
                result.fetchall(),
                columns=result.keys()
            )

        return df

    except Exception as e:

        raise RuntimeError(
            f"Database query failed: {str(e)}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_sql = """
        SELECT
            p.category,
            SUM(oi.revenue) AS total_revenue
        FROM products p
        JOIN order_items oi
            ON p.product_id = oi.product_id
        GROUP BY p.category
        ORDER BY total_revenue DESC
        LIMIT 5
    """

    print("=" * 60)
    print("SQL QUERY EXECUTOR TEST")
    print("=" * 60)

    try:

        df = execute_query(test_sql)

        print("\nQuery executed successfully!")

        print("\nResults:")
        print("-" * 60)

        print(df.to_string(index=False))

        print("-" * 60)

        print(
            f"\nRows returned: {len(df)}"
        )

    except Exception as e:

        print("\nERROR:")
        print(e)