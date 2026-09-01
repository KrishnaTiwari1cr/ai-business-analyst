import pandas as pd

from sqlalchemy import text

from app.database.connection import engine


# =========================================================
# GET MONTHLY REVENUE
# =========================================================

def get_monthly_revenue():
    """
    Get total revenue for every month.
    """

    query = text("""
        SELECT
            DATE_TRUNC(
                'month',
                o.order_date
            )::DATE AS month,
            SUM(oi.revenue) AS revenue

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        GROUP BY
            DATE_TRUNC('month', o.order_date)

        ORDER BY
            month;
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query
        )

        df = pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

    if df.empty:
        return df

    # Convert revenue to numeric
    df["revenue"] = pd.to_numeric(
        df["revenue"]
    )

    # Normalize to timezone-naive month dates for consistent filtering
    df["month"] = pd.to_datetime(
        df["month"],
        utc=False
    ).dt.normalize()

    return df


# =========================================================
# COMPARE MONTHS
# =========================================================

def compare_months(
    df: pd.DataFrame
):
    """
    Compare every month with
    the previous month.
    """

    if df.empty:
        return df

    df = df.copy()

    # The database query is ordered, but sort explicitly before
    # calculating the prior month so LAG-equivalent logic is never
    # affected by a changed query order.
    df = df.sort_values("month").reset_index(drop=True)

    # Previous month's revenue
    df["previous_revenue"] = (
        df["revenue"].shift(1)
    )

    # Absolute change
    df["revenue_change"] = (
        df["revenue"]
        - df["previous_revenue"]
    )

    # Percentage change
    df["revenue_change_percent"] = 0.0

    mask = (
        df["previous_revenue"]
        != 0
    )

    df.loc[
        mask,
        "revenue_change_percent"
    ] = (
        df.loc[
            mask,
            "revenue_change"
        ]
        /
        df.loc[
            mask,
            "previous_revenue"
        ]
        * 100
    )

    return df


# =========================================================
# FIND BIGGEST DROP
# =========================================================

def find_biggest_drop(
    df: pd.DataFrame
):
    """
    Find the month with the
    largest percentage revenue decline.
    """

    if df.empty:
        return None

    valid_df = df.dropna(
        subset=[
            "revenue_change_percent"
        ]
    )

    if valid_df.empty:
        return None

    drops = valid_df[
        valid_df[
            "revenue_change_percent"
        ] < 0
    ]

    if drops.empty:
        return None

    biggest_drop = drops.loc[
        drops[
            "revenue_change_percent"
        ].idxmin()
    ]

    return biggest_drop


def find_biggest_increase(
    df: pd.DataFrame
):
    """Find the month with the largest percentage revenue increase."""

    if df.empty:
        return None

    valid_df = df.dropna(
        subset=["revenue_change_percent"]
    )

    increases = valid_df[
        valid_df["revenue_change_percent"] > 0
    ]

    if increases.empty:
        return None

    return increases.loc[
        increases["revenue_change_percent"].idxmax()
    ]


# =========================================================
# GET SPECIFIC MONTH
# =========================================================

def get_month_comparison(
    df: pd.DataFrame,
    month: int,
    year: int = None
):
    """
    Find a specific month in the dataset.

    Example:

    month = 9
    year = 2025

    Returns September 2025 row.
    """

    if df.empty:
        return None

    working_df = df.copy()

    # -----------------------------------------------------
    # Filter year if supplied
    # -----------------------------------------------------

    if year is not None:

        working_df = working_df[
            working_df[
                "month"
            ].dt.year == year
        ]

    # -----------------------------------------------------
    # Filter month
    # -----------------------------------------------------

    working_df = working_df[
        working_df[
            "month"
        ].dt.month == month
    ]

    if working_df.empty:
        return None

    return working_df.iloc[0]


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MONTHLY REVENUE ANALYSIS")
    print("=" * 60)

    df = get_monthly_revenue()

    if df.empty:

        print(
            "\nNo monthly revenue data found."
        )

    else:

        df = compare_months(
            df
        )

        print("\nMonthly Revenue:")
        print("-" * 60)

        print(
            df.to_string(
                index=False
            )
        )

        # -------------------------------------------------
        # Biggest drop
        # -------------------------------------------------

        biggest_drop = find_biggest_drop(
            df
        )

        print("\n" + "=" * 60)
        print("BIGGEST REVENUE DROP")
        print("=" * 60)

        if biggest_drop is None:

            print(
                "\nNo revenue drop detected."
            )

        else:

            month = biggest_drop[
                "month"
            ].strftime(
                "%B %Y"
            )

            print(
                f"\nMonth: {month}"
            )

            print(
                f"Previous revenue: "
                f"{biggest_drop['previous_revenue']:,.2f}"
            )

            print(
                f"Current revenue: "
                f"{biggest_drop['revenue']:,.2f}"
            )

            print(
                f"Revenue change: "
                f"{biggest_drop['revenue_change']:,.2f}"
            )

            print(
                f"Percentage change: "
                f"{biggest_drop['revenue_change_percent']:.2f}%"
            )
