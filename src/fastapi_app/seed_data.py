import logging
import sys

from sqlmodel import SQLModel

from fastapi_app.models import Restaurant, Review, create_db_and_tables, engine

logger = logging.getLogger("seed_data")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


def drop_all():
    # Explicitly remove these tables first to avoid cascade errors
    SQLModel.metadata.remove(Restaurant.__table__)
    SQLModel.metadata.remove(Review.__table__)
    SQLModel.metadata.drop_all(engine)


if __name__ == "__main__":
    try:
        logger.info("Creating database and tables...")
        create_db_and_tables()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        logger.warning("Continuing startup anyway — database may not be available yet.")
        sys.exit(0)  # Exit cleanly so entrypoint continues

