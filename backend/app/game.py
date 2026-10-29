"""게임 규칙. 순수 함수만 둔다 (DB, Redis, HTTP, 현재 시각을 모른다)."""

import math
import random

MAP_WIDTH = 1600
MAP_HEIGHT = 900
ITEM_SIZE = 64
ITEMS_PER_GAME = 5
TIME_LIMIT_SEC = 600
POINTS_PER_ITEM = 100

PLAYING = "playing"
FINISHED = "finished"


def _overlaps(a, b):
    return (
        a["x"] < b["x"] + ITEM_SIZE
        and b["x"] < a["x"] + ITEM_SIZE
        and a["y"] < b["y"] + ITEM_SIZE
        and b["y"] < a["y"] + ITEM_SIZE
    )


def place_items(pool, rng=random):
    """풀에서 ITEMS_PER_GAME개를 뽑아 맵 안쪽, 서로 겹치지 않는 위치에 놓는다.

    pool: [{"id", "name", "image"}, ...]
    """
    chosen = rng.sample(pool, ITEMS_PER_GAME)
    placed = []
    for item in chosen:
        while True:
            pos = {
                "x": rng.randint(0, MAP_WIDTH - ITEM_SIZE),
                "y": rng.randint(0, MAP_HEIGHT - ITEM_SIZE),
            }
            if not any(_overlaps(pos, p) for p in placed):
                break
        placed.append({**item, **pos, "size": ITEM_SIZE})
    return placed


def new_game(game_id, pool, now, rng=random):
    return {
        "game_id": game_id,
        "status": PLAYING,
        "started_at": now,
        "ended_at": None,
        "items": place_items(pool, rng),
        "found_item_ids": [],
        "score": None,
    }


def remaining_sec(state, now):
    """남은 시간(내림한 정수 초, 0 이상). 끝난 게임은 끝난 시각 기준."""
    at = state["ended_at"] if state["status"] == FINISHED else now
    return max(0, math.floor(state["started_at"] + TIME_LIMIT_SEC - at))


def is_time_over(state, now):
    return now >= state["started_at"] + TIME_LIMIT_SEC


def expire_if_time_over(state, now):
    """진행 중인데 시간이 다 됐으면 끝낸다. 찾은 아이템 기본 점수만 인정. 바뀌었으면 True."""
    if state["status"] != PLAYING or not is_time_over(state, now):
        return False
    state["status"] = FINISHED
    state["ended_at"] = state["started_at"] + TIME_LIMIT_SEC
    state["score"] = POINTS_PER_ITEM * len(state["found_item_ids"])
    return True


def find_hit(state, x, y):
    """(x, y)가 아직 안 찾은 아이템 사각형 안(경계 포함)이면 그 아이템 id, 아니면 None."""
    for item in state["items"]:
        if item["id"] in state["found_item_ids"]:
            continue
        if item["x"] <= x <= item["x"] + item["size"] and item["y"] <= y <= item["y"] + item["size"]:
            return item["id"]
    return None


def apply_click(state, x, y, now):
    """진행 중이고 시간 안인 게임에 클릭을 적용한다. 찾은 아이템 id 또는 None을 돌려준다.

    호출 전에 expire_if_time_over로 시간 초과를 처리하고 status가 PLAYING인지 확인해야 한다.
    """
    item_id = find_hit(state, x, y)
    if item_id is None:
        return None
    state["found_item_ids"].append(item_id)
    if len(state["found_item_ids"]) == len(state["items"]):
        state["status"] = FINISHED
        state["ended_at"] = now
        state["score"] = POINTS_PER_ITEM * len(state["items"]) + remaining_sec(state, now)
    return item_id


def to_public(state, now):
    """API 응답용 Game 객체."""
    return {
        "game_id": state["game_id"],
        "status": state["status"],
        "map": {"width": MAP_WIDTH, "height": MAP_HEIGHT},
        "time_limit_sec": TIME_LIMIT_SEC,
        "remaining_sec": remaining_sec(state, now),
        "items": state["items"],
        "found_item_ids": state["found_item_ids"],
        "score": state["score"],
    }
