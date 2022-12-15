"""Test for example1.sql"""

from contextlib import closing

import apsw

import example1 as edb


def test_example1():
    con = apsw.Connection(":memory:")
    edb.create_schema(con)

    with closing(con), con:
        assert edb.count_stocks(con) == 0

        edb.insert_into_stocks(
            con,
            date="2020-01-01",
            trans="SELL",
            symbol="SPY",
            qty=1.0,
            price=300,
        )

        assert edb.count_stocks(con) == 1

        rows = list(edb.select_from_stocks(con))
        assert len(rows) == 1
        assert rows[0] == edb.StockRow(
            date="2020-01-01", trans="SELL", symbol="SPY", qty=1.0, price=300
        )
