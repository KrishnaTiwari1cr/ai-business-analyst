import re


# =========================================================
# FORBIDDEN SQL KEYWORDS
# =========================================================

FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "MERGE",
    "EXEC",
    "EXECUTE",
]


# =========================================================
# SQL VALIDATOR
# =========================================================

def validate_sql(sql: str) -> tuple[bool, str]:

    if not sql:
        return False, "SQL query is empty."

    # Remove leading/trailing whitespace
    sql = sql.strip()

    # -----------------------------------------------------
    # Check for multiple statements
    # -----------------------------------------------------

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        return (
            False,
            "Multiple SQL statements are not allowed."
        )

    # Get the actual statement
    statement = statements[0]

    # -----------------------------------------------------
    # Only SELECT or WITH queries allowed
    # -----------------------------------------------------

    normalized_sql = statement.upper()

    if not (
        normalized_sql.startswith("SELECT")
        or normalized_sql.startswith("WITH")
    ):
        return (
            False,
            "Only SELECT or WITH queries are allowed."
        )

    # -----------------------------------------------------
    # Check forbidden keywords
    # -----------------------------------------------------

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized_sql):

            return (
                False,
                f"Forbidden SQL operation detected: {keyword}"
            )

    # -----------------------------------------------------
    # Basic protection against comments
    # -----------------------------------------------------

    if "--" in statement:
        return (
            False,
            "SQL comments are not allowed."
        )

    if "/*" in statement or "*/" in statement:
        return (
            False,
            "SQL block comments are not allowed."
        )

    # -----------------------------------------------------
    # Basic LIMIT protection
    # -----------------------------------------------------

    # We want to prevent accidentally returning huge datasets.
    # Aggregate queries may not need LIMIT, so this is only
    # a basic safety check for non-aggregate SELECT queries.

    if (
        "LIMIT" not in normalized_sql
        and "GROUP BY" not in normalized_sql
        and "COUNT(" not in normalized_sql
        and "SUM(" not in normalized_sql
        and "AVG(" not in normalized_sql
        and "MIN(" not in normalized_sql
        and "MAX(" not in normalized_sql
    ):

        return (
            False,
            "Query must include a LIMIT clause."
        )

    return True, "SQL query is safe."


# =========================================================
# TEST FUNCTION
# =========================================================

def test_validator():

    test_queries = {

        "safe_select": """
            SELECT *
            FROM products
            LIMIT 10
        """,

        "safe_aggregate": """
            SELECT
                category,
                SUM(price) AS total_price
            FROM products
            GROUP BY category
        """,

        "unsafe_delete": """
            DELETE FROM customers
        """,

        "unsafe_drop": """
            DROP TABLE customers
        """,

        "unsafe_update": """
            UPDATE customers
            SET customer_name = 'Test'
        """,

        "multiple_statements": """
            SELECT * FROM products;
            DELETE FROM products;
        """,

        "comment_attack": """
            SELECT * FROM products -- malicious comment
        """,
    }

    print("=" * 60)
    print("SQL VALIDATOR TEST")
    print("=" * 60)

    for name, query in test_queries.items():

        is_valid, message = validate_sql(query)

        print()
        print(f"Test: {name}")
        print(f"Valid: {is_valid}")
        print(f"Message: {message}")


# =========================================================
# RUN TESTS
# =========================================================

if __name__ == "__main__":
    test_validator()