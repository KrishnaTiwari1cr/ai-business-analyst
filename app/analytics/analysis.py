import pandas as pd


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """
    Analyze a DataFrame returned from a business SQL query.

    The function identifies:
    - number of rows
    - columns
    - numeric columns
    - highest and lowest values
    - basic summary statistics
    """

    if df.empty:
        return {
            "status": "empty",
            "message": "No data was returned from the database."
        }

    analysis = {
        "status": "success",
        "rows": len(df),
        "columns": list(df.columns),
    }

    # ---------------------------------------------------------
    # Identify numeric columns
    # ---------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    analysis["numeric_columns"] = numeric_columns

    # ---------------------------------------------------------
    # Analyze numeric columns
    # ---------------------------------------------------------

    numeric_analysis = {}

    for column in numeric_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        numeric_analysis[column] = {
            "total": float(series.sum()),
            "average": float(series.mean()),
            "minimum": float(series.min()),
            "maximum": float(series.max()),
        }

    analysis["numeric_analysis"] = numeric_analysis

    # ---------------------------------------------------------
    # Find highest and lowest rows
    # ---------------------------------------------------------

    rankings = {}

    for column in numeric_columns:

        if len(df) == 0:
            continue

        highest_index = df[column].idxmax()
        lowest_index = df[column].idxmin()

        rankings[column] = {
            "highest": df.loc[highest_index].to_dict(),
            "lowest": df.loc[lowest_index].to_dict(),
        }

    analysis["rankings"] = rankings

    # ---------------------------------------------------------
    # Statistical summary
    # ---------------------------------------------------------

    if numeric_columns:

        summary = df[numeric_columns].describe()

        analysis["summary"] = summary.to_dict()

    else:

        analysis["summary"] = {}

    return analysis


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    # Example data
    data = {
        "category": [
            "Furniture",
            "Electronics",
            "Software",
            "Accessories",
        ],
        "total_revenue": [
            11183572.77,
            9086337.20,
            6827297.34,
            6661713.83,
        ],
    }

    df = pd.DataFrame(data)

    print("=" * 60)
    print("BUSINESS DATA ANALYSIS TEST")
    print("=" * 60)

    result = analyze_dataframe(df)

    print("\nStatus:")
    print(result["status"])

    print("\nRows:")
    print(result["rows"])

    print("\nColumns:")
    print(result["columns"])

    print("\nNumeric columns:")
    print(result["numeric_columns"])

    print("\nNumeric analysis:")
    print(result["numeric_analysis"])

    print("\nRankings:")
    print(result["rankings"])