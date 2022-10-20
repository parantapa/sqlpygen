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
class Parameter:
    name: str
    type: str
    simple_type: bool


# @dataclass
# class Parameters:
#     fn_params: str
#     conversions: list[str]
#     query_args: Optional[str]
#     explain_args: Optional[str]
#     has_params: bool


@dataclass
class Parameters:
    params: list[Parameter]


@dataclass
class ReturnType:
    type: str
    optional: bool
    simple_type: bool


# @dataclass
# class Return:
#     fn_return: str
#     conversions: list[str]
#     returns_one: Optional[bool]
#     does_return: bool


@dataclass
class Return:
    rtypes: list[ReturnType]
    returns_one: Optional[bool]


@dataclass
class Schema:
    name: str
    sql: str


@dataclass
class Query:
    name: str
    params: Parameters
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

    def pname_ptype(self, ts):
        pname, ptype = ts
        if ptype in ("str", "bytes", "int", "float", "bool"):
            simple_type = True
        else:
            simple_type = False
        return Parameter(pname, ptype, simple_type)

    def params(self, ts):
        return Parameters(list(ts))

    def rtype_opt(self, ts):
        rtype = ts[0]
        if rtype in ("str", "bytes", "int", "float", "bool"):
            simple_type = True
        else:
            simple_type = False
        return ReturnType(rtype, True, simple_type)

    def rtype_not_opt(self, ts):
        rtype = ts[0]
        if rtype in ("str", "bytes", "int", "float", "bool"):
            simple_type = True
        else:
            simple_type = False
        return ReturnType(rtype, False, simple_type)

    def returnone(self, ts):
        return Return(list(ts), True)

    def returnmany(self, ts):
        return Return(list(ts), False)

    def schema(self, ts):
        name, sql = ts
        return Schema(name, sql)

    def query(self, ts):
        name, sql = ts[0], ts[-1]
        params = Parameters([])
        return_ = Return([], None)
        for t in ts[1:-1]:
            if isinstance(t, Parameters):
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


def fn_params(params: Parameters) -> str:
    if not params.params:
        return "connection: ConnectionType"
    x = [f"{p.name}: {p.type}" for p in params.params]
    x = ", ".join(x)
    x = "connection: ConnectionType, " + x
    return x


def param_conversions(params: Parameters) -> list[str]:
    convs = []
    for p in params.params:
        if not p.simple_type:
            convs.append(f"{p.name}_json = {p.name}.json()")
    return convs


def query_args(params: Parameters) -> str:
    qa = []
    for p in params.params:
        if p.simple_type:
            qa.append(f'"{p.name}": {p.name}')
        else:
            qa.append(f'"{p.name}": {p.name}_json')
    qa = ", ".join(qa)
    qa = f"{{ {qa} }}"
    return qa


def explain_args(params: Parameters) -> str:
    ea = [f'"{p.name}": None' for p in params.params]
    ea = ", ".join(ea)
    ea = f"{{ {ea} }}"
    return ea


def ret_conversions(ret: Return) -> list[str]:
    convs = []
    for i, r in enumerate(ret.rtypes):
        if not r.simple_type:
            convs.append(
                f"row[{i}] = None if row[{i}] is None else {r.type}.parse_raw(row[{i}])"
            )
    if convs:
        convs = ["row = list(row)"] + convs + ["row = tuple(row)"]
    return convs


def fn_return(ret: Return) -> str:
    if not ret.rtypes:
        return "None"

    rstr = []
    for r in ret.rtypes:
        if r.optional:
            rstr.append(f"Optional[{r.type}]")
        else:
            rstr.append(r.type)
    rstr = ", ".join(rstr)
    if ret.returns_one:
        rstr = f"Optional[tuple[{rstr}]]"
    else:
        rstr = f"Iterable[tuple[{rstr}]]"
    return rstr


def with_params(params: Parameters) -> bool:
    return bool(params.params)


def with_return(ret: Return) -> bool:
    return bool(ret.rtypes)


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
            fn_params=fn_params,
            param_conversions=param_conversions,
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
