"""example1

This module has been generated with SqlPyGen.
"""

from typing import NewType, Sequence, cast

import sqlite3

ConnectionType = sqlite3.Connection


SCHEMA = {}
SCHEMA[
    "table_stocks"
] = """
CREATE TABLE stocks (
    date text,
    trans text,
    symbol text,
    qty real,
    price real
)
"""


QUERY = {}
QUERY[
    "insert_into_stocks"
] = """
INSERT INTO stocks VALUES (?,?,?,?,?)
"""


def create_schema(connection: ConnectionType) -> None:
    """Create the table schema."""
    with connection:
        cursor = connection.cursor()

        try:
            sql = SCHEMA["table_stocks"]

            cursor.execute(sql)
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred when creating schema: table_stocks"
            ) from e


def insert_into_stocks(
    connection: ConnectionType,
    date: str,
    trans: str,
    symbol: str,
    qty: float,
    price: float,
) -> None:
    """Query insert_into_stocks with transaction."""
    query_args = [date, trans, symbol, qty, price]

    with connection:
        cursor = connection.cursor()
        try:
            sql = QUERY["insert_into_stocks"]

            cursor.execute(sql, query_args)

        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query: insert_into_stocks"
            ) from e


def insert_into_stocks_nt(
    connection: ConnectionType,
    date: str,
    trans: str,
    symbol: str,
    qty: float,
    price: float,
) -> None:
    """Query insert_into_stocks no implied transaction."""
    query_args = [date, trans, symbol, qty, price]

    cursor = connection.cursor()
    try:
        sql = QUERY["insert_into_stocks"]

        cursor.execute(sql, query_args)

    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: insert_into_stocks"
        ) from e
