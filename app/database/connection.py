import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Load variables from .env
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)


def test_connection():
    """Test the PostgreSQL connection."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_user;"))

        print("Connected to PostgreSQL!")
        print("PostgreSQL user:", result.scalar())


if __name__ == "__main__":
    test_connection()