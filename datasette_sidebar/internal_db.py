from ulid import ULID

from .page_data import StarItem


class InternalDB:
    def __init__(self, internal_db):
        self.db = internal_db

    async def get_stars(self, actor_id: str, database_name: str | None = None) -> list[StarItem]:
        def read(conn):
            if database_name:
                rows = conn.execute(
                    "SELECT * FROM datasette_sidebar_stars WHERE actor_id = ? AND database_name = ? ORDER BY created_at DESC",
                    [actor_id, database_name],
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM datasette_sidebar_stars WHERE actor_id = ? ORDER BY created_at DESC",
                    [actor_id],
                ).fetchall()
            return [
                StarItem(
                    id=row[0],
                    actor_id=row[1],
                    star_type=row[2],
                    database_name=row[3],
                    table_name=row[4],
                    row_pks=row[5],
                    created_at=row[6],
                )
                for row in rows
            ]

        return await self.db.execute_write_fn(read)

    async def toggle_star(
        self,
        actor_id: str,
        star_type: str,
        database_name: str,
        table_name: str | None = None,
        row_pks: str | None = None,
    ) -> tuple[bool, StarItem | None]:
        """Toggle a star. Returns (is_now_starred, star_item_or_none)."""

        def write(conn):
            existing = conn.execute(
                """SELECT * FROM datasette_sidebar_stars
                WHERE actor_id = ? AND star_type = ? AND database_name = ?
                AND table_name = ? AND row_pks = ?""",
                [actor_id, star_type, database_name, table_name or "", row_pks or ""],
            ).fetchone()

            if existing:
                conn.execute(
                    "DELETE FROM datasette_sidebar_stars WHERE id = ?",
                    [existing[0]],
                )
                return False, None
            else:
                star_id = str(ULID())
                conn.execute(
                    """INSERT INTO datasette_sidebar_stars
                    (id, actor_id, star_type, database_name, table_name, row_pks)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    [star_id, actor_id, star_type, database_name, table_name or "", row_pks or ""],
                )
                row = conn.execute(
                    "SELECT * FROM datasette_sidebar_stars WHERE id = ?",
                    [star_id],
                ).fetchone()
                return True, StarItem(
                    id=row[0],
                    actor_id=row[1],
                    star_type=row[2],
                    database_name=row[3],
                    table_name=row[4],
                    row_pks=row[5],
                    created_at=row[6],
                )

        return await self.db.execute_write_fn(write)

    async def remove_star(self, actor_id: str, star_id: str) -> bool:
        def write(conn):
            result = conn.execute(
                "DELETE FROM datasette_sidebar_stars WHERE id = ? AND actor_id = ?",
                [star_id, actor_id],
            )
            return result.rowcount > 0

        return await self.db.execute_write_fn(write)
