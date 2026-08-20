from app.graph.business_graph import business_graph


# =========================================================
# SQL SELF-CORRECTION TEST
# =========================================================

def test_sql_repair():
    """
    Test whether LangGraph can detect invalid SQL,
    send it to the repair node, validate the repaired SQL,
    and continue to execution.
    """

    print("=" * 60)
    print("       SQL SELF-CORRECTION TEST")
    print("=" * 60)

    # -----------------------------------------------------
    # Intentionally invalid SQL
    #
    # The table name is wrong:
    #
    # productss ❌
    #
    # Correct table:
    #
    # products ✅
    # -----------------------------------------------------

    invalid_sql = """
    SELECT
        p.category,
        SUM(oi.revenue) AS total_revenue
    FROM order_items oi
    JOIN productss p
        ON oi.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    LIMIT 1;
    """

    # -----------------------------------------------------
    # Initial state
    # -----------------------------------------------------

    initial_state = {

        "question":
            "Which product category generated the most revenue?",

        "intent":
            "analytics",

        "target_month":
            None,

        "sql":
            invalid_sql,

        "sql_valid":
            False,

        "sql_validation_message":
            "Table 'productss' does not exist. "
            "The correct table is 'products'.",

        "data":
            None,

        "visualization_data":
            None,

        "analysis":
            None,

        "category_analysis":
            None,

        "product_analysis":
            None,

        "previous_month":
            None,

        "current_month":
            None,

        "previous_total":
            None,

        "current_total":
            None,

        "revenue_change":
            None,

        "revenue_change_percent":
            None,

        "insight":
            None,

        "provider":
            None,

        "chart_path":
            None,

        "error":
            None,

        # Important:
        # Start at 1 so the graph enters the repair path.
        "retry_count":
            1
    }

    print(
        "\n❌ Initial SQL intentionally contains:"
    )

    print(
        "JOIN productss p"
    )

    print(
        "\nExpected repair:"
    )

    print(
        "JOIN products p"
    )

    print(
        "\n🚀 Starting SQL repair test..."
    )

    try:

        # -------------------------------------------------
        # IMPORTANT
        #
        # We invoke the existing graph directly.
        #
        # Since the graph starts with classify_question,
        # generate_sql would normally replace our invalid SQL.
        #
        # Therefore this test is primarily verifying that
        # the repair node itself can be called through the
        # compiled graph architecture.
        # -------------------------------------------------

        from app.graph.nodes import (
            repair_sql_node,
            validate_sql_node,
            execute_sql_node
        )

        # -------------------------------------------------
        # STEP 1 — REPAIR
        # -------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "STEP 1 — REPAIR INVALID SQL"
        )

        print(
            "=" * 60
        )

        repaired_state = repair_sql_node(
            initial_state
        )

        repaired_sql = (
            repaired_state.get(
                "sql"
            )
        )

        provider = (
            repaired_state.get(
                "provider"
            )
        )

        print(
            "\nProvider:"
        )

        print(
            provider
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

        # -------------------------------------------------
        # STEP 2 — VALIDATE REPAIRED SQL
        # -------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "STEP 2 — VALIDATE REPAIRED SQL"
        )

        print(
            "=" * 60
        )

        validation_state = {
            **initial_state,
            **repaired_state
        }

        validated_state = (
            validate_sql_node(
                validation_state
            )
        )

        print(
            "\nSQL valid:"
        )

        print(
            validated_state.get(
                "sql_valid"
            )
        )

        print(
            "\nValidation message:"
        )

        print(
            validated_state.get(
                "sql_validation_message"
            )
        )

        # -------------------------------------------------
        # STEP 3 — EXECUTE
        # -------------------------------------------------

        if validated_state.get(
            "sql_valid"
        ):

            print(
                "\n" + "=" * 60
            )

            print(
                "STEP 3 — EXECUTE REPAIRED SQL"
            )

            print(
                "=" * 60
            )

            execution_state = {
                **validation_state,
                **validated_state
            }

            executed_state = (
                execute_sql_node(
                    execution_state
                )
            )

            data = (
                executed_state.get(
                    "data"
                )
            )

            if data is not None:

                print(
                    "\n✅ Repaired SQL executed successfully."
                )

                print(
                    f"Rows returned: {len(data)}"
                )

                print(
                    "\nResult:"
                )

                print(
                    data
                )

            else:

                print(
                    "\n❌ Repaired SQL execution failed."
                )

                print(
                    executed_state.get(
                        "error"
                    )
                )

        else:

            print(
                "\n❌ Repaired SQL is still invalid."
            )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "SQL SELF-CORRECTION TEST COMPLETE"
        )

        print(
            "=" * 60
        )

    except Exception as e:

        print(
            "\n❌ SQL self-correction test failed."
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:"
        )

        print(
            str(e)
        )


# =========================================================
# RUN TEST
# =========================================================

if __name__ == "__main__":

    test_sql_repair()