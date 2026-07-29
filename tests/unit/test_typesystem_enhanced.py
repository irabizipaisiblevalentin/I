"""
Comprehensive Test Suite for Type System Enhancements

Tests cover all new features added to the type system beyond Sprint 5:
type hierarchy enhancements, registry/database/environment/context
improvements, constraint solver enhancements, inference extensions,
generic engine features, trait resolver additions, compile-time
evaluation, diagnostics filtering, and type checker validations.
"""

import pytest
from compiler.typesystem.types import (
    Type, TypeKind, Variance,
    IntType, FloatType, BoolType, CharType, StringType, NoneType,
    AnyType, UnknownType, NeverType, BottomType,
    ListType, MapType, SetType, TupleType, RangeType,
    FunctionType, OptionalType, ResultType,
    TypeVariable, GenericType, ClassType, StructType, EnumType,
    TraitType, InterfaceType, ModuleType, PackageType,
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
from compiler.typesystem.environment import TypeEnvironment
from compiler.typesystem.context import TypeContext
from compiler.typesystem.inference import InferenceEngine
from compiler.typesystem.constraints import ConstraintSolver, Substitution
from compiler.typesystem.generics import GenericEngine, GenericParamDef
from compiler.typesystem.traits import (
    TraitResolver, TraitDefinition, InterfaceDefinition,
)
from compiler.typesystem.compiletime import (
    CompileTimeEvaluator, ConstValue, ConstValueKind,
)
from compiler.typesystem.diagnostics import (
    TypeDiagnostics, TypeErrorCode, TypeSeverity, TypeLocation,
)
from compiler.typesystem.checker import TypeChecker
from compiler.ast.nodes import (
    Program, VarDecl, FunctionDecl, ClassDecl, StructDecl,
    TraitDecl, InterfaceDecl, MethodDecl, BlockStmt, ExpressionStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, NamedType,
    Parameter, StructField, ReturnStmt,
)


# ══════════════════════════════════════════════════════════════════
# 1. Type Hierarchy Enhancements
# ══════════════════════════════════════════════════════════════════


class TestTypeHierarchyEnhancements:
    def test_type_id_unique_for_different_instances(self):
        a = IntType()
        b = IntType()
        assert a.type_id != b.type_id

    def test_type_id_same_for_same_instance(self):
        a = IntType()
        assert a.type_id == a.type_id

    def test_type_id_different_for_different_types(self):
        assert TYPE_INT.type_id != TYPE_FLOAT.type_id

    def test_variance_enum_exists(self):
        assert Variance.INVARIANT is not None
        assert Variance.COVARIANT is not None
        assert Variance.CONTRAVARIANT is not None

    def test_variance_enum_members(self):
        assert Variance.INVARIANT != Variance.COVARIANT
        assert Variance.COVARIANT != Variance.CONTRAVARIANT
        assert Variance.INVARIANT != Variance.CONTRAVARIANT

    def test_type_variable_default_variance(self):
        tv = TypeVariable("T")
        assert tv.variance == Variance.INVARIANT

    def test_type_variable_covariant(self):
        tv = TypeVariable("T", variance=Variance.COVARIANT)
        assert tv.variance == Variance.COVARIANT

    def test_type_variable_contravariant(self):
        tv = TypeVariable("T", variance=Variance.CONTRAVARIANT)
        assert tv.variance == Variance.CONTRAVARIANT

    def test_type_variable_variance_is_stored(self):
        tv = TypeVariable("U", variance=Variance.COVARIANT)
        assert tv.variance is Variance.COVARIANT
        assert tv.name == "U"

    def test_package_type_hash(self):
        p1 = PackageType("core")
        p2 = PackageType("core")
        assert hash(p1) == hash(p2)

    def test_package_type_hash_different(self):
        p1 = PackageType("core")
        p2 = PackageType("std")
        assert hash(p1) != hash(p2)

    def test_package_type_equality(self):
        p1 = PackageType("core")
        p2 = PackageType("core")
        assert p1 == p2

    def test_package_type_assignable_to_any(self):
        p = PackageType("core")
        assert p.is_assignable_to(TYPE_ANY)

    def test_package_type_assignable_to_self(self):
        p1 = PackageType("core")
        p2 = PackageType("core")
        assert p1.is_assignable_to(p2)

    def test_package_type_not_assignable_to_different(self):
        p1 = PackageType("core")
        p2 = PackageType("std")
        assert not p1.is_assignable_to(p2)

    def test_package_type_not_assignable_to_int(self):
        p = PackageType("core")
        assert not p.is_assignable_to(TYPE_INT)

    def test_common_type_optional_and_none(self):
        opt = make_optional(TYPE_INT)
        result = common_type(TYPE_NONE, opt)
        assert result is not None
        assert result.kind == TypeKind.OPTIONAL
        assert result.inner == TYPE_INT

    def test_common_type_none_and_optional(self):
        opt = make_optional(TYPE_STRING)
        result = common_type(opt, TYPE_NONE)
        assert result is not None
        assert result.kind == TypeKind.OPTIONAL
        assert result.inner == TYPE_STRING

    def test_common_type_optional_and_optional_same(self):
        opt1 = make_optional(TYPE_INT)
        opt2 = make_optional(TYPE_INT)
        result = common_type(opt1, opt2)
        assert result is not None
        assert result.kind == TypeKind.OPTIONAL
        assert result.inner == TYPE_INT

    def test_common_type_optional_and_optional_different(self):
        opt1 = make_optional(TYPE_INT)
        opt2 = make_optional(TYPE_FLOAT)
        result = common_type(opt1, opt2)
        assert result is not None
        assert result.kind == TypeKind.OPTIONAL
        assert result.inner == TYPE_FLOAT

    def test_common_type_list_covariance(self):
        list_int = make_list(TYPE_INT)
        list_float = make_list(TYPE_FLOAT)
        result = common_type(list_int, list_float)
        assert result is not None
        assert result.kind == TypeKind.LIST
        assert result.element_type == TYPE_FLOAT

    def test_common_type_list_same(self):
        list_int = make_list(TYPE_INT)
        list_int2 = make_list(TYPE_INT)
        result = common_type(list_int, list_int2)
        assert result is not None
        assert result.kind == TypeKind.LIST
        assert result.element_type == TYPE_INT

    def test_common_type_map_covariance(self):
        map1 = make_map(TYPE_STRING, TYPE_INT)
        map2 = make_map(TYPE_STRING, TYPE_FLOAT)
        result = common_type(map1, map2)
        assert result is not None
        assert result.kind == TypeKind.MAP
        assert result.key_type == TYPE_STRING
        assert result.value_type == TYPE_FLOAT

    def test_common_type_set_covariance(self):
        set_int = make_set(TYPE_INT)
        set_float = make_set(TYPE_FLOAT)
        result = common_type(set_int, set_float)
        assert result is not None
        assert result.kind == TypeKind.SET
        assert result.element_type == TYPE_FLOAT

    def test_common_type_range_covariance(self):
        range_int = make_range(TYPE_INT)
        range_float = make_range(TYPE_FLOAT)
        result = common_type(range_int, range_float)
        assert result is not None
        assert result.kind == TypeKind.RANGE
        assert result.element_type == TYPE_FLOAT

    def test_common_type_function_covariance(self):
        func1 = make_function([TYPE_INT], TYPE_INT)
        func2 = make_function([TYPE_INT], TYPE_FLOAT)
        result = common_type(func1, func2)
        assert result is not None
        assert result.kind == TypeKind.FUNCTION
        assert result.return_type == TYPE_FLOAT

    def test_common_type_function_arity_mismatch(self):
        func1 = make_function([TYPE_INT], TYPE_STRING)
        func2 = make_function([TYPE_INT, TYPE_FLOAT], TYPE_STRING)
        result = common_type(func1, func2)
        assert result is None

    def test_is_compatible_same_type(self):
        assert is_compatible(TYPE_INT, TYPE_INT)

    def test_is_compatible_int_to_float(self):
        assert is_compatible(TYPE_INT, TYPE_FLOAT)

    def test_is_compatible_int_to_any(self):
        assert is_compatible(TYPE_INT, TYPE_ANY)

    def test_is_compatible_incompatible(self):
        assert not is_compatible(TYPE_INT, TYPE_STRING)

    def test_strict_subtype_int_to_float(self):
        assert is_strict_subtype(TYPE_INT, TYPE_FLOAT)

    def test_strict_subtype_not_same(self):
        assert not is_strict_subtype(TYPE_INT, TYPE_INT)

    def test_strict_subtype_class_parent(self):
        dog = make_class_type("Dog", parent="Animal")
        animal = make_class_type("Animal")
        assert is_strict_subtype(dog, animal)

    def test_strict_subtype_never(self):
        assert is_strict_subtype(TYPE_NEVER, TYPE_INT)

    def test_common_type_optional_with_int(self):
        opt_int = make_optional(TYPE_INT)
        result = common_type(opt_int, TYPE_INT)
        assert result is not None
        assert result.kind == TypeKind.OPTIONAL

    def test_common_type_none_none(self):
        result = common_type(TYPE_NONE, TYPE_NONE)
        assert result == TYPE_NONE

    def test_common_type_incompatible_returns_none(self):
        result = common_type(make_list(TYPE_INT), make_map(TYPE_STRING, TYPE_INT))
        assert result is None

    def test_package_type_kind(self):
        p = PackageType("core")
        assert p.kind == TypeKind.PACKAGE

    def test_package_type_name(self):
        p = PackageType("core")
        assert p.name == "core"

    def test_common_type_list_incompatible_elements(self):
        list_str = make_list(TYPE_STRING)
        list_int = make_list(TYPE_INT)
        result = common_type(list_str, list_int)
        assert result is None


# ══════════════════════════════════════════════════════════════════
# 2. Registry Enhancements
# ══════════════════════════════════════════════════════════════════


class TestRegistryEnhancements:
    def test_registered_count_initial(self):
        reg = TypeRegistry()
        assert reg.registered_count > 0

    def test_registered_count_after_register(self):
        reg = TypeRegistry()
        initial = reg.registered_count
        reg.register(TypeDefinition(
            name="MyClass",
            kind=TypeKind.CLASS,
            type_obj=ClassType("MyClass"),
        ))
        assert reg.registered_count == initial + 1

    def test_get_all_methods_returns_dict_of_dicts(self):
        reg = TypeRegistry()
        defn = TypeDefinition(
            name="Dog",
            kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
        )
        defn.methods["bark"] = MethodSignature(name="bark", return_type=TYPE_STRING)
        reg.register(defn)
        all_methods = reg.get_all_methods()
        assert isinstance(all_methods, dict)
        assert "Dog" in all_methods
        assert isinstance(all_methods["Dog"], dict)
        assert "bark" in all_methods["Dog"]

    def test_get_trait_names(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Drawable", kind=TypeKind.TRAIT,
            type_obj=TraitType("Drawable"),
        ))
        names = reg.get_trait_names()
        assert "Drawable" in names

    def test_get_interface_names(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Comparable", kind=TypeKind.INTERFACE,
            type_obj=InterfaceType("Comparable"),
        ))
        names = reg.get_interface_names()
        assert "Comparable" in names

    def test_get_class_names(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="MyClass", kind=TypeKind.CLASS,
            type_obj=ClassType("MyClass"),
        ))
        names = reg.get_class_names()
        assert "MyClass" in names

    def test_get_inheritance_chain_three_levels(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Living", kind=TypeKind.CLASS,
            type_obj=ClassType("Living"),
        ))
        reg.register(TypeDefinition(
            name="Animal", kind=TypeKind.CLASS,
            type_obj=ClassType("Animal"),
            parent_name="Living",
        ))
        reg.register(TypeDefinition(
            name="Dog", kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
            parent_name="Animal",
        ))
        chain = reg.get_inheritance_chain("Dog")
        assert chain == ["Dog", "Animal", "Living"]

    def test_get_inheritance_chain_single(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Base", kind=TypeKind.CLASS,
            type_obj=ClassType("Base"),
        ))
        chain = reg.get_inheritance_chain("Base")
        assert chain == ["Base"]

    def test_get_all_subtypes(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Animal", kind=TypeKind.CLASS,
            type_obj=ClassType("Animal"),
        ))
        reg.register(TypeDefinition(
            name="Dog", kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
            parent_name="Animal",
        ))
        reg.register(TypeDefinition(
            name="Cat", kind=TypeKind.CLASS,
            type_obj=ClassType("Cat"),
            parent_name="Animal",
        ))
        subtypes = reg.get_all_subtypes("Animal")
        assert "Dog" in subtypes
        assert "Cat" in subtypes
        assert "Animal" not in subtypes

    def test_implements_trait_with_parent_traversal(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Animal", kind=TypeKind.CLASS,
            type_obj=ClassType("Animal"),
            implemented_traits=["Pet"],
        ))
        reg.register(TypeDefinition(
            name="Dog", kind=TypeKind.CLASS,
            type_obj=ClassType("Dog"),
            parent_name="Animal",
        ))
        assert reg.implements_trait("Dog", "Pet")

    def test_implements_trait_direct(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Circle", kind=TypeKind.CLASS,
            type_obj=ClassType("Circle"),
            implemented_traits=["Drawable"],
        ))
        assert reg.implements_trait("Circle", "Drawable")

    def test_implements_trait_not_found(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="Circle", kind=TypeKind.CLASS,
            type_obj=ClassType("Circle"),
        ))
        assert not reg.implements_trait("Circle", "Drawable")

    def test_get_trait_names_empty(self):
        reg = TypeRegistry()
        names = reg.get_trait_names()
        assert isinstance(names, list)

    def test_get_interface_names_empty(self):
        reg = TypeRegistry()
        names = reg.get_interface_names()
        assert isinstance(names, list)


# ══════════════════════════════════════════════════════════════════
# 3. Database Enhancements
# ══════════════════════════════════════════════════════════════════


class TestDatabaseEnhancements:
    def test_invalidate_types(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        db.record_subtype("B", "C")
        assert db.is_subtype_cached("A", "B") is True
        db.invalidate_types(["A"])
        assert db.is_subtype_cached("A", "B") is None
        assert db.is_subtype_cached("B", "C") is True

    def test_invalidate_types_multiple(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        db.record_subtype("C", "D")
        db.invalidate_types(["A", "C"])
        assert db.is_subtype_cached("A", "B") is None
        assert db.is_subtype_cached("C", "D") is None

    def test_get_subtype_chain_direct(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        chain = db.get_subtype_chain("A", "B")
        assert chain == ["A", "B"]

    def test_get_subtype_chain_same(self):
        db = TypeDatabase()
        chain = db.get_subtype_chain("A", "A")
        assert chain == ["A"]

    def test_get_subtype_chain_multi_hop(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        db.record_subtype("B", "C")
        chain = db.get_subtype_chain("A", "C")
        assert chain is not None
        assert chain[0] == "A"
        assert chain[-1] == "C"
        assert "B" in chain

    def test_get_subtype_chain_no_path(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        chain = db.get_subtype_chain("A", "Z")
        assert chain is None

    def test_get_constraint_stats_empty(self):
        db = TypeDatabase()
        stats = db.get_constraint_stats()
        assert stats["total_constraints"] == 0
        assert stats["types_with_constraints"] == 0

    def test_get_constraint_stats_with_data(self):
        db = TypeDatabase()
        db.record_type_constraints("T", [TYPE_INT])
        db.record_type_constraints("U", [])
        stats = db.get_constraint_stats()
        assert stats["total_constraints"] == 2
        assert stats["types_with_constraints"] == 1

    def test_stats_includes_unique_trait_providers(self):
        db = TypeDatabase()
        db.record_trait_impl(
            TraitImplementation(type_name="Dog", trait_name="Pet"),
        )
        db.record_trait_impl(
            TraitImplementation(type_name="Cat", trait_name="Pet"),
        )
        stats = db.stats
        assert "unique_trait_providers" in stats
        assert stats["unique_trait_providers"] >= 1

    def test_stats_keys(self):
        db = TypeDatabase()
        stats = db.stats
        assert "subtype_relations" in stats
        assert "compatible_relations" in stats
        assert "trait_implementations" in stats
        assert "file_dependencies" in stats
        assert "cached_constraints" in stats
        assert "unique_trait_providers" in stats


# ══════════════════════════════════════════════════════════════════
# 4. Environment Enhancements
# ══════════════════════════════════════════════════════════════════


class TestEnvironmentEnhancements:
    def test_binding_count(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.define("y", TYPE_STRING)
        assert env.binding_count == 2

    def test_binding_count_with_scopes(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        count = env.binding_count
        assert count == 2
        env.pop()

    def test_local_binding_count(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        assert env.local_binding_count == 1
        env.pop()

    def test_local_binding_count_global(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        assert env.local_binding_count == 1

    def test_get_all_names(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.define("y", TYPE_STRING)
        names = env.get_all_names()
        assert isinstance(names, list)
        assert "x" in names
        assert "y" in names

    def test_get_all_names_with_scope(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        names = env.get_all_names()
        assert "x" in names
        assert "y" in names
        env.pop()
        names = env.get_all_names()
        assert "x" in names
        assert "y" not in names

    def test_has_name(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        assert env.has_name("x")
        assert not env.has_name("y")

    def test_has_name_with_scope(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        assert env.has_name("x")
        assert env.has_name("y")
        env.pop()
        assert env.has_name("x")
        assert not env.has_name("y")

    def test_reset_to_global(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        env.reset_to_global()
        assert env.current_depth == 0
        assert env.lookup("x") is None

    def test_snapshot(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.define("y", TYPE_STRING)
        bindings = env.get_all_bindings()
        assert isinstance(bindings, dict)
        assert "x" in bindings
        assert "y" in bindings
        assert bindings["x"] == TYPE_INT

    def test_snapshot_with_scope(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.push("<block>")
        env.define("y", TYPE_STRING)
        bindings = env.get_all_bindings()
        assert "x" in bindings
        assert "y" in bindings
        env.pop()
        bindings = env.get_all_bindings()
        assert "x" in bindings
        assert "y" not in bindings


# ══════════════════════════════════════════════════════════════════
# 5. Context Enhancements
# ══════════════════════════════════════════════════════════════════


class TestContextEnhancements:
    def test_function_depth_zero(self):
        ctx = TypeContext()
        assert ctx.function_depth == 0

    def test_function_depth_one(self):
        ctx = TypeContext()
        ctx.enter_function("outer")
        assert ctx.function_depth == 1
        ctx.exit_function()

    def test_function_depth_nested(self):
        ctx = TypeContext()
        ctx.enter_function("outer")
        ctx.enter_function("inner")
        assert ctx.function_depth == 2
        ctx.exit_function()
        assert ctx.function_depth == 1
        ctx.exit_function()
        assert ctx.function_depth == 0

    def test_class_depth_zero(self):
        ctx = TypeContext()
        assert ctx.class_depth == 0

    def test_class_depth_one(self):
        ctx = TypeContext()
        ctx.enter_class("Animal")
        assert ctx.class_depth == 1
        ctx.exit_class()

    def test_class_depth_nested(self):
        ctx = TypeContext()
        ctx.enter_class("Outer")
        ctx.enter_class("Inner")
        assert ctx.class_depth == 2
        ctx.exit_class()
        assert ctx.class_depth == 1
        ctx.exit_class()

    def test_generic_count_zero(self):
        ctx = TypeContext()
        assert ctx.generic_count == 0

    def test_generic_count_with_generics(self):
        ctx = TypeContext()
        tv = TypeVariable("T")
        ctx.add_generic("T", tv)
        assert ctx.generic_count == 1

    def test_generic_count_multiple(self):
        ctx = TypeContext()
        tv1 = TypeVariable("T")
        tv2 = TypeVariable("U")
        ctx.add_generic("T", tv1)
        ctx.add_generic("U", tv2)
        assert ctx.generic_count == 2

    def test_constraint_count_zero(self):
        ctx = TypeContext()
        assert ctx.get_constraint_count() == 0

    def test_constraint_count_with_assignments(self):
        ctx = TypeContext()
        ctx.record_assignment("x", TYPE_INT)
        ctx.record_assignment("y", TYPE_STRING)
        assert ctx.get_constraint_count() == 2

    def test_deferred_count_zero(self):
        ctx = TypeContext()
        assert ctx.deferred_count == 0

    def test_deferred_count_with_checks(self):
        ctx = TypeContext()
        ctx.defer_check(lambda: None)
        ctx.defer_check(lambda: None)
        assert ctx.deferred_count == 2

    def test_deferred_count_after_process(self):
        ctx = TypeContext()
        ctx.defer_check(lambda: None)
        ctx.process_deferred()
        assert ctx.deferred_count == 0


# ══════════════════════════════════════════════════════════════════
# 6. Constraint Solver Enhancements
# ══════════════════════════════════════════════════════════════════


class TestConstraintSolverEnhancements:
    def test_constraint_count_zero(self):
        solver = ConstraintSolver()
        assert solver.constraint_count == 0

    def test_constraint_count_after_add(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        solver.add_equality(t, TYPE_INT)
        assert solver.constraint_count == 1

    def test_resolved_count_zero(self):
        solver = ConstraintSolver()
        assert solver.resolved_count == 0

    def test_resolved_count_after_solve(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        solver.add_equality(t, TYPE_INT)
        solver.solve()
        assert solver.resolved_count >= 1

    def test_failed_count_zero(self):
        solver = ConstraintSolver()
        assert solver.failed_count == 0

    def test_failed_count_on_failure(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        solver.add_equality(t, TYPE_INT)
        solver.add_equality(t, TYPE_STRING)
        solver.solve()
        assert solver.failed_count > 0

    def test_get_all_resolved_types(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        solver.add_equality(t, TYPE_INT)
        solver.add_equality(u, TYPE_STRING)
        solver.solve()
        resolved = solver.get_all_resolved_types()
        assert isinstance(resolved, dict)
        assert "T" in resolved
        assert "U" in resolved
        assert resolved["T"] == TYPE_INT
        assert resolved["U"] == TYPE_STRING

    def test_is_type_var_resolved_true(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        solver.add_equality(t, TYPE_INT)
        solver.solve()
        assert solver.is_type_var_resolved("T")

    def test_is_type_var_resolved_false(self):
        solver = ConstraintSolver()
        solver.add_equality(TypeVariable("T"), TypeVariable("T"))
        solver.solve()
        assert not solver.is_type_var_resolved("T")

    def test_substitution_resolve_set(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        set_type = SetType(TypeVariable("T"))
        resolved = sub.resolve(set_type)
        assert resolved.kind == TypeKind.SET
        assert resolved.element_type == TYPE_INT

    def test_substitution_resolve_range(self):
        sub = Substitution()
        sub.bind("T", TYPE_FLOAT)
        range_type = RangeType(TypeVariable("T"))
        resolved = sub.resolve(range_type)
        assert resolved.kind == TypeKind.RANGE
        assert resolved.element_type == TYPE_FLOAT

    def test_chain_resolution_three_levels(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        v = TypeVariable("V")
        solver.add_equality(u, t)
        solver.add_equality(v, u)
        solver.add_equality(t, TYPE_INT)
        solver.solve()
        assert solver.resolve_type(v) == TYPE_INT
        assert solver.resolve_type(u) == TYPE_INT
        assert solver.resolve_type(t) == TYPE_INT

    def test_chain_resolution_two_vars(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        u = TypeVariable("U")
        solver.add_equality(t, TYPE_FLOAT)
        solver.add_equality(u, t)
        solver.solve()
        assert solver.resolve_type(u) == TYPE_FLOAT

    def test_substitution_resolve_tuple(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        sub.bind("U", TYPE_STRING)
        tuple_type = TupleType((TypeVariable("T"), TypeVariable("U")))
        resolved = sub.resolve(tuple_type)
        assert resolved.kind == TypeKind.TUPLE
        assert resolved.element_types == (TYPE_INT, TYPE_STRING)

    def test_substitution_resolve_function(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        func_type = FunctionType((TypeVariable("T"),), TypeVariable("T"))
        resolved = sub.resolve(func_type)
        assert resolved.kind == TypeKind.FUNCTION
        assert resolved.param_types == (TYPE_INT,)
        assert resolved.return_type == TYPE_INT

    def test_substitution_resolve_optional(self):
        sub = Substitution()
        sub.bind("T", TYPE_STRING)
        opt_type = OptionalType(TypeVariable("T"))
        resolved = sub.resolve(opt_type)
        assert resolved.kind == TypeKind.OPTIONAL
        assert resolved.inner == TYPE_STRING


# ══════════════════════════════════════════════════════════════════
# 7. Inference Enhancements
# ══════════════════════════════════════════════════════════════════


class TestInferenceEnhancements:
    def _make_engine(self):
        ctx = TypeContext()
        diag = TypeDiagnostics()
        return InferenceEngine(ctx, diag)

    def test_constraint_count_zero(self):
        engine = self._make_engine()
        assert engine.constraint_count == 0

    def test_constraint_count_after_inference(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        engine.infer_binary(TYPE_INT, "+", TYPE_STRING, loc)
        assert engine.constraint_count >= 0

    def test_type_var_count_zero(self):
        engine = self._make_engine()
        assert engine.type_var_count == 0

    def test_type_var_count_increments(self):
        engine = self._make_engine()
        engine.new_type_var()
        assert engine.type_var_count == 1
        engine.new_type_var()
        assert engine.type_var_count == 2

    def test_infer_set_literal_non_empty(self):
        engine = self._make_engine()
        result = engine.infer_set_literal([TYPE_INT, TYPE_INT, TYPE_INT])
        assert result.kind == TypeKind.SET
        assert result.element_type == TYPE_INT

    def test_infer_set_literal_empty(self):
        engine = self._make_engine()
        result = engine.infer_set_literal([])
        assert result.kind == TypeKind.SET

    def test_infer_set_literal_mixed_numeric(self):
        engine = self._make_engine()
        result = engine.infer_set_literal([TYPE_INT, TYPE_FLOAT])
        assert result.kind == TypeKind.SET
        assert result.element_type == TYPE_FLOAT

    def test_infer_range_type(self):
        engine = self._make_engine()
        result = engine.infer_range_type(TYPE_INT, TYPE_INT)
        assert result.kind == TypeKind.RANGE
        assert result.element_type == TYPE_INT

    def test_infer_range_type_mixed_numeric(self):
        engine = self._make_engine()
        result = engine.infer_range_type(TYPE_INT, TYPE_FLOAT)
        assert result.kind == TypeKind.RANGE
        assert result.element_type == TYPE_FLOAT

    def test_infer_ternary_same_types(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_ternary(TYPE_BOOL, TYPE_INT, TYPE_INT, loc)
        assert result == TYPE_INT

    def test_infer_ternary_different_types(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_ternary(TYPE_BOOL, TYPE_INT, TYPE_FLOAT, loc)
        assert result == TYPE_FLOAT

    def test_infer_ternary_int_float(self):
        engine = self._make_engine()
        loc = TypeLocation("<test>", 1, 1)
        result = engine.infer_ternary(TYPE_BOOL, TYPE_FLOAT, TYPE_INT, loc)
        assert result == TYPE_FLOAT


# ══════════════════════════════════════════════════════════════════
# 8. Generic Engine Enhancements
# ══════════════════════════════════════════════════════════════════


class TestGenericEngineEnhancements:
    def _make_engine(self):
        reg = TypeRegistry()
        return GenericEngine(reg)

    def test_detect_cyclic_constraint_no_cycle(self):
        engine = self._make_engine()
        engine.register_generic_function("fn", [
            GenericParamDef("T", upper_bound=TYPE_ANY),
        ])
        assert not engine.detect_cyclic_constraint("fn")

    def test_detect_cyclic_constraint_with_cycle(self):
        engine = self._make_engine()
        params_a = [
            GenericParamDef("T", upper_bound=GenericType("B", TypeVariable("T"))),
        ]
        engine.register_generic_function("A", params_a)
        params_b = [
            GenericParamDef("U", upper_bound=GenericType("A", TypeVariable("U"))),
        ]
        engine.register_generic_function("B", params_b)
        assert engine.detect_cyclic_constraint("A")

    def test_detect_cyclic_constraint_nonexistent(self):
        engine = self._make_engine()
        assert not engine.detect_cyclic_constraint("nonexistent")

    def test_get_variance_default(self):
        engine = self._make_engine()
        engine.register_generic_function("fn", [
            GenericParamDef("T"),
        ])
        assert engine.get_variance("fn", "T") == "invariant"

    def test_get_variance_covariant(self):
        engine = self._make_engine()
        engine.register_generic_function("fn", [
            GenericParamDef("T", variance="covariant"),
        ])
        assert engine.get_variance("fn", "T") == "covariant"

    def test_get_variance_contravariant(self):
        engine = self._make_engine()
        engine.register_generic_function("fn", [
            GenericParamDef("T", variance="contravariant"),
        ])
        assert engine.get_variance("fn", "T") == "contravariant"

    def test_get_variance_nonexistent_param(self):
        engine = self._make_engine()
        engine.register_generic_function("fn", [
            GenericParamDef("T"),
        ])
        assert engine.get_variance("fn", "U") == "invariant"

    def test_count_instantiations_of(self):
        engine = self._make_engine()
        engine.register_generic_class("Container", [GenericParamDef("T")])
        engine.instantiate_generic("Container", [TYPE_INT])
        engine.instantiate_generic("Container", [TYPE_STRING])
        assert engine.count_instantiations_of("Container") == 2

    def test_count_instantiations_of_none(self):
        engine = self._make_engine()
        assert engine.count_instantiations_of("Nonexistent") == 0

    def test_get_all_generic_names(self):
        engine = self._make_engine()
        engine.register_generic_function("fn1", [GenericParamDef("T")])
        engine.register_generic_function("fn2", [GenericParamDef("U")])
        names = engine.get_all_generic_names()
        assert isinstance(names, list)
        assert "fn1" in names
        assert "fn2" in names

    def test_get_all_generic_names_empty(self):
        engine = self._make_engine()
        names = engine.get_all_generic_names()
        assert names == []


# ══════════════════════════════════════════════════════════════════
# 9. Trait Resolver Enhancements
# ══════════════════════════════════════════════════════════════════


class TestTraitResolverEnhancements:
    def _make_resolver(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        return TraitResolver(reg, diag)

    def test_get_all_trait_names(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="Drawable",
            required_methods={
                "draw": MethodSignature(name="draw", return_type=TYPE_NONE),
            },
        ))
        resolver.register_trait(TraitDefinition(
            name="Serializable",
            required_methods={
                "serialize": MethodSignature(name="serialize", return_type=TYPE_STRING),
            },
        ))
        names = resolver.get_all_trait_names()
        assert "Drawable" in names
        assert "Serializable" in names

    def test_get_all_trait_names_empty(self):
        resolver = self._make_resolver()
        names = resolver.get_all_trait_names()
        assert names == []

    def test_get_all_interface_names(self):
        resolver = self._make_resolver()
        resolver.register_interface(InterfaceDefinition(
            name="Comparable",
            required_methods={
                "compare_to": MethodSignature(
                    name="compare_to",
                    param_types=[TYPE_ANY],
                    return_type=TYPE_INT,
                ),
            },
        ))
        names = resolver.get_all_interface_names()
        assert "Comparable" in names

    def test_get_all_interface_names_empty(self):
        resolver = self._make_resolver()
        names = resolver.get_all_interface_names()
        assert names == []

    def test_is_trait_sealed_true(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="SealedTrait",
            is_sealed=True,
            required_methods={},
        ))
        assert resolver.is_trait_sealed("SealedTrait")

    def test_is_trait_sealed_false(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="OpenTrait",
            is_sealed=False,
            required_methods={},
        ))
        assert not resolver.is_trait_sealed("OpenTrait")

    def test_is_trait_sealed_nonexistent(self):
        resolver = self._make_resolver()
        assert not resolver.is_trait_sealed("Nonexistent")

    def test_get_super_traits_direct(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="Base",
            required_methods={},
        ))
        resolver.register_trait(TraitDefinition(
            name="Child",
            required_methods={},
            super_traits=["Base"],
        ))
        supers = resolver.get_super_traits("Child")
        assert "Base" in supers

    def test_get_super_traits_chain(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="A", required_methods={},
        ))
        resolver.register_trait(TraitDefinition(
            name="B", required_methods={},
            super_traits=["A"],
        ))
        resolver.register_trait(TraitDefinition(
            name="C", required_methods={},
            super_traits=["B"],
        ))
        supers = resolver.get_super_traits("C")
        assert "B" in supers
        assert "A" in supers

    def test_get_super_traits_none(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="Root", required_methods={},
        ))
        supers = resolver.get_super_traits("Root")
        assert supers == []

    def test_get_trait_summary(self):
        resolver = self._make_resolver()
        resolver.register_trait(TraitDefinition(
            name="Drawable",
            required_methods={
                "draw": MethodSignature(name="draw", return_type=TYPE_NONE),
            },
            default_methods={
                "resize": MethodSignature(name="resize", return_type=TYPE_NONE),
            },
            super_traits=["Base"],
            is_sealed=False,
        ))
        summary = resolver.get_trait_summary("Drawable")
        assert summary["name"] == "Drawable"
        assert "draw" in summary["required_methods"]
        assert "resize" in summary["default_methods"]
        assert "Base" in summary["super_traits"]
        assert summary["is_sealed"] is False

    def test_get_trait_summary_nonexistent(self):
        resolver = self._make_resolver()
        summary = resolver.get_trait_summary("Nonexistent")
        assert summary == {}

    def test_get_interface_summary(self):
        resolver = self._make_resolver()
        resolver.register_interface(InterfaceDefinition(
            name="Comparable",
            required_methods={
                "compare_to": MethodSignature(
                    name="compare_to",
                    param_types=[TYPE_ANY],
                    return_type=TYPE_INT,
                ),
            },
            super_interfaces=["Equality"],
        ))
        summary = resolver.get_interface_summary("Comparable")
        assert summary["name"] == "Comparable"
        assert "compare_to" in summary["required_methods"]
        assert "Equality" in summary["super_interfaces"]

    def test_get_interface_summary_nonexistent(self):
        resolver = self._make_resolver()
        summary = resolver.get_interface_summary("Nonexistent")
        assert summary == {}


# ══════════════════════════════════════════════════════════════════
# 10. Compile-Time Enhancements
# ══════════════════════════════════════════════════════════════════


class TestCompileTimeEnhancements:
    def _make_eval(self):
        return CompileTimeEvaluator(TypeDiagnostics())

    def test_eval_string_equal_same(self):
        ev = self._make_eval()
        result = ev.eval_string_equal(
            ConstValue.string_val("hello"),
            ConstValue.string_val("hello"),
        )
        assert result.value is True

    def test_eval_string_equal_different(self):
        ev = self._make_eval()
        result = ev.eval_string_equal(
            ConstValue.string_val("hello"),
            ConstValue.string_val("world"),
        )
        assert result.value is False

    def test_eval_string_not_equal_same(self):
        ev = self._make_eval()
        result = ev.eval_string_not_equal(
            ConstValue.string_val("hello"),
            ConstValue.string_val("hello"),
        )
        assert result.value is False

    def test_eval_string_not_equal_different(self):
        ev = self._make_eval()
        result = ev.eval_string_not_equal(
            ConstValue.string_val("hello"),
            ConstValue.string_val("world"),
        )
        assert result.value is True

    def test_eval_string_not_equal_non_string(self):
        ev = self._make_eval()
        result = ev.eval_string_not_equal(
            ConstValue.int_val(42),
            ConstValue.string_val("hello"),
        )
        assert result.is_error

    def test_eval_string_concat(self):
        ev = self._make_eval()
        result = ev.eval_string_concat(
            ConstValue.string_val("hello"),
            ConstValue.string_val(" world"),
        )
        assert result.value == "hello world"

    def test_eval_string_concat_empty(self):
        ev = self._make_eval()
        result = ev.eval_string_concat(
            ConstValue.string_val(""),
            ConstValue.string_val(""),
        )
        assert result.value == ""

    def test_eval_string_concat_non_string(self):
        ev = self._make_eval()
        result = ev.eval_string_concat(
            ConstValue.int_val(42),
            ConstValue.string_val("hello"),
        )
        assert result.is_error

    def test_eval_ternary_true(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_ternary(
            ConstValue.bool_val(True),
            ConstValue.int_val(1),
            ConstValue.int_val(2),
            loc,
        )
        assert result.value == 1

    def test_eval_ternary_false(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_ternary(
            ConstValue.bool_val(False),
            ConstValue.int_val(1),
            ConstValue.int_val(2),
            loc,
        )
        assert result.value == 2

    def test_eval_ternary_non_bool_condition(self):
        ev = self._make_eval()
        loc = TypeLocation("<test>", 1, 1)
        result = ev.eval_ternary(
            ConstValue.int_val(42),
            ConstValue.int_val(1),
            ConstValue.int_val(2),
            loc,
        )
        assert result.is_error

    def test_eval_typeof_int(self):
        ev = self._make_eval()
        result = ev.eval_typeof(ConstValue.int_val(42))
        assert result.value == "int"

    def test_eval_typeof_string(self):
        ev = self._make_eval()
        result = ev.eval_typeof(ConstValue.string_val("hello"))
        assert result.value == "umuntu"

    def test_eval_typeof_bool(self):
        ev = self._make_eval()
        result = ev.eval_typeof(ConstValue.bool_val(True))
        assert result.value == "bool"

    def test_eval_typeof_none(self):
        ev = self._make_eval()
        result = ev.eval_typeof(ConstValue.none_val())
        assert result.value == "none"

    def test_constant_count_zero(self):
        ev = self._make_eval()
        assert ev.constant_count == 0

    def test_constant_count_after_define(self):
        ev = self._make_eval()
        ev.define_constant("PI", ConstValue.float_val(3.14))
        assert ev.constant_count == 1

    def test_constant_count_multiple(self):
        ev = self._make_eval()
        ev.define_constant("PI", ConstValue.float_val(3.14))
        ev.define_constant("E", ConstValue.float_val(2.718))
        assert ev.constant_count == 2

    def test_eval_string_equal_non_string(self):
        ev = self._make_eval()
        result = ev.eval_string_equal(
            ConstValue.int_val(42),
            ConstValue.string_val("hello"),
        )
        assert result.is_error


# ══════════════════════════════════════════════════════════════════
# 11. Diagnostics Enhancements
# ══════════════════════════════════════════════════════════════════


class TestDiagnosticsEnhancements:
    def test_filter_by_severity_error(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.warning(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        errors = diag.filter_by_severity(TypeSeverity.ERROR)
        assert len(errors) == 1
        assert errors[0].severity == TypeSeverity.ERROR

    def test_filter_by_severity_warning(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.warning(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        warnings = diag.filter_by_severity(TypeSeverity.WARNING)
        assert len(warnings) == 1
        assert warnings[0].severity == TypeSeverity.WARNING

    def test_filter_by_severity_none_match(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        infos = diag.filter_by_severity(TypeSeverity.INFO)
        assert len(infos) == 0

    def test_filter_by_code(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.error(TypeErrorCode.TYP200_NOT_CALLABLE, loc, "int")
        filtered = diag.filter_by_code(TypeErrorCode.TYP100_TYPE_MISMATCH)
        assert len(filtered) == 1
        assert filtered[0].code == TypeErrorCode.TYP100_TYPE_MISMATCH

    def test_filter_by_code_multiple(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "float", "bool")
        filtered = diag.filter_by_code(TypeErrorCode.TYP100_TYPE_MISMATCH)
        assert len(filtered) == 2

    def test_filter_by_code_none_match(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        filtered = diag.filter_by_code(TypeErrorCode.TYP200_NOT_CALLABLE)
        assert len(filtered) == 0

    def test_filter_by_file(self):
        diag = TypeDiagnostics()
        loc1 = TypeLocation("file1.i", 1, 1)
        loc2 = TypeLocation("file2.i", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc1, "int", "string")
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc2, "int", "string")
        filtered = diag.filter_by_file("file1.i")
        assert len(filtered) == 1
        assert filtered[0].location.file == "file1.i"

    def test_filter_by_file_none_match(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("file1.i", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        filtered = diag.filter_by_file("file3.i")
        assert len(filtered) == 0

    def test_format_summary_no_diagnostics(self):
        diag = TypeDiagnostics()
        summary = diag.format_summary()
        assert summary == "No diagnostics"

    def test_format_summary_with_errors(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        summary = diag.format_summary()
        assert "1 error(s)" in summary

    def test_format_summary_with_warnings(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.warning(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        summary = diag.format_summary()
        assert "1 warning(s)" in summary

    def test_format_summary_mixed(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "float", "bool")
        diag.warning(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        summary = diag.format_summary()
        assert "2 error(s)" in summary
        assert "1 warning(s)" in summary

    def test_to_json(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 10, 5)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        json_data = diag.to_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 1
        assert json_data[0]["code"] == "TYP100_TYPE_MISMATCH"
        assert json_data[0]["severity"] == "error"
        assert json_data[0]["location"]["line"] == 10

    def test_to_json_multiple(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.warning(TypeErrorCode.TYP200_NOT_CALLABLE, loc, "int")
        json_data = diag.to_json()
        assert len(json_data) == 2

    def test_generate_suggestion_existing_fix(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(
            TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string",
            suggested_fix="Cast to int",
        )
        suggestion = diag.generate_suggestion(d)
        assert suggestion == "Cast to int"

    def test_generate_suggestion_not_callable(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP200_NOT_CALLABLE, loc, "int")
        suggestion = diag.generate_suggestion(d)
        assert suggestion is not None
        assert "parentheses" in suggestion.lower()

    def test_generate_suggestion_undefined_variable(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP250_UNDEFINED_VARIABLE, loc, "x")
        suggestion = diag.generate_suggestion(d)
        assert suggestion is not None
        assert "spelling" in suggestion.lower()

    def test_generate_suggestion_const_assign(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP500_CANNOT_ASSIGN_CONST, loc, "x")
        suggestion = diag.generate_suggestion(d)
        assert suggestion is not None
        assert "nibyo" in suggestion

    def test_generate_suggestion_no_match(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        d = diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        suggestion = diag.generate_suggestion(d)
        assert suggestion is None

    def test_diagnostic_count_zero(self):
        diag = TypeDiagnostics()
        assert diag.diagnostic_count == 0

    def test_diagnostic_count_after_errors(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.error(TypeErrorCode.TYP200_NOT_CALLABLE, loc, "int")
        assert diag.diagnostic_count == 2

    def test_diagnostic_count_after_mixed(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.warning(TypeErrorCode.TYP200_NOT_CALLABLE, loc, "int")
        diag.info(TypeErrorCode.TYP250_UNDEFINED_VARIABLE, loc, "x")
        assert diag.diagnostic_count == 3


# ══════════════════════════════════════════════════════════════════
# 12. Type Checker Enhancements
# ══════════════════════════════════════════════════════════════════


class TestTypeCheckerEnhancements:
    def _check(self, decls):
        prog = Program(declarations=decls)
        checker = TypeChecker()
        return checker, checker.check(prog)

    def test_self_inheritance_detected(self):
        cls = ClassDecl(
            name="SelfRef",
            parent="SelfRef",
            members=[],
        )
        checker, diags = self._check([cls])
        assert diags.has_errors

    def test_sealed_class_inheritance_error(self):
        parent = ClassDecl(
            name="SealedBase",
            parent=None,
            members=[],
        )
        child = ClassDecl(
            name="Child",
            parent="SealedBase",
            members=[],
        )
        checker, diags = self._check([parent, child])
        sealed_defn = TypeDefinition(
            name="SealedBase",
            kind=TypeKind.CLASS,
            type_obj=ClassType("SealedBase"),
            is_sealed=True,
        )
        checker.registry.clear()
        checker.registry.register(sealed_defn)
        prog = Program(declarations=[child])
        diags = checker.check(prog)
        assert diags.has_errors

    def test_normal_class_no_self_inheritance(self):
        cls = ClassDecl(
            name="NormalClass",
            parent=None,
            members=[],
        )
        checker, diags = self._check([cls])
        assert not diags.has_errors

    def test_class_with_valid_parent(self):
        parent = ClassDecl(
            name="Parent",
            parent=None,
            members=[],
        )
        child = ClassDecl(
            name="Child",
            parent="Parent",
            members=[],
        )
        checker, diags = self._check([parent, child])
        assert not diags.has_errors

    def test_var_decl_still_works(self):
        decl = VarDecl(
            name="x",
            type_annotation=None,
            initializer=LiteralExpr(42),
        )
        checker, diags = self._check([decl])
        assert not diags.has_errors

    def test_function_decl_still_works(self):
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


# ══════════════════════════════════════════════════════════════════
# Bonus: Additional Edge Case Tests
# ══════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_type_id_preserves_across_subclass(self):
        class MyInt(IntType):
            pass
        a = IntType()
        b = MyInt()
        assert a.type_id != b.type_id

    def test_variance_equality(self):
        assert Variance.INVARIANT == Variance.INVARIANT
        assert Variance.COVARIANT == Variance.COVARIANT
        assert Variance.INVARIANT != Variance.COVARIANT

    def test_package_type_usable_in_set(self):
        p1 = PackageType("core")
        p2 = PackageType("core")
        s = {p1, p2}
        assert len(s) == 1

    def test_common_type_deeply_nested_optional(self):
        opt_int = make_optional(TYPE_INT)
        opt_opt_int = make_optional(opt_int)
        result = common_type(opt_int, TYPE_NONE)
        assert result is not None

    def test_registry_clear(self):
        reg = TypeRegistry()
        reg.register(TypeDefinition(
            name="TestType", kind=TypeKind.CLASS,
            type_obj=ClassType("TestType"),
        ))
        reg.clear()
        assert not reg.has("TestType")

    def test_database_clear(self):
        db = TypeDatabase()
        db.record_subtype("A", "B")
        db.clear()
        assert db.is_subtype_cached("A", "B") is None

    def test_environment_clear(self):
        env = TypeEnvironment()
        env.define("x", TYPE_INT)
        env.clear()
        assert env.lookup("x") is None

    def test_context_clear(self):
        ctx = TypeContext()
        ctx.enter_function("test")
        ctx.record_error()
        ctx.clear()
        assert not ctx.has_errors
        assert not ctx.in_function

    def test_constraint_solver_clear(self):
        solver = ConstraintSolver()
        t = TypeVariable("T")
        solver.add_equality(t, TYPE_INT)
        solver.clear()
        assert solver.constraint_count == 0

    def test_inference_engine_reset(self):
        ctx = TypeContext()
        diag = TypeDiagnostics()
        engine = InferenceEngine(ctx, diag)
        engine.new_type_var()
        engine.reset()
        assert engine.type_var_count == 0

    def test_generics_engine_clear(self):
        reg = TypeRegistry()
        engine = GenericEngine(reg)
        engine.register_generic_function("fn", [GenericParamDef("T")])
        engine.clear()
        assert not engine.has_generics("fn")

    def test_trait_resolver_clear(self):
        reg = TypeRegistry()
        diag = TypeDiagnostics()
        resolver = TraitResolver(reg, diag)
        resolver.register_trait(TraitDefinition(
            name="Test", required_methods={},
        ))
        resolver.clear()
        assert resolver.get_trait("Test") is None

    def test_compiletime_clear(self):
        ev = CompileTimeEvaluator(TypeDiagnostics())
        ev.define_constant("X", ConstValue.int_val(1))
        ev.clear()
        assert ev.constant_count == 0

    def test_diagnostics_clear(self):
        diag = TypeDiagnostics()
        loc = TypeLocation("<test>", 1, 1)
        diag.error(TypeErrorCode.TYP100_TYPE_MISMATCH, loc, "int", "string")
        diag.clear()
        assert diag.diagnostic_count == 0

    def test_substitution_len(self):
        sub = Substitution()
        assert len(sub) == 0
        sub.bind("T", TYPE_INT)
        assert len(sub) == 1

    def test_substitution_has(self):
        sub = Substitution()
        assert not sub.has("T")
        sub.bind("T", TYPE_INT)
        assert sub.has("T")

    def test_substitution_clear(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        sub.clear()
        assert len(sub) == 0

    def test_substitution_bindings(self):
        sub = Substitution()
        sub.bind("T", TYPE_INT)
        sub.bind("U", TYPE_STRING)
        bindings = sub.bindings
        assert isinstance(bindings, dict)
        assert "T" in bindings
        assert "U" in bindings

    def test_registry_count(self):
        reg = TypeRegistry()
        assert reg.count == reg.registered_count

    def test_common_type_float_int(self):
        result = common_type(TYPE_FLOAT, TYPE_INT)
        assert result == TYPE_FLOAT

    def test_common_type_int_int(self):
        result = common_type(TYPE_INT, TYPE_INT)
        assert result == TYPE_INT

    def test_is_compatible_bidirectional(self):
        assert is_compatible(TYPE_INT, TYPE_INT)
        assert not is_compatible(TYPE_STRING, TYPE_INT)
