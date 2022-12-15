"""example2

This module has been generated with SqlPyGen from example2.sql.
"""

from dataclasses import dataclass
from typing import Optional, Iterable

from typeguard import typechecked

import apsw

ConnectionType = apsw.Connection

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

QUERY[
    "select_from_stocks2"
] = """
SELECT * FROM stocks
"""


@dataclass
class StockRow:
    date: Optional[str]
    trans: Optional[str]
    symbol: Optional[str]
    qty: Optional[float]
    price: Optional[float]


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


@typechecked
def insert_into_stocks(
    connection: ConnectionType,
    *,
    date: str,
    trans: str,
    symbol: str,
    qty: Optional[float],
    price: Optional[float]
) -> None:
    """Query insert_into_stocks."""
    cursor = connection.cursor()
    try:
        sql = QUERY["insert_into_stocks"]

        query_args = {
            "date": date,
            "trans": trans,
            "symbol": symbol,
            "qty": qty,
            "price": price,
        }
        cursor.execute(sql, query_args)

    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: insert_into_stocks"
        ) from e


@typechecked
def select_from_stocks(connection: ConnectionType) -> Iterable[StockRow]:
    """Query select_from_stocks."""
    cursor = connection.cursor()
    try:
        sql = QUERY["select_from_stocks"]

        cursor.execute(sql)

        for row in cursor:
            row = StockRow(*row)
            yield row
    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: select_from_stocks"
        ) from e


@typechecked
def select_from_stocks2(connection: ConnectionType) -> Iterable[StockRow]:
    """Query select_from_stocks2."""
    cursor = connection.cursor()
    try:
        sql = QUERY["select_from_stocks2"]

        cursor.execute(sql)

        for row in cursor:
            row = StockRow(*row)
            yield row
    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: select_from_stocks2"
        ) from e


def explain_queries() -> None:
    connection = apsw.Connection(":memory:")
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

            print("Query insert_into_stocks is syntactically valid.")
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: insert_into_stocks"
            ) from e

        try:
            sql = QUERY["select_from_stocks"]
            sql = "EXPLAIN " + sql

            cursor.execute(sql)

            print("Query select_from_stocks is syntactically valid.")
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: select_from_stocks"
            ) from e

        try:
            sql = QUERY["select_from_stocks2"]
            sql = "EXPLAIN " + sql

            cursor.execute(sql)

            print("Query select_from_stocks2 is syntactically valid.")
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: select_from_stocks2"
            ) from e


if __name__ == "__main__":
    try:
        explain_queries()
    except RuntimeError as e:
        print(e)
        print(e.__cause__)
