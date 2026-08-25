import re
import pandas as pd

from app.agents.sql_generator import generate_sql
from app.agents.sql_validator import validate_sql
from app.agents.query_executor import execute_query
from app.agents.insight_generator import generate_insight

from app.agents.deep_root_cause_agent import (
    generate_deep_root_cause_insight
)

from app.analytics.analysis import (
    analyze_dataframe
)

from app.analytics.visualization import (
    create_chart
)

from app.analytics.monthly_analysis import (
    get_monthly_revenue,
    compare_months,
    find_biggest_drop,
    get_month_comparison
)

from app.analytics.root_cause import (
    analyze_category_change
)

from app.analytics.product_root_cause import (
    analyze_product_change
)

from app.analytics.question_parser import (
    get_target_month
)


# =========================================================
# MONEY FORMATTER
# =========================================================

def format_money(value):
    """
    Convert raw numbers into
    ₹K / ₹M / ₹B format.
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
# ROOT CAUSE QUESTION DETECTOR
# =========================================================

def is_root_cause_question(question: str):
    """
    Determine whether the user is asking
    for revenue root-cause analysis.
    """

    question = question.lower()

    keywords = [

        "why did revenue",

        "why has revenue",

        "why revenue",

        "reason for revenue",

        "cause of revenue",

        "revenue drop",

        "revenue decline",

        "revenue decreased",

        "revenue fell",

        "why did sales",

        "why has sales",

        "which products caused",

        "which products contributed",

        "which categories contributed",

        "largest revenue loss",

        "largest revenue decline",

        "revenue drivers"

    ]

    return any(
        keyword in question
        for keyword in keywords
    )


# =========================================================
# RANKING / LIMIT DETECTOR
# =========================================================

def is_single_result_ranking_query(sql: str):
    """
    Detect queries that intentionally return only
    the top result using LIMIT 1.

    Example:

        ORDER BY total_revenue DESC
        LIMIT 1;
    """

    if not sql:
        return False

    pattern = r"\s+LIMIT\s+1\s*;?\s*$"

    return bool(
        re.search(
            pattern,
            sql,
            flags=re.IGNORECASE
        )
    )


# =========================================================
# BUILD VISUALIZATION QUERY
# =========================================================

def build_visualization_query(sql: str):
    """
    For ranking queries using LIMIT 1, remove LIMIT 1
    so the visualization can display the complete
    comparison.

    The original SQL remains untouched and is still used
    for the actual business answer.
    """

    if not is_single_result_ranking_query(sql):

        return None

    visualization_sql = re.sub(
        r"\s+LIMIT\s+1\s*;?\s*$",
        "",
        sql,
        flags=re.IGNORECASE
    )

    visualization_sql = (
        visualization_sql.strip()
        + ";"
    )

    return visualization_sql


# =========================================================
# GET VISUALIZATION DATA
# =========================================================

def get_visualization_data(
    sql: str,
    answer_df: pd.DataFrame
):
    """
    Return the best DataFrame for visualization.

    Normal query:
        use the original result.

    Ranking query:
        execute a second query without LIMIT 1 so
        the chart can compare all categories/products.
    """

    # -----------------------------------------------------
    # Only special-case ranking queries
    # -----------------------------------------------------

    visualization_sql = (
        build_visualization_query(sql)
    )

    if visualization_sql is None:

        return answer_df

    print(
        "\n📊 Ranking query detected."
    )

    print(
        "Creating expanded query for visualization..."
    )

    print(
        "\nVisualization SQL:"
    )

    print(
        "-" * 60
    )

    print(
        visualization_sql
    )

    print(
        "-" * 60
    )

    # -----------------------------------------------------
    # Validate visualization SQL
    # -----------------------------------------------------

    is_valid, message = (
        validate_sql(
            visualization_sql
        )
    )

    if not is_valid:

        print(
            "\n⚠️ Visualization SQL rejected."
        )

        print(
            "Reason:",
            message
        )

        print(
            "Using original result for chart."
        )

        return answer_df

    # -----------------------------------------------------
    # Execute visualization SQL
    # -----------------------------------------------------

    try:

        visualization_df = (
            execute_query(
                visualization_sql
            )
        )

    except Exception as e:

        print(
            "\n⚠️ Expanded visualization query failed."
        )

        print(
            "Reason:",
            e
        )

        print(
            "Using original result for chart."
        )

        return answer_df

    # -----------------------------------------------------
    # Validate returned data
    # -----------------------------------------------------

    if visualization_df.empty:

        print(
            "\n⚠️ Expanded visualization query "
            "returned no data."
        )

        print(
            "Using original result for chart."
        )

        return answer_df

    print(
        "\n✅ Expanded visualization data loaded."
    )

    print(
        "Rows for visualization:",
        len(visualization_df)
    )

    return visualization_df


# =========================================================
# DEEP ROOT CAUSE PIPELINE
# =========================================================

def run_root_cause_analysis(
    target_month=None
):
    """
    Complete root-cause pipeline.

    Level 1:
        Overall revenue

    Level 2:
        Category drivers

    Level 3:
        Product drivers

    Level 4:
        AI business explanation
    """

    print("\n" + "=" * 60)

    print(
        "DEEP ROOT CAUSE ANALYSIS"
    )

    print("=" * 60)

    # =====================================================
    # STEP 1 — MONTHLY REVENUE
    # =====================================================

    print(
        "\nSTEP 1: ANALYZING MONTHLY REVENUE"
    )

    monthly_df = get_monthly_revenue()

    if monthly_df.empty:

        print(
            "\n❌ No monthly revenue data found."
        )

        return None

    # =====================================================
    # STEP 2 — MONTH COMPARISON
    # =====================================================

    monthly_df = compare_months(
        monthly_df
    )

    # =====================================================
    # STEP 3 — TARGET MONTH
    # =====================================================

    if target_month is not None:

        requested_month = (
            target_month["month"]
        )

        requested_year = (
            target_month["year"]
        )

        print(
            f"\nRequested month: "
            f"{requested_month}/"
            f"{requested_year or 'auto'}"
        )

        target_row = get_month_comparison(
            monthly_df,
            requested_month,
            requested_year
        )

        if target_row is None:

            print(
                "\n❌ Requested month "
                "was not found."
            )

            return None

    else:

        print(
            "\nNo specific month detected."
        )

        print(
            "Finding biggest revenue drop..."
        )

        target_row = find_biggest_drop(
            monthly_df
        )

        if target_row is None:

            print(
                "\nNo revenue decline detected."
            )

            return None

    # =====================================================
    # STEP 4 — DATE INFORMATION
    # =====================================================

    current_month_date = (
        target_row["month"]
    )

    previous_month_date = (
        current_month_date
        - pd.DateOffset(
            months=1
        )
    )

    current_month = (
        current_month_date.strftime(
            "%Y-%m-%d"
        )
    )

    previous_month = (
        previous_month_date.strftime(
            "%Y-%m-%d"
        )
    )

    # =====================================================
    # STEP 5 — REVENUE VALUES
    # =====================================================

    previous_total = float(
        target_row[
            "previous_revenue"
        ]
    )

    current_total = float(
        target_row[
            "revenue"
        ]
    )

    change = float(
        target_row[
            "revenue_change"
        ]
    )

    change_percent = float(
        target_row[
            "revenue_change_percent"
        ]
    )

    # =====================================================
    # DISPLAY OVERALL CHANGE
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "OVERALL REVENUE CHANGE"
    )

    print("=" * 60)

    print(
        f"\n{previous_month_date.strftime('%B %Y')}: "
        f"{format_money(previous_total)}"
    )

    print(
        f"{current_month_date.strftime('%B %Y')}: "
        f"{format_money(current_total)}"
    )

    print(
        f"\nRevenue change: "
        f"{format_money(change)}"
    )

    print(
        f"Percentage change: "
        f"{change_percent:.2f}%"
    )

    # =====================================================
    # STEP 6 — CATEGORY ANALYSIS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 2: CATEGORY ROOT CAUSE"
    )

    print("=" * 60)

    category_df = analyze_category_change(
        previous_month,
        current_month
    )

    if category_df.empty:

        print(
            "\n❌ No category data found."
        )

        return None

    # =====================================================
    # SHOW TOP CATEGORY DECLINES
    # =====================================================

    category_declines = category_df[
        category_df[
            "revenue_change"
        ] < 0
    ]

    print(
        "\nTop category declines:"
    )

    for _, row in (
        category_declines.head(5)
        .iterrows()
    ):

        print(
            f"- {row['category']}: "
            f"{format_money(row['revenue_change'])} "
            f"({row['revenue_change_percent']:.2f}%)"
        )

    # =====================================================
    # STEP 7 — PRODUCT ANALYSIS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 3: PRODUCT ROOT CAUSE"
    )

    print("=" * 60)

    product_df = analyze_product_change(
        previous_month,
        current_month
    )

    if product_df.empty:

        print(
            "\n❌ No product data found."
        )

        return None

    # =====================================================
    # SHOW TOP PRODUCT DECLINES
    # =====================================================

    product_declines = product_df[
        product_df[
            "revenue_change"
        ] < 0
    ]

    print(
        "\nTop product declines:"
    )

    for _, row in (
        product_declines.head(10)
        .iterrows()
    ):

        print(
            f"- {row['product_name']} "
            f"({row['category']}): "
            f"{format_money(row['revenue_change'])} "
            f"({row['revenue_change_percent']:.2f}%)"
        )

    # =====================================================
    # STEP 8 — DEEP AI ANALYSIS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 4: GENERATING DEEP AI INSIGHT"
    )

    print("=" * 60)

    insight = (
        generate_deep_root_cause_insight(

            previous_month=(
                previous_month_date.strftime(
                    "%B %Y"
                )
            ),

            current_month=(
                current_month_date.strftime(
                    "%B %Y"
                )
            ),

            previous_total=previous_total,

            current_total=current_total,

            category_df=category_df,

            product_df=product_df
        )
    )

    # =====================================================
    # FINAL
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "FINAL BUSINESS ROOT-CAUSE ANALYSIS"
    )

    print("=" * 60)

    print()

    print(
        insight
    )

    print("\n" + "=" * 60)

    return {

        "previous_month":
            previous_month,

        "current_month":
            current_month,

        "previous_total":
            previous_total,

        "current_total":
            current_total,

        "revenue_change":
            change,

        "revenue_change_percent":
            change_percent,

        "category_analysis":
            category_df.to_dict(
                orient="records"
            ),

        "product_analysis":
            product_df.head(10).to_dict(
                orient="records"
            ),

        "insight":
            insight
    }


# =========================================================
# NORMAL BUSINESS QUESTION
# =========================================================

def run_normal_question(
    question: str
):
    """
    Normal SQL-based analytics pipeline.

    The original SQL/result is used for the actual
    business answer.

    Ranking queries receive a second expanded query
    only for visualization.
    """

    # =====================================================
    # STEP 1 — SQL GENERATION
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 1: GENERATING SQL"
    )

    print("=" * 60)

    sql = generate_sql(
        question
    )

    print("\nGenerated SQL:")

    print("-" * 60)

    print(sql)

    print("-" * 60)

    # =====================================================
    # STEP 2 — SQL VALIDATION
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 2: VALIDATING SQL"
    )

    print("=" * 60)

    is_valid, message = (
        validate_sql(sql)
    )

    if not is_valid:

        print(
            "\n❌ SQL rejected!"
        )

        print(
            "Reason:",
            message
        )

        return None

    print(
        "\n✅ SQL is safe."
    )

    # =====================================================
    # STEP 3 — EXECUTE ANSWER SQL
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 3: EXECUTING SQL"
    )

    print("=" * 60)

    try:

        df = execute_query(
            sql
        )

    except Exception as e:

        print(
            "\n❌ Database execution failed."
        )

        print(
            e
        )

        return None

    # =====================================================
    # STEP 4 — RESULTS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 4: DATABASE RESULTS"
    )

    print("=" * 60)

    if df.empty:

        print(
            "\nNo data found."
        )

        return None

    print()

    print(
        df.to_string(
            index=False
        )
    )

    print(
        "\nRows returned:",
        len(df)
    )

    # =====================================================
    # STEP 5 — ANALYSIS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 5: ANALYZING DATA"
    )

    print("=" * 60)

    analysis = analyze_dataframe(
        df
    )

    print(
        "\nAnalysis completed."
    )

    # =====================================================
    # STEP 6 — VISUALIZATION
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 6: CREATING VISUALIZATION"
    )

    print("=" * 60)

    chart_path = None

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # Keep `df` for the actual answer.
    #
    # Use `chart_df` only for visualization.
    #
    # If SQL contains LIMIT 1, chart_df will contain
    # all matching categories/products.
    # -----------------------------------------------------

    chart_df = get_visualization_data(
        sql,
        df
    )

    try:

        figure = create_chart(
            chart_df
        )

        chart_path = (
            "business_chart.html"
        )

        figure.write_html(
            chart_path
        )

        print(
            f"\n📊 Chart created successfully: "
            f"{chart_path}"
        )

        print(
            f"📊 Chart rows: "
            f"{len(chart_df)}"
        )

    except Exception as e:

        print(
            "\n⚠️ Chart could not be created."
        )

        print(
            "Reason:",
            e
        )

    # =====================================================
    # STEP 7 — AI INSIGHT
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "STEP 7: GENERATING BUSINESS INSIGHT"
    )

    print("=" * 60)

    # IMPORTANT:
    # Use original answer results, NOT chart results.

    results = df.to_dict(
        orient="records"
    )

    insight = generate_insight(

        question=question,

        sql=sql,

        results=results,

        analysis=analysis
    )

    # =====================================================
    # FINAL
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "FINAL BUSINESS INSIGHT"
    )

    print("=" * 60)

    print()

    print(
        insight
    )

    print("\n" + "=" * 60)

    return {

        "question":
            question,

        "sql":
            sql,

        "results":
            results,

        "analysis":
            analysis,

        "chart_path":
            chart_path,

        "insight":
            insight,

        # -------------------------------------------------
        # Additional visualization data
        # -------------------------------------------------

        "visualization_data":
            chart_df.to_dict(
                orient="records"
            )
    }


# =========================================================
# MAIN ASSISTANT
# =========================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "       AI BUSINESS ANALYST ASSISTANT"
    )

    print("=" * 60)

    question = input(
        "\nAsk a business question: "
    ).strip()

    # =====================================================
    # EMPTY QUESTION
    # =====================================================

    if not question:

        print(
            "\nQuestion cannot be empty."
        )

    # =====================================================
    # ROOT CAUSE QUESTION
    # =====================================================

    elif is_root_cause_question(
        question
    ):

        print(
            "\n🔍 Root-cause question detected."
        )

        # -------------------------------------------------
        # Detect month/year
        # -------------------------------------------------

        target_month = (
            get_target_month(
                question
            )
        )

        if target_month:

            print(
                f"📅 Requested month: "
                f"{target_month['month']}/"
                f"{target_month['year'] or 'auto'}"
            )

        else:

            print(
                "📅 No specific month detected."
            )

        # -------------------------------------------------
        # Run deep analysis
        # -------------------------------------------------

        run_root_cause_analysis(
            target_month
        )

    # =====================================================
    # NORMAL QUESTION
    # =====================================================

    else:

        run_normal_question(
            question
        )
