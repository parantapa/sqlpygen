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
-- testargs: ('2006-01-05', 'BUY', 'RHAT', 100, 35.14)

INSERT INTO stocks VALUES (?,?,?,?,?) ;
