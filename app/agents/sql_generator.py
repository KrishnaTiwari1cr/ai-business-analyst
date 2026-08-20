import os

from dotenv import load_dotenv

from app.llm.llm_client import generate_text


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


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


# =========================================================
# GENERATE SQL
# =========================================================

def generate_sql(question: str):
    """
    Convert a natural-language business question
    into a PostgreSQL SQL query.

    Returns:

        sql, provider

    Example:

        (
            "SELECT ...",
            "gemini"
        )

    or:

        (
            "SELECT ...",
            "groq"
        )
    """

    prompt = f"""
You are an expert Business Intelligence SQL analyst.

Convert the user's natural-language business question
into a PostgreSQL SQL query.

DATABASE SCHEMA:

{DATABASE_SCHEMA}

STRICT RULES:

1. Generate ONLY SQL.
2. Only SELECT or WITH queries are allowed.
3. Never generate INSERT.
4. Never generate UPDATE.
5. Never generate DELETE.
6. Never generate DROP.
7. Never generate ALTER.
8. Never generate CREATE.
9. Never generate TRUNCATE.
10. Never generate GRANT.
11. Never generate REVOKE.
12. Use ONLY tables and columns present in the schema.
13. Do not invent columns.
14. Do not invent tables.
15. Use correct JOIN conditions.
16. Use PostgreSQL syntax.
17. Do not use markdown.
18. Do not put SQL inside ```sql fences.
19. Do not explain the query.
20. Return ONLY the SQL query.

USER QUESTION:

{question}
"""

    # =====================================================
    # CALL GEMINI → GROQ FALLBACK
    # =====================================================

    print(
        "\n🤖 Generating SQL..."
    )

    response, provider = generate_text(
        prompt
    )

    # =====================================================
    # CLEAN AI RESPONSE
    # =====================================================

    sql = response.strip()

    # -----------------------------------------------------
    # Remove markdown SQL fences
    # -----------------------------------------------------

    if sql.startswith("```sql"):

        sql = sql[
            len("```sql"):
        ]

    elif sql.startswith("```"):

        sql = sql[
            len("```"):
        ]

    if sql.endswith("```"):

        sql = sql[
            :-3
        ]

    sql = sql.strip()

    # =====================================================
    # EMPTY RESPONSE CHECK
    # =====================================================

    if not sql:

        raise RuntimeError(
            "AI returned an empty SQL query."
        )

    # =====================================================
    # BASIC SQL SAFETY CHECK
    #
    # The real validation is still handled by
    # app.agents.sql_validator.
    #
    # This only catches obviously invalid AI output.
    # =====================================================

    sql_upper = sql.upper().strip()

    if not (
        sql_upper.startswith("SELECT")
        or sql_upper.startswith("WITH")
    ):

        raise ValueError(
            "AI generated a non-SELECT SQL statement."
        )

    # =====================================================
    # RESULT
    # =====================================================

    print(
        f"\n🤖 SQL generated using: {provider}"
    )

    return sql, provider


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "AI BUSINESS ANALYST - SQL GENERATOR TEST"
    )

    print("=" * 60)

    question = input(
        "\nEnter your business question: "
    ).strip()

    if not question:

        print(
            "\nQuestion cannot be empty."
        )

        raise SystemExit


    try:

        sql, provider = generate_sql(
            question
        )

        print(
            "\n" + "=" * 60
        )

        print(
            "SQL GENERATION COMPLETE"
        )

        print(
            "=" * 60
        )

        print(
            "\nProvider:"
        )

        print(
            provider
        )

        print(
            "\nGenerated SQL:"
        )

        print(
            "-" * 60
        )

        print(
            sql
        )

        print(
            "-" * 60
        )

    except Exception as e:

        print(
            "\n❌ SQL generation failed."
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )