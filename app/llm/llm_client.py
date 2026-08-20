import os

from dotenv import load_dotenv
from google import genai
from groq import Groq


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


# =========================================================
# CLIENTS
# =========================================================

gemini_client = None
groq_client = None


if GEMINI_API_KEY:

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


if GROQ_API_KEY:

    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


# =========================================================
# MODELS
# =========================================================

GEMINI_MODEL = "gemini-3.6-flash"

GROQ_MODEL = "openai/gpt-oss-120b"


# =========================================================
# GEMINI
# =========================================================

def call_gemini(prompt: str):

    if gemini_client is None:

        raise RuntimeError(
            "Gemini client is not configured."
        )

    response = (
        gemini_client
        .models
        .generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


# =========================================================
# GROQ
# =========================================================

def call_groq(prompt: str):

    if groq_client is None:

        raise RuntimeError(
            "Groq client is not configured."
        )

    response = (
        groq_client.chat.completions.create(
            model=GROQ_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:

        raise RuntimeError(
            "Groq returned an empty response."
        )

    return content.strip()


# =========================================================
# MAIN LLM FUNCTION
# =========================================================

def generate_text(
    prompt: str
):
    """
    AI provider fallback:

    1. Gemini
    2. Groq
    3. Raise exception

    Deterministic fallbacks should be handled
    by the individual business/analytics agent.
    """

    # =====================================================
    # TRY GEMINI
    # =====================================================

    try:

        print(
            "\n🤖 Trying Gemini..."
        )

        response = call_gemini(
            prompt
        )

        print(
            "✅ Gemini response received."
        )

        return response, "gemini"

    except Exception as gemini_error:

        print(
            "\n⚠️ Gemini unavailable."
        )

        print(
            f"Gemini reason: {gemini_error}"
        )

    # =====================================================
    # TRY GROQ
    # =====================================================

    try:

        print(
            "\n🟢 Switching to Groq..."
        )

        response = call_groq(
            prompt
        )

        print(
            "✅ Groq response received."
        )

        return response, "groq"

    except Exception as groq_error:

        print(
            "\n⚠️ Groq unavailable."
        )

        print(
            f"Groq reason: {groq_error}"
        )

    # =====================================================
    # BOTH FAILED
    # =====================================================

    raise RuntimeError(
        "Both Gemini and Groq are unavailable."
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "LLM FALLBACK TEST"
    )

    print("=" * 60)

    prompt = (
        "Explain revenue in one simple sentence."
    )

    try:

        response, provider = generate_text(
            prompt
        )

        print(
            "\nProvider used:",
            provider
        )

        print(
            "\nResponse:"
        )

        print(response)

    except Exception as e:

        print(
            "\n❌ All AI providers failed."
        )

        print(e)