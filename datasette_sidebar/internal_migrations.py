from sqlite_utils import Database
from sqlite_migrate import Migrations

internal_migrations = Migrations("datasette-sidebar.internal")


@internal_migrations()
def m001_stars(db: Database):
    db.executescript("""
        CREATE TABLE datasette_sidebar_stars (
            id TEXT PRIMARY KEY,
            actor_id TEXT NOT NULL,
            star_type TEXT NOT NULL CHECK(star_type IN ('database', 'table', 'row')),
            database_name TEXT NOT NULL,
            table_name TEXT DEFAULT '',
            row_pks TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now')),
            UNIQUE(actor_id, star_type, database_name, table_name, row_pks)
        );
    """)
