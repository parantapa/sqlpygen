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
-- return*: str, str, str, float, float

SELECT * FROM stocks ;

-- query: count_stocks
-- return?: int!

SELECT COUNT(*) FROM stocks ;
