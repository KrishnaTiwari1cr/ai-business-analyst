from app.llm.llm_client import generate_text


# =========================================================
# DEEP ROOT CAUSE ANALYSIS
# =========================================================

def generate_deep_root_cause_insight(
    previous_month,
    current_month,
    previous_total,
    current_total,
    category_df,
    product_df
):
    """
    Generate a deep business root-cause analysis.

    Returns:

        insight, provider

    Example:

        (
            "Revenue declined because...",
            "gemini"
        )

    or:

        (
            "Revenue declined because...",
            "groq"
        )
    """

    # =====================================================
    # CALCULATE REVENUE CHANGE
    # =====================================================

    revenue_change = (
        current_total
        - previous_total
    )

    revenue_change_percent = (

        revenue_change
        / previous_total
        * 100

        if previous_total != 0

        else 0
    )


    # =====================================================
    # CONVERT DATAFRAMES TO TEXT
    # =====================================================

    if category_df is not None:

        category_data = (
            category_df.to_string(
                index=False
            )
        )

    else:

        category_data = (
            "No category analysis available."
        )


    if product_df is not None:

        product_data = (
            product_df.to_string(
                index=False
            )
        )

    else:

        product_data = (
            "No product analysis available."
        )


    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
You are a senior Business Intelligence analyst
performing a deep root-cause analysis.

Analyze the revenue change between two months.

PREVIOUS MONTH:

{previous_month}


CURRENT MONTH:

{current_month}


PREVIOUS REVENUE:

₹{previous_total:,.2f}


CURRENT REVENUE:

₹{current_total:,.2f}


REVENUE CHANGE:

₹{revenue_change:,.2f}


REVENUE CHANGE PERCENTAGE:

{revenue_change_percent:.2f}%


=========================================================
CATEGORY ANALYSIS
=========================================================

{category_data}


=========================================================
PRODUCT ANALYSIS
=========================================================

{product_data}


=========================================================
INSTRUCTIONS
=========================================================

1. Explain the overall revenue movement.
2. Identify the largest category-level drivers.
3. Identify the largest product-level drivers.
4. Distinguish absolute revenue decline from percentage decline.
5. Use ONLY the provided data.
6. Do not invent causes such as pricing, demand,
   inventory or customer behavior unless the data
   explicitly supports them.
7. Do not claim causation when the data only shows
   correlation or revenue movement.
8. Use ₹K, ₹M or ₹B for monetary values.
9. Include percentages where useful.
10. Prioritize the largest business impacts.
11. Keep the analysis professional and concise.
12. Make the final takeaway actionable but grounded
    strictly in the available evidence.

Use this structure:

Executive Summary:

Overall Revenue Impact:

Category Drivers:

Product Drivers:

Key Observation:

Business Takeaway:
"""


    # =====================================================
    # CALL GEMINI → GROQ FALLBACK
    # =====================================================

    print(
        "\n🤖 Generating deep root-cause analysis..."
    )

    response, provider = generate_text(
        prompt
    )


    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    insight = response.strip()


    # =====================================================
    # EMPTY RESPONSE CHECK
    # =====================================================

    if not insight:

        raise RuntimeError(
            "AI returned an empty root-cause analysis."
        )


    # =====================================================
    # RESULT
    # =====================================================

    print(
        f"✅ Root-cause analysis generated using: {provider}"
    )

    return insight, provider


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    import pandas as pd


    print("=" * 60)

    print(
        "DEEP ROOT CAUSE ANALYSIS TEST"
    )

    print("=" * 60)


    # =====================================================
    # SAMPLE CATEGORY DATA
    # =====================================================

    category_df = pd.DataFrame({

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

    })


    # =====================================================
    # SAMPLE PRODUCT DATA
    # =====================================================

    product_df = pd.DataFrame({

        "product": [

            "Office Chair 99",

            "Printer 17",

            "Keyboard 56"

        ],

        "category": [

            "Office Supplies",

            "Furniture",

            "Furniture"

        ],

        "revenue_change": [

            -53700,

            -53200,

            -38400

        ],

        "revenue_change_percent": [

            -76.32,

            -73.33,

            -69.70

        ]

    })


    try:

        insight, provider = (
            generate_deep_root_cause_insight(

                previous_month=
                    "August 2025",

                current_month=
                    "September 2025",

                previous_total=
                    2080000,

                current_total=
                    1616100,

                category_df=
                    category_df,

                product_df=
                    product_df
            )
        )


        print(
            "\n" + "=" * 60
        )

        print(
            "ROOT CAUSE ANALYSIS COMPLETE"
        )

        print(
            "=" * 60
        )


        print(
            "\nProvider:"
        )

        print(
            provider
        )


        print(
            "\nRoot Cause Insight:"
        )

        print(
            insight
        )


    except Exception as e:

        print(
            "\n❌ Root-cause generation failed."
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )