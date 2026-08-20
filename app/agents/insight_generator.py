from app.llm.llm_client import generate_text


# =========================================================
# GENERATE BUSINESS INSIGHT
# =========================================================

def generate_insight(
    question,
    sql,
    results,
    analysis
):
    """
    Generate a concise, question-specific business insight.

    The generated response must directly answer the
    user's question before providing supporting evidence.
    """

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
You are a senior Business Intelligence analyst.

Your job is to answer the user's business question using
ONLY the database results and analysis provided below.

=========================================================
USER QUESTION
=========================================================

{question}


=========================================================
GENERATED SQL
=========================================================

{sql}


=========================================================
DATABASE RESULTS
=========================================================

{results}


=========================================================
DATA ANALYSIS
=========================================================

{analysis}


=========================================================
CORE RULE
=========================================================

The FIRST sentence under "Key Insight" MUST directly
answer the user's exact question.

Do not give a generic business statement.

For example:

User asks:
"How did revenue change over the last 6 months?"

Good:
"Revenue fluctuated over the six-month period, rising
from ₹1.64M in July to a peak of ₹2.08M in August,
then falling to ₹1.62M in September before recovering
to ₹1.74M in December."

Bad:
"Revenue performance should be monitored closely."

The answer must be based strictly on the supplied data.


=========================================================
INSTRUCTIONS
=========================================================

1. Directly answer the user's question.
2. Use ONLY the provided database results and analysis.
3. Do not invent facts.
4. Do not invent causes.
5. Do not make assumptions that are not supported by data.
6. Use exact numbers when useful.
7. Format monetary values using ₹K, ₹M or ₹B.
8. Use percentages where relevant.
9. For time-series questions, describe the actual trend.
10. For ranking questions, identify the top result.
11. For comparison questions, compare the relevant values.
12. For root-cause questions, identify the largest drivers.
13. Mention important changes or extremes when supported.
14. Keep the answer concise and business-friendly.
15. Do not mention that you are an AI.
16. Do not mention this prompt.
17. Do not unnecessarily repeat the SQL.
18. Do not invent business recommendations unless they
    naturally follow from the provided evidence.


=========================================================
REQUIRED RESPONSE FORMAT
=========================================================

Key Insight:
[Direct answer to the user's question.]

Evidence:
- [Most important supporting fact.]
- [Second supporting fact if useful.]
- [Third supporting fact if useful.]

Business Takeaway:
[One concise interpretation based only on the data.]
"""

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    response, provider = generate_text(
        prompt
    )

    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    insight = response.strip()

    if not insight:

        raise RuntimeError(
            "AI returned an empty business insight."
        )

    # =====================================================
    # RETURN
    # =====================================================

    return insight, provider


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "BUSINESS INSIGHT GENERATOR TEST"
    )

    print("=" * 60)

    question = (
        "How did revenue change over the last 6 months?"
    )

    sql = """
    SELECT
        month,
        revenue,
        revenue - LAG(revenue)
        OVER (ORDER BY month) AS revenue_change
    FROM monthly_revenue
    ORDER BY month;
    """

    results = [
        {
            "month": "2025-07",
            "revenue": 1640000,
            "revenue_change": None
        },
        {
            "month": "2025-08",
            "revenue": 2080000,
            "revenue_change": 440000
        },
        {
            "month": "2025-09",
            "revenue": 1620000,
            "revenue_change": -460000
        },
        {
            "month": "2025-10",
            "revenue": 1900000,
            "revenue_change": 280000
        },
        {
            "month": "2025-11",
            "revenue": 1650000,
            "revenue_change": -250000
        },
        {
            "month": "2025-12",
            "revenue": 1740000,
            "revenue_change": 90000
        }
    ]

    analysis = {
        "rows": 6,
        "columns": [
            "month",
            "revenue",
            "revenue_change"
        ]
    }

    try:

        insight, provider = generate_insight(
            question=question,
            sql=sql,
            results=results,
            analysis=analysis
        )

        print(
            "\n" + "=" * 60
        )

        print(
            "INSIGHT GENERATION COMPLETE"
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
            "\nInsight:"
        )

        print(
            insight
        )

    except Exception as e:

        print(
            "\n❌ Insight generation failed."
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )