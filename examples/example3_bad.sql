# example2.sql
# Two different return types may not have the same name.

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

# This is not OK
-- query: select_from_stocks2
-- return*: StockRow(date: str, trans: str)

SELECT date, trans FROM stocks ;
