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
-- testargs: date='2006-01-05', trans='BUY', symbol='RHAT', qty=100, price=35.14

INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price) ;

-- query: select_from_stocks
-- return: str, str, str, float, float

SELECT * FROM stocks ;
