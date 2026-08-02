/// UBUBIKO example application

import ububiko.ububiko as ububiko
import ububiko.ikubiye as ikubiye

fn main() {
    let config = ububiko.ConnectionConfig {
        db_type: ububiko.DatabaseType.SQLite,
        database: "app.db",
    }

    let conn = ububiko.create_connection(config)
    let repo = ikubiye.repository(User)

    // Create table and insert data
    repo.create_table()
    let user = User { name: "I Developer", email: "dev@example.com" }
    repo.save(user)

    // Query
    let users = repo.find(active: true)
    for user in users {
        print("User: {user.name}")
    }
}
