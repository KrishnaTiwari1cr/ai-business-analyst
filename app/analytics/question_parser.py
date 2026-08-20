import re


# =========================================================
# MONTH MAPPING
# =========================================================

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}


# =========================================================
# EXTRACT MONTH
# =========================================================

def extract_month(question: str):
    """
    Extract month number from a question.

    Example:
    "Why did revenue drop in September?"
    -> 9
    """

    question = question.lower()

    for month_name, month_number in MONTHS.items():

        if re.search(
            rf"\b{month_name}\b",
            question
        ):
            return month_number

    return None


# =========================================================
# EXTRACT YEAR
# =========================================================

def extract_year(question: str):
    """
    Extract a four-digit year.

    Example:
    "Why did revenue drop in September 2025?"
    -> 2025
    """

    match = re.search(
        r"\b(20\d{2})\b",
        question
    )

    if match:
        return int(match.group(1))

    return None


# =========================================================
# GET TARGET MONTH
# =========================================================

def get_target_month(question: str):
    """
    Return detected month and year.

    Example:
    {
        "month": 9,
        "year": 2025
    }

    If no month exists:
        None
    """

    month = extract_month(question)

    year = extract_year(question)

    if month is None:
        return None

    return {
        "month": month,
        "year": year
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    questions = [
        "Why did revenue drop in September?",
        "Why did revenue decline in November 2025?",
        "Why did revenue fall in March 2025?",
        "Which category generated the most revenue?"
    ]

    print("=" * 60)
    print("QUESTION PARSER TEST")
    print("=" * 60)

    for question in questions:

        result = get_target_month(
            question
        )

        print("\nQuestion:")
        print(question)

        print("Detected:")
        print(result)