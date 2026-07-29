"""graphql — GraphQL foundation for urubuga.

Provides schema definition, type system, resolvers, query/mutation/subscription
support, and GraphQL-over-HTTP endpoint handling.
"""

from __future__ import annotations

import enum
import json
from typing import Any, Callable, Dict, List, Optional


class GraphQLType(enum.Enum):
    STRING = "String"
    INT = "Int"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    ID = "ID"
    OBJECT = "Object"
    LIST = "List"
    NON_NULL = "NonNull"


class FieldDef:
    """A field definition in a GraphQL type."""
    __slots__ = ("name", "type_name", "nullable", "args", "resolver",
                 "description", "deprecated")

    def __init__(self, name: str, type_name: str = "String",
                 nullable: bool = True,
                 args: Optional[Dict[str, Any]] = None,
                 resolver: Optional[Callable] = None,
                 description: str = "",
                 deprecated: bool = False) -> None:
        self.name = name
        self.type_name = type_name
        self.nullable = nullable
        self.args = args or {}
        self.resolver = resolver
        self.description = description
        self.deprecated = deprecated


class TypeDef:
    """A GraphQL type definition."""
    __slots__ = ("name", "fields", "description", "interfaces")

    def __init__(self, name: str,
                 fields: Optional[List[FieldDef]] = None,
                 description: str = "",
                 interfaces: Optional[List[str]] = None) -> None:
        self.name = name
        self.fields: Dict[str, FieldDef] = {}
        if fields:
            for f in fields:
                self.fields[f.name] = f
        self.description = description
        self.interfaces = interfaces or []

    def field(self, name: str, type_name: str = "String",
              **kwargs: Any) -> None:
        self.fields[name] = FieldDef(name, type_name, **kwargs)

    def toSDL(self) -> str:
        parts = [f"type {self.name}"]
        if self.interfaces:
            parts[0] += f" implements {', '.join(self.interfaces)}"
        parts.append("{")

        for f in self.fields.items():
            field = f[1]
            nullable = "" if field.nullable else "!"
            parts.append(f"  {field.name}: {field.type_name}{nullable}")

        parts.append("}")
        return "\n".join(parts)


class QueryDef:
    """A GraphQL query/mutation/subscription definition."""
    __slots__ = ("name", "type_name", "args", "resolver", "description")

    def __init__(self, name: str, type_name: str = "String",
                 args: Optional[Dict[str, Any]] = None,
                 resolver: Optional[Callable] = None,
                 description: str = "") -> None:
        self.name = name
        self.type_name = type_name
        self.args = args or {}
        self.resolver = resolver
        self.description = description


class GraphQLSchema:
    """A GraphQL schema definition."""

    def __init__(self) -> None:
        self._types: Dict[str, TypeDef] = {}
        self._queries: Dict[str, QueryDef] = {}
        self._mutations: Dict[str, QueryDef] = {}
        self._subscriptions: Dict[str, QueryDef] = {}
        self._resolvers: Dict[str, Callable] = {}

    def type(self, name: str, **kwargs: Any) -> TypeDef:
        td = TypeDef(name, **kwargs)
        self._types[name] = td
        return td

    def query(self, name: str, type_name: str = "String",
              resolver: Optional[Callable] = None,
              args: Optional[Dict[str, Any]] = None,
              description: str = "") -> Callable:
        def decorator(fn: Optional[Callable] = None) -> Callable:
            actual_resolver = resolver or fn
            q = QueryDef(name, type_name, args or {}, actual_resolver, description)
            self._queries[name] = q
            if actual_resolver:
                self._resolvers[f"Query.{name}"] = actual_resolver
            return fn or actual_resolver
        return decorator

    def mutation(self, name: str, type_name: str = "String",
                 resolver: Optional[Callable] = None,
                 args: Optional[Dict[str, Any]] = None,
                 description: str = "") -> Callable:
        def decorator(fn: Optional[Callable] = None) -> Callable:
            actual_resolver = resolver or fn
            q = QueryDef(name, type_name, args or {}, actual_resolver, description)
            self._mutations[name] = q
            if actual_resolver:
                self._resolvers[f"Mutation.{name}"] = actual_resolver
            return fn or actual_resolver
        return decorator

    def subscription(self, name: str, type_name: str = "String",
                     resolver: Optional[Callable] = None,
                     args: Optional[Dict[str, Any]] = None) -> Callable:
        def decorator(fn: Optional[Callable] = None) -> Callable:
            actual_resolver = resolver or fn
            q = QueryDef(name, type_name, args or {}, actual_resolver)
            self._subscriptions[name] = q
            if actual_resolver:
                self._resolvers[f"Subscription.{name}"] = actual_resolver
            return fn or actual_resolver
        return decorator

    def resolve(self, type_name: str, field_name: str,
                resolver: Callable) -> None:
        self._resolvers[f"{type_name}.{field_name}"] = resolver

    def get_resolver(self, type_name: str,
                     field_name: str) -> Optional[Callable]:
        return self._resolvers.get(f"{type_name}.{field_name}")

    def toSDL(self) -> str:
        parts = []
        for td in self._types.values():
            parts.append(td.toSDL())

        if self._queries:
            parts.append("type Query {")
            for q in self._queries.values():
                args = ""
                if q.args:
                    arg_parts = [f"${k}: {v}" for k, v in q.args.items()]
                    args = f"({', '.join(arg_parts)})"
                nullable = "" if q.type_name != "String!" else "!"
                parts.append(f"  {q.name}{args}: {q.type_name}")
            parts.append("}")

        if self._mutations:
            parts.append("type Mutation {")
            for m in self._mutations.values():
                args = ""
                if m.args:
                    arg_parts = [f"${k}: {v}" for k, v in m.args.items()]
                    args = f"({', '.join(arg_parts)})"
                parts.append(f"  {m.name}{args}: {m.type_name}")
            parts.append("}")

        return "\n\n".join(parts)

    def execute(self, query: str,
                variables: Optional[Dict[str, Any]] = None,
                operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute a GraphQL query (simplified parser)."""
        query = query.strip()
        is_mutation = query.startswith("mutation")
        is_subscription = query.startswith("subscription")

        operation_type = "query"
        body = query
        if is_mutation:
            operation_type = "mutation"
            body = query[8:].strip()
        elif is_subscription:
            operation_type = "subscription"
            body = query[12:].strip()

        if body.startswith("{"):
            body = body[1:-1].strip()

        operations = self._operations[operation_type] if hasattr(self, '_operations') else {}
        results = {}

        for field_name in self._parse_fields(body):
            resolver_key = f"{operation_type.capitalize()}.{field_name}"
            resolver = self._resolvers.get(resolver_key)
            if resolver:
                try:
                    args = {}
                    for arg_name in (self._queries.get(field_name) or
                                     self._mutations.get(field_name) or
                                     QueryDef("")).args:
                        if variables and arg_name in variables:
                            args[arg_name] = variables[arg_name]
                    results[field_name] = resolver(**args) if args else resolver()
                except Exception as e:
                    results[field_name] = None
            else:
                results[field_name] = None

        return {"data": results}

    def _parse_fields(self, body: str) -> List[str]:
        fields = []
        depth = 0
        current = ""
        for char in body:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            elif char == "," and depth == 0:
                if current.strip():
                    fields.append(current.strip().split("(")[0].split(":")[0].strip())
                current = ""
            else:
                current += char
        if current.strip():
            fields.append(current.strip().split("(")[0].split(":")[0].strip())
        return fields

    def type_count(self) -> int:
        return len(self._types)

    def query_count(self) -> int:
        return len(self._queries)

    def mutation_count(self) -> int:
        return len(self._mutations)
