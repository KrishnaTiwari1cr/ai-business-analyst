import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
# CREATE CHART
# =========================================================

def create_chart(df: pd.DataFrame):
    """
    Automatically creates the most appropriate
    visualization from a DataFrame.

    Supported:

    1. Category + numeric
       -> Bar chart

    2. Date/time + numeric
       -> Line chart

    3. Single numeric value
       -> KPI card

    """

    # =====================================================
    # VALIDATION
    # =====================================================

    if df is None or df.empty:

        raise ValueError(
            "Cannot create visualization from empty data."
        )


    # =====================================================
    # COPY DATA
    # =====================================================

    chart_df = df.copy()


    # =====================================================
    # CONVERT NUMERIC VALUES
    # =====================================================

    for column in chart_df.columns:

        converted = pd.to_numeric(
            chart_df[column],
            errors="coerce"
        )

        if converted.notna().sum() == len(chart_df):

            chart_df[column] = converted


    # =====================================================
    # FIND DATE COLUMNS
    # =====================================================

    date_columns = []

    for column in chart_df.columns:

        column_lower = column.lower()

        if any(
            keyword in column_lower
            for keyword in [
                "date",
                "month",
                "year",
                "time"
            ]
        ):

            converted_date = pd.to_datetime(
                chart_df[column],
                errors="coerce"
            )

            if converted_date.notna().sum() == len(
                chart_df
            ):

                chart_df[column] = converted_date

                date_columns.append(
                    column
                )


    # =====================================================
    # NUMERIC COLUMNS
    # =====================================================

    numeric_columns = (
        chart_df
        .select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )


    # =====================================================
    # CATEGORICAL COLUMNS
    # =====================================================

    categorical_columns = (
        chart_df
        .select_dtypes(
            include=[
                "object",
                "string",
                "category"
            ]
        )
        .columns
        .tolist()
    )


    # =====================================================
    # CASE 1 — SINGLE NUMERIC VALUE
    # =====================================================

    if (
        len(chart_df) == 1
        and len(numeric_columns) == 1
        and not categorical_columns
        and not date_columns
    ):

        value_column = numeric_columns[0]

        value = float(
            chart_df[
                value_column
            ].iloc[0]
        )

        formatted_value = format_money(
            value
        )

        title = (
            value_column
            .replace(
                "_",
                " "
            )
            .title()
        )


        # =================================================
        # CREATE KPI FIGURE
        # =================================================

        fig = go.Figure()


        # =================================================
        # BORDER
        # =================================================

        fig.add_shape(
            type="rect",

            x0=0,
            y0=0,

            x1=1,
            y1=1,

            xref="paper",
            yref="paper",

            line=dict(
                width=2
            ),

            fillcolor="rgba(0,0,0,0)"
        )


        # =================================================
        # KPI TITLE
        # =================================================

        fig.add_annotation(

            x=0.5,
            y=0.68,

            xref="paper",
            yref="paper",

            text=title,

            showarrow=False,

            font=dict(
                size=18
            )
        )


        # =================================================
        # KPI VALUE
        # =================================================

        fig.add_annotation(

            x=0.5,
            y=0.40,

            xref="paper",
            yref="paper",

            text=formatted_value,

            showarrow=False,

            font=dict(
                size=40
            )
        )


        # =================================================
        # LAYOUT
        # =================================================

        fig.update_layout(

            height=260,

            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),

            template="plotly_dark",

            xaxis=dict(
                visible=False
            ),

            yaxis=dict(
                visible=False
            ),

            plot_bgcolor="rgba(0,0,0,0)",

            paper_bgcolor="rgba(0,0,0,0)"
        )


        return fig


    # =====================================================
    # CASE 2 — DATE + NUMERIC
    # =====================================================

    if (
        date_columns
        and numeric_columns
    ):

        date_column = date_columns[0]

        value_column = numeric_columns[0]


        chart_df = (
            chart_df
            .sort_values(
                by=date_column
            )
        )


        fig = px.line(

            chart_df,

            x=date_column,

            y=value_column,

            title=(
                f"{value_column.replace('_', ' ').title()} "
                f"Over Time"
            ),

            markers=True
        )


        fig.update_layout(

            xaxis_title=(
                date_column
                .replace(
                    "_",
                    " "
                )
                .title()
            ),

            yaxis_title=(
                value_column
                .replace(
                    "_",
                    " "
                )
                .title()
            ),

            template="plotly_dark",

            margin=dict(
                l=50,
                r=30,
                t=70,
                b=50
            )
        )


        return fig


    # =====================================================
    # CASE 3 — CATEGORY + NUMERIC
    # =====================================================

    if (
        categorical_columns
        and numeric_columns
    ):

        category_column = (
            categorical_columns[0]
        )

        value_column = (
            numeric_columns[0]
        )


        chart_df = (
            chart_df
            .sort_values(
                by=value_column,
                ascending=False
            )
        )


        fig = px.bar(

            chart_df,

            x=category_column,

            y=value_column,

            title=(
                f"{value_column.replace('_', ' ').title()} "
                f"by "
                f"{category_column.replace('_', ' ').title()}"
            ),

            text=value_column
        )


        fig.update_layout(

            xaxis_title=(
                category_column
                .replace(
                    "_",
                    " "
                )
                .title()
            ),

            yaxis_title=(
                value_column
                .replace(
                    "_",
                    " "
                )
                .title()
            ),

            template="plotly_dark",

            margin=dict(
                l=50,
                r=30,
                t=70,
                b=50
            )
        )


        fig.update_traces(

            texttemplate="%{text:,.2f}",

            textposition="outside"
        )


        return fig


    # =====================================================
    # NO SUITABLE VISUALIZATION
    # =====================================================

    raise ValueError(
        "No suitable columns found "
        "for visualization."
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "VISUALIZATION TEST"
    )

    print("=" * 60)


    # =====================================================
    # KPI TEST
    # =====================================================

    kpi_df = pd.DataFrame(
        {
            "total_revenue": [
                43501095.73
            ]
        }
    )


    try:

        fig = create_chart(
            kpi_df
        )

        fig.write_html(
            "total_revenue_kpi.html"
        )

        print(
            "\n✅ KPI card created successfully."
        )

        print(
            "Value:",
            format_money(
                43501095.73
            )
        )

    except Exception as e:

        print(
            "\n❌ KPI test failed:"
        )

        print(
            type(e).__name__,
            str(e)
        )


    # =====================================================
    # CATEGORY TEST
    # =====================================================

    category_df = pd.DataFrame(
        {
            "category": [
                "Furniture",
                "Office Supplies",
                "Electronics",
                "Software",
                "Accessories"
            ],

            "total_revenue": [
                11183572.77,
                9742174.59,
                9086337.20,
                6827297.34,
                6661713.83
            ]
        }
    )


    try:

        fig = create_chart(
            category_df
        )

        fig.write_html(
            "revenue_by_category.html"
        )

        print(
            "\n✅ Category chart created successfully."
        )

    except Exception as e:

        print(
            "\n❌ Category test failed:"
        )

        print(
            type(e).__name__,
            str(e)
        )


    # =====================================================
    # TIME SERIES TEST
    # =====================================================

    monthly_df = pd.DataFrame(
        {
            "month": [
                "2025-07-01",
                "2025-08-01",
                "2025-09-01",
                "2025-10-01",
                "2025-11-01",
                "2025-12-01"
            ],

            "revenue": [
                1640000,
                2080000,
                1620000,
                1900000,
                1650000,
                1740000
            ]
        }
    )


    try:

        fig = create_chart(
            monthly_df
        )

        fig.write_html(
            "monthly_revenue.html"
        )

        print(
            "\n✅ Time-series chart created successfully."
        )

    except Exception as e:

        print(
            "\n❌ Time-series test failed:"
        )

        print(
            type(e).__name__,
            str(e)
        )


    print(
        "\n" + "=" * 60
    )

    print(
        "VISUALIZATION TEST COMPLETE"
    )

    print(
        "=" * 60
    )