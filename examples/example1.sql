# This is an exmaple of sqlpygen file
-- module: example1

-- schema: table_stocks

CREATE TABLE stocks (
    date text,
    trans text,
    symbol text,
    qty real,
    price real
) ;

-- query: insert_into_stocks
-- params: date: str, trans: str, symbol: str, qty: float, price: float

INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price) ;

-- query: select_from_stocks
-- return*: date: str, trans: str, symbol: str, qty: float, price: float

SELECT * FROM stocks ;

-- query: count_stocks
-- return?: count: int!

SELECT COUNT(*) FROM stocks ;
