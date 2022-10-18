# This is an exmaple of sqlpygen file
-- module: example1
-- import: from stock_info import StockInfo

-- schema: table_stocks

CREATE TABLE stocks (
    date text,
    trans text,
    symbol text,
    qty real,
    price real,
    stock_info text
) ;

-- query: insert_into_stocks
-- params: date: str, trans: str, symbol: str, qty: float, price: float, stock_info: StockInfo

INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price, :stock_info) ;

-- query: select_from_stocks
-- return*: str, str, str, float, float, StockInfo

SELECT * FROM stocks ;

-- query: count_stocks
-- return?: int!

SELECT COUNT(*) FROM stocks ;
