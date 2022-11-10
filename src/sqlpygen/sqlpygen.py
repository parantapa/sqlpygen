"""Generate type annotated python from SQL."""

from importlib.resources import read_text
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from black import format_str, Mode  # type: ignore
from lark import Lark, Transformer, UnexpectedToken  # type: ignore
from jinja2 import Environment, PackageLoader, StrictUndefined


@dataclass
class Module:
    name: str


@dataclass
class Import:
    import_stmt: str


@dataclass
class Schema:
    name: str
    sql: str


@dataclass
class VType:
    name: str
    maybe_none: bool


@dataclass
class VNameVType:
    name: str
    type: VType


@dataclass
class Params:
    vname_vtypes: list[VNameVType]


@dataclass
class Return:
    vname_vtypes: list[VNameVType]
    returns_one: Optional[bool]


@dataclass
class Query:
    name: str
    params: Params
    return_: Return
    sql: str


@dataclass
class SqlFile:
    module: Optional[Module]
    imports: list[Import]
    schemas: list[Schema]
    queries: list[Query]


class SqlPyGenTransformer(Transformer):
    """Transform the parse tree for code generation."""

    CNAME = str

    def SQL_STRING(self, t):
        return t.strip().rstrip(";").strip()

    def IMPORT_STRING(self, t):
        return " ".join(t.split())

    def import_(self, ts):
        (import_stmt,) = ts
        return Import(import_stmt)

    def module(self, ts):
        (name,) = ts
        return Module(name)

    def vtype_opt(self, ts):
        (name,) = ts
        return VType(name, True)

    def vtype_not_opt(self, ts):
        (name,) = ts
        return VType(name, False)

    def vname_vtype(self, ts):
        vname, vtype = ts
        return VNameVType(vname, vtype)

    def params(self, ts):
        return Params(list(ts))

    def returnone(self, ts):
        return Return(list(ts), True)

    def returnmany(self, ts):
        return Return(list(ts), False)

    def schema(self, ts):
        name, sql = ts
        return Schema(name, sql)

    def query(self, ts):
        name, sql = ts[0], ts[-1]
        params = Params([])
        return_ = Return([], None)
        for t in ts[1:-1]:
            if isinstance(t, Params):
                params = t
            elif isinstance(t, Return):
                return_ = t
            else:
                raise ValueError(f"Unexpected child: {t=}")

        return Query(name, params, return_, sql)

    def start(self, ts):
        ret = SqlFile(None, [], [], [])
        for t in ts:
            if isinstance(t, Module):
                ret.module = t
            elif isinstance(t, Import):
                ret.imports.append(t)
            elif isinstance(t, Query):
                ret.queries.append(t)
            elif isinstance(t, Schema):
                ret.schemas.append(t)
            else:
                raise ValueError(f"Unexpected child: {t=}")
        return ret


def get_parser() -> Lark:
    """Return the parser."""
    grammar = read_text("sqlpygen", "sqlpygen.lark")
    parser = Lark(grammar, parser="lalr")
    return parser


def return_type_name(query: Query) -> str:
    xs = query.name.split("_")
    xs = [x.title() for x in xs]
    xs = "".join(xs)
    xs = xs + "ReturnType"
    return xs


def py_type(vtype: VType) -> str:
    if vtype.maybe_none:
        return f"Optional[{vtype.name}]"
    else:
        return vtype.name


def fn_params(params: Params) -> str:
    if not params.vname_vtypes:
        return "connection: ConnectionType"

    xs = [(vnt.name, py_type(vnt.type)) for vnt in params.vname_vtypes]
    xs = [f"{name}: {type}" for name, type in xs]
    xs = ", ".join(xs)
    xs = "connection: ConnectionType, " + xs
    return xs


def query_args(params: Params) -> str:
    qa = []
    for vnt in params.vname_vtypes:
        qa.append(f'"{vnt.name}": {vnt.name}')
    qa = ", ".join(qa)
    qa = f"{{ {qa} }}"
    return qa


def explain_args(params: Params) -> str:
    ea = [f'"{vnt.name}": None' for vnt in params.vname_vtypes]
    ea = ", ".join(ea)
    ea = f"{{ {ea} }}"
    return ea


def ret_conversions(query: Query) -> str:
    ps = []
    for i, vnt in enumerate(query.return_.vname_vtypes):
        p = f"{vnt.name} = row[{i}]"
        ps.append(p)

    ps = ",".join(ps)
    rtn = return_type_name(query)
    return f"{rtn}({ps})"


def fn_return(query: Query) -> str:
    if not query.return_.vname_vtypes:
        return "None"

    rtn = return_type_name(query)
    if query.return_.returns_one:
        return f"Optional[{rtn}]"
    else:
        return f"Iterable[{rtn}]"


def with_params(params: Params) -> bool:
    return bool(params.vname_vtypes)


def with_return(ret: Return) -> bool:
    return bool(ret.vname_vtypes)


def generate(text: str, src: str, dbcon: str, verbose: bool) -> str:
    """Generate python from annotated sql."""
    parser = get_parser()
    transformer = SqlPyGenTransformer()
    env = Environment(
        loader=PackageLoader("sqlpygen", ""),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(
        dict(
            return_type_name=return_type_name,
            py_type=py_type,
            fn_params=fn_params,
            query_args=query_args,
            explain_args=explain_args,
            ret_conversions=ret_conversions,
            fn_return=fn_return,
        )
    )
    env.tests.update(dict(with_params=with_params, with_return=with_return))

    if verbose:
        console = Console()

    try:
        parse_tree = parser.parse(text)
    except UnexpectedToken as e:
        line, col = e.line - 1, e.column - 1
        col_m1 = max(0, col)
        err_line = text.split("\n")[line]
        err_marker = "-" * col_m1 + "^"
        msg = f"Error parsing input:\n{e}\n{err_line}\n{err_marker}"
        raise RuntimeError(msg)

    if verbose:
        console.rule("Parse Tree")  # type: ignore
        console.print(parse_tree)  # type: ignore

    trans_tree = transformer.transform(parse_tree)

    if verbose:
        console.rule("Transformed tree")  # type: ignore
        console.print(trans_tree)  # type: ignore

    template = env.get_template("sqlpygen.jinja2")

    rendered_tree = template.render(
        src=src,
        dbcon=dbcon,
        module=trans_tree.module,
        imports=trans_tree.imports,
        schemas=trans_tree.schemas,
        queries=trans_tree.queries,
    )
    rendered_tree = format_str(rendered_tree, mode=Mode())
    return rendered_tree
