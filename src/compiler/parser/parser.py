"""
Parser Engine for the I Programming Language

Recursive descent parser with Pratt expression parsing.
Transforms token stream into validated AST.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field

from ..lexer.token import Token, TokenType
from ..lexer import tokenize as lex_tokenize
from ..ast.nodes import (
    ASTNode,
    AssignmentExpr,
    BinaryExpr,
    BlockExpr,
    BlockStmt,
    BreakStmt,
    CallExpr,
    ClassStmt,
    CompoundAssignmentExpr,
    ConstructorExpr,
    ContinueStmt,
    DictExpr,
    ElifBranch,
    EnumStmt,
    EnumVariant,
    Expr,
    ExportStmt,
    ExpressionStmt,
    ForEachStmt,
    ForStmt,
    FunctionParam,
    FunctionStmt,
    GetExpr,
    IfExpr,
    IfStmt,
    IdentifierExpr,
    ImportStmt,
    IndexExpr,
    InterfaceStmt,
    LambdaExpr,
    ListExpr,
    LiteralExpr,
    LogicalExpr,
    Program,
    ReturnStmt,
    SetExpr,
    SliceExpr,
    SourceSpan,
    StructField,
    StructStmt,
    SuperExpr,
    SelfExpr,
    ThrowStmt,
    TraitStmt,
    TupleExpr,
    TryStmt,
    UnaryExpr,
    UntilStmt,
    VarStmt,
    WhileStmt,
)
from .errors import ParseError, ParseErrorCode, ParseErrorCollector


# ══════════════════════════════════════════════════════════════════
# Precedence Levels
# ══════════════════════════════════════════════════════════════════


class Precedence:
    NONE = 0
    ASSIGNMENT = 1    # = += -= *= /= %= **=
    OR = 2            # cyangwa
    AND = 3           # kandi
    EQUALITY = 4      # == != === !==
    COMPARISON = 5    # > < >= <= irenze munsi munsi_ya
    BITWISE_OR = 6    # |
    BITWISE_XOR = 7   # ^
    BITWISE_AND = 8   # &
    SHIFT = 9         # << >> >>>
    TERM = 10         # + -
    FACTOR = 11       # * / %
    POWER = 12        # ** (right-assoc)
    UNARY = 13        # - ! ~ si
    CALL = 14         # () [] .
    PRIMARY = 15      # literals, identifiers


# Comparison words used as infix operators (spec'd in ILS v1.0)
WORD_OPERATORS = frozenset({'irenze', 'munsi', 'munsi_ya'})


# ══════════════════════════════════════════════════════════════════
# Statement-starting tokens
# ══════════════════════════════════════════════════════════════════

STMT_STARTERS = {
    TokenType.KW_SHYIRA, TokenType.KW_SHYIRA_KO,
    TokenType.KW_UMURIMO, TokenType.KW_IGICERI,
    TokenType.KW_IKINDI, TokenType.KW_URWEGO,
    TokenType.KW_AKABUTO, TokenType.KW_URUBINGO,
    TokenType.KW_SHYIRAMO, TokenType.KW_TANGA_YIELD,
    TokenType.KW_NIBA, TokenType.KW_WIHUSE,
    TokenType.KW_KUGEZA, TokenType.KW_KURI,
    TokenType.KW_BURI, TokenType.KW_GUKOMA,
    TokenType.KW_KUGENDA, TokenType.KW_SUBIRA,
    TokenType.KW_GUSHYINGURA, TokenType.KW_KORA,
}


# ══════════════════════════════════════════════════════════════════
# Parser
# ══════════════════════════════════════════════════════════════════


class Parser:
    """
    Recursive descent parser for the I programming language.
    
    Uses Pratt parsing for expressions.
    Blocks delimited by kora/iherezo.
    """

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._pos = 0
        self._errors = ParseErrorCollector()

    @property
    def errors(self) -> ParseErrorCollector:
        return self._errors

    @property
    def has_errors(self) -> bool:
        return self._errors.has_errors

    def parse(self) -> Program:
        """Parse token stream into a Program AST."""
        stmts: List = []
        start = self._peek()

        while not self._at_end:
            if self._errors.should_abort:
                break
            stmt = self._statement()
            if stmt is not None:
                stmts.append(stmt)

        end = self._previous() if self._pos > 0 else start
        span = self._span_between(start, end)

        return Program(declarations=stmts, location=span)

    # ── Statement Parsing ──────────────────────────────────────

    def _statement(self):
        """Parse a single statement."""
        # Skip leading newlines
        while self._match(TokenType.NEWLINE):
            pass
        if self._at_end:
            return None
        tok = self._peek()

        if tok.type == TokenType.KW_NIBA:
            return self._if_statement()
        if tok.type == TokenType.KW_WIHUSE:
            return self._while_statement()
        if tok.type == TokenType.KW_KUGEZA:
            return self._until_statement()
        if tok.type == TokenType.KW_KURI:
            return self._for_statement()
        if tok.type == TokenType.KW_BURI:
            return self._for_each_statement()
        if tok.type == TokenType.KW_GUKOMA:
            return self._break_statement()
        if tok.type == TokenType.KW_KUGENDA:
            return self._continue_statement()
        if tok.type == TokenType.KW_SUBIRA:
            return self._return_statement()
        if tok.type == TokenType.KW_GUSHYINGURA:
            return self._throw_statement()
        if tok.type == TokenType.KW_KORA:
            return self._try_statement()
        if tok.type == TokenType.KW_IHEREZO:
            return self._empty_statement()
        if tok.type == TokenType.KW_SHYIRA or tok.type == TokenType.KW_SHYIRA_KO:
            return self._var_declaration()
        if tok.type == TokenType.KW_UMURIMO:
            return self._function_declaration()
        if tok.type == TokenType.KW_IGICERI:
            return self._struct_declaration()
        if tok.type == TokenType.KW_IKINDI:
            return self._enum_declaration()
        if tok.type == TokenType.KW_URWEGO:
            return self._class_declaration()
        if tok.type == TokenType.KW_AKABUTO:
            return self._interface_declaration()
        if tok.type == TokenType.KW_URUBINGO:
            return self._trait_declaration()
        if tok.type == TokenType.KW_SHYIRAMO:
            return self._import_declaration()
        if tok.type == TokenType.KW_TANGA_YIELD:
            return self._export_declaration()

        if tok.type == TokenType.IDENTIFIER and tok.lexeme == 'andika':
            return self._print_statement()

        return self._expression_statement()

    # ── Declaration Statements ──────────────────────────────────

    def _var_declaration(self):
        """Parse: shyira name [: type] [= expr]"""
        is_const = self._peek().type == TokenType.KW_SHYIRA_KO
        kw = self._advance()

        name = self._consume(
            TokenType.IDENTIFIER,
            "variable name",
            f"Expected variable name after '{kw.lexeme}'",
        )

        type_ann = None
        if self._match(TokenType.COLON):
            type_ann = self._consume(
                TokenType.IDENTIFIER,
                "type name",
                "Expected type after ':'",
            )

        init = None
        if self._match(TokenType.EQ):
            init = self._expression()

        self._consume_newline_or_iherezo()
        self._errors.record_success()

        return VarStmt(
            name=name.lexeme,
            type_annotation=type_ann.lexeme if type_ann else None,
            initializer=init,
            is_const=is_const,
            location=self._span_from(kw),
        )

    def _function_declaration(self):
        """Parse: umurimo name(params) [-> type] kora body iherezo"""
        kw = self._advance()

        name = self._consume(
            TokenType.IDENTIFIER,
            "function name",
            "Expected function name after 'umurimo'",
        )

        self._consume(
            TokenType.LPAREN,
            "'('",
            "Expected '(' after function name",
        )
        params = self._parameters()
        self._consume(
            TokenType.RPAREN,
            "')'",
            "Expected ')' after parameters",
        )

        ret_type = None
        if self._match(TokenType.ARROW):
            ret_type = self._consume(
                TokenType.IDENTIFIER,
                "return type",
                "Expected return type after '->'",
            )

        body = self._block_body(kw)
        self._errors.record_success()

        return FunctionStmt(
            name=name.lexeme,
            parameters=params,
            return_type=ret_type.lexeme if ret_type else None,
            body=body,
            location=self._span_from(kw),
        )

    def _struct_declaration(self):
        """Parse: igiceri name kora fields iherezo"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "struct name",
            "Expected struct name after 'igiceri'",
        )

        self._consume(
            TokenType.KW_KORA,
            "kora",
            "Expected 'kora' to open struct body",
        )

        fields = []
        methods = []

        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            if self._check(TokenType.KW_UMURIMO):
                methods.append(self._function_declaration())
            else:
                field_name = self._consume(
                    TokenType.IDENTIFIER,
                    "field name",
                    "Expected field name",
                )
                self._consume(
                    TokenType.COLON,
                    "':'",
                    "Expected ':' after field name",
                )
                field_type = self._consume(
                    TokenType.IDENTIFIER,
                    "type",
                    "Expected field type",
                )
                default = None
                if self._match(TokenType.EQ):
                    default = self._expression()
                fields.append(StructField(name=field_name.lexeme, type_annotation=field_type.lexeme, default=default))
                self._consume_newline_or_iherezo()

        self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close struct",
        )

        return StructStmt(name=name.lexeme, fields=fields, methods=methods, location=self._span_from(kw))

    def _enum_declaration(self):
        """Parse: ikindi name kora variants iherezo"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "enum name",
            "Expected enum name after 'ikindi'",
        )

        self._consume(
            TokenType.KW_KORA,
            "kora",
            "Expected 'kora' to open enum body",
        )

        variants = []
        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            var_name = self._consume(
                TokenType.IDENTIFIER,
                "variant name",
                "Expected enum variant",
            )
            value = None
            if self._match(TokenType.EQ):
                value = self._expression()
            variants.append(EnumVariant(name=var_name.lexeme, value=value))
            self._consume_newline_or_iherezo()

        self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close enum",
        )

        return EnumStmt(name=name.lexeme, variants=variants, location=self._span_from(kw))

    def _class_declaration(self):
        """Parse: urwego name [kugira parent] kora members iherezo"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "class name",
            "Expected class name after 'urwego'",
        )

        parent = None
        if self._match(TokenType.KW_KUGIRA):
            parent = self._consume(
                TokenType.IDENTIFIER,
                "parent class",
                "Expected parent class name after 'kugira'",
            )

        self._consume(
            TokenType.KW_KORA,
            "kora",
            "Expected 'kora' to open class body",
        )

        members = []
        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            members.append(self._statement())

        self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close class",
        )

        return ClassStmt(name=name.lexeme, parent=parent.lexeme if parent else None, members=members, location=self._span_from(kw))

    def _interface_declaration(self):
        """Parse: akabuto name kora members iherezo"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "interface name",
            "Expected interface name after 'akabuto'",
        )

        self._consume(
            TokenType.KW_KORA,
            "kora",
            "Expected 'kora' to open interface body",
        )

        members = []
        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            members.append(self._statement())

        self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close interface",
        )

        return InterfaceStmt(name=name.lexeme, members=members, location=self._span_from(kw))

    def _trait_declaration(self):
        """Parse: urubingo name kora members iherezo"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "trait name",
            "Expected trait name after 'urubingo'",
        )

        self._consume(
            TokenType.KW_KORA,
            "kora",
            "Expected 'kora' to open trait body",
        )

        members = []
        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            members.append(self._statement())

        self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close trait",
        )

        return TraitStmt(name=name.lexeme, members=members, location=self._span_from(kw))

    def _import_declaration(self):
        """Parse: shyiramo path [kugira_ngo alias]"""
        kw = self._advance()
        path = self._consume(
            TokenType.IDENTIFIER,
            "module path",
            "Expected module name after 'shyiramo'",
        )

        alias = None
        if self._match(TokenType.KW_KUGIRA_NGO):
            alias = self._consume(
                TokenType.IDENTIFIER,
                "alias",
                "Expected alias after 'kugira ngo'",
            )

        self._consume_newline_or_iherezo()
        return ImportStmt(path=path.lexeme, alias=alias.lexeme if alias else None, location=self._span_from(kw))

    def _export_declaration(self):
        """Parse: tanga name"""
        kw = self._advance()
        name = self._consume(
            TokenType.IDENTIFIER,
            "name",
            "Expected name after 'tanga'",
        )
        self._consume_newline_or_iherezo()
        return ExportStmt(name=name.lexeme, location=self._span_from(kw))

    # ── Block Statements ────────────────────────────────────────

    def _block_body(self, opening_token: Token) -> BlockStmt:
        """Parse block body: kora ... iherezo"""
        self._match(TokenType.KW_KORA)
        stmts = []
        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            stmt = self._statement()
            if stmt is not None:
                stmts.append(stmt)

        iherezo = self._consume(
            TokenType.KW_IHEREZO,
            "iherezo",
            "Expected 'iherezo' to close block",
        )

        return BlockStmt(
            statements=stmts,
            location=SourceSpan(
                file="<input>",
                start_line=opening_token.line,
                start_column=opening_token.column,
                end_line=iherezo.line,
                end_column=iherezo.column,
            ),
        )

    def _branch_body(self, opening_token: Token, extra_stop: set = None) -> BlockStmt:
        """Parse branch body: kora ... until cyangwa_niba/cyangwa/iherezo"""
        self._match(TokenType.KW_KORA)
        stop_tokens = {TokenType.KW_IHEREZO, TokenType.KW_CYANGWA, TokenType.KW_CYANGWA_NIBA}
        if extra_stop:
            stop_tokens |= extra_stop
        stmts = []
        while not self._at_end:
            tok = self._peek()
            if tok.type in stop_tokens:
                break
            if tok.type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._statement()
            if stmt is not None:
                stmts.append(stmt)
        return BlockStmt(
            statements=stmts,
            location=SourceSpan(
                file="<input>",
                start_line=opening_token.line,
                start_column=opening_token.column,
                end_line=0, end_column=0,
            ),
        )

    def _if_statement(self):
        """Parse: niba cond kora body [cyangwa_niba ...] [cyangwa ...] [iherezo]"""
        kw = self._advance()
        condition = self._expression()
        then_body = self._branch_body(kw)
        self._match(TokenType.KW_IHEREZO)

        elifs = []
        self._consume_newlines()
        while self._match(TokenType.KW_CYANGWA_NIBA):
            elif_kw = self._previous()
            elif_cond = self._expression()
            elif_body = self._branch_body(elif_kw)
            self._match(TokenType.KW_IHEREZO)
            self._consume_newlines()
            elifs.append(ElifBranch(condition=elif_cond, body=elif_body, location=self._span_from(elif_kw)))

        else_body = None
        if self._match(TokenType.KW_CYANGWA):
            else_kw = self._previous()
            else_body = self._branch_body(else_kw)
            self._match(TokenType.KW_IHEREZO)

        return IfStmt(
            condition=condition,
            then_branch=then_body,
            elif_branches=elifs,
            else_branch=else_body,
            location=self._span_from(kw),
        )

    def _while_statement(self):
        """Parse: wihuse condition kora body iherezo"""
        kw = self._advance()
        condition = self._expression()
        body = self._block_body(kw)
        return WhileStmt(condition=condition, body=body, location=self._span_from(kw))

    def _until_statement(self):
        """Parse: kugeza condition kora body iherezo"""
        kw = self._advance()
        condition = self._expression()
        body = self._block_body(kw)
        return UntilStmt(condition=condition, body=body, location=self._span_from(kw))

    def _for_statement(self):
        """Parse: kuri var (muri|=) start kugeza end [step]? kora body iherezo"""
        kw = self._advance()
        var = self._consume(TokenType.IDENTIFIER, "loop variable", "Expected variable name after 'kuri'")
        if not self._match(TokenType.EQ, TokenType.KW_MURI):
            self._error(
                ParseErrorCode.PARS002_MISSING_TOKEN,
                self._peek(),
                "'=' or 'muri'",
                self._peek().lexeme,
            )
        start = self._expression()
        self._consume(TokenType.KW_KUGEZA, "kugeza", "Expected 'kugeza' after start")
        end = self._expression()

        step = None
        if (
            not self._check(TokenType.KW_KORA)
            and not self._check(TokenType.NEWLINE)
            and not self._at_end
        ):
            step = self._expression()

        body = self._block_body(kw)
        return ForStmt(variable=var.lexeme, start=start, end=end, step=step, body=body, location=self._span_from(kw))

    def _for_each_statement(self):
        """Parse: buri element muri iterable [kugeza end]? kora body iherezo"""
        kw = self._advance()
        elem = self._consume(TokenType.IDENTIFIER, "element", "Expected element name after 'buri'")
        self._consume(TokenType.KW_MURI, "muri", "Expected 'muri' after element name")
        iterable = self._expression()

        if self._match(TokenType.KW_KUGEZA):
            end = self._expression()
            body = self._block_body(kw)
            return ForStmt(
                variable=elem.lexeme, start=iterable, end=end, step=None,
                body=body, location=self._span_from(kw),
            )

        body = self._block_body(kw)
        return ForEachStmt(element=elem.lexeme, iterable=iterable, body=body, location=self._span_from(kw))

    def _break_statement(self):
        kw = self._advance()
        self._consume_newline_or_iherezo()
        return BreakStmt( location=self._span_from(kw))

    def _continue_statement(self):
        kw = self._advance()
        self._consume_newline_or_iherezo()
        return ContinueStmt( location=self._span_from(kw))

    def _return_statement(self):
        kw = self._advance()
        value = None
        if not self._check(TokenType.NEWLINE) and not self._check(TokenType.KW_IHEREZO) and not self._at_end:
            value = self._expression()
        self._consume_newline_or_iherezo()
        return ReturnStmt( value=value, location=self._span_from(kw))

    def _throw_statement(self):
        kw = self._advance()
        value = self._expression()
        self._consume_newline_or_iherezo()
        return ThrowStmt( value=value, location=self._span_from(kw))

    def _try_statement(self):
        """Parse: kora body kubika var body [ikinyoma body] iherezo"""
        kw = self._advance()
        try_body = self._branch_body(kw, {TokenType.KW_KUBIKA, TokenType.KW_IKINYOMA})

        catch_var = None
        catch_body = None
        if self._match(TokenType.KW_KUBIKA):
            catch_var = self._consume(TokenType.IDENTIFIER, "catch variable", "Expected variable name after 'kubika'")
            catch_body = self._branch_body(kw, {TokenType.KW_IKINYOMA})

        finally_body = None
        if self._match(TokenType.KW_IKINYOMA):
            finally_body = self._branch_body(kw)

        self._consume(TokenType.KW_IHEREZO, "iherezo", "Expected 'iherezo' to close try block")

        return TryStmt(
            try_body=try_body,
            catch_var=catch_var.lexeme if catch_var else None,
            catch_body=catch_body,
            finally_body=finally_body,
            location=self._span_from(kw),
        )

    def _empty_statement(self):
        kw = self._advance()
        self._consume_newline_or_iherezo()
        return BlockStmt(statements=[], location=self._span_from(kw))

    def _expression_statement(self):
        expr = self._expression()
        self._consume_newline_or_iherezo()
        return ExpressionStmt(expression=expr, location=expr.span)

    def _print_statement(self):
        """Parse a print statement: andika <expr>"""
        kw = self._advance()

        if self._at_end or self._peek().type in (TokenType.NEWLINE, TokenType.KW_IHEREZO):
            self._error(
                ParseErrorCode.PARS003_INVALID_EXPRESSION,
                self._peek(),
                "expression",
                "end of statement",
            )
            self._consume_newline_or_iherezo()
            return None

        expr = self._expression()
        self._consume_newline_or_iherezo()

        callee = IdentifierExpr(name="andika", location=self._span_from(kw))
        call = CallExpr(callee=callee, arguments=[expr], location=expr.span)
        return ExpressionStmt(expression=call, location=expr.span)

    # ── Expression Parsing (Pratt) ─────────────────────────────

    def _expression(self):
        return self._parse_precedence(Precedence.ASSIGNMENT)

    def _parse_precedence(self, min_prec: int):
        """Pratt parsing: parse expression with minimum precedence."""
        left = self._prefix()

        while not self._at_end:
            prec = self._infix_precedence(self._peek().type)
            if self._is_word_operator(self._peek()):
                prec = Precedence.COMPARISON
            if min_prec > prec:
                break
            left = self._infix(left)

        return left

    def _is_word_operator(self, tok: Token) -> bool:
        """Check if a token is a word comparison operator."""
        return tok.type == TokenType.IDENTIFIER and tok.lexeme in WORD_OPERATORS

    def _prefix(self):
        """Parse prefix expression."""
        tok = self._peek()

        # Literals
        if tok.type == TokenType.INTEGER:
            self._advance()
            return LiteralExpr(value=tok.value, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.FLOAT:
            self._advance()
            return LiteralExpr(value=tok.value, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.STRING:
            self._advance()
            return LiteralExpr(value=tok.value, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.TRIPLE_STRING:
            self._advance()
            return LiteralExpr(value=tok.value, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.CHARACTER:
            self._advance()
            return LiteralExpr(value=tok.value, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.BOOLEAN_TRUE or tok.type == TokenType.KW_TRUE_EN:
            self._advance()
            return LiteralExpr(value=True, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.BOOLEAN_FALSE or tok.type == TokenType.KW_FALSE_EN:
            self._advance()
            return LiteralExpr(value=False, token_type=tok.type, location=SourceSpan.from_token(tok))
        if tok.type == TokenType.NULL or tok.type == TokenType.KW_NULL_EN:
            self._advance()
            return LiteralExpr(value=None, token_type=tok.type, location=SourceSpan.from_token(tok))

        # Identifier (including keywords used as identifiers)
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return IdentifierExpr(name=tok.lexeme, location=SourceSpan.from_token(tok))

        # Keywords allowed as identifiers in expression context
        if tok.type in (TokenType.KW_UBWOKO, TokenType.KW_KUBIKA, TokenType.KW_IKINYOMA, TokenType.KW_IHEREZO):
            self._advance()
            return IdentifierExpr(name=tok.lexeme, location=SourceSpan.from_token(tok))

        # Unary operators
        if tok.type in (TokenType.MINUS, TokenType.BANG, TokenType.TILDE, TokenType.KW_SI):
            self._advance()
            right = self._parse_precedence(Precedence.UNARY)
            return UnaryExpr(operator=tok.lexeme, right=right, location=self._span_from(tok))

        # Self/Super
        if tok.type == TokenType.KW_SELF:
            self._advance()
            return SelfExpr( location=SourceSpan.from_token(tok))
        if tok.type == TokenType.KW_SUPER:
            self._advance()
            self._consume(TokenType.DOT, "'.'", "Expected '.' after 'super'")
            method = self._consume(TokenType.IDENTIFIER, "method name", "Expected method name after 'super.'")
            return SuperExpr(method=method.lexeme, location=self._span_from(tok))

        # Grouping
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._expression()
            self._consume(TokenType.RPAREN, "')'", "Expected ')' after expression")
            return GroupingExprWrapper(expr, location=self._span_from(tok))

        # List literal
        if tok.type == TokenType.LBRACKET:
            return self._list_literal()

        # Dict literal
        if tok.type == TokenType.LBRACE:
            return self._dict_literal()

        # Constructor: gukora ClassName(...)
        if tok.type == TokenType.KW_GUKORA:
            return self._constructor()

        # Block expression: kora ... iherezo
        if tok.type == TokenType.KW_KORA:
            return self._block_expression()

        # If expression: niba ... kora expr iherezo
        if tok.type == TokenType.KW_NIBA:
            return self._if_expression()

        self._error(
            ParseErrorCode.PARS003_INVALID_EXPRESSION,
            tok,
            "expression",
            tok.lexeme,
        )
        self._advance()
        return LiteralExpr(value=None, token_type=tok.type, location=SourceSpan.from_token(tok))

    def _infix(self, left):
        """Parse infix expression."""
        tok = self._peek()

        # Assignment
        if tok.type == TokenType.EQ:
            return self._assignment_expr(left)
        if tok.type in (
            TokenType.PLUS_EQ, TokenType.MINUS_EQ, TokenType.STAR_EQ,
            TokenType.SLASH_EQ, TokenType.PERCENT_EQ, TokenType.STAR_STAR_EQ,
        ):
            return self._compound_assignment_expr(left)

        # Logical operators
        if tok.type == TokenType.KW_CYANGWA or tok.type == TokenType.OR_OR:
            return self._logical_expr(left)
        if tok.type == TokenType.KW_KANDI or tok.type == TokenType.AND_AND:
            return self._logical_expr(left)

        # Binary operators
        if tok.type in (
            TokenType.EQ_EQ, TokenType.BANG_EQ, TokenType.IS_EQ, TokenType.BANG_IS_EQ,
            TokenType.GT, TokenType.LT, TokenType.GT_EQ, TokenType.LT_EQ,
            TokenType.PLUS, TokenType.MINUS,
            TokenType.STAR, TokenType.SLASH, TokenType.PERCENT,
            TokenType.STAR_STAR,
            TokenType.AMP, TokenType.PIPE, TokenType.CARET,
            TokenType.LT_LT, TokenType.GT_GT, TokenType.GT_GT_GT,
        ):
            return self._binary_expr(left)

        # Word comparison operators (irenze, munsi, munsi_ya)
        if self._is_word_operator(tok):
            return self._binary_expr(left)

        # Call
        if tok.type == TokenType.LPAREN:
            return self._call_expr(left)

        # Property access
        if tok.type == TokenType.DOT:
            return self._get_expr(left)

        # Index
        if tok.type == TokenType.LBRACKET:
            return self._index_expr(left)

        # Optional chaining
        if tok.type == TokenType.QUESTION_DOT:
            return self._get_expr(left)

        return left

    def _infix_precedence(self, tok_type: TokenType) -> int:
        """Get precedence for infix operator."""
        if tok_type == TokenType.EQ:
            return Precedence.ASSIGNMENT
        if tok_type in (
            TokenType.PLUS_EQ, TokenType.MINUS_EQ, TokenType.STAR_EQ,
            TokenType.SLASH_EQ, TokenType.PERCENT_EQ, TokenType.STAR_STAR_EQ,
        ):
            return Precedence.ASSIGNMENT
        if tok_type == TokenType.KW_CYANGWA or tok_type == TokenType.OR_OR:
            return Precedence.OR
        if tok_type == TokenType.KW_KANDI or tok_type == TokenType.AND_AND:
            return Precedence.AND
        if tok_type in (TokenType.EQ_EQ, TokenType.BANG_EQ, TokenType.IS_EQ, TokenType.BANG_IS_EQ):
            return Precedence.EQUALITY
        if tok_type in (TokenType.GT, TokenType.LT, TokenType.GT_EQ, TokenType.LT_EQ):
            return Precedence.COMPARISON
        if tok_type == TokenType.PIPE:
            return Precedence.BITWISE_OR
        if tok_type == TokenType.CARET:
            return Precedence.BITWISE_XOR
        if tok_type == TokenType.AMP:
            return Precedence.BITWISE_AND
        if tok_type in (TokenType.LT_LT, TokenType.GT_GT, TokenType.GT_GT_GT):
            return Precedence.SHIFT
        if tok_type in (TokenType.PLUS, TokenType.MINUS):
            return Precedence.TERM
        if tok_type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            return Precedence.FACTOR
        if tok_type == TokenType.STAR_STAR:
            return Precedence.POWER
        if tok_type in (TokenType.LPAREN, TokenType.DOT, TokenType.LBRACKET, TokenType.QUESTION_DOT):
            return Precedence.CALL
        return Precedence.NONE

    def _binary_expr(self, left):
        op = self._advance()
        prec = self._infix_precedence(op.type)
        if self._is_word_operator(op):
            prec = Precedence.COMPARISON
        # Right-associative for **
        if op.type == TokenType.STAR_STAR:
            right = self._parse_precedence(Precedence.POWER)
        else:
            right = self._parse_precedence(prec + 1)
        return BinaryExpr(left=left, operator=op.lexeme, right=right, location=self._span_from_tokens(left.span, right.span))

    def _logical_expr(self, left):
        op = self._advance()
        right = self._parse_precedence(self._infix_precedence(op.type) + 1)
        return LogicalExpr(left=left, operator=op.lexeme, right=right, location=self._span_from_tokens(left.span, right.span))

    def _assignment_expr(self, left):
        eq = self._advance()
        value = self._parse_precedence(Precedence.ASSIGNMENT)
        return AssignmentExpr(target=left, value=value, location=self._span_from_tokens(left.span, value.span))

    def _compound_assignment_expr(self, left):
        op = self._advance()
        value = self._parse_precedence(Precedence.ASSIGNMENT)
        return CompoundAssignmentExpr(target=left, operator=op.lexeme, value=value, location=self._span_from_tokens(left.span, value.span))

    def _call_expr(self, callee):
        paren = self._advance()
        args = self._arguments()
        self._consume(TokenType.RPAREN, "')'", "Expected ')' after arguments")
        return CallExpr(callee=callee, arguments=args, location=self._span_from_tokens(callee.span, SourceSpan.from_token(self._previous())))

    def _get_expr(self, obj):
        dot = self._advance()
        name = self._consume(TokenType.IDENTIFIER, "property name", "Expected property name after '.'")
        return GetExpr(object=obj, property=name.lexeme, location=self._span_from_tokens(obj.span, SourceSpan.from_token(name)))

    def _index_expr(self, obj):
        bracket = self._advance()
        idx = self._expression()

        if self._match(TokenType.COLON):
            end = None
            if not self._check(TokenType.RBRACKET):
                end = self._expression()
            self._consume(TokenType.RBRACKET, "']'", "Expected ']' after slice")
            return SliceExpr(object=obj, start=idx, end=end, location=self._span_from_tokens(obj.span, SourceSpan.from_token(self._previous())))

        self._consume(TokenType.RBRACKET, "']'", "Expected ']' after index")
        return IndexExpr(object=obj, index=idx, location=self._span_from_tokens(obj.span, SourceSpan.from_token(self._previous())))

    def _constructor(self):
        kw = self._advance()
        name = self._consume(TokenType.IDENTIFIER, "class name", "Expected class name after 'gukora'")
        paren = self._consume(TokenType.LPAREN, "'('", "Expected '(' after class name")
        args = self._arguments()
        self._consume(TokenType.RPAREN, "')'", "Expected ')' after arguments")
        return ConstructorExpr(class_name=name.lexeme, arguments=args, location=self._span_from(kw))

    def _list_literal(self):
        bracket = self._advance()
        elements = []
        if not self._check(TokenType.RBRACKET):
            elements.append(self._expression())
            while self._match(TokenType.COMMA):
                elements.append(self._expression())
        self._consume(TokenType.RBRACKET, "']'", "Expected ']' after list")
        return ListExpr(elements=elements, location=SourceSpan.from_token(bracket))

    def _dict_literal(self):
        brace = self._advance()
        keys = []
        values = []
        if not self._check(TokenType.RBRACE):
            k = self._expression()
            self._consume(TokenType.COLON, "':'", "Expected ':' after dict key")
            v = self._expression()
            keys.append(k)
            values.append(v)
            while self._match(TokenType.COMMA):
                k = self._expression()
                self._consume(TokenType.COLON, "':'", "Expected ':' after dict key")
                v = self._expression()
                keys.append(k)
                values.append(v)
        self._consume(TokenType.RBRACE, "'}'", "Expected '}' after dict")
        return DictExpr(keys=keys, values=values, location=SourceSpan.from_token(brace))

    def _block_expression(self):
        kw = self._advance()
        stmts = []
        result = None

        while not self._at_end:
            if self._match(TokenType.NEWLINE):
                continue
            if self._check(TokenType.KW_IHEREZO):
                break
            if self._peek_next_type() == TokenType.KW_IHEREZO:
                result = self._expression()
            else:
                stmts.append(self._statement())

        self._consume(TokenType.KW_IHEREZO, "iherezo", "Expected 'iherezo' to close block expression")
        return BlockExpr(statements=stmts, location=self._span_from(kw))

    def _if_expression(self):
        kw = self._advance()
        condition = self._expression()
        self._consume(TokenType.KW_KORA, "kora", "Expected 'kora' after if condition")
        then_expr = self._expression()
        self._consume(TokenType.KW_IHEREZO, "iherezo", "Expected 'iherezo' to close if expression")
        else_expr = None
        if self._match(TokenType.KW_CYANGWA):
            else_expr = self._expression()
        return IfExpr(condition=condition, then_branch=then_expr, else_branch=else_expr, location=self._span_from(kw))

    def _lambda_expr(self):
        kw = self._advance()
        params = self._parameters()
        self._consume(TokenType.FAT_ARROW, "'=>'", "Expected '=>' after lambda parameters")
        body = self._expression()
        return LambdaExpr(parameters=params, body=body, location=self._span_from(kw))

    # ── Helpers ─────────────────────────────────────────────────

    def _arguments(self) -> list:
        args = []
        if not self._check(TokenType.RPAREN):
            args.append(self._expression())
            while self._match(TokenType.COMMA):
                args.append(self._expression())
        return args

    def _parameters(self) -> List[FunctionParam]:
        params = []
        if not self._check(TokenType.RPAREN):
            name = self._consume(TokenType.IDENTIFIER, "parameter name", "Expected parameter name")
            type_ann = None
            if self._match(TokenType.COLON):
                type_ann = self._consume(TokenType.IDENTIFIER, "type", "Expected type after ':'")
            default = None
            if self._match(TokenType.EQ):
                default = self._expression()
            params.append(FunctionParam(name=name.lexeme, type_annotation=type_ann.lexeme if type_ann else None, default=default))
            while self._match(TokenType.COMMA):
                name = self._consume(TokenType.IDENTIFIER, "parameter name", "Expected parameter name")
                type_ann = None
                if self._match(TokenType.COLON):
                    type_ann = self._consume(TokenType.IDENTIFIER, "type", "Expected type after ':'")
                default = None
                if self._match(TokenType.EQ):
                    default = self._expression()
                params.append(FunctionParam(name=name.lexeme, type_annotation=type_ann.lexeme if type_ann else None, default=default))
        return params

    def _consume_newline_or_iherezo(self):
        """Consume optional newline."""
        self._match(TokenType.NEWLINE)

    def _consume_newlines(self):
        """Consume all consecutive newlines."""
        while self._match(TokenType.NEWLINE):
            pass

    # ── Token Operations ───────────────────────────────────────

    def _peek(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return self._tokens[-1] if self._tokens else Token(
            type=TokenType.EOF, lexeme="", location=None
        )

    def _peek_next_type(self) -> Optional[TokenType]:
        if self._pos + 1 < len(self._tokens):
            return self._tokens[self._pos + 1].type
        return None

    def _advance(self) -> Token:
        tok = self._peek()
        if not self._at_end:
            self._pos += 1
        return tok

    def _check(self, token_type: TokenType) -> bool:
        return not self._at_end and self._peek().type == token_type

    @property
    def _at_end(self) -> bool:
        return self._pos >= len(self._tokens) or self._peek().type == TokenType.EOF

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._peek().type == t:
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, expected_name: str, error_msg: str) -> Token:
        if self._peek().type == token_type:
            return self._advance()

        self._error(
            ParseErrorCode.PARS001_UNEXPECTED_TOKEN,
            self._peek(),
            expected_name,
            self._peek().lexeme,
        )
        return self._peek()

    def _previous(self) -> Token:
        if self._pos > 0:
            return self._tokens[self._pos - 1]
        return self._tokens[0]

    def _error(self, code: ParseErrorCode, token: Token, expected: str, found: str):
        self._errors.add(code, token, expected, found)

    def _span_from(self, start_token: Token) -> SourceSpan:
        return SourceSpan.from_token(start_token)

    def _span_from_tokens(self, start: SourceSpan, end: SourceSpan) -> SourceSpan:
        return SourceSpan.merge(start, end)

    def _span_between(self, start: Token, end: Token) -> SourceSpan:
        return SourceSpan(
            file="<input>",
            start_line=start.line,
            start_column=start.column,
            end_line=end.line,
            end_column=end.column + end.span,
        )


@dataclass
class GroupingExprWrapper(Expr):
    """Wrapper for grouping expression (parenthesized)."""
    expression: Any
    span: SourceSpan = field(default_factory=SourceSpan)

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self) if hasattr(visitor, 'visit_grouping_expr') else None


# ══════════════════════════════════════════════════════════════════
# Convenience Function
# ══════════════════════════════════════════════════════════════════


def parse(source: str) -> tuple:
    """
    Parse I language source code.
    
    Returns:
        Tuple of (Program AST, list of errors)
    """
    tokens, lex_errors = lex_tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast, parser.errors.errors + lex_errors
