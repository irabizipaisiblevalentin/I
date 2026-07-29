/// ikubiye.i — Entity definition DSL for the UBUBIKO data platform.
///
/// Provides entity (model) definition, field types, and
/// relationship declarations for the ORM.

pub enum RelationshipType {
    OneToOne = "one_to_one",
    OneToMany = "one_to_many",
    ManyToOne = "many_to_one",
    ManyToMany = "many_to_many",
}

pub struct Field {
    name: String,
    field_type: Type = String,
    primary_key: Bool = false,
    unique: Bool = false,
    nullable: Bool = false,
    default: Any = None,
    max_length: Int = 255,
}

pub struct Relationship {
    rel_type: RelationshipType = RelationshipType.OneToMany,
    target: String = "",
    foreign_key: String = "",
    lazy: Bool = true,
}

pub trait Entity {
    fn table_name() -> String;
    fn fields() -> [Field];
    fn relationships() -> [Relationship];
    fn to_dict() -> Map;
    fn from_dict(data: Map) -> Self;
}

pub fn create_entity(name: String, fields: [Field]) -> Entity {
    // Creates a new entity definition
}
