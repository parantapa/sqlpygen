# example2.sql
# Two queries can return dataclasses of same type

-- module: example2

-- schema: table_stocks

CREATE TABLE stocks (
    date text,
    trans text,
    symbol text,
    qty real,
    price real
) ;

-- query: insert_into_stocks
-- params: (date: str!, trans: str!, symbol: str!, qty: float, price: float)

INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price) ;

-- query: select_from_stocks
-- return*: StockRow(date: str, trans: str, symbol: str, qty: float, price: float)

SELECT * FROM stocks ;

# This is OK
-- query: select_from_stocks2
-- return*: StockRow(date: str, trans: str, symbol: str, qty: float, price: float)

SELECT * FROM stocks ;
