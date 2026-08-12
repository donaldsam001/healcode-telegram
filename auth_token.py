import os
from typing import Optional

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
                    current_repo TEXT,
                    chat_id INTEGER,
                    telegram_username TEXT
                )
                """
            )
            await self._migrate_legacy_username_schema(db)
            await self._ensure_identity_columns(db)
            await db.commit()

    async def _ensure_identity_columns(self, db) -> None:
        """Add identity fields without disrupting installations from older bots."""
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = {column[1] for column in await cursor.fetchall()}
        if "chat_id" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN chat_id INTEGER")
        if "telegram_username" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN telegram_username TEXT")

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

    async def set_telegram_identity(
        self, user_id: int, chat_id: int, username: Optional[str]
    ) -> None:
        """Persist the delivery chat independently of the Telegram user id.

        A user can initiate the bot from a private chat today and a group chat in
        the future, so downstream notifications must target ``chat_id``.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, chat_id, telegram_username)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    chat_id = excluded.chat_id,
                    telegram_username = excluded.telegram_username
                """,
                (int(user_id), int(chat_id), username),
            )
            await db.commit()

    async def get_telegram_identity(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT chat_id, telegram_username FROM users WHERE user_id = ?",
                (int(user_id),),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None or row[0] is None:
            return None
        return {"chat_id": int(row[0]), "telegram_username": row[1]}

    async def get_token(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT auth_token FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
