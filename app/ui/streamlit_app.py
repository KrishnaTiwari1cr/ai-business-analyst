import sys
import os

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd

from app.graph.business_graph import run_business_graph
from app.analytics.visualization import create_chart


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero-title {
        font-size: 3.1rem;
        font-weight: 750;
        letter-spacing: -1.5px;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #9ca3af;
        margin-bottom: 2rem;
    }


    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-title {
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }


    /* =====================================================
       KPI CARD
       ===================================================== */

    .kpi-card {
        border: 1px solid #343840;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        background: #15171c;
        min-height: 125px;
    }

    .kpi-label {
        color: #9ca3af;
        font-size: 0.9rem;
        margin-bottom: 0.45rem;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 0.8rem;
        margin-top: 4rem;
        padding-top: 1rem;
        border-top: 1px solid #272a30;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FORMAT MONEY
# =========================================================

def format_money(value):

    try:
        value = float(value)

    except (TypeError, ValueError):

        return str(value)

    sign = "-" if value < 0 else ""

    value = abs(value)

    if value >= 1_000_000_000:

        return (
            f"{sign}₹"
            f"{value / 1_000_000_000:.2f}B"
        )

    if value >= 1_000_000:

        return (
            f"{sign}₹"
            f"{value / 1_000_000:.2f}M"
        )

    if value >= 1_000:

        return (
            f"{sign}₹"
            f"{value / 1_000:.1f}K"
        )

    return f"{sign}₹{value:,.0f}"


# =========================================================
# FORMAT DATAFRAME
# =========================================================

def format_dataframe(df):

    if df is None:

        return pd.DataFrame()

    display_df = df.copy()

    for column in display_df.columns:

        column_lower = column.lower()

        if any(
            word in column_lower
            for word in [
                "revenue",
                "sales",
                "profit",
                "cost"
            ]
        ):

            display_df[column] = (
                display_df[column]
                .apply(
                    lambda x:
                    format_money(x)
                    if pd.notna(x)
                    else x
                )
            )

        elif (
            "percent" in column_lower
            or "percentage" in column_lower
        ):

            display_df[column] = (
                display_df[column]
                .apply(
                    lambda x:
                    f"{float(x):.2f}%"
                    if pd.notna(x)
                    else x
                )
            )

    return display_df


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero-title">
        🤖 AI Business Analyst
    </div>

    <div class="hero-subtitle">
        Ask questions about your business data using natural language.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# BUSINESS QUESTION
# =========================================================

question = st.text_input(
    "Business Question",
    placeholder=(
        "e.g. Which product category generated the most revenue?"
    ),
    label_visibility="visible"
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

col_button, col_space = st.columns(
    [1, 7]
)

with col_button:

    analyze = st.button(
        "🔍 Analyze",
        type="primary",
        use_container_width=True
    )


# =========================================================
# EXAMPLE QUESTIONS
# =========================================================

with st.expander(
    "💡 Example questions"
):

    example_cols = st.columns(2)

    with example_cols[0]:

        st.markdown(
            """
            **Analytics**

            • Which product category generated the most revenue?

            • What is the total revenue?

            • What are the top 5 products by revenue?

            • How did revenue change over the last 6 months?
            """
        )

    with example_cols[1]:

        st.markdown(
            """
            **Root Cause Analysis**

            • Why did revenue drop?

            • Why did revenue drop in September 2025?

            • Which categories contributed most to the decline?

            • Which products caused the largest revenue loss?
            """
        )


# =========================================================
# RUN ANALYSIS
# =========================================================

if analyze:

    if not question.strip():

        st.warning(
            "Please enter a business question."
        )

        st.stop()


    # =====================================================
    # RUN LANGGRAPH
    # =====================================================

    with st.spinner(
        "🤖 AI Business Analyst is analyzing your data..."
    ):

        try:

            result = run_business_graph(
                question.strip()
            )

        except Exception as e:

            st.error(
                "The analysis could not be completed."
            )

            with st.expander(
                "Technical details"
            ):

                st.code(
                    str(e)
                )

            st.stop()


    # =====================================================
    # EXTRACT RESULT
    # =====================================================

    intent = result.get(
        "intent"
    )

    provider = result.get(
        "provider"
    )

    sql = result.get(
        "sql"
    )

    data = result.get(
        "data"
    )

    visualization_data = result.get(
        "visualization_data"
    )

    insight = result.get(
        "insight"
    )

    retry_count = result.get(
        "retry_count",
        0
    )

    execution_success = result.get(
        "execution_success",
        False
    )

    sql_valid = result.get(
        "sql_valid",
        False
    )

    execution_error = result.get(
        "execution_error"
    )

    error = result.get(
        "error"
    )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    if error and not execution_success:

        st.error(
            "The AI Business Analyst could not complete the request."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                str(error)
            )

        st.stop()


    # =====================================================
    # AGENT EXECUTION
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '⚙️ Agent Execution'
        '</div>',
        unsafe_allow_html=True
    )


    status1, status2, status3, status4 = (
        st.columns(4)
    )


    with status1:

        st.success(
            "✅ Intent detected"
        )

        st.caption(
            intent or "Unknown"
        )


    with status2:

        if sql:

            st.success(
                "✅ SQL generated"
            )

        else:

            st.warning(
                "⚠️ SQL missing"
            )


    with status3:

        if sql_valid:

            st.success(
                "✅ SQL validated"
            )

        else:

            st.warning(
                "⚠️ SQL validation failed"
            )


    with status4:

        if execution_success:

            st.success(
                "✅ Query executed"
            )

        else:

            st.warning(
                "⚠️ Execution incomplete"
            )


    # =====================================================
    # PROVIDER + REPAIR
    # =====================================================

    provider_col, repair_col = (
        st.columns(2)
    )


    with provider_col:

        provider_name = (
            str(provider).upper()
            if provider
            else "N/A"
        )

        st.info(
            f"🤖 LLM Provider: **{provider_name}**"
        )


    with repair_col:

        if retry_count > 0:

            st.warning(
                f"🔧 SQL self-repaired "
                f"{retry_count} time(s)"
            )

        else:

            st.success(
                "🔒 No SQL repair required"
            )


    # =====================================================
    # ROOT CAUSE KPI SECTION
    # =====================================================

    if intent == "root_cause":

        previous_total = result.get(
            "previous_total"
        )

        current_total = result.get(
            "current_total"
        )

        revenue_change = result.get(
            "revenue_change"
        )

        revenue_change_percent = result.get(
            "revenue_change_percent"
        )


        if (
            previous_total is not None
            and current_total is not None
        ):

            st.markdown(
                '<div class="section-title">'
                '📊 Revenue Overview'
                '</div>',
                unsafe_allow_html=True
            )


            k1, k2, k3 = st.columns(3)


            with k1:

                st.markdown(
                    f"""
                    <div class="kpi-card">

                        <div class="kpi-label">
                            Previous Month
                        </div>

                        <div class="kpi-value">
                            {format_money(previous_total)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with k2:

                st.markdown(
                    f"""
                    <div class="kpi-card">

                        <div class="kpi-label">
                            Current Month
                        </div>

                        <div class="kpi-value">
                            {format_money(current_total)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with k3:

                change_value = (
                    format_money(
                        revenue_change
                    )
                    if revenue_change is not None
                    else "N/A"
                )

                change_percent = (
                    f"{revenue_change_percent:.2f}%"
                    if revenue_change_percent is not None
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="kpi-card">

                        <div class="kpi-label">
                            Revenue Change
                        </div>

                        <div class="kpi-value">
                            {change_value}
                        </div>

                        <div class="kpi-label">
                            {change_percent}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # QUERY RESULT
    # =====================================================

    if (
        data is not None
        and not data.empty
    ):

        st.markdown(
            '<div class="section-title">'
            '📊 Query Result'
            '</div>',
            unsafe_allow_html=True
        )


        display_df = format_dataframe(
            data
        )


        # =================================================
        # SINGLE NUMERIC RESULT
        # =================================================

        if (
            len(data) == 1
            and len(data.columns) == 1
            and pd.api.types.is_numeric_dtype(
                data.iloc[:, 0]
            )
        ):

            value = data.iloc[0, 0]

            st.markdown(
                f"""
                <div class="kpi-card">

                    <div class="kpi-label">
                        {data.columns[0].replace("_", " ").title()}
                    </div>

                    <div class="kpi-value">
                        {format_money(value)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


        st.caption(
            f"{len(data)} row(s) returned"
        )


    # =====================================================
    # GENERATED SQL
    # =====================================================

    if sql:

        with st.expander(
            "🔧 View generated SQL"
        ):

            st.code(
                sql,
                language="sql"
            )


    # =====================================================
    # VISUALIZATION
    #
    # IMPORTANT:
    # If LangGraph did not create separate
    # visualization_data, use the main query result.
    # This fixes single-value KPI queries.
    # =====================================================

    chart_data = None

    if (
        visualization_data is not None
        and not visualization_data.empty
    ):

        chart_data = visualization_data.copy()

    elif (
        data is not None
        and not data.empty
    ):

        chart_data = data.copy()


    # =====================================================
    # CREATE VISUALIZATION
    # =====================================================

    if (
        chart_data is not None
        and not chart_data.empty
    ):

        st.markdown(
            '<div class="section-title">'
            '📈 Visualization'
            '</div>',
            unsafe_allow_html=True
        )


        try:

            figure = create_chart(
                chart_data
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )

        except Exception as e:

            st.info(
                "No suitable visualization is available "
                "for this result."
            )

            with st.expander(
                "Visualization details"
            ):

                st.code(
                    str(e)
                )


    # =====================================================
    # VISUALIZATION DATA
    # =====================================================

    if (
        chart_data is not None
        and not chart_data.empty
    ):

        with st.expander(
            "📋 View visualization data"
        ):

            st.dataframe(
                format_dataframe(
                    chart_data
                ),
                use_container_width=True,
                hide_index=True
            )


    # =====================================================
    # ROOT CAUSE — CATEGORY DRIVERS
    # =====================================================

    if intent == "root_cause":

        category_df = result.get(
            "category_analysis"
        )


        if (
            category_df is not None
            and not category_df.empty
        ):

            st.markdown(
                '<div class="section-title">'
                '🔍 Category Drivers'
                '</div>',
                unsafe_allow_html=True
            )


            st.dataframe(
                format_dataframe(
                    category_df
                ),
                use_container_width=True,
                hide_index=True
            )


        # =================================================
        # PRODUCT DRIVERS
        # =================================================

        product_df = result.get(
            "product_analysis"
        )


        if (
            product_df is not None
            and not product_df.empty
        ):

            st.markdown(
                '<div class="section-title">'
                '📦 Product Drivers'
                '</div>',
                unsafe_allow_html=True
            )


            product_display = (
                product_df.copy()
            )


            if (
                "revenue_change"
                in product_display.columns
            ):

                negative = (
                    product_display[
                        product_display[
                            "revenue_change"
                        ] < 0
                    ]
                    .sort_values(
                        "revenue_change"
                    )
                    .head(10)
                )


                if not negative.empty:

                    product_display = negative


            st.dataframe(
                format_dataframe(
                    product_display
                ),
                use_container_width=True,
                hide_index=True
            )


    # =====================================================
    # AI BUSINESS INSIGHT
    # =====================================================

    if insight:

        st.markdown(
            '<div class="section-title">'
            '💡 AI Business Insight'
            '</div>',
            unsafe_allow_html=True
        )


        with st.container(
            border=True
        ):

            st.markdown(
                insight
            )


    # =====================================================
    # LANGGRAPH EXECUTION DETAILS
    # =====================================================

    with st.expander(
        "🧠 LangGraph execution details"
    ):

        trace_col1, trace_col2 = (
            st.columns(2)
        )


        with trace_col1:

            st.write(
                "**Intent:**",
                intent
            )

            st.write(
                "**LLM Provider:**",
                provider
            )

            st.write(
                "**SQL Repair Attempts:**",
                retry_count
            )


        with trace_col2:

            st.write(
                "**SQL Validation:**",
                sql_valid
            )

            st.write(
                "**Execution Successful:**",
                execution_success
            )


            if execution_error:

                st.write(
                    "**Execution Error:**",
                    execution_error
                )


    # =====================================================
    # FOOTER
    # =====================================================

    st.markdown(
        """
        <div class="footer">
            AI Business Analyst · LangGraph · SQL · PostgreSQL · LLM-powered Analytics
        </div>
        """,
        unsafe_allow_html=True
    )