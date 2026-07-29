/// icyanditswe.i — Query DSL for the UBUBIKO data platform.
///
/// Provides fluent query building for database operations.

pub enum JoinType {
    Inner = "INNER JOIN",
    Left = "LEFT JOIN",
    Right = "RIGHT JOIN",
    Full = "FULL OUTER JOIN",
    Cross = "CROSS JOIN",
}

pub enum OrderDirection {
    Asc = "ASC",
    Desc = "DESC",
}

pub struct Query {
    table: String,
    columns: [String] = [],
    conditions: [String] = [],
    joins: [Join] = [],
    group_by: [String] = [],
    order_by: [OrderClause] = [],
    limit: Int = 0,
    offset: Int = 0,
}

pub struct Join {
    join_type: JoinType = JoinType.Inner,
    table: String,
    condition: String,
}

pub struct OrderClause {
    expression: String,
    direction: OrderDirection = OrderDirection.Asc,
}

pub fn query(table: String) -> Query {
    Query { table }
}

pub fn select(columns: ...[String]) -> Query {
    // Starts a SELECT query
}

pub fn raw(sql: String, params: Map = {}) -> RawQuery {
    // Creates a raw SQL query
}
