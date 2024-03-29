"""example1

This module has been generated with SqlPyGen from example1.sql.
"""

from contextlib import closing
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
    "count_stocks"
] = """
SELECT COUNT(*) FROM stocks
"""


@dataclass(frozen=True)
class StockRow:
    date: Optional[str]
    trans: Optional[str]
    symbol: Optional[str]
    qty: Optional[float]
    price: Optional[float]


def create_schema(connection: ConnectionType) -> None:
    """Create the table schema."""
    try:
        sql = SCHEMA["table_stocks"]

        connection.execute(sql)
    except Exception as e:
        raise RuntimeError("Error executing schema: table_stocks") from e


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
        raise RuntimeError("Error executing query: insert_into_stocks") from e


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
        raise RuntimeError("Error executing query: select_from_stocks") from e


@typechecked
def count_stocks(connection: ConnectionType) -> Optional[int]:
    """Query count_stocks."""
    cursor = connection.cursor()
    try:
        sql = QUERY["count_stocks"]

        cursor.execute(sql)

        row = cursor.fetchone()
        if row is None:
            return None
        return int(row[0])
    except Exception as e:
        raise RuntimeError("Error executing query: count_stocks") from e


def explain_queries() -> None:
    connection = apsw.Connection(":memory:")
    create_schema(connection)

    with connection:
        cursor = connection.cursor()
        with closing(cursor):

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
                    "Error executing query plan: insert_into_stocks"
                ) from e

            try:
                sql = QUERY["select_from_stocks"]
                sql = "EXPLAIN " + sql

                cursor.execute(sql)

                print("Query select_from_stocks is syntactically valid.")
            except Exception as e:
                raise RuntimeError(
                    "Error executing query plan: select_from_stocks"
                ) from e

            try:
                sql = QUERY["count_stocks"]
                sql = "EXPLAIN " + sql

                cursor.execute(sql)

                print("Query count_stocks is syntactically valid.")
            except Exception as e:
                raise RuntimeError("Error executing query plan: count_stocks") from e


if __name__ == "__main__":
    try:
        explain_queries()
    except RuntimeError as e:
        print(e)
        print(e.__cause__)
