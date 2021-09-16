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

INSERT INTO stocks VALUES (?,?,?,?,?) ;
