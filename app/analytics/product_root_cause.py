import pandas as pd

from sqlalchemy import text

from app.database.connection import engine


# =========================================================
# PRODUCT-LEVEL ROOT CAUSE ANALYSIS
# =========================================================

def analyze_product_change(
    previous_month: str,
    current_month: str
):
    """
    Compare product-level revenue between two months.

    Returns products sorted by largest revenue decline.
    """

    query = text("""
        SELECT
            p.product_id,
            p.product_name,
            p.category,

            SUM(
                CASE
                    WHEN DATE_TRUNC(
                        'month',
                        o.order_date
                    )
                    =
                    DATE_TRUNC(
                        'month',
                        CAST(:previous_month AS DATE)
                    )
                    THEN oi.revenue
                    ELSE 0
                END
            ) AS previous_revenue,

            SUM(
                CASE
                    WHEN DATE_TRUNC(
                        'month',
                        o.order_date
                    )
                    =
                    DATE_TRUNC(
                        'month',
                        CAST(:current_month AS DATE)
                    )
                    THEN oi.revenue
                    ELSE 0
                END
            ) AS current_revenue

        FROM products p

        JOIN order_items oi
            ON p.product_id = oi.product_id

        JOIN orders o
            ON oi.order_id = o.order_id

        WHERE DATE_TRUNC(
            'month',
            o.order_date
        )
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

        GROUP BY
            p.product_id,
            p.product_name,
            p.category

        ORDER BY
            p.category,
            p.product_name;
    """)

    # =====================================================
    # EXECUTE QUERY
    # =====================================================

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

    # =====================================================
    # CONVERT NUMERIC COLUMNS
    # =====================================================

    df["previous_revenue"] = pd.to_numeric(
        df["previous_revenue"]
    )

    df["current_revenue"] = pd.to_numeric(
        df["current_revenue"]
    )

    # =====================================================
    # REVENUE CHANGE
    # =====================================================

    df["revenue_change"] = (
        df["current_revenue"]
        -
        df["previous_revenue"]
    )

    # =====================================================
    # PERCENTAGE CHANGE
    # =====================================================

    df["revenue_change_percent"] = 0.0

    mask = (
        df["previous_revenue"] != 0
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

    # =====================================================
    # SORT BY BIGGEST ABSOLUTE DECLINE
    # =====================================================

    df = df.sort_values(
        "revenue_change"
    )

    return df


# =========================================================
# FORMAT MONEY
# =========================================================

def format_money(
    value: float
):
    """
    Format revenue using K / M / B.
    """

    value = float(value)

    sign = "-" if value < 0 else ""

    value = abs(value)

    if value >= 1_000_000_000:

        return (
            f"{sign}"
            f"₹{value / 1_000_000_000:.2f}B"
        )

    elif value >= 1_000_000:

        return (
            f"{sign}"
            f"₹{value / 1_000_000:.2f}M"
        )

    elif value >= 1_000:

        return (
            f"{sign}"
            f"₹{value / 1_000:.1f}K"
        )

    else:

        return (
            f"{sign}"
            f"₹{value:,.0f}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    previous_month = "2025-08-01"

    current_month = "2025-09-01"

    print("=" * 60)
    print("PRODUCT ROOT CAUSE ANALYSIS")
    print("=" * 60)

    print(
        f"\nComparing "
        f"{previous_month} → {current_month}"
    )

    df = analyze_product_change(
        previous_month,
        current_month
    )

    if df.empty:

        print(
            "\nNo product data found."
        )

    else:

        print("\nProduct Revenue Changes:")
        print("-" * 60)

        display_df = df.copy()

        display_df[
            "previous_revenue"
        ] = display_df[
            "previous_revenue"
        ].apply(
            format_money
        )

        display_df[
            "current_revenue"
        ] = display_df[
            "current_revenue"
        ].apply(
            format_money
        )

        display_df[
            "revenue_change"
        ] = display_df[
            "revenue_change"
        ].apply(
            format_money
        )

        display_df[
            "revenue_change_percent"
        ] = display_df[
            "revenue_change_percent"
        ].apply(
            lambda x: f"{x:.2f}%"
        )

        print(
            display_df.head(20)
            .to_string(
                index=False
            )
        )

        # =================================================
        # BIGGEST PRODUCT DECLINES
        # =================================================

        print("\n" + "=" * 60)
        print("BIGGEST PRODUCT DECLINES")
        print("=" * 60)

        declines = df[
            df["revenue_change"] < 0
        ]

        if declines.empty:

            print(
                "\nNo product experienced "
                "a revenue decline."
            )

        else:

            for _, row in declines.head(10).iterrows():

                print(
                    f"\n{row['product_name']}"
                )

                print(
                    f"Category: "
                    f"{row['category']}"
                )

                print(
                    f"Revenue change: "
                    f"{format_money(row['revenue_change'])}"
                )

                print(
                    f"Percentage change: "
                    f"{row['revenue_change_percent']:.2f}%"
                )

        # =================================================
        # BIGGEST PRODUCT DRIVER
        # =================================================

        print("\n" + "=" * 60)
        print("BIGGEST PRODUCT DRIVER")
        print("=" * 60)

        biggest = df.iloc[0]

        print(
            f"\nProduct: "
            f"{biggest['product_name']}"
        )

        print(
            f"Category: "
            f"{biggest['category']}"
        )

        print(
            f"Previous revenue: "
            f"{format_money(biggest['previous_revenue'])}"
        )

        print(
            f"Current revenue: "
            f"{format_money(biggest['current_revenue'])}"
        )

        print(
            f"Revenue change: "
            f"{format_money(biggest['revenue_change'])}"
        )

        print(
            f"Percentage change: "
            f"{biggest['revenue_change_percent']:.2f}%"
        )