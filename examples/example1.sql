# example1.sql
# This is an example annotated sql file.

# Lines starting with # are ignored by SqlPyGen.
# Lines starting with -- are used to provide SqlPyGen with annotations.

# Using the "module" annotation
# we name the python module to be generated.
-- module: example1

# We use "schema" annotations to annotate
# create table and create index sql statements.
# The statements are given a name which is used in the generated code
# to produce better error messages.
# All SQL statements must end with a semicolon.
-- schema: table_stocks

CREATE TABLE stocks (
    date text,
    trans text,
    symbol text,
    qty real,
    price real
) ;

# Here we annotate a query.
# The name of the query is used as the name of the function that is generated.
# The query parameters are named and annotated with types.
# The names can then be used in the query.
# Since this query doesn't specify a return annotation,
# SqlPyGen assumes that this SQL statement doesn't return anything.
# The types here are builtin Python types.
# By marking types ! at their end, we inform SqlPyGen,
# that the specific parameter may never by None.
-- query: insert_into_stocks
-- params: (date: str!, trans: str!, symbol: str!, qty: float, price: float)

INSERT INTO stocks VALUES (:date, :trans, :symbol, :qty, :price) ;

# Here we annotate a query with no parameters
# but one that returns some columns.
# The return annotation defines a row type that SqlPyGen will define
# and return instances of.
# In this case SqlPyGen will generate a Python dataclass called StockRow.
# The "return*" annotation tells SqlPyGen that this query may return
# zero or more rows.
# The following query is annotated with "return?",
# tells SqlPyGen that it will return zero or exactly one row.
-- query: select_from_stocks
-- return*: StockRow(date: str, trans: str, symbol: str, qty: float, price: float)

SELECT * FROM stocks ;

-- query: count_stocks
-- return?: int!

SELECT COUNT(*) FROM stocks ;
