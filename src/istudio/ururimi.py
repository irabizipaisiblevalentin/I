"""I STUDIO — Language Server / Language Intelligence (Ururimi)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    CodeAction,
    CompletionItem,
    CompletionKind,
    Diagnostic,
    DiagnosticSeverity,
    DocumentPosition,
    DocumentRange,
    HoverInfo,
    LanguageServerError,
    SymbolInfo,
    SymbolKind,
)


class LanguageServer:
    def __init__(self):
        self._diagnostics: Dict[str, List[Diagnostic]] = {}
        self._symbols: Dict[str, List[SymbolInfo]] = {}
        self._workspace_files: List[str] = []

    def analyze(self, content: str, file_path: str = "unnamed.i") -> List[Diagnostic]:
        diagnostics: List[Diagnostic] = []
        lines = content.split("\n")

        for line_idx, line in enumerate(lines):
            if re.search(r'\bundefined\b', line, re.IGNORECASE):
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    message="Possible undefined reference",
                    range=DocumentRange(
                        start=DocumentPosition(line=line_idx, column=0),
                        end=DocumentPosition(line=line_idx, column=len(line)),
                    ),
                    source="i",
                    code="undefined-ref",
                ))

            quote_count = line.count('"')
            if quote_count % 2 != 0:
                last_quote = line.rfind('"')
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    message="Unterminated string literal",
                    range=DocumentRange(
                        start=DocumentPosition(line=line_idx, column=last_quote),
                        end=DocumentPosition(line=line_idx, column=len(line)),
                    ),
                    source="i",
                    code="unterminated-string",
                ))

            for match in re.finditer(r'(?<!\w)(\d+)(?!\w)', line):
                num = int(match.group(1))
                if num > 2147483647:
                    diagnostics.append(Diagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        message="Integer literal exceeds 32-bit range",
                        range=DocumentRange(
                            start=DocumentPosition(line=line_idx, column=match.start()),
                            end=DocumentPosition(line=line_idx, column=match.end()),
                        ),
                        source="i",
                        code="int-overflow",
                    ))

        self._diagnostics[file_path] = diagnostics
        return diagnostics

    def get_completions(self, content: str, position: DocumentPosition, file_path: str = "unnamed.i") -> List[CompletionItem]:
        lines = content.split("\n")
        if position.line >= len(lines):
            return []
        line = lines[position.line][:position.column]

        keyword_completions = [
            CompletionItem(label="if", kind=CompletionKind.KEYWORD, detail="Conditional statement"),
            CompletionItem(label="else", kind=CompletionKind.KEYWORD, detail="Alternative branch"),
            CompletionItem(label="for", kind=CompletionKind.KEYWORD, detail="For loop"),
            CompletionItem(label="while", kind=CompletionKind.KEYWORD, detail="While loop"),
            CompletionItem(label="return", kind=CompletionKind.KEYWORD, detail="Return from function"),
            CompletionItem(label="function", kind=CompletionKind.KEYWORD, detail="Function declaration"),
            CompletionItem(label="let", kind=CompletionKind.KEYWORD, detail="Variable declaration"),
            CompletionItem(label="const", kind=CompletionKind.KEYWORD, detail="Constant declaration"),
            CompletionItem(label="class", kind=CompletionKind.KEYWORD, detail="Class declaration"),
            CompletionItem(label="import", kind=CompletionKind.KEYWORD, detail="Import module"),
            CompletionItem(label="from", kind=CompletionKind.KEYWORD, detail="Import from module"),
            CompletionItem(label="export", kind=CompletionKind.KEYWORD, detail="Export declaration"),
            CompletionItem(label="match", kind=CompletionKind.KEYWORD, detail="Pattern matching"),
            CompletionItem(label="try", kind=CompletionKind.KEYWORD, detail="Error handling"),
            CompletionItem(label="catch", kind=CompletionKind.KEYWORD, detail="Catch exception"),
            CompletionItem(label="throw", kind=CompletionKind.KEYWORD, detail="Throw exception"),
            CompletionItem(label="async", kind=CompletionKind.KEYWORD, detail="Async function"),
            CompletionItem(label="await", kind=CompletionKind.KEYWORD, detail="Await expression"),
        ]

        snipped_completions = [
            CompletionItem(label="for_loop", kind=CompletionKind.SNIPPET, detail="For loop snippet", insert_text="for (let i = 0; i < $1; i++) {\n    $2\n}"),
            CompletionItem(label="function_def", kind=CompletionKind.SNIPPET, detail="Function definition", insert_text="function $1($2) {\n    $3\n}"),
            CompletionItem(label="class_def", kind=CompletionKind.SNIPPET, detail="Class definition", insert_text="class $1 {\n    constructor($2) {\n        $3\n    }\n}"),
            CompletionItem(label="import_module", kind=CompletionKind.SNIPPET, detail="Import module", insert_text="import { $1 } from '$2'"),
            CompletionItem(label="if_block", kind=CompletionKind.SNIPPET, detail="If statement block", insert_text="if ($1) {\n    $2\n}"),
        ]

        word_match = re.search(r'(\w+)$', line)
        if word_match:
            prefix = word_match.group(1).lower()
            keyword_completions = [c for c in keyword_completions if c.label.lower().startswith(prefix)]

        return keyword_completions + snipped_completions

    def _get_word_at(self, line: str, column: int) -> Optional[str]:
        start = column
        while start > 0 and line[start - 1].isalnum():
            start -= 1
        end = column
        while end < len(line) and line[end].isalnum():
            end += 1
        if start < end:
            return line[start:end]
        return None

    def _get_word_range(self, line: str, column: int) -> Optional[DocumentRange]:
        start = column
        while start > 0 and line[start - 1].isalnum():
            start -= 1
        end = column
        while end < len(line) and line[end].isalnum():
            end += 1
        if start < end:
            return DocumentRange(
                start=DocumentPosition(line=0, column=start),
                end=DocumentPosition(line=0, column=end),
            )
        return None

    def get_hover(self, content: str, position: DocumentPosition, file_path: str = "unnamed.i") -> Optional[HoverInfo]:
        lines = content.split("\n")
        if position.line >= len(lines):
            return None
        line = lines[position.line]
        if position.column >= len(line) and position.column > 0:
            position = DocumentPosition(line=position.line, column=len(line) - 1)
        if position.column >= len(line):
            return None

        word = self._get_word_at(line, position.column)
        if not word:
            return None

        builtins = {
            "print": "print(value) -> void\nOutputs a value to stdout.",
            "len": "len(collection) -> int\nReturns the length of a collection.",
            "range": "range(start, end, step=1) -> iterable\nCreates a range of numbers.",
            "type": "type(value) -> str\nReturns the type name of a value.",
            "int": "int(value) -> int\nConverts value to integer.",
            "str": "str(value) -> str\nConverts value to string.",
            "float": "float(value) -> float\nConverts value to float.",
            "list": "list(iterable) -> list\nCreates a list from iterable.",
            "dict": "dict(mapping) -> dict\nCreates a dictionary.",
            "map": "map(func, iterable) -> iterable\nApplies function to each element.",
            "filter": "filter(func, iterable) -> iterable\nFilters elements by predicate.",
            "reduce": "reduce(func, iterable) -> value\nReduces iterable to single value.",
            "open": "open(file, mode='r') -> file\nOpens a file.",
            "read": "read(file) -> str\nReads entire file content.",
            "write": "write(file, content) -> int\nWrites content to file.",
        }

        if word in builtins:
            wrange = self._get_word_range(line, position.column)
            if wrange:
                wrange.start.line = position.line
                wrange.end.line = position.line
            return HoverInfo(
                contents=[f"**{word}**\n\n{builtins[word]}"],
                range=wrange or DocumentRange(
                    start=DocumentPosition(line=position.line, column=max(0, position.column - len(word))),
                    end=DocumentPosition(line=position.line, column=position.column + 1),
                ),
            )
        return None

    def get_symbols(self, content: str, file_path: str = "unnamed.i") -> List[SymbolInfo]:
        symbols: List[SymbolInfo] = []
        lines = content.split("\n")

        for line_idx, line in enumerate(lines):
            stripped = line.strip()

            func_match = re.match(r'function\s+(\w+)', stripped)
            if func_match:
                symbols.append(SymbolInfo(
                    name=func_match.group(1),
                    kind=SymbolKind.FUNCTION,
                    range=DocumentRange(
                        start=DocumentPosition(line=line_idx, column=0),
                        end=DocumentPosition(line=line_idx, column=len(line)),
                    ),
                ))

            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                symbols.append(SymbolInfo(
                    name=class_match.group(1),
                    kind=SymbolKind.CLASS,
                    range=DocumentRange(
                        start=DocumentPosition(line=line_idx, column=0),
                        end=DocumentPosition(line=line_idx, column=len(line)),
                    ),
                ))

            var_match = re.match(r'(?:let|const|var)\s+(\w+)', stripped)
            if var_match:
                symbols.append(SymbolInfo(
                    name=var_match.group(1),
                    kind=SymbolKind.VARIABLE,
                    range=DocumentRange(
                        start=DocumentPosition(line=line_idx, column=0),
                        end=DocumentPosition(line=line_idx, column=len(line)),
                    ),
                ))

        self._symbols[file_path] = symbols
        return symbols

    def go_to_definition(self, content: str, position: DocumentPosition, file_path: str = "unnamed.i") -> Optional[DocumentRange]:
        lines = content.split("\n")
        if position.line >= len(lines):
            return None
        line = lines[position.line]
        if position.column >= len(line):
            return None
        word = self._get_word_at(line, position.column)
        if not word:
            return None

        for line_idx, l in enumerate(lines):
            def_match = re.match(
                rf'(?:function|class|let|const|var|import)\s+{re.escape(word)}\b', l.strip()
            )
            if def_match:
                return DocumentRange(
                    start=DocumentPosition(line=line_idx, column=0),
                    end=DocumentPosition(line=line_idx, column=len(l)),
                )

        return None

    def get_references(self, content: str, position: DocumentPosition, file_path: str = "unnamed.i") -> List[DocumentRange]:
        lines = content.split("\n")
        if position.line >= len(lines):
            return []
        line = lines[position.line]
        if position.column >= len(line):
            return []
        word = self._get_word_at(line, position.column)
        if not word:
            return []

        refs = []
        for line_idx, l in enumerate(lines):
            for m in re.finditer(re.escape(word), l):
                refs.append(DocumentRange(
                    start=DocumentPosition(line=line_idx, column=m.start()),
                    end=DocumentPosition(line=line_idx, column=m.end()),
                ))
        return refs

    def get_code_actions(self, diagnostics: List[Diagnostic], file_path: str = "unnamed.i") -> List[CodeAction]:
        actions: List[CodeAction] = []
        for d in diagnostics:
            if "undefined" in d.message.lower():
                actions.append(CodeAction(
                    title=f"Fix: {d.message}",
                    kind="quickfix",
                    diagnostics=[d],
                ))
        return actions

    def format_document(self, content: str, file_path: str = "unnamed.i") -> str:
        lines = content.split("\n")
        formatted: List[str] = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue

            if any(stripped.startswith(kw) for kw in ["}", "]", ")", "end"]):
                indent_level = max(0, indent_level - 1)

            formatted.append("    " * indent_level + stripped)

            if any(stripped.endswith(kw) for kw in ["{", "[", "(", ":"]):
                indent_level += 1

        return "\n".join(formatted)

    def set_workspace_files(self, files: List[str]) -> None:
        self._workspace_files = files

    def get_diagnostics(self, file_path: str) -> List[Diagnostic]:
        return self._diagnostics.get(file_path, [])

    def clear_diagnostics(self, file_path: Optional[str] = None) -> None:
        if file_path:
            self._diagnostics.pop(file_path, None)
        else:
            self._diagnostics.clear()
