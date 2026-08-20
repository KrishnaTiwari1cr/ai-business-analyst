import os
import json

import pandas as pd

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in .env"
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# FORMAT MONEY
# =========================================================

def format_money(value: float) -> str:
    """
    Convert raw values into business-friendly
    ₹K / ₹M / ₹B format.
    """

    value = float(value)

    sign = "-" if value < 0 else ""

    value = abs(value)

    if value >= 1_000_000_000:
        return f"{sign}₹{value / 1_000_000_000:.2f}B"

    elif value >= 1_000_000:
        return f"{sign}₹{value / 1_000_000:.2f}M"

    elif value >= 1_000:
        return f"{sign}₹{value / 1_000:.1f}K"

    else:
        return f"{sign}₹{value:,.0f}"


# =========================================================
# PREPARE CATEGORY DATA
# =========================================================

def prepare_root_cause_data(
    df: pd.DataFrame,
    previous_month: str,
    current_month: str
):
    """
    Convert category DataFrame into
    JSON-friendly business data.
    """

    records = []

    for _, row in df.iterrows():

        records.append({
            "category": row["category"],

            "previous_revenue": format_money(
                row["previous_revenue"]
            ),

            "current_revenue": format_money(
                row["current_revenue"]
            ),

            "revenue_change": format_money(
                row["revenue_change"]
            ),

            "revenue_change_percent": (
                f"{row['revenue_change_percent']:.2f}%"
            )
        })

    return {
        "previous_month": previous_month,
        "current_month": current_month,
        "categories": records
    }


# =========================================================
# GENERATE FALLBACK INSIGHT
# =========================================================

def generate_fallback_insight(
    previous_month: str,
    current_month: str,
    previous_total: float,
    current_total: float,
    total_change: float,
    total_change_percent: float,
    category_df: pd.DataFrame,
    biggest_driver_category: str,
    biggest_driver_change: float,
    biggest_percentage_category: str,
    biggest_percentage_change: float
):
    """
    Generate a deterministic business insight
    when Gemini is unavailable.
    """

    # -----------------------------------------------------
    # Get declining categories
    # -----------------------------------------------------

    declines = category_df[
        category_df["revenue_change"] < 0
    ].copy()

    # -----------------------------------------------------
    # Build driver list
    # -----------------------------------------------------

    driver_lines = []

    for _, row in declines.head(3).iterrows():

        category = row["category"]

        change = row["revenue_change"]

        percentage = row[
            "revenue_change_percent"
        ]

        driver_lines.append(
            f"- {category}: revenue decreased by "
            f"{format_money(abs(change))} "
            f"({abs(percentage):.2f}%)."
        )

    if not driver_lines:

        driver_lines.append(
            "- No category-level revenue decline was detected."
        )

    drivers = "\n".join(
        driver_lines
    )

    # -----------------------------------------------------
    # Final deterministic insight
    # -----------------------------------------------------

    insight = f"""
Key Finding:
Revenue decreased by {format_money(abs(total_change))}
from {format_money(previous_total)} to
{format_money(current_total)}, representing a
{abs(total_change_percent):.2f}% decline.

Overall Change:
Revenue fell from {format_money(previous_total)}
in {previous_month} to {format_money(current_total)}
in {current_month}.

Main Drivers:
{drivers}

Important Distinction:
{biggest_driver_category} had the largest absolute
revenue impact, decreasing by
{format_money(abs(biggest_driver_change))}.
{biggest_percentage_category} had the largest
percentage decline at
{abs(biggest_percentage_change):.2f}%.

Business Takeaway:
The revenue decline was broad-based across the
analyzed product categories, with
{biggest_driver_category} contributing the largest
absolute decrease.
"""

    return insight.strip()


# =========================================================
# GENERATE ROOT CAUSE INSIGHT
# =========================================================

def generate_root_cause_insight(
    previous_month: str,
    current_month: str,
    previous_total: float,
    current_total: float,
    category_df: pd.DataFrame
):
    """
    Generate an AI explanation for a revenue change.

    If Gemini is unavailable, automatically use
    deterministic business analysis.
    """

    # -----------------------------------------------------
    # Calculate total change
    # -----------------------------------------------------

    total_change = (
        current_total
        - previous_total
    )

    if previous_total != 0:

        total_change_percent = (
            total_change
            / previous_total
            * 100
        )

    else:

        total_change_percent = 0

    # -----------------------------------------------------
    # Prepare category data
    # -----------------------------------------------------

    category_data = prepare_root_cause_data(
        category_df,
        previous_month,
        current_month
    )

    # -----------------------------------------------------
    # Find declining categories
    # -----------------------------------------------------

    declines = category_df[
        category_df["revenue_change"] < 0
    ].copy()

    # -----------------------------------------------------
    # Biggest absolute driver
    # -----------------------------------------------------

    if not declines.empty:

        biggest_absolute_driver = declines.loc[
            declines["revenue_change"].idxmin()
        ]

        biggest_driver_category = str(
            biggest_absolute_driver["category"]
        )

        biggest_driver_change = float(
            biggest_absolute_driver[
                "revenue_change"
            ]
        )

    else:

        biggest_driver_category = "None"

        biggest_driver_change = 0.0

    # -----------------------------------------------------
    # Biggest percentage decline
    # -----------------------------------------------------

    percentage_declines = category_df[
        category_df["revenue_change_percent"] < 0
    ].copy()

    if not percentage_declines.empty:

        biggest_percentage_decline = (
            percentage_declines.loc[
                percentage_declines[
                    "revenue_change_percent"
                ].idxmin()
            ]
        )

        biggest_percentage_category = str(
            biggest_percentage_decline[
                "category"
            ]
        )

        biggest_percentage_change = float(
            biggest_percentage_decline[
                "revenue_change_percent"
            ]
        )

    else:

        biggest_percentage_category = "None"

        biggest_percentage_change = 0.0

    # =====================================================
    # GEMINI PROMPT
    # =====================================================

    prompt = f"""
You are a senior Business Analyst performing
root-cause analysis.

Previous month:
{previous_month}

Current month:
{current_month}

Previous total revenue:
{format_money(previous_total)}

Current total revenue:
{format_money(current_total)}

Total revenue change:
{format_money(total_change)}

Total revenue change percentage:
{total_change_percent:.2f}%


CATEGORY-LEVEL DATA:

{json.dumps(category_data, indent=2)}


BIGGEST ABSOLUTE DRIVER:

Category:
{biggest_driver_category}

Revenue change:
{format_money(biggest_driver_change)}


BIGGEST PERCENTAGE DECLINE:

Category:
{biggest_percentage_category}

Percentage change:
{biggest_percentage_change:.2f}%


Your task is to explain why revenue changed.

STRICT RULES:

1. Use ONLY the provided data.
2. Do not invent causes.
3. Do not claim unsupported reasons.
4. Distinguish absolute impact from percentage decline.
5. Use ₹ with K, M, or B formatting.
6. Never use raw revenue numbers.
7. Use the word "revenue", not "sales volume".
8. Do not mention SQL.
9. Do not mention Python.
10. Do not mention the database.
11. Do not invent customer, region, product, or channel information.
12. Keep the explanation concise.
13. Use "revenue" instead of "sales".
14. Do not describe revenue as sales volume.
15. Base every numerical statement strictly on the supplied data.

Use this exact structure:

Key Finding:
<one or two sentences>

Overall Change:
<explain the total revenue change>

Main Drivers:
- <category and absolute revenue impact>
- <category and absolute revenue impact>
- <category and absolute revenue impact>

Important Distinction:
<explain largest absolute driver versus largest percentage decline>

Business Takeaway:
<one concise sentence>
"""

    # =====================================================
    # TRY GEMINI
    # =====================================================

    try:

        print(
            "\nSending root-cause analysis to Gemini..."
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response.text:

            print(
                "Gemini root-cause response received."
            )

            return response.text.strip()

        print(
            "\n⚠️ Gemini returned an empty response."
        )

    except Exception as e:

        print(
            "\n⚠️ Gemini is temporarily unavailable."
        )

        print(
            "Using deterministic business analysis instead."
        )

        print(
            "Gemini error:",
            e
        )

    # =====================================================
    # FALLBACK
    # =====================================================

    return generate_fallback_insight(
        previous_month=previous_month,
        current_month=current_month,
        previous_total=previous_total,
        current_total=current_total,
        total_change=total_change,
        total_change_percent=total_change_percent,
        category_df=category_df,
        biggest_driver_category=biggest_driver_category,
        biggest_driver_change=biggest_driver_change,
        biggest_percentage_category=biggest_percentage_category,
        biggest_percentage_change=biggest_percentage_change
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Sample data based on your actual result
    # -----------------------------------------------------

    data = {
        "category": [
            "Furniture",
            "Office Supplies",
            "Software",
            "Accessories",
            "Electronics"
        ],

        "previous_revenue": [
            594846.10,
            447507.67,
            300328.89,
            255092.31,
            487053.60
        ],

        "current_revenue": [
            416652.39,
            331701.21,
            197853.60,
            203092.32,
            471634.76
        ],

        "revenue_change": [
            -178193.71,
            -115806.46,
            -102475.29,
            -51999.99,
            -15418.84
        ],

        "revenue_change_percent": [
            -29.956271,
            -25.878095,
            -34.121023,
            -20.384774,
            -3.165738
        ]
    }

    df = pd.DataFrame(data)

    previous_total = 2_084_828.57

    current_total = 1_620_934.28

    print("=" * 60)
    print("AI ROOT CAUSE ANALYSIS")
    print("=" * 60)

    print(
        f"\nRevenue: "
        f"{format_money(previous_total)}"
        f" → "
        f"{format_money(current_total)}"
    )

    print(
        f"\nDecline: "
        f"{format_money(current_total - previous_total)}"
    )

    insight = generate_root_cause_insight(
        previous_month="August 2025",
        current_month="September 2025",
        previous_total=previous_total,
        current_total=current_total,
        category_df=df
    )

    print("\n" + "=" * 60)
    print("ROOT CAUSE INSIGHT")
    print("=" * 60)

    print()
    print(insight)

    print("\n" + "=" * 60)