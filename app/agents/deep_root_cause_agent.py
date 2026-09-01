from app.llm.llm_client import generate_text


# =========================================================
# QUESTION FOCUS
# =========================================================

def detect_rca_focus(question: str | None) -> str:
    """
    Identify what the user actually asked about so the
    insight answers that question instead of repeating
    a generic revenue-drop writeup.
    """

    if not question:
        return "overall"

    text = question.lower()

    if any(
        keyword in text
        for keyword in (
            "product",
            "sku",
            "item"
        )
    ):
        return "products"

    if any(
        keyword in text
        for keyword in (
            "categor",
            "segment"
        )
    ):
        return "categories"

    return "overall"


def _period_context(
    period_source: str | None,
    previous_month,
    current_month
) -> str:

    if period_source == "largest_decline":
        return (
            f"The user did not name a month. "
            f"The comparison {previous_month} → "
            f"{current_month} was selected automatically "
            f"because it is the largest month-over-month "
            f"revenue decline in the data."
        )

    if period_source == "largest_increase":
        return (
            f"The user did not name a month. "
            f"The comparison {previous_month} → "
            f"{current_month} was selected automatically "
            f"because it is the largest month-over-month "
            f"revenue increase in the data."
        )

    if period_source == "user_specified":
        return (
            f"The user asked about {current_month} "
            f"compared with {previous_month}."
        )

    return (
        f"The comparison period is "
        f"{previous_month} → {current_month}."
    )


def _focus_instructions(focus: str) -> str:

    if focus == "products":
        return """
Answer a PRODUCT-level question.
Lead with the products that drove the largest
absolute revenue change. Mention category only
as supporting context. Do not open with a
generic overall-revenue essay.
"""

    if focus == "categories":
        return """
Answer a CATEGORY-level question.
Lead with the categories that drove the largest
absolute revenue change. Mention products only
as supporting evidence. Do not open with a
generic overall-revenue essay.
"""

    return """
Answer an overall root-cause question.
Explain the revenue movement first, then name
the largest category and product drivers.
"""


# =========================================================
# DEEP ROOT CAUSE ANALYSIS
# =========================================================

def generate_deep_root_cause_insight(
    previous_month,
    current_month,
    previous_total,
    current_total,
    category_df,
    product_df,
    question=None,
    period_source=None,
    focus=None
):
    """
    Generate a deep business root-cause analysis
    that answers the user's specific question.

    Returns:

        insight, provider
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

    user_question = (
        question.strip()
        if question and question.strip()
        else "Why did revenue change between these months?"
    )

    focus = focus or detect_rca_focus(user_question)
    period_note = _period_context(
        period_source,
        previous_month,
        current_month
    )
    focus_note = _focus_instructions(focus)

    prompt = f"""
You are a senior Business Intelligence analyst
performing a deep root-cause analysis.

Your job is to answer THIS user's question using
ONLY the driver data below. Do not write a generic
template that could apply to any question.

=========================================================
USER QUESTION
=========================================================

{user_question}

Question focus: {focus}

{period_note}

{focus_note}

=========================================================
PERIOD AND TOTALS
=========================================================

Previous month: {previous_month}
Current month: {current_month}
Previous revenue: ₹{previous_total:,.2f}
Current revenue: ₹{current_total:,.2f}
Revenue change: ₹{revenue_change:,.2f}
Revenue change percentage: {revenue_change_percent:.2f}%


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

1. The first sentence MUST directly answer the
   user's exact question.
2. Different questions must produce different answers.
   A product question is not a category question.
   A named-month question is not an "overall drop"
   question.
3. Identify the largest relevant drivers for the
   question that was asked.
4. Distinguish absolute revenue change from
   percentage change.
5. Use ONLY the provided data.
6. Do not invent causes such as pricing, demand,
   inventory or customer behavior unless the data
   explicitly supports them.
7. Do not claim causation when the data only shows
   correlation or revenue movement.
8. Use ₹K, ₹M or ₹B for monetary values.
9. Include percentages where useful.
10. Keep the analysis professional and concise.
11. If the period was auto-selected as the largest
    decline, say that clearly.

Use this structure:

Direct Answer:
[One or two sentences that answer the user question.]

Supporting Evidence:
- [Largest relevant driver]
- [Second relevant driver]
- [Third relevant driver if useful]

Context:
[Only the extra overall / category / product context
needed to interpret the answer.]

Business Takeaway:
[One concise takeaway grounded in the evidence.]
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
