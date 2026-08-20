from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.graph.state import BusinessAnalystState

from app.graph.nodes import (
    validate_sql_node,
    repair_sql_node,
    execute_sql_node,
    route_sql_validation,
    route_execution
)


# =========================================================
# BUILD TEST GRAPH
# =========================================================

def build_test_graph():

    graph = StateGraph(
        BusinessAnalystState
    )

    # =====================================================
    # REGISTER NODES
    # =====================================================

    graph.add_node(
        "validate_sql",
        validate_sql_node
    )

    graph.add_node(
        "repair_sql",
        repair_sql_node
    )

    graph.add_node(
        "execute_sql",
        execute_sql_node
    )

    # =====================================================
    # START → VALIDATE
    # =====================================================

    graph.add_edge(
        START,
        "validate_sql"
    )

    # =====================================================
    # VALIDATION ROUTING
    #
    # VALID
    #   ↓
    # EXECUTE
    #
    # INVALID
    #   ↓
    # REPAIR
    # =====================================================

    graph.add_conditional_edges(

        "validate_sql",

        route_sql_validation,

        {
            "execute":
                "execute_sql",

            "repair":
                "repair_sql",

            "end":
                END
        }
    )

    # =====================================================
    # REPAIR → VALIDATE
    # =====================================================

    graph.add_edge(
        "repair_sql",
        "validate_sql"
    )

    # =====================================================
    # EXECUTION ROUTING
    #
    # SUCCESS
    #   ↓
    # END
    #
    # DATABASE ERROR
    #   ↓
    # REPAIR
    # =====================================================

    graph.add_conditional_edges(

        "execute_sql",

        route_execution,

        {
            "analyze":
                END,

            "repair":
                "repair_sql",

            "end":
                END
        }
    )

    return graph.compile()


# =========================================================
# MAIN TEST
# =========================================================

def main():

    print("=" * 60)

    print(
        "       END-TO-END SQL SELF-CORRECTION TEST"
    )

    print("=" * 60)

    # =====================================================
    # INTENTIONALLY BROKEN SQL
    # =====================================================

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

    print(
        "\n❌ Intentionally broken SQL:"
    )

    print(
        "-" * 60
    )

    print(
        invalid_sql
    )

    print(
        "-" * 60
    )

    print(
        "\nExpected repair:"
    )

    print(
        "productss → products"
    )

    # =====================================================
    # INITIAL STATE
    # =====================================================

    initial_state: BusinessAnalystState = {

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
            None,

        "execution_error":
            None,

        "execution_success":
            False,

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

        "retry_count":
            0
    }

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    test_graph = build_test_graph()

    print(
        "\n🚀 Starting LangGraph self-correction..."
    )

    try:

        result = test_graph.invoke(
            initial_state
        )

        # =================================================
        # FINAL RESULT
        # =================================================

        print(
            "\n" + "=" * 60
        )

        print(
            "SELF-CORRECTION TEST COMPLETE"
        )

        print(
            "=" * 60
        )

        # =================================================
        # RETRIES
        # =================================================

        print(
            "\nRepair attempts:"
        )

        print(
            result.get(
                "retry_count",
                0
            )
        )

        # =================================================
        # PROVIDER
        # =================================================

        print(
            "\nProvider:"
        )

        print(
            result.get(
                "provider"
            )
        )

        # =================================================
        # FINAL SQL
        # =================================================

        print(
            "\nFinal SQL:"
        )

        print(
            "-" * 60
        )

        print(
            result.get(
                "sql"
            )
        )

        print(
            "-" * 60
        )

        # =================================================
        # SQL VALID
        # =================================================

        print(
            "\nSQL valid:"
        )

        print(
            result.get(
                "sql_valid"
            )
        )

        # =================================================
        # EXECUTION STATUS
        # =================================================

        print(
            "\nExecution successful:"
        )

        print(
            result.get(
                "execution_success"
            )
        )

        # =================================================
        # DATABASE RESULT
        # =================================================

        data = result.get(
            "data"
        )

        if data is not None:

            print(
                "\nDatabase rows:"
            )

            print(
                len(data)
            )

            print(
                "\nDatabase result:"
            )

            print(
                data
            )

        # =================================================
        # ERROR
        # =================================================

        if result.get(
            "error"
        ):

            print(
                "\n⚠️ Error:"
            )

            print(
                result.get(
                    "error"
                )
            )

        # =================================================
        # EXECUTION ERROR
        # =================================================

        if result.get(
            "execution_error"
        ):

            print(
                "\nDatabase execution error:"
            )

            print(
                result.get(
                    "execution_error"
                )
            )

        # =================================================
        # SUCCESS CHECK
        # =================================================

        if (

            result.get(
                "sql_valid"
            )

            and

            result.get(
                "execution_success"
            )

            and

            data is not None

            and

            not data.empty

            and

            result.get(
                "retry_count",
                0
            ) >= 1

        ):

            print(
                "\n" + "=" * 60
            )

            print(
                "🎉 SELF-CORRECTION SUCCESSFUL"
            )

            print(
                "=" * 60
            )

            print(
                "\nThe LangGraph agent successfully:"
            )

            print(
                "1. Detected the database error"
            )

            print(
                "2. Routed the error to the repair node"
            )

            print(
                "3. Generated corrected SQL"
            )

            print(
                "4. Re-validated the SQL"
            )

            print(
                "5. Re-executed the repaired SQL"
            )

        else:

            print(
                "\n❌ SELF-CORRECTION TEST FAILED"
            )

    except Exception as e:

        print(
            "\n❌ Test execution failed."
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
# RUN
# =========================================================

if __name__ == "__main__":

    main()