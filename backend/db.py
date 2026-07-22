import os
from datetime import date, datetime
from decimal import Decimal

import pymssql
from dotenv import load_dotenv

load_dotenv()

MSSQL_SERVER = os.environ["MSSQL_SERVER"]
MSSQL_PORT = int(os.environ.get("MSSQL_PORT", "1433"))
MSSQL_DATABASE = os.environ["MSSQL_DATABASE"]
MSSQL_USER = os.environ["MSSQL_USER"]
MSSQL_PASSWORD = os.environ["MSSQL_PASSWORD"]


def get_connection():
    return pymssql.connect(
        server=MSSQL_SERVER,
        port=MSSQL_PORT,
        database=MSSQL_DATABASE,
        user=MSSQL_USER,
        password=MSSQL_PASSWORD,
    )


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def run_query(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
    return [
        {col: _jsonable(value) for col, value in zip(columns, row)}
        for row in rows
    ]
