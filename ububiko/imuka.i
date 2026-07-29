/// imuka.i — Migration DSL for the UBUBIKO data platform.
///
/// Provides schema creation, migration definitions,
/// and seed data declarations.

pub struct ColumnType {
    pub const Integer = "INTEGER"
    pub const BigInt = "BIGINT"
    pub const VarChar = "VARCHAR"
    pub const Text = "TEXT"
    pub const Boolean = "BOOLEAN"
    pub const Date = "DATE"
    pub const Timestamp = "TIMESTAMP"
    pub const Blob = "BLOB"
    pub const Json = "JSON"
    pub const Vector = "VECTOR"
}

pub struct Column {
    name: String,
    col_type: String = ColumnType.Text,
    primary_key: Bool = false,
    unique: Bool = false,
    nullable: Bool = true,
    default: Any = None,
}

pub struct Table {
    name: String,
    columns: [Column] = [],
}

pub trait Migration {
    fn version() -> String;
    fn description() -> String;
    fn up();
    fn down();
    fn seed();
}

pub fn create_migration(name: String) {
    // Creates a new migration file
}

pub fn migrate() {
    // Runs all pending migrations
}

pub fn rollback(version: String = "") {
    // Rolls back migrations
}
