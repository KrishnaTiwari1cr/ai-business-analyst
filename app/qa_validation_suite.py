"""
Comprehensive QA validation suite for AI Business Analyst.
Run: .venv/bin/python app/qa_validation_suite.py
"""
import json
import re
import sys
import traceback
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy import text

from app.agents.business_agent import is_root_cause_question
from app.agents.query_executor import execute_query
from app.agents.sql_validator import validate_sql
from app.analytics.monthly_analysis import (
    compare_months,
    find_biggest_drop,
    get_month_comparison,
    get_monthly_revenue,
)
from app.analytics.question_parser import get_target_month
from app.analytics.root_cause import analyze_category_change
from app.analytics.visualization import create_chart
from app.database.connection import engine
from app.graph.business_graph import run_business_graph


class TestResult:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.status = "PASS"
        self.details: list[str] = []
        self.warnings: list[str] = []

    def fail(self, msg: str):
        self.status = "FAIL"
        self.details.append(msg)

    def warn(self, msg: str):
        if self.status == "PASS":
            self.status = "WARN"
        self.warnings.append(msg)


def to_float(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    return float(val)


def load_ground_truth() -> dict:
    with engine.connect() as conn:
        kpis = conn.execute(
            text(
                """
                SELECT
                    SUM(oi.revenue) AS total_revenue,
                    SUM(oi.profit) AS total_profit,
                    COUNT(DISTINCT o.order_id) AS total_orders,
                    COUNT(DISTINCT o.customer_id) AS total_customers,
                    SUM(oi.quantity) AS total_quantity
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                """
            )
        ).fetchone()

        top_cat = conn.execute(
            text(
                """
                SELECT p.category, SUM(oi.revenue) AS rev
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                GROUP BY p.category
                ORDER BY rev DESC
                LIMIT 1
                """
            )
        ).fetchone()

        monthly = get_monthly_revenue()
        monthly = compare_months(monthly)

    return {
        "total_revenue": to_float(kpis.total_revenue),
        "total_profit": to_float(kpis.total_profit),
        "total_orders": int(kpis.total_orders),
        "total_customers": int(kpis.total_customers),
        "total_quantity": int(kpis.total_quantity),
        "avg_order_value": to_float(kpis.total_revenue) / int(kpis.total_orders),
        "top_category": top_cat.category,
        "top_category_revenue": to_float(top_cat.rev),
        "monthly": monthly,
    }


def check_sql_schema(sql: str) -> list[str]:
    issues = []
    if not sql:
        return ["No SQL generated"]
    lower = sql.lower()
    if "orders.total_amount" in lower or "order.total_amount" in lower:
        issues.append("Hallucinated orders.total_amount column")
    if "total_amount" in lower and "order_items" not in lower:
        issues.append("Possible hallucinated total_amount without order_items")
    return issues


def extract_single_numeric(df: pd.DataFrame) -> float | None:
    if df is None or df.empty:
        return None
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        for col in df.columns:
            try:
                return to_float(df[col].iloc[0])
            except (TypeError, ValueError):
                continue
        return None
    return to_float(numeric.iloc[0, 0])


def test_sql_validator() -> list[TestResult]:
    results = []
    cases = [
        ("valid_select_limit", "SELECT * FROM products LIMIT 10", True),
        ("valid_aggregate", "SELECT category, SUM(revenue) FROM order_items oi JOIN products p ON oi.product_id=p.product_id GROUP BY category", True),
        ("invalid_delete", "DELETE FROM customers", False),
        ("invalid_drop", "DROP TABLE customers", False),
        ("invalid_update", "UPDATE customers SET customer_name='x'", False),
        ("invalid_insert", "INSERT INTO customers VALUES (1)", False),
        ("invalid_alter", "ALTER TABLE customers ADD col INT", False),
        ("invalid_create", "CREATE TABLE hack (id INT)", False),
        ("invalid_truncate", "TRUNCATE customers", False),
        ("invalid_grant", "GRANT ALL ON customers TO public", False),
        ("invalid_revoke", "REVOKE ALL ON customers FROM public", False),
        ("multi_stmt", "SELECT 1; DELETE FROM products", False),
        ("comment", "SELECT * FROM products LIMIT 1 -- evil", False),
        ("no_limit_plain", "SELECT * FROM products", False),
    ]
    for name, sql, expected in cases:
        tr = TestResult(name, "SQL Validation")
        ok, msg = validate_sql(sql)
        if ok != expected:
            tr.fail(f"Expected valid={expected}, got valid={ok}: {msg}")
        results.append(tr)
    return results


def test_visualization_matrix() -> list[TestResult]:
    results = []
    cases = [
        ("kpi", pd.DataFrame({"total_revenue": [43501095.73]})),
        (
            "category",
            pd.DataFrame(
                {
                    "category": ["A", "B", "C"],
                    "total_revenue": [100, 200, 150],
                }
            ),
        ),
        (
            "time_series",
            pd.DataFrame(
                {
                    "month": pd.to_datetime(
                        ["2025-06-01", "2025-07-01", "2025-08-01"]
                    ),
                    "total_revenue": [100, 120, 110],
                }
            ),
        ),
        (
            "multi_metric_time",
            pd.DataFrame(
                {
                    "month": ["2025-06", "2025-07"],
                    "revenue": [100, 120],
                    "profit": [20, 28],
                }
            ),
        ),
        (
            "scatter",
            pd.DataFrame({"quantity": [1, 2, 3], "revenue": [10, 20, 30]}),
        ),
        (
            "numeric_strings",
            pd.DataFrame({"category": ["A", "B"], "revenue": ["100", "200"]}),
        ),
    ]
    for name, df in cases:
        tr = TestResult(name, "Visualization")
        try:
            fig = create_chart(df)
            if fig is None:
                tr.fail("create_chart returned None")
        except Exception as e:
            tr.fail(str(e))
        results.append(tr)

    tr = TestResult("empty_dataframe", "Visualization")
    try:
        create_chart(pd.DataFrame())
        tr.fail("Expected error for empty DataFrame")
    except ValueError:
        pass
    except Exception as e:
        tr.warn(f"Unexpected exception type: {e}")
    results.append(tr)

    return results


def test_root_cause_pipeline(gt: dict) -> list[TestResult]:
    results = []

    tr = TestResult("generic_why_drop", "Root Cause")
    try:
        monthly = get_monthly_revenue()
        monthly = compare_months(monthly)
        drop = find_biggest_drop(monthly)
        if drop is None:
            tr.fail("No revenue drop found in data")
        else:
            prev = drop["month"] - pd.DateOffset(months=1)
            cat = analyze_category_change(
                prev.strftime("%Y-%m-%d"),
                drop["month"].strftime("%Y-%m-%d"),
            )
            if cat.empty:
                tr.fail("Category analysis empty")
            elif cat.iloc[0]["revenue_change"] > 0:
                tr.warn("Biggest drop month has positive top category change")
    except Exception as e:
        tr.fail(str(e))
    results.append(tr)

    tr = TestResult("september_2025", "Root Cause")
    try:
        monthly = compare_months(get_monthly_revenue())
        row = get_month_comparison(monthly, 9, 2025)
        if row is None:
            tr.fail("September 2025 not found")
        else:
            expected_rev = row["revenue"]
            db_row = gt["monthly"][
                (gt["monthly"]["month"].dt.month == 9)
                & (gt["monthly"]["month"].dt.year == 2025)
            ]
            if db_row.empty:
                tr.fail("No September 2025 in ground truth")
            elif abs(to_float(expected_rev) - to_float(db_row.iloc[0]["revenue"])) > 0.01:
                tr.fail("September revenue mismatch")
    except Exception as e:
        tr.fail(str(e))
    results.append(tr)

    tr = TestResult("target_month_parser", "Root Cause")
    tm = get_target_month("Why did revenue drop in September 2025?")
    if tm != {"month": 9, "year": 2025}:
        tr.fail(f"Expected month 9/2025, got {tm}")
    results.append(tr)

    tr = TestResult("root_cause_intent", "Root Cause")
    if not is_root_cause_question("Why did revenue drop?"):
        tr.fail("Failed to detect root cause question")
    if is_root_cause_question("What is total revenue?"):
        tr.fail("False positive root cause detection")
    results.append(tr)

    return results


def test_pipeline_question(
    question: str,
    category: str,
    gt: dict,
    check_fn=None,
    skip_llm: bool = False,
) -> TestResult:
    tr = TestResult(question[:60], category)

    if skip_llm:
        tr.warn("LLM pipeline skipped (--quick mode)")
        return tr

    try:
        result = run_business_graph(question)
    except Exception as e:
        tr.fail(f"Pipeline exception: {e}")
        return tr

    intent = result.get("intent")
    error = result.get("error")
    sql = result.get("sql")
    data = result.get("data")
    viz = result.get("visualization_data")
    insight = result.get("insight")

    if error and not result.get("execution_success"):
        tr.fail(f"Pipeline error: {error}")
        return tr

    if intent == "root_cause":
        if result.get("previous_total") is None:
            tr.fail("Root cause missing previous_total")
        if not insight:
            tr.fail("Root cause missing insight")
        if check_fn:
            check_fn(tr, result, gt)
        return tr

    if not sql:
        tr.fail("No SQL generated")
        return tr

    schema_issues = check_sql_schema(sql)
    for issue in schema_issues:
        tr.fail(issue)

    if not result.get("sql_valid"):
        tr.fail(f"SQL validation failed: {result.get('sql_validation_message')}")

    if not result.get("execution_success"):
        tr.fail(f"Execution failed: {result.get('execution_error')}")

    if data is None or data.empty:
        tr.fail("Empty DataFrame returned")
        return tr

    chart_df = viz if viz is not None and not viz.empty else data
    try:
        fig = create_chart(chart_df)
        if fig is None:
            tr.fail("Visualization returned None")
    except Exception as e:
        tr.fail(f"Visualization failed: {e}")

    if not insight:
        tr.warn("No insight generated")

    if check_fn:
        check_fn(tr, result, gt)

    return tr


def run_llm_pipeline_tests(gt: dict, quick: bool = False) -> list[TestResult]:
    results = []

    kpi_checks = [
        (
            "What is the total revenue?",
            lambda tr, r, g: (
                tr.fail("Revenue mismatch")
                if abs(extract_single_numeric(r["data"]) - g["total_revenue"]) > 1
                else None
            ),
        ),
        (
            "What is the total profit?",
            lambda tr, r, g: (
                tr.fail("Profit mismatch")
                if abs(extract_single_numeric(r["data"]) - g["total_profit"]) > 1
                else None
            ),
        ),
        (
            "What is the total number of orders?",
            lambda tr, r, g: (
                tr.fail("Order count mismatch")
                if int(extract_single_numeric(r["data"])) != g["total_orders"]
                else None
            ),
        ),
    ]

    if quick:
        questions = kpi_checks[:1]
    else:
        questions = kpi_checks + [
            (
                "Which product category generated the most revenue?",
                lambda tr, r, g: (
                    tr.fail(f"Top category wrong: {r['data'].iloc[0, 0]}")
                    if str(r["data"].iloc[0, 0]).lower() != g["top_category"].lower()
                    and "category" in str(r["data"].columns[0]).lower()
                    else (
                        tr.fail("Top category revenue mismatch")
                        if len(r["data"].select_dtypes(include="number").columns) > 0
                        and abs(
                            to_float(
                                r["data"]
                                .select_dtypes(include="number")
                                .iloc[0, 0]
                            )
                            - g["top_category_revenue"]
                        )
                        > 100
                        else None
                    )
                ),
            ),
            ("Show monthly revenue.", None),
            ("What are the top 5 products by revenue?", None),
            ("Show revenue by region.", None),
            ("Show revenue by sales channel.", None),
            ("Show revenue and profit by category.", None),
            ("Why did revenue drop?", None),
            (
                "Why did revenue drop in September 2025?",
                lambda tr, r, g: (
                    tr.fail("September root cause revenue mismatch")
                    if r.get("current_total")
                    and abs(
                        to_float(r["current_total"])
                        - to_float(
                            g["monthly"][
                                (g["monthly"]["month"].dt.month == 9)
                                & (g["monthly"]["month"].dt.year == 2025)
                            ].iloc[0]["revenue"]
                        )
                    )
                    > 1
                    else None
                ),
            ),
        ]

    for q, check in questions:
        results.append(
            test_pipeline_question(q, "E2E Pipeline", gt, check_fn=check, skip_llm=False)
        )

    return results


def test_sql_repair_e2e() -> TestResult:
    from app.graph.test_end_to_end_repair import build_test_graph
    from app.graph.state import BusinessAnalystState

    tr = TestResult("sql_repair_e2e", "SQL Repair")

    invalid_sql = """
    SELECT p.category, SUM(oi.revenue) AS total_revenue
    FROM order_items oi
    JOIN productss p ON oi.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    LIMIT 1;
    """

    initial_state: BusinessAnalystState = {
        "question": "Which product category generated the most revenue?",
        "intent": "analytics",
        "target_month": None,
        "sql": invalid_sql,
        "sql_valid": False,
        "sql_validation_message": None,
        "execution_error": None,
        "execution_success": False,
        "data": None,
        "visualization_data": None,
        "analysis": None,
        "category_analysis": None,
        "product_analysis": None,
        "previous_month": None,
        "current_month": None,
        "previous_total": None,
        "current_total": None,
        "revenue_change": None,
        "revenue_change_percent": None,
        "insight": None,
        "provider": None,
        "chart_path": None,
        "error": None,
        "retry_count": 0,
    }

    try:
        result = build_test_graph().invoke(initial_state)
        if result.get("retry_count", 0) < 1:
            tr.fail(f"No repair attempted, retry_count={result.get('retry_count')}")
        if not result.get("execution_success"):
            tr.fail(f"Repair execution failed: {result.get('execution_error') or result.get('error')}")
        if result.get("retry_count", 0) > 2:
            tr.fail("Exceeded max retry count")
    except Exception as e:
        tr.fail(str(e))

    return tr


def summarize(results: list[TestResult]) -> dict:
    by_cat: dict[str, list[TestResult]] = {}
    for r in results:
        by_cat.setdefault(r.category, []).append(r)

    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    warnings = sum(1 for r in results if r.status == "WARN")

    return {
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "total": len(results),
        "by_category": {
            cat: {
                "tests": len(items),
                "passed": sum(1 for x in items if x.status == "PASS"),
                "failed": sum(1 for x in items if x.status == "FAIL"),
                "warnings": sum(1 for x in items if x.status == "WARN"),
            }
            for cat, items in by_cat.items()
        },
        "failures": [
            {
                "name": r.name,
                "category": r.category,
                "details": r.details,
                "warnings": r.warnings,
            }
            for r in results
            if r.status == "FAIL"
        ],
        "warn_items": [
            {"name": r.name, "category": r.category, "warnings": r.warnings}
            for r in results
            if r.status == "WARN"
        ],
    }


def main():
    quick = "--quick" in sys.argv
    no_llm = "--no-llm" in sys.argv

    print("Loading ground truth...")
    gt = load_ground_truth()

    all_results: list[TestResult] = []

    print("Phase 6: SQL Validation...")
    all_results.extend(test_sql_validator())

    print("Phase 9: Visualization...")
    all_results.extend(test_visualization_matrix())

    print("Phase 4: Root Cause (deterministic)...")
    all_results.extend(test_root_cause_pipeline(gt))

    if not no_llm:
        print("Phase 3/7/11: E2E Pipeline (LLM)...")
        all_results.extend(run_llm_pipeline_tests(gt, quick=quick))

        print("Phase 7: SQL Repair E2E...")
        all_results.append(test_sql_repair_e2e())
    else:
        print("Skipping LLM tests (--no-llm)")

    summary = summarize(all_results)

    print("\n" + "=" * 60)
    print("QA VALIDATION SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))

    out_path = "qa_validation_results.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults written to {out_path}")

    return 1 if summary["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
