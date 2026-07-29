/// ihuriro.i — Define Once, Use Everywhere
///
/// A single model definition automatically produces:
/// database schemas, validation rules, REST APIs, GraphQL schemas,
/// JSON serialization, form definitions, admin dashboards,
/// documentation, test data, and AI embedding metadata.

pub enum GeneratorTarget {
    Database = "database",
    Validation = "validation",
    RestApi = "rest_api",
    GraphQL = "graphql",
    Serialization = "serialization",
    Forms = "forms",
    Admin = "admin",
    Docs = "docs",
    TestData = "test_data",
    Embeddings = "embeddings",
}

pub struct ModelField {
    name: String,
    native_type: String = "string",
    required: Bool = false,
    unique: Bool = false,
    primary_key: Bool = false,
    auto_increment: Bool = false,
    default: Any = None,
    max_length: Int = 255,
    min_value: Float = 0.0,
    max_value: Float = 0.0,
    description: String = "",
    secret: Bool = false,
    embed: Bool = false,
    widget: String = "",
    choices: [(Any, String)] = [],
}

pub struct ModelDefinition {
    name: String,
    table: String,
    fields: {String: ModelField},
    description: String = "",
    audit_fields: Bool = true,
    soft_delete: Bool = false,
    generate: [GeneratorTarget] = [Database, Validation, RestApi, Serialization, Docs],
}

pub fn define(model: ModelDefinition) -> ModelDefinition {
    /// Register a model definition for code generation.
}

pub fn generate(model: ModelDefinition, targets: [GeneratorTarget] = []) -> {String: {String: String}} {
    /// Generate all artifacts for a model.
}

pub fn generate_all() -> {String: {String: {String: String}}} {
    /// Generate artifacts for all registered models.
}
