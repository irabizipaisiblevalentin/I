/// Models for UBUBIKO example application

pub model User {
    table: "users",
    fields: {
        id: Int, primary_key, auto_increment,
        name: String(255),
        email: String(255), unique,
        created_at: Timestamp,
    },
}

pub model Post {
    table: "posts",
    fields: {
        id: Int, primary_key, auto_increment,
        title: String(255),
        content: Text,
        user_id: Int,
        created_at: Timestamp,
    },
    relationships: {
        author: ManyToOne(User, foreign_key: "user_id"),
    },
}
