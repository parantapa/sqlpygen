import apsw

import example1 as edb


def test_example1():
    con = apsw.Connection(":memory:")
    edb.create_schema(con)

    edb.insert_into_stocks(
        con,
        date="2020-01-01",
        trans="SELL",
        symbol="SPY",
        qty=1.0,
        price=300,
    )

    for row in edb.select_from_stocks(con):
        print(row)

    print(edb.count_stocks(con))
