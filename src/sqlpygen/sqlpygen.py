"""Generate type annotated python from SQL."""

from importlib.resources import read_text
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from black import format_str, Mode  # type: ignore
from lark import Lark, Transformer, UnexpectedToken  # type: ignore
from jinja2 import Template, StrictUndefined, TemplateSyntaxError


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


@dataclass
class Parameters:
    fn_params: str
    conversions: list[str]
    query_args: Optional[str]
    explain_args: Optional[str]
    has_params: bool


@dataclass
class RType:
    type: str
    optional: bool
    simple_type: bool


@dataclass
class Return:
    fn_return: str
    conversions: list[str]
    returns_one: Optional[bool]
    does_return: bool


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
        fn_params = [f"{p.name}: {p.type}" for p in ts]
        fn_params = ", ".join(fn_params)
        fn_params = "connection: ConnectionType, " + fn_params

        conversions = []
        for p in ts:
            if not p.simple_type:
                conversions.append(f"{p.name}_json = {p.name}.json()")

        query_args = []
        for p in ts:
            if p.simple_type:
                query_args.append(f'"{p.name}": {p.name}')
            else:
                query_args.append(f'"{p.name}": {p.name}_json')
        query_args = ", ".join(query_args)
        query_args = f"{{ {query_args} }}"

        explain_args = [f'"{p.name}": None' for p in ts]
        explain_args = ", ".join(explain_args)
        explain_args = f"{{ {explain_args} }}"

        return Parameters(fn_params, conversions, query_args, explain_args, True)

    def rtype_opt(self, ts):
        rtype = ts[0]
        if rtype in ("str", "bytes", "int", "float", "bool"):
            simple_type = True
        else:
            simple_type = False
        return RType(rtype, True, simple_type)

    def rtype_not_opt(self, ts):
        rtype = ts[0]
        if rtype in ("str", "bytes", "int", "float", "bool"):
            simple_type = True
        else:
            simple_type = False
        return RType(rtype, False, simple_type)

    def returnone(self, ts):
        conversions = []
        for i, r in enumerate(ts):
            if not r.simple_type:
                conversions.append(f"row[{i}] = None if row[{i}] is None else {r.type}.parse_raw(row[{i}])")

        fn_return = []
        for r in ts:
            if r.optional:
                fn_return.append(f"Optional[{r.type}]")
            else:
                fn_return.append(r.type)
        fn_return = ", ".join(fn_return)
        fn_return = f"Optional[tuple[{fn_return}]]"

        return Return(fn_return, conversions, True, True)

    def returnmany(self, ts):
        conversions = []
        for i, r in enumerate(ts):
            if not r.simple_type:
                conversions.append(f"row[{i}] = None if row[{i}] is None else {r.type}.parse_raw(row[{i}])")

        fn_return = []
        for r in ts:
            if r.optional:
                fn_return.append(f"Optional[{r.type}]")
            else:
                fn_return.append(r.type)
        fn_return = ", ".join(fn_return)
        fn_return = f"Iterable[tuple[{fn_return}]]"

        return Return(fn_return, conversions, False, True)

    def schema(self, ts):
        name, sql = ts
        return Schema(name, sql)

    def query(self, ts):
        name, sql = ts[0], ts[-1]
        params = Parameters("connection: ConnectionType", [], None, None, False)
        return_ = Return("None", [], None, False)
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


def get_template() -> Template:
    """Return the code generation template."""
    tpl_text = read_text("sqlpygen", "sqlpygen.jinja2")
    try:
        tpl_obj = Template(
            tpl_text, trim_blocks=True, lstrip_blocks=True, undefined=StrictUndefined
        )
    except TemplateSyntaxError as e:
        raise ValueError(f"Syntax error in template line {e.lineno}") from e
    return tpl_obj


def generate(text: str, src: str, dbcon: str, verbose: bool) -> str:
    """Generate python from annotated sql."""
    parser = get_parser()
    transformer = SqlPyGenTransformer()
    template = get_template()

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
