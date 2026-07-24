import os

import pymssql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymssql.connect(
        server=os.environ["MSSQL_SERVER"],
        port=int(os.environ.get("MSSQL_PORT", "1433")),
        database=os.environ["MSSQL_DATABASE"],
        user=os.environ["MSSQL_USER"],
        password=os.environ["MSSQL_PASSWORD"],
    )


def bulk_insert(conn, table: str, columns: list[str], rows: list[tuple], batch_size: int = 1000):
    """Fast chunked bulk insert: builds one multi-row INSERT ... VALUES (...),(...)
    per batch instead of one round-trip per row. pymssql has no fast_executemany
    (that's a pyodbc/SQLAlchemy feature) - this is the pymssql-native equivalent."""
    if not rows:
        return 0

    col_list = ", ".join(columns)
    row_placeholder = "(" + ", ".join(["%s"] * len(columns)) + ")"

    cursor = conn.cursor()
    total = 0
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        placeholders = ", ".join([row_placeholder] * len(batch))
        flat_params = [value for row in batch for value in row]
        query = f"INSERT INTO {table} ({col_list}) VALUES {placeholders};"
        cursor.execute(query, flat_params)
        total += len(batch)
    conn.commit()
    cursor.close()
    return total


def bulk_insert_with_identity(conn, table: str, columns: list[str], rows: list[tuple], batch_size: int = 1000):
    """Same as bulk_insert, but temporarily enables IDENTITY_INSERT for tables
    where we need to control the primary key value ourselves (DimCustomer,
    so CustomerId lines up with the CIF we generate for it)."""
    cursor = conn.cursor()
    cursor.execute(f"SET IDENTITY_INSERT {table} ON;")
    conn.commit()
    try:
        total = bulk_insert(conn, table, columns, rows, batch_size)
    finally:
        cursor.execute(f"SET IDENTITY_INSERT {table} OFF;")
        conn.commit()
    cursor.close()
    return total
