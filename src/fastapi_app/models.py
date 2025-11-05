import logging
import os
import typing
from datetime import datetime
from sqlalchemy.engine import URL
from sqlmodel import Field, SQLModel, create_engine

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

def parse_azure_conn_str(conn_str: str) -> dict:
    """
    Azure PG conn string looks like:
    "host=... port=5432 dbname=... user=... password=... sslmode=require"
    """
    parts = {}
    for token in conn_str.split():
        if "=" in token:
            k, v = token.split("=", 1)
            parts[k.strip()] = v.strip()
    return parts

def build_url() -> URL:
    # Prefer explicit DATABASE_URL if provided (already a full SQLAlchemy URL)
    database_url = os.getenv("DATABASE_URL")

    # Azure-style connection string (space-separated key=value)
    azure_conn = os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")

    # Split vars (good for local/dev)
    host = os.getenv("DBHOST") or os.getenv("DB_HOST")
    name = os.getenv("DBNAME") or os.getenv("DB_NAME")
    user = os.getenv("DBUSER") or os.getenv("DB_USER")
    pwd  = os.getenv("DBPASS") or os.getenv("DB_PASSWORD")
    port = int(os.getenv("DBPORT") or os.getenv("DB_PORT") or "5432")

    # Choose driver that matches your requirements:
    # - psycopg (v3): "postgresql+psycopg"
    # - psycopg2 (v2): "postgresql+psycopg2"
    driver = os.getenv("DB_DRIVER", "postgresql+psycopg")

    if database_url:
        logger.info("Using DATABASE_URL from environment.")
        # Let SQLAlchemy parse/validate it
        return URL.create(database_url)

    if azure_conn:
        logger.info("Using AZURE_POSTGRESQL_CONNECTIONSTRING.")
        d = parse_azure_conn_str(azure_conn)
        required = ("host", "dbname", "user", "password")
        if not all(k in d and d[k] for k in required):
            raise RuntimeError("AZURE_POSTGRESQL_CONNECTIONSTRING is incomplete.")
        sslmode = d.get("sslmode", "require")
        return URL.create(
            drivername=driver,
            username=d["user"],
            password=d["password"],
            host=d["host"],
            port=int(d.get("port", 5432)),
            database=d["dbname"],
            query={"sslmode": sslmode},
        )

    if all([host, name, user, pwd]):
        logger.info("Using split DB_* variables.")
        return URL.create(
            drivername=driver,
            username=user,
            password=pwd,
            host=host,
            port=port,
            database=name,
            query={"sslmode": "require"} if "azure.com" in (host or "") else {},
        )

    raise RuntimeError(
        "No database configuration found. Set one of: "
        "DATABASE_URL, AZURE_POSTGRESQL_CONNECTIONSTRING, or DB_HOST/DB_NAME/DB_USER/DB_PASSWORD."
    )

# ---- Build engine ----
url = build_url()
engine = create_engine(url, pool_pre_ping=True)

def create_db_and_tables():
    return SQLModel.metadata.create_all(engine)

class Restaurant(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    street_address: str = Field(max_length=50)
    description: str = Field(max_length=250)

    def __str__(self):
        return f"{self.name}"

class Review(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    restaurant: int = Field(foreign_key="restaurant.id")
    user_name: str = Field(max_length=50)
    rating: typing.Optional[int]
    review_text: str = Field(max_length=500)
    review_date: datetime

    def __str__(self):
        return f"{self.user_name} -> {self.rating}"
