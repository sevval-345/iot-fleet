import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MSSQL_SERVER = os.getenv("MSSQL_SERVER", r"DESKTOP-O7GV2S9\\SQLEXPRESS")
    MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "iot_sim_fleet")
    MSSQL_USERNAME = os.getenv("MSSQL_USERNAME", "***")
    MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "*****")
    MSSQL_DRIVER   = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
    ALLOW_ORIGINS  = os.getenv("ALLOW_ORIGINS", "http://localhost:4200")

settings = Settings()
