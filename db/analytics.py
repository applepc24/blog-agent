import aiosqlite
from datetime import datetime

DB_PATH = "jangdokdae.db"


async def init_analytics_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT DEFAULT 'running'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                agent TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                duration_sec REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                wp_post_id INTEGER,
                title TEXT,
                keywords TEXT,
                tags TEXT,
                published_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        """)
        await db.commit()


async def start_run(topic: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO runs (topic, started_at) VALUES (?, ?)",
            (topic, datetime.now().isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def finish_run(run_id: int, status: str = "success"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE runs SET finished_at = ?, status = ? WHERE id = ?",
            (datetime.now().isoformat(), status, run_id)
        )
        await db.commit()


async def log_agent(run_id: int, agent: str, input_tokens: int | None = None,
                    output_tokens: int | None = None, duration_sec: float | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO agent_logs (run_id, agent, input_tokens, output_tokens, duration_sec, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (run_id, agent, input_tokens, output_tokens, duration_sec, datetime.now().isoformat())
        )
        await db.commit()


async def log_post(run_id: int, wp_post_id: int, title: str,
                   keywords: str, tags: list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO posts (run_id, wp_post_id, title, keywords, tags, published_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (run_id, wp_post_id, title, keywords, ",".join(tags), datetime.now().isoformat())
        )
        await db.commit()


# 모델별 토큰 단가 (per 1M tokens)
TOKEN_PRICE = {
    "researcher": {"input": 0.80, "output": 4.00},   # Haiku
    "seo":        {"input": 0.80, "output": 4.00},   # Haiku
    "writer":     {"input": 3.00, "output": 15.00},  # Sonnet
}

def calc_cost(agent: str, input_tokens: int, output_tokens: int) -> float:
    price = TOKEN_PRICE.get(agent, {"input": 3.00, "output": 15.00})
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


async def get_summary() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT status, COUNT(*) as cnt FROM runs GROUP BY status") as cur:
            status_rows = await cur.fetchall()
        async with db.execute("SELECT COUNT(*) as cnt FROM posts") as cur:
            post_count = (await cur.fetchone())["cnt"]
        async with db.execute("SELECT agent, SUM(input_tokens) as inp, SUM(output_tokens) as out FROM agent_logs GROUP BY agent") as cur:
            token_rows = await cur.fetchall()

    status = {r["status"]: r["cnt"] for r in status_rows}
    total_cost = sum(calc_cost(r["agent"], r["inp"] or 0, r["out"] or 0) for r in token_rows)
    tokens_by_agent = {r["agent"]: {"input": r["inp"] or 0, "output": r["out"] or 0} for r in token_rows}

    return {"status": status, "post_count": post_count, "tokens": tokens_by_agent, "total_cost": total_cost}


async def get_run_list() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT r.id, r.topic, r.status, r.started_at, r.finished_at, p.title
            FROM runs r
            LEFT JOIN posts p ON p.run_id = r.id
            GROUP BY r.id
            ORDER BY r.id DESC
            LIMIT 20
        """) as cur:
            runs = await cur.fetchall()
        async with db.execute("""
            SELECT run_id, agent, SUM(input_tokens) as inp, SUM(output_tokens) as out
            FROM agent_logs GROUP BY run_id, agent
        """) as cur:
            log_rows = await cur.fetchall()

    logs_by_run: dict[int, list] = {}
    for row in log_rows:
        logs_by_run.setdefault(row["run_id"], []).append(dict(row))

    result = []
    for r in runs:
        run_dict = dict(r)
        run_logs = logs_by_run.get(r["id"], [])
        run_dict["cost"] = sum(calc_cost(l["agent"], l["inp"] or 0, l["out"] or 0) for l in run_logs)
        result.append(run_dict)
    return result


async def get_run_detail(run_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM runs WHERE id = ?", (run_id,)) as cur:
            run = await cur.fetchone()
        if not run:
            return None
        async with db.execute("SELECT * FROM agent_logs WHERE run_id = ?", (run_id,)) as cur:
            agents = await cur.fetchall()
        async with db.execute("SELECT * FROM posts WHERE run_id = ?", (run_id,)) as cur:
            post = await cur.fetchone()

    return {"run": dict(run), "agents": [dict(a) for a in agents], "post": dict(post) if post else None}
