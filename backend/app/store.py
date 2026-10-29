"""Redis: 진행 중인 게임 상태."""

import json
import os

import redis

GAME_TTL_SEC = 3600

_client = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))


def _key(game_id):
    return f"game:{game_id}"


def create(state):
    _client.set(_key(state["game_id"]), json.dumps(state), ex=GAME_TTL_SEC)


def update(game_id, change):
    """게임 상태를 읽고 change(state)로 고친 뒤 저장한다. 동시 요청은 WATCH로 막고 다시 시도한다.

    change는 state를 제자리에서 고치고 아무 값이나 돌려준다. 그 값을 (state, 값)으로 돌려준다.
    게임이 없으면 (None, None). change가 상태를 바꾸지 않았으면 저장하지 않는다.
    """
    key = _key(game_id)
    with _client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                raw = pipe.get(key)
                if raw is None:
                    pipe.unwatch()
                    return None, None
                state = json.loads(raw)
                result = change(state)
                new_raw = json.dumps(state)
                if new_raw == raw.decode():
                    pipe.unwatch()
                    return state, result
                pipe.multi()
                pipe.set(key, new_raw, keepttl=True)
                pipe.execute()
                return state, result
            except redis.WatchError:
                continue


def ping():
    _client.ping()
