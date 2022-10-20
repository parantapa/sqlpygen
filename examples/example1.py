"""example1

This module has been generated with SqlPyGen from example1.sql.
"""

from typing import Optional, Iterable
from stock_info import StockInfo

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
    price real,
    stock_info text
)
"""


QUERY = {}
QUERY[
    "insert_into_stocks"
] = """
INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price, :stock_info)
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
    stock_info: StockInfo,
) -> None:
    """Query insert_into_stocks."""
    stock_info_json = stock_info.json()

    cursor = connection.cursor()
    try:
        sql = QUERY["insert_into_stocks"]

        query_args = {
            "date": date,
            "trans": trans,
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "stock_info": stock_info_json,
        }
        cursor.execute(sql, query_args)

    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: insert_into_stocks"
        ) from e


def select_from_stocks(
    connection: ConnectionType,
) -> Iterable[
    tuple[
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[float],
        Optional[float],
        Optional[StockInfo],
    ]
]:
    """Query select_from_stocks."""

    cursor = connection.cursor()
    try:
        sql = QUERY["select_from_stocks"]

        cursor.execute(sql)

        for row in cursor:
            row = list(row)
            row[5] = None if row[5] is None else StockInfo.parse_raw(row[5])
            row = tuple(row)
            yield row
    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: select_from_stocks"
        ) from e


def count_stocks(connection: ConnectionType) -> Optional[tuple[int]]:
    """Query count_stocks."""

    cursor = connection.cursor()
    try:
        sql = QUERY["count_stocks"]

        cursor.execute(sql)

        row = cursor.fetchone()
        return row
    except Exception as e:
        raise RuntimeError(
            "An unexpected exception occurred while executing query: count_stocks"
        ) from e


def explain_queries() -> None:
    from rich.console import Console
    from rich.table import Table

    connection = apsw.Connection(":memory:")
    create_schema(connection)

    console = Console()

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
                "stock_info": None,
            }
            cursor.execute(sql, query_args)

            table = Table(
                title="Query explanation for insert_into_stocks", show_header=False
            )
            for row in cursor:
                table.add_row(*[str(x) for x in row])
            console.print(table)
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: insert_into_stocks"
            ) from e

        try:
            sql = QUERY["select_from_stocks"]
            sql = "EXPLAIN " + sql

            cursor.execute(sql)

            table = Table(
                title="Query explanation for select_from_stocks", show_header=False
            )
            for row in cursor:
                table.add_row(*[str(x) for x in row])
            console.print(table)
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: select_from_stocks"
            ) from e

        try:
            sql = QUERY["count_stocks"]
            sql = "EXPLAIN " + sql

            cursor.execute(sql)

            table = Table(title="Query explanation for count_stocks", show_header=False)
            for row in cursor:
                table.add_row(*[str(x) for x in row])
            console.print(table)
        except Exception as e:
            raise RuntimeError(
                "An unexpected exception occurred while executing query plan for: count_stocks"
            ) from e


if __name__ == "__main__":
    explain_queries()
