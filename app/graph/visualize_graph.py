from pathlib import Path

from app.graph.business_graph import business_graph


# =========================================================
# LANGGRAPH VISUALIZATION
# =========================================================

def visualize_graph():

    print("=" * 60)
    print("       LANGGRAPH ARCHITECTURE VISUALIZER")
    print("=" * 60)

    try:

        # -------------------------------------------------
        # Get Mermaid representation
        # -------------------------------------------------

        mermaid = (
            business_graph
            .get_graph()
            .draw_mermaid()
        )

        # -------------------------------------------------
        # Save Mermaid source
        # -------------------------------------------------

        mermaid_path = Path(
            "business_analyst_graph.mmd"
        )

        mermaid_path.write_text(
            mermaid,
            encoding="utf-8"
        )

        print(
            "\n✅ Mermaid graph created:"
        )

        print(
            mermaid_path
        )

        # -------------------------------------------------
        # Print graph
        # -------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "LANGGRAPH STRUCTURE"
        )

        print(
            "=" * 60
        )

        print(
            mermaid
        )

        print(
            "=" * 60
        )

        # -------------------------------------------------
        # Try PNG generation
        # -------------------------------------------------

        try:

            png_bytes = (
                business_graph
                .get_graph()
                .draw_mermaid_png()
            )

            png_path = Path(
                "business_analyst_graph.png"
            )

            png_path.write_bytes(
                png_bytes
            )

            print(
                "\n✅ PNG graph created:"
            )

            print(
                png_path
            )

        except Exception as png_error:

            print(
                "\n⚠️ PNG generation unavailable."
            )

            print(
                "Reason:"
            )

            print(
                str(png_error)
            )

            print(
                "\nThe Mermaid file was still created successfully."
            )

    except Exception as e:

        print(
            "\n❌ Graph visualization failed."
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

    visualize_graph()