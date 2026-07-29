"""
Comprehensive Test Suite for Type System Sprint 5

Tests cover: type representation, registry, database, environment,
inference, constraint solving, generics, traits, compile-time evaluation,
diagnostics, and full type checker integration.
"""

import pytest
from compiler.typesystem.types import (
    Type, TypeKind, TypeVariable,
    IntType, FloatType, BoolType, CharType, StringType, NoneType,
    AnyType, UnknownType, NeverType, BottomType,
    ListType, MapType, SetType, TupleType, RangeType,
    FunctionType, OptionalType, ResultType,
    ClassType, StructType, EnumType, TraitType, InterfaceType,
    GenericType, ModuleType, PackageType,
    FutureType, CoroutineType, SimdVectorType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_CHAR, TYPE_STRING,
    TYPE_NONE, TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER, TYPE_BOTTOM,
    common_type, is_compatible, is_strict_subtype,
    make_list, make_map, make_set, make_tuple, make_optional,
    make_result, make_function, make_class_type, make_struct_type,
    make_enum_type, make_trait_type, make_interface_type,
    make_type_var, make_generic, make_range, make_future,
    make_coroutine, make_simd,
)
from compiler.typesystem.registry import (
    TypeRegistry, TypeDefinition, MemberInfo, MethodSignature,
)
from compiler.typesystem.database import (
    TypeDatabase, SubtypeRelation, TraitImplementation,
)
from compiler.typesystem.environment import (
    TypeEnvironment, TypeScope, TypeEntry,
)
from compiler.typesystem.context import (
    TypeContext, FunctionContext, ClassContext, LoopContext,
)
from compiler.typesystem.inference import (
    InferenceEngine, InferenceResult,
)
from compiler.typesystem.constraints import (
    ConstraintSolver, Constraint, ConstraintKind, Substitution,
)
from compiler.typesystem.generics import (
    GenericEngine, GenericParamDef, GenericInstantiation,
)
from compiler.typesystem.traits import (
    TraitResolver, TraitDefinition, InterfaceDefinition,
    ImplementationCheck,
)
from compiler.typesystem.compiletime import (
    CompileTimeEvaluator, ConstValue, ConstValueKind,
)
from compiler.typesystem.diagnostics import (
    TypeDiagnostics, TypeErrorCode, TypeSeverity, TypeLocation,
    TypeDiagnostic, get_bilingual_message,
)
from compiler.typesystem.checker import (
    TypeChecker, check_types,
)
from compiler.ast.nodes import (
    Program, LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    LogicalExpr, AssignmentExpr, CompoundAssignmentExpr, CallExpr,
    GetExpr, IndexExpr, ListExpr, DictExpr, TupleExpr, LambdaExpr,
    BlockStmt, IfStmt, WhileStmt, UntilStmt, ForStmt, ForEachStmt,
    ReturnStmt, BreakStmt, ContinueStmt, ExpressionStmt,
    VarDecl, FunctionDecl, StructDecl,
    ClassDecl, TraitDecl, InterfaceDecl, MethodDecl,
    Parameter, StructField, NamedType,
)


# ══════════════════════════════════════════════════════════════════
# Type Representation Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeRepresentation:
    def test_primitive_types(self):
        assert TYPE_INT.kind == TypeKind.INT
        assert TYPE_INT.name == "int"
        assert TYPE_INT.is_primitive
        assert TYPE_INT.is_numeric

        assert TYPE_FLOAT.kind == TypeKind.FLOAT
        assert TYPE_FLOAT.name == "float"
        assert TYPE_FLOAT.is_numeric

        assert TYPE_BOOL.kind == TypeKind.BOOL
        assert TYPE_BOOL.name == "bool"
        assert not TYPE_BOOL.is_numeric

        assert TYPE_STRING.kind == TypeKind.STRING
        assert TYPE_STRING.name == "umuntu"
        assert TYPE_STRING.is_reference_type

        assert TYPE_NONE.kind == TypeKind.NONE_TYPE
        assert TYPE_NONE.name == "none"

    def test_special_types(self):
        assert TYPE_ANY.kind == TypeKind.ANY
        assert TYPE_ANY.name == "any"
        assert TYPE_UNKNOWN.kind == TypeKind.UNKNOWN
        assert TYPE_NEVER.kind == TypeKind.NEVER

    def test_type_equality(self):
        assert TYPE_INT == TYPE_INT
        assert TYPE_INT != TYPE_FLOAT
        assert IntType() == IntType()
        assert hash(TYPE_INT) == hash(IntType())

    def test_type_assignability(self):
        assert TYPE_INT.is_assignable_to(TYPE_ANY)
        assert TYPE_INT.is_assignable_to(TYPE_INT)
        assert TYPE_INT.is_assignable_to(TYPE_FLOAT)
        assert not TYPE_STRING.is_assignable_to(TYPE_INT)

    def test_none_assignability(self):
        assert TYPE_NONE.is_assignable_to(TYPE_NONE)
        assert TYPE_NONE.is_assignable_to(TYPE_ANY)
        assert not TYPE_NONE.is_assignable_to(TYPE_INT)

    def test_any_assignability(self):
        assert TYPE_ANY.is_assignable_to(TYPE_INT)
        assert TYPE_ANY.is_assignable_to(TYPE_STRING)
        assert TYPE_ANY.is_assignable_to(TYPE_ANY)

    def test_list_type(self):
        list_int = make_list(TYPE_INT)
        assert list_int.kind == TypeKind.LIST
        assert list_int.element_type == TYPE_INT
        assert "urutonde<int>" in list_int.name

    def test_list_assignability(self):
        list_int = make_list(TYPE_INT)
        list_any = make_list(TYPE_ANY)
        assert list_int.is_assignable_to(list_any)
        assert not list_int.is_assignable_to(TYPE_INT)

    def test_map_type(self):
        map_type = make_map(TYPE_STRING, TYPE_INT)
        assert map_type.kind == TypeKind.MAP
        assert map_type.key_type == TYPE_STRING
        assert map_type.value_type == TYPE_INT

    def test_set_type(self):
        set_type = make_set(TYPE_INT)
        assert set_type.kind == TypeKind.SET
        assert set_type.element_type == TYPE_INT

    def test_tuple_type(self):
        tup = make_tuple(TYPE_INT, TYPE_STRING, TYPE_BOOL)
        assert tup.kind == TypeKind.TUPLE
        assert tup.arity == 3
        assert tup.element_types == (TYPE_INT, TYPE_STRING, TYPE_BOOL)

    def test_tuple_assignability(self):
        t1 = make_tuple(TYPE_INT, TYPE_STRING)
        t2 = make_tuple(TYPE_INT, TYPE_STRING)
        t3 = make_tuple(TYPE_INT, TYPE_INT)
        assert t1.is_assignable_to(t2)
        assert not t1.is_assignable_to(t3)

    def test_range_type(self):
        r = make_range(TYPE_INT)
        assert r.kind == TypeKind.RANGE
        assert r.element_type == TYPE_INT

    def test_function_type(self):
        func = make_function([TYPE_INT, TYPE_STRING], TYPE_BOOL)
        assert func.kind == TypeKind.FUNCTION
        assert func.arity == 2
        assert func.return_type == TYPE_BOOL

    def test_function_assignability(self):
        f1 = make_function([TYPE_INT], TYPE_STRING)
        f2 = make_function([TYPE_INT], TYPE_STRING)
        f3 = make_function([TYPE_FLOAT], TYPE_STRING)
        assert f1.is_assignable_to(f2)
        assert not f1.is_assignable_to(f3)

    def test_optional_type(self):
        opt = make_optional(TYPE_INT)
        assert opt.kind == TypeKind.OPTIONAL
        assert opt.inner == TYPE_INT
        assert "int?" in opt.name
        assert opt.unwrap() == TYPE_INT

    def test_optional_assignability(self):
        opt_int = make_optional(TYPE_INT)
        assert opt_int.is_assignable_to(opt_int)
        assert opt_int.is_assignable_to(TYPE_ANY)
        assert opt_int.is_assignable_to(TYPE_NONE)

    def test_result_type(self):
        res = make_result(TYPE_INT, TYPE_STRING)
        assert res.kind == TypeKind.RESULT
        assert res.ok_type == TYPE_INT
        assert res.err_type == TYPE_STRING

    def test_class_type(self):
        cls = make_class_type("Animal")
        assert cls.kind == TypeKind.CLASS
        assert cls.name == "Animal"
        assert cls.is_reference_type

    def test_struct_type(self):
        st = make_struct_type("Point")
        assert st.kind == TypeKind.STRUCT
        assert st.name == "Point"

    def test_enum_type(self):
        en = make_enum_type("Color")
        assert en.kind == TypeKind.ENUM
        assert en.name == "Color"

    def test_trait_type(self):
        tr = make_trait_type("Drawable")
        assert tr.kind == TypeKind.TRAIT
        assert tr.name == "Drawable"

    def test_interface_type(self):
        iface = make_interface_type("Comparable")
        assert iface.kind == TypeKind.INTERFACE
        assert iface.name == "Comparable"

    def test_type_variable(self):
        tv = make_type_var("T")
        assert tv.kind == TypeKind.TYPE_VAR
        assert tv.name == "T"
        assert tv.is_assignable_to(TYPE_ANY)

    def test_generic_type(self):
        gen = make_generic("List", TYPE_INT)
        assert gen.kind == TypeKind.PARAMETERIZED
        assert gen.base_name == "List"
        assert "List<int>" in gen.name

    def test_future_type(self):
        fut = make_future(TYPE_INT)
        assert fut.kind == TypeKind.FUTURE
        assert "Tegerereza<int>" in fut.name

    def test_coroutine_type(self):
        coro = make_coroutine(TYPE_INT, TYPE_STRING)
        assert coro.kind == TypeKind.COROUTINE

    def test_simd_type(self):
        simd = make_simd(TYPE_FLOAT, 8)
        assert simd.kind == TypeKind.SIMD_VECTOR
        assert simd.size == 8

    def test_module_type(self):
        mod = ModuleType("math")
        assert mod.kind == TypeKind.MODULE
        assert mod.name == "math"

    def test_type_properties(self):
        assert TYPE_INT.is_value_type
        assert not TYPE_INT.is_reference_type
        assert make_class_type("X").is_reference_type
        assert not make_class_type("X").is_value_type


# ══════════════════════════════════════════════════════════════════
# Common Type Tests
# ══════════════════════════════════════════════════════════════════


class TestCommonType:
    def test_same_type(self):
        assert common_type(TYPE_INT, TYPE_INT) == TYPE_INT

    def test_int_float(self):
        result = common_type(TYPE_INT, TYPE_FLOAT)
        assert result == TYPE_FLOAT

    def test_float_int(self):
        result = common_type(TYPE_FLOAT, TYPE_INT)
        assert result == TYPE_FLOAT

    def test_any_with_int(self):
        assert common_type(TYPE_ANY, TYPE_INT) == TYPE_INT
        assert common_type(TYPE_INT, TYPE_ANY) == TYPE_INT

    def test_never_with_any(self):
        assert common_type(TYPE_NEVER, TYPE_INT) == TYPE_INT
        assert common_type(TYPE_INT, TYPE_NEVER) == TYPE_INT

    def test_none_optional(self):
        opt = make_optional(TYPE_INT)
        result = common_type(TYPE_NONE, opt)
        assert result == opt

    def test_incompatible(self):
        result = common_type(TYPE_INT, TYPE_STRING)
        assert result is None


# ══════════════════════════════════════════════════════════════════
# Type Registry Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeRegistry:
    def test_builtins_registered(self):
        reg = TypeRegistry()
        assert reg.has("int")
        assert reg.has("float")
        assert reg.has("bool")
        assert reg.has("umuntu")
        assert reg.has("none")
        assert reg.has("any")

    def test_register_custom_type(self):
        reg = TypeRegistry()
        defn = TypeDefinition(
            name="Point",
            kind=TypeKind.CLASS,
            type_obj=ClassType("Point"),
        )
        assert reg.register(defn) is True
        assert reg.has("Point")
        assert reg.get("Point").type_obj.kind == TypeKind.CLASS

    def test_register_duplicate_sealed(self):
        reg = TypeRegistry()
        defn = TypeDefinition(
            name="int",
            kind=TypeKind.INT,
            type_obj=TYPE_INT,
            is_sealed=True,
        )
        assert reg.register(defn) is False

    def test_get_type(self):
        reg = TypeRegistry()
        assert reg.get_type("int") == TYPE_INT
        assert reg.get_type("float") == TYPE_FLOAT

    def test_members_and_methods(self):
        reg = TypeRegistry()
        defn = TypeDefinition(
            name="Dog",
            kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
        )
        defn.members["name"] = MemberInfo("name", TYPE_STRING)
        defn.methods["bark"] = MethodSignature(
            name="bark",
            return_type=TYPE_STRING,
        )
        reg.register(defn)

        assert "name" in reg.get_members("Dog")
        assert "bark" in reg.get_methods("Dog")

    def test_parent_tracking(self):
        reg = TypeRegistry()
        animal_def = TypeDefinition(
            name="Animal", kind=TypeKind.CLASS,
            type_obj=ClassType("Animal"),
        )
        dog_def = TypeDefinition(
            name="Dog", kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
            parent_name="Animal",
        )
        reg.register(animal_def)
        reg.register(dog_def)

        assert reg.get_parent("Dog") == "Animal"
        assert reg.is_subclass_of("Dog", "Animal")
        assert not reg.is_subclass_of("Animal", "Dog")

    def test_remove_file(self):
        reg = TypeRegistry()
        defn = TypeDefinition(
            name="TestClass",
            kind=TypeKind.CLASS,
            type_obj=ClassType("TestClass"),
            declaration_file="test.i",
        )
        reg.register(defn, "test.i")
        assert reg.has("TestClass")
        removed = reg.remove_file("test.i")
        assert "TestClass" in removed
        assert not reg.has("TestClass")

    def test_alias(self):
        reg = TypeRegistry()
        reg.add_alias("tandukanya", "float")
        assert reg.get_type("tandukanya") == TYPE_FLOAT


# ══════════════════════════════════════════════════════════════════
# Type Database Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeDatabase:
    def test_subtype_tracking(self):
        db = TypeDatabase()
        db.record_subtype("Dog", "Animal")
        assert db.is_subtype_cached("Dog", "Animal") is True
        assert db.is_subtype_cached("Cat", "Animal") is None

    def test_compatibility_tracking(self):
        db = TypeDatabase()
        db.record_compatible("int", "float")
        assert db.is_compatible_cached("int", "float") is True

    def test_trait_tracking(self):
        db = TypeDatabase()
        impl = TraitImplementation(
            type_name="Dog",
            trait_name="Pet",
        )
        db.record_trait_impl(impl)
        assert db.implements_trait("Dog", "Pet") is True
        assert "Dog" in db.get_trait_providers("Pet")

    def test_file_invalidation(self):
        db = TypeDatabase()
        db.record_file_type("test.i", "Point")
        db.record_subtype("Point", "Shape")
        removed = db.invalidate_file("test.i")
        assert "Point" in removed

    def test_stats(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        stats = db.stats
        assert stats["subtype_relations"] == 1


# ══════════════════════════════════════════════════════════════════
# Type Environment Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeEnvironment:
    def test_define_and_lookup(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        assert env.lookup("x") == TYPE_INT

    def test_lookup_not_found(self):
        env = TypeEnvironment()
        assert env.lookup("undefined") is None

    def test_scope_nesting(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<fn:test>")
        env.define("y", TYPE_STRING)
        assert env.lookup("x") == TYPE_INT
        assert env.lookup("y") == TYPE_STRING
        env.pop()
        assert env.lookup("y") is None

    def test_shadowing(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        old = env.define("x", TYPE_STRING)
        assert old is not None
        assert env.lookup("x") == TYPE_STRING

    def test_lookup_local(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        assert env.lookup_local("x") is None
        assert env.lookup_local("y") == TYPE_STRING
        env.pop()

    def test_mutable_tracking(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT, is_mutable=False)
        assert not env.is_mutable("x")

    def test_const_tracking(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT, is_const=True)
        assert env.is_const("x")

    def test_update_type(self):
        env = TypeEnvironment()
        env.define("x", TYPE_UNKNOWN)
        assert env.update_type("x", TYPE_INT)
        assert env.lookup("x") == TYPE_INT

    def test_all_bindings(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        bindings = env.get_all_bindings()
        assert "x" in bindings
        assert "y" in bindings
        env.pop()

    def test_function_scope(self):
        env = TypeEnvironment()
        fn_scope = env.enter_function("test_fn")
        assert fn_scope.name == "<fn:test_fn>"
        env.exit_function()

    def test_class_scope(self):
        env = TypeEnvironment()
        cls_scope = env.enter_class("Animal")
        assert cls_scope.name == "<class:Animal>"
        env.exit_class()


# ══════════════════════════════════════════════════════════════════
# Type Context Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeContext:
    def test_function_context(self):
        ctx = TypeContext()
        ctx.enter_function("add", TYPE_INT, [TYPE_INT, TYPE_INT])
        assert ctx.in_function
        assert ctx.current_function.name == "add"
        assert ctx.current_return_type == TYPE_INT
        ctx.exit_function()
        assert not ctx.in_function

    def test_class_context(self):
        ctx = TypeContext()
        ctx.enter_class("Dog", "Animal")
        assert ctx.in_class
        assert ctx.current_class.name == "Dog"
        assert ctx.current_class.parent_name == "Animal"
        ctx.exit_class()
        assert not ctx.in_class

    def test_loop_context(self):
        ctx = TypeContext()
        ctx.enter_loop("while")
        assert ctx.in_loop
        assert ctx.loop_depth == 1
        ctx.exit_loop()
        assert not ctx.in_loop

    def test_generic_tracking(self):
        ctx = TypeContext()
        tv = TypeVariable("T")
        ctx.add_generic("T", tv)
        assert ctx.has_generic("T")
        assert ctx.get_generic("T") == tv

    def test_error_tracking(self):
        ctx = TypeContext()
        assert not ctx.has_errors
        assert ctx.error_count == 0
        ctx.record_error()
        assert ctx.has_errors
        assert ctx.error_count == 1

    def test_deferred_checks(self):
        ctx = TypeContext()
        called = []
        ctx.defer_check(lambda: called.append(1))
        ctx.process_deferred()
        assert called == [1]


# ══════════════════════════════════════════════════════════════════
# Substitution Tests
# ══════════════════════════════════════════════════════════════════


class TestSubstitution:
    def test_bind_and_lookup(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        assert sub.lookup("T") == TYPE_INT

    def test_resolve_through(self):
        sub = Substitution()
        sub.bind("T", TYPE_STRING)
        sub.bind("U", TypeVariable("T"))
        resolved = sub.resolve(TypeVariable("U"))
        assert resolved == TYPE_STRING

    def test_resolve_non_variable(self):
        sub = Substitution()
        assert sub.resolve(TYPE_INT) == TYPE_INT

    def test_no_bind_conflict(self):
        sub = Substitution()
        assert sub.bind("T", TYPE_INT) is True
        assert sub.bind("T", TYPE_STRING) is False


# ══════════════════════════════════════════════════════════════════
# Constraint Solver Tests
# ══════════════════════════════════════════════════════════════════


class TestConstraintSolver:
    def test_equality_constraint(self):
        solver = ConstraintSolver()
        tv = TypeVariable("T")
        solver.add_equality(tv, TYPE_INT)
        result = solver.solve()
        resolved = result.resolve(tv)
        assert resolved == TYPE_INT

    def test_subtype_constraint(self):
        solver = ConstraintSolver()
        tv = TypeVariable("T")
        solver.add_subtype(tv, TYPE_INT)
        result = solver.solve()
        resolved = result.resolve(tv)
        assert resolved == TYPE_INT

    def test_multiple_constraints(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        solver.add_equality(t, TYPE_INT)
        solver.add_equality(u, TYPE_STRING)
        solver.solve()
        assert solver.resolve_type(t) == TYPE_INT
        assert solver.resolve_type(u) == TYPE_STRING

    def test_chain_resolution(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        solver.add_equality(t, u)
        solver.add_equality(u, TYPE_FLOAT)
        solver.solve()
        assert solver.resolve_type(t) == TYPE_FLOAT
        assert solver.resolve_type(u) == TYPE_FLOAT

    def test_no_progress_terminates(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        solver.add_equality(t, t)
        solver.solve()
        assert solver.iterations <= 1


# ══════════════════════════════════════════════════════════════════
# Inference Engine Tests
# ══════════════════════════════════════════════════════════════════


class TestInferenceEngine:
    def _make_engine(self):
        ctx = TypeContext()
        diag = TypeDiagnostics()
        return InferenceEngine(ctx, diag)

    def test_infer_literal(self):
        engine = self._make_engine()
        assert engine.infer_literal(42) == TYPE_INT
        assert engine.infer_literal(3.14) == TYPE_FLOAT
        assert engine.infer_literal(True) == TYPE_BOOL
        assert engine.infer_literal("hello") == TYPE_STRING
        assert engine.infer_literal(None) == TYPE_NONE

    def test_new_type_var(self):
        engine = self._make_engine()
        tv = engine.new_type_var()
        assert tv.kind == TypeKind.TYPE_VAR
        tv2 = engine.new_type_var()
        assert tv.name != tv2.name

    def test_infer_binary_arithmetic(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_binary(TYPE_INT, "+", TYPE_INT, loc)
        assert result == TYPE_INT

    def test_infer_binary_int_float(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_binary(TYPE_INT, "+", TYPE_FLOAT, loc)
        assert result == TYPE_FLOAT

    def test_infer_binary_comparison(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_binary(TYPE_INT, "==", TYPE_INT, loc)
        assert result == TYPE_BOOL

    def test_infer_binary_string_concat(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_binary(TYPE_STRING, "+", TYPE_STRING, loc)
        assert result == TYPE_STRING

    def test_infer_unary_minus(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_unary("-", TYPE_INT, loc)
        assert result == TYPE_INT

    def test_infer_unary_not(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_unary("!", TYPE_BOOL, loc)
        assert result == TYPE_BOOL

    def test_infer_list_literal(self):
        engine = self._make_engine()
        result = engine.infer_list_literal([TYPE_INT, TYPE_INT, TYPE_INT])
        assert result.kind == TypeKind.LIST
        assert result.element_type == TYPE_INT

    def test_infer_dict_literal(self):
        engine = self._make_engine()
        result = engine.infer_dict_literal(
            [TYPE_STRING, TYPE_STRING],
            [TYPE_INT, TYPE_INT],
        )
        assert result.kind == TypeKind.MAP
        assert result.key_type == TYPE_STRING
        assert result.value_type == TYPE_INT

    def test_infer_tuple_literal(self):
        engine = self._make_engine()
        result = engine.infer_tuple_literal([TYPE_INT, TYPE_STRING])
        assert result.kind == TypeKind.TUPLE
        assert result.arity == 2

    def test_infer_lambda(self):
        engine = self._make_engine()
        result = engine.infer_lambda(
            ["x", "y"],
            [TYPE_INT, TYPE_STRING],
            TYPE_BOOL,
        )
        assert result.kind == TypeKind.FUNCTION
        assert result.arity == 2
        assert result.return_type == TYPE_BOOL

    def test_infer_if_expr_same(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_if_expr(TYPE_INT, TYPE_INT, loc)
        assert result == TYPE_INT

    def test_infer_if_expr_optional(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_if_expr(TYPE_INT, None, loc)
        assert result.kind == TypeKind.OPTIONAL


# ══════════════════════════════════════════════════════════════════
# Generic Engine Tests
# ══════════════════════════════════════════════════════════════════


class TestGenericEngine:
    def test_register_and_query(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        params = [GenericParamDef("T", upper_bound=TYPE_ANY)]
        engine.register_generic_function("identity", params)
        assert engine.has_generics("identity")
        assert len(engine.get_generic_params("identity")) == 1

    def test_validate_constraints(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition("Animal", TypeKind.CLASS, ClassType("Animal")))
        reg.register(TypeDefinition("Dog", TypeKind.CLASS, ClassType("Dog"), parent_name="Animal"))
        engine = GenericEngine(reg)
        params = [GenericParamDef("T", upper_bound=ClassType("Animal"))]
        engine.register_generic_function("fn", params)

        errors = engine.validate_constraints("fn", [ClassType("Dog")])
        assert len(errors) == 0

    def test_constraint_violation(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        params = [GenericParamDef("T", upper_bound=make_class_type("Animal"))]
        engine.register_generic_function("fn", params)

        errors = engine.validate_constraints("fn", [TYPE_INT])
        assert len(errors) > 0

    def test_count_mismatch(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        params = [GenericParamDef("T"), GenericParamDef("U")]
        engine.register_generic_function("fn", params)

        errors = engine.validate_constraints("fn", [TYPE_INT])
        assert len(errors) > 0

    def test_instantiate(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        params = [GenericParamDef("T")]
        engine.register_generic_class("Container", params)

        result = engine.instantiate_generic("Container", [TYPE_INT])
        assert result is not None
        assert result.base_name == "Container"
        assert result.type_args == (TYPE_INT,)

    def test_instantiate_with_defaults(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        params = [
            GenericParamDef("T"),
            GenericParamDef("U", default=TYPE_STRING),
        ]
        engine.register_generic_function("fn", params)

        filled = engine.fill_defaults("fn", [TYPE_INT])
        assert len(filled) == 2
        assert filled[0] == TYPE_INT
        assert filled[1] == TYPE_STRING

    def test_instantiate_function(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        func_type = FunctionType(
            (TypeVariable("T"), TypeVariable("T")),
            TypeVariable("T"),
        )
        t_var = TypeVariable("T")
        result = engine.instantiate_generic_function(
            func_type, [TYPE_INT], [t_var],
        )
        assert result.param_types == (TYPE_INT, TYPE_INT)
        assert result.return_type == TYPE_INT


# ══════════════════════════════════════════════════════════════════
# Trait Resolver Tests
# ══════════════════════════════════════════════════════════════════


class TestTraitResolver:
    def test_register_trait(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        resolver = TraitResolver(reg, diag)
        trait_def = TraitDefinition(
            name="Drawable",
            required_methods={
                "draw": MethodSignature(name="draw", return_type=TYPE_NONE),
            },
        )
        resolver.register_trait(trait_def)
        assert resolver.get_trait("Drawable") is not None

    def test_check_implementation_satisfied(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        resolver = TraitResolver(reg, diag)

        trait_def = TraitDefinition(
            name="Drawable",
            required_methods={
                "draw": MethodSignature(name="draw", return_type=TYPE_NONE),
            },
        )
        resolver.register_trait(trait_def)

        circle_def = TypeDefinition(
            name="Circle",
            kind=TypeKind.CLASS,
            type_obj=ClassType("Circle"),
        )
        circle_def.methods["draw"] = MethodSignature(
            name="draw", return_type=TYPE_NONE,
        )
        reg.register(circle_def)

        loc = TypeLocation("<test>", 1, 1)
        check = resolver.check_trait_implementation("Circle", "Drawable", loc)
        assert check.is_satisfied

    def test_check_implementation_missing(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        resolver = TraitResolver(reg, diag)

        trait_def = TraitDefinition(
            name="Drawable",
            required_methods={
                "draw": MethodSignature(name="draw", return_type=TYPE_NONE),
                "resize": MethodSignature(name="resize", param_types=[TYPE_INT], return_type=TYPE_NONE),
            },
        )
        resolver.register_trait(trait_def)

        circle_def = TypeDefinition(
            name="Circle",
            kind=TypeKind.CLASS,
            type_obj=ClassType("Circle"),
        )
        circle_def.methods["draw"] = MethodSignature(
            name="draw", return_type=TYPE_NONE,
        )
        reg.register(circle_def)

        loc = TypeLocation("<test>", 1, 1)
        check = resolver.check_trait_implementation("Circle", "Drawable", loc)
        assert not check.is_satisfied
        assert "resize" in check.missing_methods

    def test_register_interface(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        resolver = TraitResolver(reg, diag)
        iface_def = InterfaceDefinition(
            name="Comparable",
            required_methods={
                "compare_to": MethodSignature(
                    name="compare_to",
                    param_types=[TYPE_ANY],
                    return_type=TYPE_INT,
                ),
            },
        )
        resolver.register_interface(iface_def)
        assert resolver.get_interface("Comparable") is not None


# ══════════════════════════════════════════════════════════════════
# Compile-Time Evaluator Tests
# ══════════════════════════════════════════════════════════════════


class TestCompileTimeEvaluator:
    def _make_eval(self):
        return CompileTimeEvaluator(TypeDiagnostics())

    def test_add_integers(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_add(ConstValue.int_val(3), ConstValue.int_val(4), loc)
        assert result.value == 7

    def test_add_strings(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_add(
            ConstValue.string_val("hello"),
            ConstValue.string_val(" world"),
            loc,
        )
        assert result.value == "hello world"

    def test_subtract(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_subtract(ConstValue.int_val(10), ConstValue.int_val(3), loc)
        assert result.value == 7

    def test_multiply(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_multiply(ConstValue.int_val(6), ConstValue.int_val(7), loc)
        assert result.value == 42

    def test_divide(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_divide(ConstValue.int_val(10), ConstValue.int_val(3), loc)
        assert result.value == 3

    def test_division_by_zero(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_divide(ConstValue.int_val(10), ConstValue.int_val(0), loc)
        assert result.is_error

    def test_modulo(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_modulo(ConstValue.int_val(10), ConstValue.int_val(3), loc)
        assert result.value == 1

    def test_power(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_power(ConstValue.int_val(2), ConstValue.int_val(10), loc)
        assert result.value == 1024

    def test_comparisons(self):
        ev = self._make_eval()
        assert ev.eval_equal(ConstValue.int_val(5), ConstValue.int_val(5)).value is True
        assert ev.eval_not_equal(ConstValue.int_val(5), ConstValue.int_val(3)).value is True
        assert ev.eval_less(ConstValue.int_val(3), ConstValue.int_val(5)).value is True
        assert ev.eval_greater(ConstValue.int_val(5), ConstValue.int_val(3)).value is True

    def test_boolean_ops(self):
        ev = self._make_eval()
        assert ev.eval_and(ConstValue.bool_val(True), ConstValue.bool_val(True)).value is True
        assert ev.eval_and(ConstValue.bool_val(True), ConstValue.bool_val(False)).value is False
        assert ev.eval_or(ConstValue.bool_val(False), ConstValue.bool_val(True)).value is True
        assert ev.eval_not(ConstValue.bool_val(True)).value is False

    def test_negate(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_negate(ConstValue.int_val(42), loc)
        assert result.value == -42

    def test_assert_pass(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_assert(ConstValue.bool_val(True), None, loc)
        assert not result.is_error

    def test_assert_fail(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_assert(ConstValue.bool_val(False), "test message", loc)
        assert result.is_error

    def test_constants(self):
        ev = self._make_eval()
        ev.define_constant("PI", ConstValue.float_val(3.14159))
        assert ev.get_constant("PI").value == 3.14159
        assert ev.is_constant_expression("PI")


# ══════════════════════════════════════════════════════════════════
# Diagnostics Tests
# ══════════════════════════════════════════════════════════════════


class TestDiagnostics:
    def test_error_emission(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        assert diag.has_errors
        assert d.expected_type is None or d.expected_type == "int"

    def test_warning_emission(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.warning(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        assert diag.has_warnings

    def test_bilingual_message(self):
        rw, en = get_bilingual_message(
            TypeErrorCode.TYP100_TYPE_MISMATCH, "int", "string",
        )
        assert "int" in en
        assert "string" in en
        assert len(rw) > 0

    def test_type_mismatch_convenience(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.type_mismatch(loc, TYPE_INT, TYPE_STRING)
        assert d.code == TypeErrorCode.TYP100_TYPE_MISMATCH

    def test_format_all(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        formatted = diag.format_all()
        assert "TYP100_TYPE_MISMATCH" in formatted

    def test_format_bilingual(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        formatted = diag.format_all(bilingual=True)
        assert "Kinyarwanda" in formatted
        assert "English" in formatted

    def test_clear(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.clear()
        assert not diag.has_errors

    def test_diagnostic_to_dict(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        d_dict = d.to_dict()
        assert d_dict['code'] == "TYP100_TYPE_MISMATCH"
        assert d_dict['severity'] == "error"


# ══════════════════════════════════════════════════════════════════
# Type Checker Integration Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeChecker:
    def _check(self, decls):
        prog = Program(declarations=decls)
        checker = TypeChecker()
        return checker, checker.check(prog)

    def test_var_decl_with_literal(self):
        decl = VarDecl(
            name="x",
            type_annotation=None,
            initializer=LiteralExpr(42),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_var_decl_with_type_annotation(self):
        decl = VarDecl(
            name="x",
            type_annotation=NamedType("int"),
            initializer=LiteralExpr(42),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_type_mismatch(self):
        decl = VarDecl(
            name="x",
            type_annotation=NamedType("int"),
            initializer=LiteralExpr("hello"),
        )
        checker, diags = self._check([decl])
        assert diags.has_errors

    def test_function_decl(self):
        decl = FunctionDecl(
            name="add",
            parameters=[
                Parameter("a", NamedType("int")),
                Parameter("b", NamedType("int")),
            ],
            return_type=NamedType("int"),
            body=BlockStmt(statements=[
                ReturnStmt(BinaryExpr(IdentifierExpr("a"), "+", IdentifierExpr("b"))),
            ]),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_if_stmt(self):
        decl = VarDecl(
            name="x",
            type_annotation=None,
            initializer=LiteralExpr(42),
        )
        if_stmt = IfStmt(
            condition=BinaryExpr(IdentifierExpr("x"), "==", LiteralExpr(42)),
            then_branch=BlockStmt(statements=[ExpressionStmt(LiteralExpr(1))]),
            elif_branches=[],
            else_branch=None,
        )
        checker, diags = self._check([decl, if_stmt])
        assert not diags.has_errors

    def test_list_literal(self):
        decl = VarDecl(
            name="items",
            type_annotation=None,
            initializer=ListExpr([
                LiteralExpr(1), LiteralExpr(2), LiteralExpr(3),
            ]),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_dict_literal(self):
        decl = VarDecl(
            name="scores",
            type_annotation=None,
            initializer=DictExpr(
                keys=[LiteralExpr("math"), LiteralExpr("science")],
                values=[LiteralExpr(95), LiteralExpr(88)],
            ),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_struct_decl(self):
        struct = StructDecl(
            name="Point",
            fields=[
                StructField("x", NamedType("int")),
                StructField("y", NamedType("int")),
            ],
            methods=[],
        )
        checker, diags = self._check([struct])
        assert not diags.has_errors

    def test_class_decl(self):
        cls = ClassDecl(
            name="Animal",
            parent=None,
            members=[
                MethodDecl(
                    name="speak",
                    parameters=[],
                    return_type=NamedType("umuntu"),
                    body=BlockStmt(statements=[
                        ReturnStmt(LiteralExpr("...")),
                    ]),
                ),
            ],
        )
        checker, diags = self._check([cls])
        assert not diags.has_errors

    def test_trait_decl(self):
        trait = TraitDecl(
            name="Drawable",
            members=[
                MethodDecl(
                    name="draw",
                    parameters=[],
                    return_type=None,
                    body=BlockStmt(statements=[]),
                ),
            ],
        )
        checker, diags = self._check([trait])
        assert not diags.has_errors

    def test_interface_decl(self):
        iface = InterfaceDecl(
            name="Comparable",
            members=[
                MethodDecl(
                    name="compare_to",
                    parameters=[Parameter("other", NamedType("any"))],
                    return_type=NamedType("int"),
                    body=BlockStmt(statements=[]),
                ),
            ],
        )
        checker, diags = self._check([iface])
        assert not diags.has_errors

    def test_const_assignment_error(self):
        const_decl = VarDecl(
            name="x",
            type_annotation=None,
            initializer=LiteralExpr(42),
            is_const=True,
        )
        assign = ExpressionStmt(
            AssignmentExpr(
                target=IdentifierExpr("x"),
                value=LiteralExpr(100),
            )
        )
        checker, diags = self._check([const_decl, assign])
        assert diags.has_errors

    def test_while_loop(self):
        decl = VarDecl(
            name="x",
            type_annotation=None,
            initializer=LiteralExpr(0),
        )
        while_stmt = WhileStmt(
            condition=BinaryExpr(IdentifierExpr("x"), "<", LiteralExpr(10)),
            body=BlockStmt(statements=[
                ExpressionStmt(CompoundAssignmentExpr(
                    IdentifierExpr("x"), "+", LiteralExpr(1),
                )),
            ]),
        )
        checker, diags = self._check([decl, while_stmt])
        assert not diags.has_errors

    def test_for_loop(self):
        for_stmt = ForStmt(
            variable="i",
            start=LiteralExpr(0),
            end=LiteralExpr(10),
            step=None,
            body=BlockStmt(statements=[
                ExpressionStmt(LiteralExpr(1)),
            ]),
        )
        checker, diags = self._check([for_stmt])
        assert not diags.has_errors

    def test_for_each_loop(self):
        list_decl = VarDecl(
            name="items",
            type_annotation=None,
            initializer=ListExpr([LiteralExpr(1)]),
        )
        foreach = ForEachStmt(
            element="item",
            iterable=IdentifierExpr("items"),
            body=BlockStmt(statements=[
                ExpressionStmt(IdentifierExpr("item")),
            ]),
        )
        checker, diags = self._check([list_decl, foreach])
        assert not diags.has_errors

    def test_break_outside_loop(self):
        break_stmt = BreakStmt()
        checker, diags = self._check([break_stmt])
        assert diags.has_errors


# ══════════════════════════════════════════════════════════════════
# Location Tests
# ══════════════════════════════════════════════════════════════════


class TestTypeLocation:
    def test_location_str(self):
        loc = TypeLocation("test.i", 10, 5, 10, 15)
        assert str(loc) == "test.i:10:5"

    def test_location_multiline(self):
        loc = TypeLocation("test.i", 10, 5, 12, 20)
        assert str(loc) == "test.i:10:5-12:20"

    def test_location_zero_line(self):
        loc = TypeLocation("test.i", 0, 0, 0, 0)
        assert str(loc) == "test.i"


# ══════════════════════════════════════════════════════════════════
# Fuzz Tests
# ══════════════════════════════════════════════════════════════════


class TestFuzz:
    def test_random_types_not_crash(self):
        """Ensure type system doesn't crash with arbitrary inputs."""
        import random
        types = [TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE, TYPE_ANY]
        for _ in range(100):
            a = random.choice(types)
            b = random.choice(types)
            common_type(a, b)
            a.is_assignable_to(b)
            a.is_subtype_of(b)

    def test_random_collections(self):
        """Ensure collection types handle various element types."""
        import random
        elem_types = [TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING]
        for _ in range(50):
            et = random.choice(elem_types)
            lst = make_list(et)
            assert lst.kind == TypeKind.LIST

            kt = random.choice(elem_types)
            vt = random.choice(elem_types)
            mp = make_map(kt, vt)
            assert mp.kind == TypeKind.MAP

    def test_random_functions(self):
        """Ensure function types handle various signatures."""
        import random
        for _ in range(50):
            n = random.randint(0, 5)
            params = [random.choice([TYPE_INT, TYPE_FLOAT, TYPE_STRING]) for _ in range(n)]
            ret = random.choice([TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_NONE])
            func = make_function(params, ret)
            assert func.arity == n
