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
import plotly.express as px

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

        if intent == "root_cause":

            st.success(
                "✅ Root-cause analysis"
            )

        elif sql:

            st.success(
                "✅ SQL generated"
            )

        else:

            st.warning(
                "⚠️ SQL missing"
            )


    with status3:

        if intent == "root_cause":

            st.success(
                "✅ Revenue comparison loaded"
            )

        elif sql_valid:

            st.success(
                "✅ SQL validated"
            )

        else:

            st.warning(
                "⚠️ SQL validation failed"
            )


    with status4:

        if intent == "root_cause":

            st.success(
                "✅ Driver analysis complete"
            )

        elif execution_success:

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

                st.metric(
                    "Previous month",
                    format_money(previous_total),
                    border=True
                )


            with k2:

                st.metric(
                    "Current month",
                    format_money(current_total),
                    border=True
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

                st.metric(
                    "Revenue change",
                    change_value,
                    change_percent,
                    border=True
                )


    # =====================================================
    # QUERY RESULT
    # =====================================================

    if data is not None and not data.empty:

        st.markdown(
            '<div class="section-title">'
            '📊 Query Result'
            '</div>',
            unsafe_allow_html=True
        )

        display_df = format_dataframe(data)

        if (
            len(data) == 1
            and len(data.columns) == 1
            and pd.api.types.is_numeric_dtype(data.iloc[:, 0])
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
                width="stretch",
                hide_index=True
            )

        st.caption(f"{len(data)} row(s) returned")


    # =====================================================
    # GENERATED SQL
    # =====================================================

    if sql:

        with st.expander("🔧 View generated SQL"):

            st.code(sql, language="sql")


    # =====================================================
    # ADAPTIVE VISUALIZATION
    # =====================================================

    chart_data = None

    if (
        visualization_data is not None
        and not visualization_data.empty
    ):
        chart_data = visualization_data.copy()

    elif data is not None and not data.empty:
        chart_data = data.copy()


    if chart_data is not None and not chart_data.empty:

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

            if figure is None:
                raise ValueError(
                    "create_chart() returned None."
                )

            st.plotly_chart(
                figure,
                use_container_width=True,
                key="business_analytics_chart"
            )

        except Exception as primary_error:

            try:

                import plotly.express as px

                df_chart = chart_data.copy()

                date_column = None
                numeric_columns = []
                categorical_columns = []

                # =================================================
                # DETECT DATE / TIME
                # =================================================

                for column in df_chart.columns:

                    name = str(column).lower()

                    converted = pd.to_datetime(
                        df_chart[column],
                        errors="coerce"
                    )

                    if (
                        any(
                            word in name
                            for word in (
                                "date",
                                "month",
                                "year",
                                "time",
                                "timestamp"
                            )
                        )
                        and converted.notna().sum() > 0
                    ):

                        df_chart[column] = converted

                        date_column = column

                        break


                # =================================================
                # DETECT NUMERIC / CATEGORICAL
                # =================================================

                for column in df_chart.columns:

                    if column == date_column:
                        continue

                    converted = pd.to_numeric(
                        df_chart[column],
                        errors="coerce"
                    )

                    if (
                        converted.notna().sum()
                        >= max(
                            1,
                            int(
                                len(df_chart) * 0.7
                            )
                        )
                    ):

                        df_chart[column] = converted

                        numeric_columns.append(
                            column
                        )

                    else:

                        categorical_columns.append(
                            column
                        )


                # =================================================
                # TIME SERIES
                # =================================================

                if (
                    date_column is not None
                    and numeric_columns
                ):

                    plot_df = (
                        df_chart
                        .dropna(
                            subset=[
                                date_column
                            ]
                        )
                        .sort_values(
                            date_column
                        )
                    )

                    metrics = [
                        column
                        for column in numeric_columns
                        if plot_df[column].nunique() > 1
                    ]

                    if metrics:

                        figure = px.line(
                            plot_df,
                            x=date_column,
                            y=metrics,
                            markers=True,
                            title=(
                                "Business Metrics Over Time"
                            )
                        )

                        figure.update_layout(
                            template="plotly_dark",
                            hovermode="x unified",
                            xaxis_title=(
                                str(
                                    date_column
                                )
                                .replace(
                                    "_",
                                    " "
                                )
                                .title()
                            ),
                            yaxis_title="Value"
                        )

                        st.plotly_chart(
                            figure,
                            use_container_width=True,
                            key="fallback_time_series_chart"
                        )

                    else:

                        st.warning(
                            "Numeric values do not vary "
                            "enough to plot."
                        )


                # =================================================
                # CATEGORY / DIMENSION
                # =================================================

                elif (
                    categorical_columns
                    and numeric_columns
                ):

                    category_column = (
                        categorical_columns[0]
                    )

                    metric_column = (
                        numeric_columns[0]
                    )

                    figure = px.bar(
                        df_chart,
                        x=category_column,
                        y=metric_column,
                        title=(
                            f"{str(metric_column).replace('_', ' ').title()} "
                            f"by "
                            f"{str(category_column).replace('_', ' ').title()}"
                        )
                    )

                    figure.update_layout(
                        template="plotly_dark"
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        key="fallback_category_chart"
                    )


                # =================================================
                # MULTIPLE NUMERIC COLUMNS
                # =================================================

                elif len(numeric_columns) >= 2:

                    figure = px.line(
                        df_chart,
                        y=numeric_columns,
                        markers=True,
                        title="Business Metrics"
                    )

                    figure.update_layout(
                        template="plotly_dark",
                        hovermode="x unified"
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        key="fallback_multi_metric_chart"
                    )


                # =================================================
                # SINGLE NUMERIC COLUMN
                # =================================================

                elif len(numeric_columns) == 1:

                    metric_column = (
                        numeric_columns[0]
                    )

                    figure = px.bar(
                        df_chart,
                        y=metric_column,
                        title=(
                            str(
                                metric_column
                            )
                            .replace(
                                "_",
                                " "
                            )
                            .title()
                        )
                    )

                    figure.update_layout(
                        template="plotly_dark"
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        key="fallback_single_metric_chart"
                    )


                else:

                    st.info(
                        "No numeric data was found "
                        "for visualization."
                    )


            except Exception as fallback_error:

                st.error(
                    "Visualization failed."
                )

                with st.expander(
                    "Visualization details"
                ):

                    st.code(
                        f"Primary visualization error:\n"
                        f"{primary_error}\n\n"
                        f"Fallback visualization error:\n"
                        f"{fallback_error}"
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


            if (
                "product_name" in product_display.columns
                and "revenue_change" in product_display.columns
            ):

                st.markdown(
                    '<div class="section-title">'
                    '📉 Largest product revenue losses'
                    '</div>',
                    unsafe_allow_html=True
                )

                loss_chart = px.bar(
                    product_display.sort_values(
                        "revenue_change",
                        ascending=True
                    ),
                    x="revenue_change",
                    y="product_name",
                    color="category"
                    if "category" in product_display.columns
                    else None,
                    orientation="h",
                    title="Largest product revenue losses"
                )

                loss_chart.update_layout(
                    template="plotly_dark",
                    xaxis_title="Revenue change",
                    yaxis_title="Product",
                    showlegend="category" in product_display.columns
                )

                st.plotly_chart(
                    loss_chart,
                    width="stretch",
                    key="root_cause_product_loss_chart"
                )


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
