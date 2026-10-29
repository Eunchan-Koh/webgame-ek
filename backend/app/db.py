"""PostgreSQL: 아이템 풀, 끝난 판 기록."""

import os
from datetime import datetime, timezone

import psycopg

SEED_ITEMS = [
    ("key", "열쇠"),
    ("coin", "동전"),
    ("ring", "반지"),
    ("clock", "시계"),
    ("cup", "컵"),
    ("book", "책"),
    ("glasses", "안경"),
    ("umbrella", "우산"),
]


def _connect():
    return psycopg.connect(os.environ.get("DATABASE_URL", "postgresql://game:game@localhost:5432/game"))


def init():
    """테이블을 만들고, items가 비어 있으면 시드한다."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                image TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_results (
                game_id TEXT PRIMARY KEY,
                score INTEGER NOT NULL,
                found_count INTEGER NOT NULL,
                started_at TIMESTAMPTZ NOT NULL,
                ended_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        if conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO items (slug, name, image) VALUES (%s, %s, %s) ON CONFLICT (slug) DO NOTHING",
                    [(slug, name, f"/assets/items/{slug}.svg") for slug, name in SEED_ITEMS],
                )


def list_items():
    with _connect() as conn:
        rows = conn.execute("SELECT id, name, image FROM items ORDER BY id").fetchall()
    return [{"id": r[0], "name": r[1], "image": r[2]} for r in rows]


def save_result(state):
    def ts(epoch):
        return datetime.fromtimestamp(epoch, tz=timezone.utc)

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO game_results (game_id, score, found_count, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (game_id) DO NOTHING
            """,
            (
                state["game_id"],
                state["score"],
                len(state["found_item_ids"]),
                ts(state["started_at"]),
                ts(state["ended_at"]),
            ),
        )
