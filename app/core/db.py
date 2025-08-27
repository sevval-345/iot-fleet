# app/core/db.py
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from app.core.config import settings

def get_engine():
    encrypt = os.getenv("MSSQL_ENCRYPT", "no").lower()  # Varsayılan: no
    trust = os.getenv("MSSQL_TRUST_SERVER_CERT", "yes").lower()
    conn_str = (
        f"mssql+pyodbc://{settings.MSSQL_USERNAME}:{quote_plus(settings.MSSQL_PASSWORD)}@"
        f"{settings.MSSQL_SERVER}/{settings.MSSQL_DATABASE}"
        f"?driver={quote_plus(settings.MSSQL_DRIVER)}&Encrypt={encrypt}&TrustServerCertificate={trust}"
    )
    return create_engine(conn_str, fast_executemany=True, pool_pre_ping=True)

ENGINE = get_engine()
