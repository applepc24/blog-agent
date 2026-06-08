import aiosqlite
import asyncio
from datetime import datetime

DB_PATH = "jangdokdae.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT DEFAULT '미분류',
                status TEXT DEFAULT '대기중',
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def add_idea(content: str, category: str = "미분류") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO ideas (content, category, status, created_at) VALUES (?, ?, '대기중', ?)",
            (content, category, datetime.now().isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def get_pending_ideas() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ideas WHERE status = '대기중' ORDER BY created_at ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_status(idea_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE ideas SET status = ? WHERE id = ?",
            (status, idea_id)
        )
        await db.commit()


async def get_all_ideas() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ideas ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    async def test():
        await init_db()
        idea_id = await add_idea("파이썬 비동기 처리 정리", "개발")
        print(f"저장됨: id={idea_id}")
        ideas = await get_pending_ideas()
        for i in ideas:
            print(i)

    asyncio.run(test())
