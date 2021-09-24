"""example1

This module has been generated with SqlPyGen.
"""

from pprint import pprint
from typing import NewType, Iterable, cast

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
INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price)
"""

QUERY[
    "select_from_stocks"
] = """
SELECT * FROM stocks
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
    query_args = {
        "date": date,
        "trans": trans,
        "symbol": symbol,
        "qty": qty,
        "price": price,
    }

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
    query_args = {
        "date": date,
        "trans": trans,
        "symbol": symbol,
        "qty": qty,
        "price": price,
    }

    cursor = connection.cursor()
    try:
        sql = QUERY["insert_into_stocks"]

        cursor.execute(sql, query_args)

    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: insert_into_stocks"
        ) from e


def select_from_stocks(
    connection: ConnectionType,
) -> list[tuple[str, str, str, float, float]]:
    """Query select_from_stocks with transaction."""

    with connection:
        cursor = connection.cursor()
        try:
            sql = QUERY["select_from_stocks"]

            cursor.execute(sql)

            return cursor.fetchall()
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query: select_from_stocks"
            ) from e


def select_from_stocks_nt(
    connection: ConnectionType,
) -> Iterable[tuple[str, str, str, float, float]]:
    """Query select_from_stocks no implied transaction."""

    cursor = connection.cursor()
    try:
        sql = QUERY["select_from_stocks"]

        cursor.execute(sql)

        return cast(Iterable[tuple[str, str, str, float, float]], cursor)
    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: select_from_stocks"
        ) from e


def explain_queries() -> None:
    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    with connection:
        cursor = connection.cursor()

        try:
            sql = QUERY["insert_into_stocks"]
            sql = "EXPLAIN " + sql

            query_args = {
                "date": None,
                "trans": None,
                "symbol": None,
                "qty": None,
                "price": None,
            }

            cursor.execute(sql, query_args)

            print("Query explanation for insert_into_stocks")
            print("-" * 80)
            pprint(cursor.fetchall())
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: insert_into_stocks"
            ) from e

        try:
            sql = QUERY["select_from_stocks"]
            sql = "EXPLAIN " + sql

            cursor.execute(sql)

            print("Query explanation for select_from_stocks")
            print("-" * 80)
            pprint(cursor.fetchall())
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: select_from_stocks"
            ) from e


if __name__ == "__main__":
    explain_queries()
