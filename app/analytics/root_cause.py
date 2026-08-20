import pandas as pd
from sqlalchemy import text

from app.database.connection import engine


def analyze_category_change(
    previous_month: str,
    current_month: str
):
    """
    Compare category-level revenue between two months.
    """

    query = text("""
        SELECT
            p.category,

            SUM(
                CASE
                    WHEN DATE_TRUNC('month', o.order_date)
                         = DATE_TRUNC(
                             'month',
                             CAST(:previous_month AS DATE)
                         )
                    THEN oi.revenue
                    ELSE 0
                END
            ) AS previous_revenue,

            SUM(
                CASE
                    WHEN DATE_TRUNC('month', o.order_date)
                         = DATE_TRUNC(
                             'month',
                             CAST(:current_month AS DATE)
                         )
                    THEN oi.revenue
                    ELSE 0
                END
            ) AS current_revenue

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        JOIN products p
            ON oi.product_id = p.product_id

        WHERE DATE_TRUNC('month', o.order_date)
              IN (
                  DATE_TRUNC(
                      'month',
                      CAST(:previous_month AS DATE)
                  ),

                  DATE_TRUNC(
                      'month',
                      CAST(:current_month AS DATE)
                  )
              )

        GROUP BY p.category
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "previous_month": previous_month,
                "current_month": current_month
            }
        )

        df = pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

    if df.empty:
        return df

    # -----------------------------------------------------
    # Convert numeric values
    # -----------------------------------------------------

    df["previous_revenue"] = pd.to_numeric(
        df["previous_revenue"]
    )

    df["current_revenue"] = pd.to_numeric(
        df["current_revenue"]
    )

    # -----------------------------------------------------
    # Calculate revenue change
    # -----------------------------------------------------

    df["revenue_change"] = (
        df["current_revenue"]
        - df["previous_revenue"]
    )

    # -----------------------------------------------------
    # Calculate percentage change
    # -----------------------------------------------------

    df["revenue_change_percent"] = 0.0

    mask = df["previous_revenue"] != 0

    df.loc[mask, "revenue_change_percent"] = (
        df.loc[mask, "revenue_change"]
        / df.loc[mask, "previous_revenue"]
        * 100
    )

    # -----------------------------------------------------
    # Sort biggest decline first
    # -----------------------------------------------------

    df = df.sort_values(
        "revenue_change"
    )

    return df


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    previous_month = "2025-08-01"
    current_month = "2025-09-01"

    print("=" * 60)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 60)

    print(
        f"\nComparing "
        f"{previous_month} → {current_month}"
    )

    df = analyze_category_change(
        previous_month,
        current_month
    )

    if df.empty:

        print("\nNo category data found.")

    else:

        print("\nCategory Revenue Changes:")
        print("-" * 60)

        print(
            df.to_string(index=False)
        )

        # -------------------------------------------------
        # Biggest category declines
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("BIGGEST CATEGORY DECLINES")
        print("=" * 60)

        declines = df[
            df["revenue_change"] < 0
        ]

        if declines.empty:

            print(
                "\nNo category experienced "
                "a revenue decline."
            )

        else:

            print(
                declines.head(5)
                .to_string(index=False)
            )

        # -------------------------------------------------
        # Biggest driver
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("BIGGEST REVENUE DRIVER")
        print("=" * 60)

        biggest_driver = df.iloc[0]

        print(
            f"\nCategory: "
            f"{biggest_driver['category']}"
        )

        print(
            f"Previous revenue: "
            f"{biggest_driver['previous_revenue']:,.2f}"
        )

        print(
            f"Current revenue: "
            f"{biggest_driver['current_revenue']:,.2f}"
        )

        print(
            f"Revenue change: "
            f"{biggest_driver['revenue_change']:,.2f}"
        )

        print(
            f"Percentage change: "
            f"{biggest_driver['revenue_change_percent']:.2f}%"
        )