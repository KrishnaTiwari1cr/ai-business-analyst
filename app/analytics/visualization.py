import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# FORMATTING HELPERS
# =========================================================

def format_money(value):

    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000_000:
        return f"{sign}₹{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"{sign}₹{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{sign}₹{value / 1_000:.1f}K"

    return f"{sign}₹{value:,.0f}"


def pretty_name(column):

    return (
        str(column)
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


# =========================================================
# COLUMN DETECTION
# =========================================================

def find_date_columns(df):

    date_columns = []

    for column in df.columns:

        series = df[column]

        if pd.api.types.is_datetime64_any_dtype(
            series
        ):
            date_columns.append(column)
            continue

        name = str(column).lower()

        date_keywords = [
            "date",
            "month",
            "year",
            "time",
            "timestamp",
            "week",
            "quarter"
        ]

        if any(
            keyword in name
            for keyword in date_keywords
        ):

            converted = pd.to_datetime(
                series,
                errors="coerce"
            )

            if (
                len(series) > 0
                and converted.notna().sum()
                >= max(
                    1,
                    int(len(series) * 0.8)
                )
            ):

                date_columns.append(column)

    return date_columns


def find_numeric_columns(df):

    numeric_columns = []

    for column in df.columns:

        series = df[column]

        if pd.api.types.is_numeric_dtype(
            series
        ):

            numeric_columns.append(column)
            continue

        converted = pd.to_numeric(
            series,
            errors="coerce"
        )

        if (
            len(series) > 0
            and converted.notna().sum()
            == len(series)
        ):

            numeric_columns.append(column)

    return numeric_columns


def find_categorical_columns(
    df,
    date_columns
):

    categorical_columns = []

    for column in df.columns:

        if column in date_columns:
            continue

        series = df[column]

        if (
            pd.api.types.is_object_dtype(
                series
            )
            or pd.api.types.is_string_dtype(
                series
            )
            or isinstance(
                series.dtype,
                pd.CategoricalDtype
            )
        ):

            categorical_columns.append(
                column
            )

    return categorical_columns


# =========================================================
# COLUMN SCORING
# =========================================================

def score_metric(column):

    name = str(column).lower()

    score = 0

    strong_terms = [
        "revenue",
        "sales",
        "profit",
        "amount",
        "value",
        "total",
        "income",
        "earnings",
        "margin"
    ]

    medium_terms = [
        "quantity",
        "count",
        "orders",
        "units",
        "volume",
        "price",
        "cost"
    ]

    change_terms = [
        "change",
        "difference",
        "delta",
        "growth",
        "variance"
    ]

    weak_terms = [
        "percent",
        "percentage",
        "rate",
        "id",
        "index"
    ]

    for term in strong_terms:

        if term in name:
            score += 10

    for term in medium_terms:

        if term in name:
            score += 5

    for term in change_terms:

        if term in name:
            score += 2

    for term in weak_terms:

        if term in name:
            score -= 5

    if (
        name.endswith("_id")
        or name == "id"
    ):

        score -= 30

    return score


def score_category(
    column,
    df
):

    name = str(column).lower()

    score = 0

    strong_terms = [
        "category",
        "product",
        "region",
        "segment",
        "channel",
        "customer",
        "name",
        "type",
        "department",
        "city",
        "country",
        "state"
    ]

    weak_terms = [
        "id",
        "code",
        "zip",
        "postal"
    ]

    for term in strong_terms:

        if term in name:
            score += 10

    for term in weak_terms:

        if term in name:
            score -= 8

    unique_count = (
        df[column]
        .nunique(
            dropna=True
        )
    )

    if unique_count <= 20:

        score += 10

    elif unique_count <= 50:

        score += 5

    elif unique_count > 100:

        score -= 10

    return score


def select_metric(
    numeric_columns,
    df
):

    if not numeric_columns:
        return None

    scored = []

    for column in numeric_columns:

        score = score_metric(
            column
        )

        series = df[column].dropna()

        if series.empty:
            score -= 20

        if series.nunique() <= 1:
            score -= 5

        scored.append(
            (
                score,
                column
            )
        )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return scored[0][1]


def select_category(
    categorical_columns,
    df
):

    if not categorical_columns:
        return None

    scored = []

    for column in categorical_columns:

        score = score_category(
            column,
            df
        )

        unique_count = (
            df[column]
            .nunique(
                dropna=True
            )
        )

        if unique_count <= 1:
            score -= 20

        scored.append(
            (
                score,
                column
            )
        )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return scored[0][1]


# =========================================================
# SPECIAL COLUMN DETECTION
# =========================================================

def find_change_columns(
    numeric_columns
):

    change_columns = []

    keywords = [
        "change",
        "difference",
        "delta",
        "growth",
        "variance",
        "increase",
        "decrease"
    ]

    for column in numeric_columns:

        name = str(column).lower()

        if any(
            keyword in name
            for keyword in keywords
        ):

            change_columns.append(
                column
            )

    return change_columns


# =========================================================
# KPI
# =========================================================

def create_kpi(
    df,
    value_column
):

    value = float(
        df[value_column].iloc[0]
    )

    fig = go.Figure()

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

    fig.add_annotation(
        x=0.5,
        y=0.68,
        xref="paper",
        yref="paper",
        text=pretty_name(
            value_column
        ),
        showarrow=False,
        font=dict(
            size=18
        )
    )

    fig.add_annotation(
        x=0.5,
        y=0.40,
        xref="paper",
        yref="paper",
        text=format_money(
            value
        ),
        showarrow=False,
        font=dict(
            size=40
        )
    )

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


# =========================================================
# TIME SERIES
# =========================================================

def create_time_chart(
    df,
    date_column,
    numeric_columns
):

    chart_df = df.copy()

    chart_df[date_column] = (
        pd.to_datetime(
            chart_df[date_column],
            errors="coerce"
        )
    )

    chart_df = (
        chart_df
        .dropna(
            subset=[
                date_column
            ]
        )
        .sort_values(
            date_column
        )
    )

    if chart_df.empty:

        raise ValueError(
            "No valid date values found."
        )

    metrics = [
        column
        for column in numeric_columns
        if column != date_column
    ]

    if not metrics:

        raise ValueError(
            "No numeric metrics found."
        )

    change_columns = (
        find_change_columns(
            metrics
        )
    )

    primary_metric = select_metric(
        [
            column
            for column in metrics
            if column not in change_columns
        ]
        or metrics,
        chart_df
    )

    if primary_metric is None:

        raise ValueError(
            "Unable to identify a primary metric."
        )

    chart_df[primary_metric] = (
        pd.to_numeric(
            chart_df[primary_metric],
            errors="coerce"
        )
    )

    chart_df = (
        chart_df
        .dropna(
            subset=[
                primary_metric
            ]
        )
    )

    # -----------------------------------------------------
    # Revenue / metric + change
    # -----------------------------------------------------

    if change_columns:

        change_column = (
            change_columns[0]
        )

        chart_df[change_column] = (
            pd.to_numeric(
                chart_df[
                    change_column
                ],
                errors="coerce"
            )
        )

        fig = px.line(
            chart_df,
            x=date_column,
            y=[
                primary_metric,
                change_column
            ],
            markers=True,
            title=(
                f"{pretty_name(primary_metric)} "
                f"Over Time"
            )
        )

    # -----------------------------------------------------
    # Multiple meaningful metrics
    # -----------------------------------------------------

    elif len(metrics) > 1:

        selected_metrics = []

        ranked = sorted(
            metrics,
            key=score_metric,
            reverse=True
        )

        for column in ranked:

            if column not in selected_metrics:

                selected_metrics.append(
                    column
                )

            if len(
                selected_metrics
            ) == 3:

                break

        fig = px.line(
            chart_df,
            x=date_column,
            y=selected_metrics,
            markers=True,
            title=(
                f"Business Metrics "
                f"Over Time"
            )
        )

    # -----------------------------------------------------
    # Single metric
    # -----------------------------------------------------

    else:

        fig = px.line(
            chart_df,
            x=date_column,
            y=primary_metric,
            markers=True,
            title=(
                f"{pretty_name(primary_metric)} "
                f"Over Time"
            )
        )

    fig.update_layout(
        xaxis_title=pretty_name(
            date_column
        ),
        yaxis_title="Value",
        template="plotly_dark",
        margin=dict(
            l=50,
            r=30,
            t=70,
            b=50
        ),
        hovermode="x unified"
    )

    return fig


# =========================================================
# CATEGORY CHART
# =========================================================

def create_category_chart(
    df,
    categorical_columns,
    numeric_columns
):

    category_column = (
        select_category(
            categorical_columns,
            df
        )
    )

    value_column = (
        select_metric(
            numeric_columns,
            df
        )
    )

    if category_column is None:

        raise ValueError(
            "No suitable category found."
        )

    if value_column is None:

        raise ValueError(
            "No suitable metric found."
        )

    chart_df = df.copy()

    chart_df[value_column] = (
        pd.to_numeric(
            chart_df[value_column],
            errors="coerce"
        )
    )

    chart_df = (
        chart_df
        .dropna(
            subset=[
                category_column,
                value_column
            ]
        )
    )

    if chart_df.empty:

        raise ValueError(
            "No valid category data found."
        )

    # Aggregate duplicated categories
    if (
        chart_df[
            category_column
        ].duplicated()
        .any()
    ):

        chart_df = (
            chart_df
            .groupby(
                category_column,
                as_index=False
            )[value_column]
            .sum()
        )

    chart_df = (
        chart_df
        .sort_values(
            value_column,
            ascending=False
        )
    )

    # Top-N detection
    if len(chart_df) > 15:

        chart_df = (
            chart_df
            .head(15)
        )

    # Horizontal bar for many categories
    if len(chart_df) >= 6:

        fig = px.bar(
            chart_df,
            x=value_column,
            y=category_column,
            orientation="h",
            title=(
                f"{pretty_name(value_column)} "
                f"by "
                f"{pretty_name(category_column)}"
            )
        )

    else:

        fig = px.bar(
            chart_df,
            x=category_column,
            y=value_column,
            title=(
                f"{pretty_name(value_column)} "
                f"by "
                f"{pretty_name(category_column)}"
            )
        )

    fig.update_layout(
        xaxis_title=pretty_name(
            value_column
        ),
        yaxis_title=pretty_name(
            category_column
        ),
        template="plotly_dark",
        margin=dict(
            l=50,
            r=30,
            t=70,
            b=70
        )
    )

    return fig


# =========================================================
# SCATTER
# =========================================================

def create_scatter_chart(
    df,
    numeric_columns
):

    if len(numeric_columns) < 2:

        raise ValueError(
            "At least two numeric columns "
            "are required."
        )

    ranked = sorted(
        numeric_columns,
        key=score_metric,
        reverse=True
    )

    y_column = ranked[0]
    x_column = ranked[1]

    chart_df = df[
        [
            x_column,
            y_column
        ]
    ].copy()

    chart_df[x_column] = (
        pd.to_numeric(
            chart_df[x_column],
            errors="coerce"
        )
    )

    chart_df[y_column] = (
        pd.to_numeric(
            chart_df[y_column],
            errors="coerce"
        )
    )

    chart_df = (
        chart_df
        .dropna()
    )

    if chart_df.empty:

        raise ValueError(
            "No valid numeric data found."
        )

    fig = px.scatter(
        chart_df,
        x=x_column,
        y=y_column,
        title=(
            f"{pretty_name(y_column)} "
            f"vs "
            f"{pretty_name(x_column)}"
        )
    )

    fig.update_layout(
        xaxis_title=pretty_name(
            x_column
        ),
        yaxis_title=pretty_name(
            y_column
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


# =========================================================
# PIE CHART
# =========================================================

def create_pie_chart(
    df,
    category_column,
    value_column
):

    chart_df = df.copy()

    chart_df[value_column] = (
        pd.to_numeric(
            chart_df[value_column],
            errors="coerce"
        )
    )

    chart_df = (
        chart_df
        .dropna(
            subset=[
                category_column,
                value_column
            ]
        )
    )

    chart_df = (
        chart_df
        .groupby(
            category_column,
            as_index=False
        )[value_column]
        .sum()
    )

    chart_df = (
        chart_df
        .sort_values(
            value_column,
            ascending=False
        )
    )

    if len(chart_df) > 6:

        return create_category_chart(
            chart_df,
            [
                category_column
            ],
            [
                value_column
            ]
        )

    fig = px.pie(
        chart_df,
        names=category_column,
        values=value_column,
        title=(
            f"{pretty_name(value_column)} "
            f"Distribution"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        margin=dict(
            l=30,
            r=30,
            t=70,
            b=30
        )
    )

    return fig


# =========================================================
# MAIN ADAPTIVE VISUALIZATION ENGINE
# =========================================================

def create_chart(
    df: pd.DataFrame
):

    if df is None:

        raise ValueError(
            "No data available."
        )

    if not isinstance(
        df,
        pd.DataFrame
    ):

        df = pd.DataFrame(df)

    if df.empty:

        raise ValueError(
            "Cannot visualize empty data."
        )

    chart_df = df.copy()

    # -----------------------------------------------------
    # Normalize column values
    # -----------------------------------------------------

    date_columns = find_date_columns(
        chart_df
    )

    for column in date_columns:

        chart_df[column] = (
            pd.to_datetime(
                chart_df[column],
                errors="coerce"
            )
        )

    numeric_columns = (
        find_numeric_columns(
            chart_df
        )
    )

    categorical_columns = (
        find_categorical_columns(
            chart_df,
            date_columns
        )
    )

    # -----------------------------------------------------
    # CASE 1 — SINGLE VALUE / KPI
    # -----------------------------------------------------

    if (
        len(chart_df) == 1
        and numeric_columns
        and not date_columns
        and not categorical_columns
    ):

        metric = select_metric(
            numeric_columns,
            chart_df
        )

        return create_kpi(
            chart_df,
            metric
        )

    # -----------------------------------------------------
    # CASE 2 — TIME SERIES
    # -----------------------------------------------------

    if (
        date_columns
        and numeric_columns
        and len(chart_df) >= 2
    ):

        date_column = (
            date_columns[0]
        )

        return create_time_chart(
            chart_df,
            date_column,
            numeric_columns
        )

    # -----------------------------------------------------
    # CASE 3 — CATEGORY + METRIC
    # -----------------------------------------------------

    if (
        categorical_columns
        and numeric_columns
    ):

        return create_category_chart(
            chart_df,
            categorical_columns,
            numeric_columns
        )

    # -----------------------------------------------------
    # CASE 4 — TWO NUMERIC VARIABLES
    # -----------------------------------------------------

    if len(numeric_columns) >= 2:

        return create_scatter_chart(
            chart_df,
            numeric_columns
        )

    # -----------------------------------------------------
    # CASE 5 — ONE NUMERIC COLUMN
    # -----------------------------------------------------

    if numeric_columns:

        metric = select_metric(
            numeric_columns,
            chart_df
        )

        if len(chart_df) == 1:

            return create_kpi(
                chart_df,
                metric
            )

    # -----------------------------------------------------
    # FINAL FALLBACK
    # -----------------------------------------------------

    raise ValueError(
        "No suitable visualization could be "
        "automatically generated for this result."
    )


# =========================================================
# LOCAL TESTS
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ADAPTIVE VISUALIZATION TESTS")
    print("=" * 60)


    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------

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
            "test_kpi.html"
        )

        print(
            "✅ KPI test passed"
        )

    except Exception as e:

        print(
            "❌ KPI test failed:",
            e
        )


    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

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
            "test_category.html"
        )

        print(
            "✅ Category test passed"
        )

    except Exception as e:

        print(
            "❌ Category test failed:",
            e
        )


    # -----------------------------------------------------
    # TIME SERIES
    # -----------------------------------------------------

    monthly_df = pd.DataFrame(
        {
            "month": [
                "2025-06-01",
                "2025-07-01",
                "2025-08-01",
                "2025-09-01",
                "2025-10-01",
                "2025-11-01"
            ],
            "total_revenue": [
                1637081.42,
                2084828.57,
                1620934.28,
                1860427.62,
                1649336.20,
                1735249.50
            ],
            "revenue_change": [
                -163182.79,
                447747.15,
                -463894.29,
                239493.34,
                -211091.42,
                85913.30
            ]
        }
    )

    try:

        fig = create_chart(
            monthly_df
        )

        fig.write_html(
            "test_time_series.html"
        )

        print(
            "✅ Time-series test passed"
        )

    except Exception as e:

        print(
            "❌ Time-series test failed:",
            e
        )


    # -----------------------------------------------------
    # SCATTER
    # -----------------------------------------------------

    scatter_df = pd.DataFrame(
        {
            "quantity": [
                10,
                20,
                30,
                40,
                50
            ],
            "revenue": [
                1000,
                2400,
                3200,
                4100,
                5300
            ]
        }
    )

    try:

        fig = create_chart(
            scatter_df
        )

        fig.write_html(
            "test_scatter.html"
        )

        print(
            "✅ Scatter test passed"
        )

    except Exception as e:

        print(
            "❌ Scatter test failed:",
            e
        )


    # -----------------------------------------------------
    # MULTIPLE METRICS
    # -----------------------------------------------------

    metrics_df = pd.DataFrame(
        {
            "month": [
                "2025-06",
                "2025-07",
                "2025-08"
            ],
            "revenue": [
                100000,
                120000,
                110000
            ],
            "profit": [
                20000,
                28000,
                24000
            ]
        }
    )

    try:

        fig = create_chart(
            metrics_df
        )

        fig.write_html(
            "test_multiple_metrics.html"
        )

        print(
            "✅ Multiple-metric test passed"
        )

    except Exception as e:

        print(
            "❌ Multiple-metric test failed:",
            e
        )


    print("=" * 60)
    print(
        "ADAPTIVE VISUALIZATION TESTS COMPLETE"
    )
    print("=" * 60)