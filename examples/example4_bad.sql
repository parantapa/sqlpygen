# example2.sql
# The same query may not be defined twice

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

-- query: select_from_stocks
-- return*: StockRow(date: str, trans: str, symbol: str, qty: float, price: float)

SELECT * FROM stocks ;
