import os
import aiosqlite


class Database:
    def __init__(self, db_path="database/bot_data.db"):
        self.db_path = db_path

    async def init(self):
        # Dam bao folder DB ton tai
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    auth_token TEXT,
                    current_repo TEXT
                )
                """
            )
            await self._migrate_legacy_username_schema(db)
            await db.commit()

    async def _migrate_legacy_username_schema(self, db):
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
        column_names = {col[1] for col in columns}

        if "user_id" in column_names:
            return
        if "username" not in column_names:
            return

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users_v2 (
                user_id INTEGER PRIMARY KEY,
                auth_token TEXT,
                current_repo TEXT
            )
            """
        )
        # Chi migrate cac dong co username la so nguyen.
        await db.execute(
            """
            INSERT OR REPLACE INTO users_v2 (user_id, auth_token, current_repo)
            SELECT CAST(username AS INTEGER), auth_token, current_repo
            FROM users
            WHERE username GLOB '[0-9]*'
            """
        )
        await db.execute("DROP TABLE users")
        await db.execute("ALTER TABLE users_v2 RENAME TO users")

    async def set_token(self, user_id: int, token: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, auth_token)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET auth_token = excluded.auth_token
                """,
                (user_id, token),
            )
            await db.commit()

    async def get_token(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT auth_token FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
