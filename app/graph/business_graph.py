from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.graph.state import (
    BusinessAnalystState
)

from app.graph.nodes import (
    classify_question,
    generate_sql_node,
    validate_sql_node,
    repair_sql_node,
    execute_sql_node,
    analyze_data_node,
    visualization_data_node,
    generate_insight_node,
    root_cause_analysis_node,
    route_intent,
    route_sql_validation,
    route_execution
)


# =========================================================
# BUILD BUSINESS ANALYST GRAPH
# =========================================================

def build_business_graph():

    graph = StateGraph(
        BusinessAnalystState
    )

    # =====================================================
    # REGISTER NODES
    # =====================================================

    graph.add_node(
        "classify_question",
        classify_question
    )

    graph.add_node(
        "generate_sql",
        generate_sql_node
    )

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

    graph.add_node(
        "analyze_data",
        analyze_data_node
    )

    graph.add_node(
        "visualization_data",
        visualization_data_node
    )

    graph.add_node(
        "generate_insight",
        generate_insight_node
    )

    graph.add_node(
        "root_cause_analysis",
        root_cause_analysis_node
    )

    # =====================================================
    # START
    # =====================================================

    graph.add_edge(
        START,
        "classify_question"
    )

    # =====================================================
    # QUESTION INTENT
    # =====================================================

    graph.add_conditional_edges(
        "classify_question",
        route_intent,
        {
            "analytics":
                "generate_sql",

            "root_cause":
                "root_cause_analysis"
        }
    )

    # =====================================================
    # SQL GENERATION
    # =====================================================

    graph.add_edge(
        "generate_sql",
        "validate_sql"
    )

    # =====================================================
    # SQL VALIDATION
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
    # SQL REPAIR
    # =====================================================

    graph.add_edge(
        "repair_sql",
        "validate_sql"
    )

    # =====================================================
    # SQL EXECUTION
    # =====================================================

    graph.add_conditional_edges(
        "execute_sql",
        route_execution,
        {
            "analyze":
                "analyze_data",

            "repair":
                "repair_sql",

            "end":
                END
        }
    )

    # =====================================================
    # DATA ANALYSIS
    # =====================================================

    graph.add_edge(
        "analyze_data",
        "visualization_data"
    )

    # =====================================================
    # VISUALIZATION DATA
    # =====================================================

    graph.add_edge(
        "visualization_data",
        "generate_insight"
    )

    # =====================================================
    # FINAL INSIGHT
    # =====================================================

    graph.add_edge(
        "generate_insight",
        END
    )

    # =====================================================
    # ROOT CAUSE
    # =====================================================

    graph.add_edge(
        "root_cause_analysis",
        END
    )

    # =====================================================
    # COMPILE
    # =====================================================

    return graph.compile()


# =========================================================
# GLOBAL GRAPH
# =========================================================

business_graph = build_business_graph()


# =========================================================
# RUN GRAPH
# =========================================================

def run_business_graph(
    question: str
):

    if not question or not question.strip():

        raise ValueError(
            "Business question cannot be empty."
        )

    # =====================================================
    # INITIAL STATE
    # =====================================================

    initial_state: BusinessAnalystState = {

        "question":
            question.strip(),

        "intent":
            None,

        "target_month":
            None,

        "root_cause_focus":
            None,

        "root_cause_direction":
            None,

        "period_source":
            None,

        "sql":
            None,

        "sql_valid":
            False,

        "sql_validation_message":
            None,

        "execution_success":
            False,

        "execution_error":
            None,

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

        "retry_count":
            0,

        "error":
            None
    }

    # =====================================================
    # RUN LANGGRAPH
    # =====================================================

    result = business_graph.invoke(
        initial_state
    )

    # =====================================================
    # IMPORTANT:
    # ENSURE QUERY DATA IS AVAILABLE TO UI
    # =====================================================

    data = result.get(
        "data"
    )

    visualization_data = result.get(
        "visualization_data"
    )

    # =====================================================
    # FALLBACK 1
    #
    # If visualization_data was not created,
    # use the original SQL result.
    # =====================================================

    if (
        visualization_data is None
        and data is not None
    ):

        result[
            "visualization_data"
        ] = data

    # =====================================================
    # FALLBACK 2
    #
    # If somehow data is missing but visualization
    # data exists, expose it as data as well.
    # =====================================================

    if (
        data is None
        and visualization_data is not None
    ):

        result[
            "data"
        ] = visualization_data

    # =====================================================
    # FINAL DEBUG INFORMATION
    # =====================================================

    final_data = result.get(
        "data"
    )

    final_visualization_data = (
        result.get(
            "visualization_data"
        )
    )

    if final_data is not None:

        try:

            print(
                f"\n📦 Final query data: "
                f"{len(final_data)} row(s)"
            )

            print(
                f"📋 Query columns: "
                f"{list(final_data.columns)}"
            )

        except Exception:
            pass

    else:

        print(
            "\n⚠️ Final query data is None."
        )

    if final_visualization_data is not None:

        try:

            print(
                f"📈 Final visualization data: "
                f"{len(final_visualization_data)} row(s)"
            )

            print(
                f"📊 Visualization columns: "
                f"{list(final_visualization_data.columns)}"
            )

        except Exception:
            pass

    else:

        print(
            "\n⚠️ Final visualization data is None."
        )

    # =====================================================
    # RETURN FINAL STATE
    # =====================================================

    return result


# =========================================================
# TERMINAL APPLICATION
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "       LANGGRAPH BUSINESS ANALYST"
    )

    print("=" * 60)

    question = input(
        "\nAsk a business question: "
    ).strip()

    if not question:

        print(
            "\n❌ Question cannot be empty."
        )

        raise SystemExit

    print(
        "\n🚀 Starting LangGraph..."
    )

    try:

        result = run_business_graph(
            question
        )

        # =================================================
        # COMPLETE
        # =================================================

        print(
            "\n" + "=" * 60
        )

        print(
            "LANGGRAPH EXECUTION COMPLETE"
        )

        print(
            "=" * 60
        )

        # =================================================
        # INTENT
        # =================================================

        print(
            "\nIntent:"
        )

        print(
            result.get(
                "intent"
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
        # RETRY COUNT
        # =================================================

        print(
            "\nSQL repair attempts:"
        )

        print(
            result.get(
                "retry_count",
                0
            )
        )

        # =================================================
        # SQL
        # =================================================

        if result.get(
            "sql"
        ):

            print(
                "\nGenerated SQL:"
            )

            print(
                "-" * 60
            )

            print(
                result[
                    "sql"
                ]
            )

            print(
                "-" * 60
            )

        # =================================================
        # DATABASE RESULTS
        # =================================================

        data = result.get(
            "data"
        )

        if data is not None:

            try:

                print(
                    "\nDatabase rows:"
                )

                print(
                    len(data)
                )

                print(
                    "\nDatabase columns:"
                )

                print(
                    list(
                        data.columns
                    )
                )

            except Exception:
                pass

        # =================================================
        # VISUALIZATION DATA
        # =================================================

        visualization_data = (
            result.get(
                "visualization_data"
            )
        )

        if visualization_data is not None:

            try:

                print(
                    "\nVisualization rows:"
                )

                print(
                    len(
                        visualization_data
                    )
                )

                print(
                    "\nVisualization columns:"
                )

                print(
                    list(
                        visualization_data.columns
                    )
                )

            except Exception:
                pass

        # =================================================
        # FINAL INSIGHT
        # =================================================

        if result.get(
            "insight"
        ):

            print(
                "\nFINAL BUSINESS INSIGHT:"
            )

            print(
                "=" * 60
            )

            print(
                result[
                    "insight"
                ]
            )

        # =================================================
        # ERROR
        # =================================================

        if result.get(
            "error"
        ):

            print(
                "\n⚠️ ERROR:"
            )

            print(
                result[
                    "error"
                ]
            )

    except Exception as e:

        print(
            "\n❌ LangGraph execution failed."
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
