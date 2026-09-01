import pandas as pd

from app.graph.state import BusinessAnalystState

from app.agents.business_agent import (
    is_root_cause_question,
    get_visualization_data
)

from app.agents.sql_generator import (
    generate_sql
)

from app.agents.sql_validator import (
    validate_sql
)

from app.agents.query_executor import (
    execute_query
)

from app.analytics.analysis import (
    analyze_dataframe
)

from app.analytics.question_parser import (
    get_target_month
)

from app.analytics.root_cause_request import (
    parse_root_cause_request
)

from app.analytics.monthly_analysis import (
    get_monthly_revenue,
    compare_months,
    find_biggest_drop,
    find_biggest_increase,
    get_month_comparison
)

from app.analytics.root_cause import (
    analyze_category_change
)

from app.analytics.product_root_cause import (
    analyze_product_change
)

from app.agents.deep_root_cause_agent import (
    generate_deep_root_cause_insight
)

from app.agents.insight_generator import (
    generate_insight
)

from app.llm.llm_client import (
    generate_text
)


# =========================================================
# DATABASE SCHEMA
# =========================================================

DATABASE_SCHEMA = """
Database: business_analytics

Tables:

regions
- region_id INTEGER PRIMARY KEY
- region_name VARCHAR(100)

sales_channels
- channel_id INTEGER PRIMARY KEY
- channel_name VARCHAR(100)

customers
- customer_id INTEGER PRIMARY KEY
- customer_name VARCHAR(150)
- email VARCHAR(200)
- region_id INTEGER FOREIGN KEY REFERENCES regions(region_id)

products
- product_id INTEGER PRIMARY KEY
- product_name VARCHAR(150)
- category VARCHAR(100)
- price NUMERIC
- cost NUMERIC

orders
- order_id INTEGER PRIMARY KEY
- customer_id INTEGER FOREIGN KEY REFERENCES customers(customer_id)
- region_id INTEGER FOREIGN KEY REFERENCES regions(region_id)
- channel_id INTEGER FOREIGN KEY REFERENCES sales_channels(channel_id)
- order_date DATE

order_items
- order_item_id INTEGER PRIMARY KEY
- order_id INTEGER FOREIGN KEY REFERENCES orders(order_id)
- product_id INTEGER FOREIGN KEY REFERENCES products(product_id)
- quantity INTEGER
- unit_price NUMERIC
- revenue NUMERIC
- cost NUMERIC
- profit NUMERIC
"""


def is_increase_question(question: str) -> bool:
    """Return whether a root-cause request asks about growth, not decline."""

    normalized_question = question.lower()

    return any(
        term in normalized_question
        for term in (
            "increase",
            "increased",
            "grew",
            "growth",
            "gain",
        )
    )


# =========================================================
# NODE 1 — CLASSIFY QUESTION
# =========================================================

def classify_question(
    state: BusinessAnalystState
):

    question = state["question"]

    print(
        "\n🧠 Classifying question..."
    )

    try:

        if is_root_cause_question(
            question
        ):

            intent = "root_cause"

        else:

            intent = "analytics"

        print(
            f"🧠 Intent detected: {intent}"
        )

        return {

            "intent":
                intent,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ Question classification failed:"
        )

        print(e)

        return {

            "error":
                str(e)
        }


# =========================================================
# NODE 2 — GENERATE SQL
# =========================================================

def generate_sql_node(
    state: BusinessAnalystState
):

    question = state["question"]

    print(
        "\n🤖 Generating SQL..."
    )

    try:

        sql, provider = generate_sql(
            question
        )

        print(
            f"\n✅ SQL generated using: {provider}"
        )

        return {

            "sql":
                sql,

            "provider":
                provider,

            "sql_valid":
                False,

            "sql_validation_message":
                None,

            "execution_error":
                None,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ SQL generation failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "error":
                str(e)
        }


# =========================================================
# NODE 3 — VALIDATE SQL
# =========================================================

def validate_sql_node(
    state: BusinessAnalystState
):

    sql = state.get(
        "sql"
    )

    if not sql:

        return {

            "sql_valid":
                False,

            "sql_validation_message":
                "No SQL was generated.",

            "error":
                "No SQL was generated."
        }

    print(
        "\n🔐 Validating SQL..."
    )

    try:

        is_valid, message = (
            validate_sql(
                sql
            )
        )

        if is_valid:

            print(
                "✅ SQL validation passed."
            )

        else:

            print(
                "❌ SQL validation failed."
            )

            print(
                f"Reason: {message}"
            )

        return {

            "sql_valid":
                is_valid,

            "sql_validation_message":
                message,

            "error":
                None
                if is_valid
                else message
        }

    except Exception as e:

        print(
            "\n❌ SQL validation error:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "sql_valid":
                False,

            "sql_validation_message":
                str(e),

            "error":
                str(e)
        }


# =========================================================
# NODE 4 — REPAIR SQL
# =========================================================

def repair_sql_node(
    state: BusinessAnalystState
):
    """
    Repair SQL using the LLM.

    The repair can be triggered by:

    1. SQL validation failure
    2. PostgreSQL execution failure
    """

    question = state["question"]

    current_sql = state.get(
        "sql"
    )

    validation_error = state.get(
        "sql_validation_message"
    )

    execution_error = state.get(
        "execution_error"
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    # =====================================================
    # DETERMINE ERROR SOURCE
    # =====================================================

    if execution_error:

        error_source = (
            "DATABASE EXECUTION ERROR"
        )

        actual_error = (
            execution_error
        )

    else:

        error_source = (
            "SQL VALIDATION ERROR"
        )

        actual_error = (
            validation_error
        )

    print(
        "\n🔧 Attempting SQL repair..."
    )

    print(
        f"Repair attempt: {retry_count + 1}"
    )

    print(
        f"Error source: {error_source}"
    )

    # =====================================================
    # REPAIR PROMPT
    # =====================================================

    prompt = f"""
You are an expert PostgreSQL SQL debugging agent.

A previous AI-generated SQL query failed.

USER BUSINESS QUESTION:

{question}


PREVIOUS SQL:

{current_sql}


ERROR TYPE:

{error_source}


ERROR:

{actual_error}


DATABASE SCHEMA:

{DATABASE_SCHEMA}


YOUR TASK:

Repair the SQL query so that it correctly answers
the original business question.

STRICT RULES:

1. Preserve the original business intent.
2. Use ONLY tables and columns from the schema.
3. Use PostgreSQL syntax.
4. Generate ONLY SELECT or WITH queries.
5. Never generate INSERT.
6. Never generate UPDATE.
7. Never generate DELETE.
8. Never generate DROP.
9. Never generate ALTER.
10. Never generate CREATE.
11. Never generate TRUNCATE.
12. Never generate GRANT.
13. Never generate REVOKE.
14. Correct the specific error shown above.
15. Do not invent tables.
16. Do not invent columns.
17. Return ONLY the corrected SQL.
18. Do not use markdown.
19. Do not explain the correction.
"""

    try:

        response, provider = (
            generate_text(
                prompt
            )
        )

        repaired_sql = (
            response.strip()
        )

        # =================================================
        # REMOVE MARKDOWN FENCES
        # =================================================

        if repaired_sql.startswith(
            "```sql"
        ):

            repaired_sql = (
                repaired_sql[
                    len("```sql"):
                ]
            )

        elif repaired_sql.startswith(
            "```"
        ):

            repaired_sql = (
                repaired_sql[
                    len("```"):
                ]
            )

        if repaired_sql.endswith(
            "```"
        ):

            repaired_sql = (
                repaired_sql[
                    :-3
                ]
            )

        repaired_sql = (
            repaired_sql.strip()
        )

        # =================================================
        # BASIC SAFETY CHECK
        # =================================================

        if not repaired_sql:

            raise RuntimeError(
                "SQL repair returned an empty query."
            )

        repaired_upper = (
            repaired_sql
            .upper()
            .strip()
        )

        if not (
            repaired_upper.startswith(
                "SELECT"
            )
            or
            repaired_upper.startswith(
                "WITH"
            )
        ):

            raise ValueError(
                "SQL repair generated a "
                "non-SELECT statement."
            )

        # =================================================
        # UPDATE RETRY COUNT
        # =================================================

        new_retry_count = (
            retry_count + 1
        )

        print(
            f"✅ SQL repaired using: {provider}"
        )

        print(
            "\nRepaired SQL:"
        )

        print(
            "-" * 60
        )

        print(
            repaired_sql
        )

        print(
            "-" * 60
        )

        return {

            "sql":
                repaired_sql,

            "provider":
                provider,

            "retry_count":
                new_retry_count,

            "sql_valid":
                False,

            "sql_validation_message":
                None,

            "execution_error":
                None,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ SQL repair failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "retry_count":
                retry_count + 1,

            "error":
                str(e)
        }


# =========================================================
# NODE 5 — EXECUTE SQL
# =========================================================

def execute_sql_node(
    state: BusinessAnalystState
):
    """
    Execute validated SQL.

    IMPORTANT:

    A SQL query can pass our static validator but still
    fail inside PostgreSQL.

    Example:

        SELECT ...
        FROM productss

    may be structurally safe but PostgreSQL can report:

        relation "productss" does not exist

    Therefore database errors are captured in
    execution_error and routed back to SQL repair.
    """

    sql = state.get(
        "sql"
    )

    if not sql:

        return {

            "execution_success":
                False,

            "execution_error":
                "No SQL available for execution.",

            "error":
                "No SQL available for execution."
        }

    if not state.get(
        "sql_valid",
        False
    ):

        return {

            "execution_success":
                False,

            "execution_error":
                "SQL execution blocked because validation failed.",

            "error":
                "SQL execution blocked because validation failed."
        }

    print(
        "\n🗄️ Executing SQL..."
    )

    try:

        df = execute_query(
            sql
        )

        if df.empty:

            print(
                "⚠️ Query returned no data."
            )

        else:

            print(
                f"✅ {len(df)} row(s) returned."
            )

        return {

            "data":
                df,

            "execution_success":
                True,

            "execution_error":
                None,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ Database execution failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        # =================================================
        # IMPORTANT
        #
        # DO NOT terminate the workflow.
        #
        # Store the database error so the repair node
        # can see exactly what PostgreSQL rejected.
        # =================================================

        return {

            "execution_success":
                False,

            "execution_error":
                str(e),

            "error":
                str(e)
        }


# =========================================================
# NODE 6 — ANALYZE DATA
# =========================================================

def analyze_data_node(
    state: BusinessAnalystState
):

    df = state.get(
        "data"
    )

    if df is None:

        return {

            "error":
                "No database data is available."
        }

    if df.empty:

        print(
            "\n⚠️ No data available for analysis."
        )

        return {

            "analysis":
                None,

            "error":
                None
        }

    print(
        "\n📊 Analyzing data..."
    )

    try:

        analysis = (
            analyze_dataframe(
                df
            )
        )

        return {

            "analysis":
                analysis,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ Data analysis failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "error":
                str(e)
        }


# =========================================================
# NODE 7 — VISUALIZATION DATA
# =========================================================

def visualization_data_node(
    state: BusinessAnalystState
):

    sql = state.get(
        "sql"
    )

    df = state.get(
        "data"
    )

    if df is None:

        return {

            "visualization_data":
                pd.DataFrame(),

            "error":
                "No data available for visualization."
        }

    print(
        "\n📈 Preparing visualization data..."
    )

    try:

        visualization_df = (
            get_visualization_data(
                sql,
                df
            )
        )

        if visualization_df is None:

            visualization_df = df

        print(
            "✅ Visualization data prepared."
        )

        print(
            f"Rows for visualization: "
            f"{len(visualization_df)}"
        )

        return {

            "visualization_data":
                visualization_df,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n⚠️ Visualization data expansion failed."
        )

        print(
            str(e)
        )

        print(
            "Using original query data."
        )

        return {

            "visualization_data":
                df,

            "error":
                None
        }


# =========================================================
# NODE 8 — GENERATE BUSINESS INSIGHT
# =========================================================

def generate_insight_node(
    state: BusinessAnalystState
):

    question = state["question"]

    sql = state.get(
        "sql"
    )

    df = state.get(
        "data"
    )

    analysis = state.get(
        "analysis"
    )

    if df is None:

        return {

            "error":
                "No data available for insight generation."
        }

    if df.empty:

        return {

            "error":
                "No data available for insight generation."
        }

    print(
        "\n💡 Generating business insight..."
    )

    try:

        results = (
            df.to_dict(
                orient="records"
            )
        )

        insight, provider = (
            generate_insight(

                question=
                    question,

                sql=
                    sql,

                results=
                    results,

                analysis=
                    analysis
            )
        )

        print(
            f"💡 Insight generated using: {provider}"
        )

        return {

            "insight":
                insight,

            "provider":
                provider,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ Business insight generation failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "insight":
                "Query results are available, but the AI "
                "business insight could not be generated "
                "because the LLM provider was unavailable.",

            "error":
                None
        }


# =========================================================
# NODE 9 — ROOT CAUSE ANALYSIS
# =========================================================

def root_cause_analysis_node(
    state: BusinessAnalystState
):

    question = state["question"]

    print(
        "\n🔍 Running root-cause analysis..."
    )

    try:

        root_cause_request = parse_root_cause_request(question)

        target_month = (
            get_target_month(
                question
            )
        )

        monthly_df = (
            get_monthly_revenue()
        )

        if monthly_df is None:

            return {

                "error":
                    "Monthly revenue analysis returned no data."
            }

        if monthly_df.empty:

            return {

                "error":
                    "No monthly revenue data found."
            }

        monthly_df = compare_months(
            monthly_df
        )

        if target_month:

            target_row = (
                get_month_comparison(

                    monthly_df,

                    target_month[
                        "month"
                    ],

                    target_month[
                        "year"
                    ]
                )
            )

        else:

            period_source = (
                "largest_increase"
                if root_cause_request["direction"] == "increase"
                else "largest_decline"
            )

            target_row = (
                (
                    find_biggest_increase
                    if period_source == "largest_increase"
                    else find_biggest_drop
                )(
                    monthly_df
                )
            )

        if target_month:

            period_source = "user_specified"

        if target_row is None:

            return {

                "error":
                    "Target month could not be found."
            }

        current_month_date = (
            target_row[
                "month"
            ]
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

        print(
            "\n📊 Analyzing category drivers..."
        )

        category_df = (
            analyze_category_change(

                previous_month,

                current_month
            )
        )

        print(
            "\n📦 Analyzing product drivers..."
        )

        product_df = (
            analyze_product_change(

                previous_month,

                current_month
            )
        )

        print(
            "\n🤖 Generating deep root-cause insight..."
        )

        insight = None
        provider = None

        try:

            insight, provider = (
                generate_deep_root_cause_insight(

                    previous_month=
                        previous_month_date.strftime(
                            "%B %Y"
                        ),

                    current_month=
                        current_month_date.strftime(
                            "%B %Y"
                        ),

                    previous_total=
                        previous_total,

                    current_total=
                        current_total,

                    category_df=
                        category_df,

                product_df=
                    product_df,

                question=
                    question,

                period_source=period_source,

                focus=root_cause_request["focus"]
            )
            )

            print(
                f"✅ Root-cause analysis generated using: "
                f"{provider}"
            )

        except Exception as insight_error:

            print(
                "\n⚠️ Deep root-cause insight generation failed."
            )

            print(
                insight_error
            )

            insight = (
                "Automated revenue driver analysis completed, "
                "but the AI insight could not be generated "
                "because the LLM provider was unavailable."
            )

        return {

            "target_month":
                target_month,

            "root_cause_focus":
                root_cause_request["focus"],

            "root_cause_direction":
                root_cause_request["direction"],

            "period_source":
                period_source,

            "previous_month":
                previous_month,

            "current_month":
                current_month,

            "previous_total":
                previous_total,

            "current_total":
                current_total,

            "revenue_change":
                revenue_change,

            "revenue_change_percent":
                revenue_change_percent,

            "category_analysis":
                category_df,

            "product_analysis":
                product_df,

            "insight":
                insight,

            "provider":
                provider,

            "error":
                None
        }

    except Exception as e:

        print(
            "\n❌ Root-cause analysis failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return {

            "error":
                str(e)
        }


# =========================================================
# ROUTING — QUESTION INTENT
# =========================================================

def route_intent(
    state: BusinessAnalystState
):

    intent = state.get(
        "intent"
    )

    if intent == "root_cause":

        return "root_cause"

    return "analytics"


# =========================================================
# ROUTING — SQL VALIDATION
# =========================================================

def route_sql_validation(
    state: BusinessAnalystState
):
    """
    Route after SQL validation.

    Valid SQL:
        → execute

    Invalid SQL:
        → repair

    Maximum repair attempts:
        → end
    """

    if state.get(
        "sql_valid",
        False
    ):

        return "execute"

    retry_count = state.get(
        "retry_count",
        0
    )

    if retry_count >= 2:

        print(
            "\n❌ Maximum SQL repair attempts reached."
        )

        return "end"

    print(
        "\n🔄 SQL requires repair."
    )

    return "repair"


# =========================================================
# ROUTING — DATABASE EXECUTION
# =========================================================

def route_execution(
    state: BusinessAnalystState
):
    """
    Route after database execution.

    Successful execution:
        → analyze

    Database failure:
        → repair SQL

    Maximum repair attempts:
        → end
    """

    if state.get(
        "execution_success",
        False
    ):

        return "analyze"

    retry_count = state.get(
        "retry_count",
        0
    )

    if retry_count >= 2:

        print(
            "\n❌ Maximum SQL repair attempts reached "
            "after database error."
        )

        return "end"

    print(
        "\n🔄 Database rejected the SQL."
    )

    print(
        "🔧 Routing database error to SQL repair..."
    )

    return "repair"
