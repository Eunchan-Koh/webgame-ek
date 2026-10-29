import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, FiniteFloat

from app import db, game, store


@asynccontextmanager
async def lifespan(_app):
    db.init()
    yield


app = FastAPI(lifespan=lifespan)


class Click(BaseModel):
    x: FiniteFloat
    y: FiniteFloat


def _not_found():
    return HTTPException(status_code=404, detail="game not found")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/games", status_code=201)
def create_game():
    now = time.time()
    state = game.new_game(uuid.uuid4().hex, db.list_items(), now)
    store.create(state)
    return game.to_public(state, now)


@app.get("/api/games/{game_id}")
def get_game(game_id: str):
    now = time.time()
    state, expired = store.update(game_id, lambda s: game.expire_if_time_over(s, now))
    if state is None:
        raise _not_found()
    if expired:
        db.save_result(state)
    return game.to_public(state, now)


@app.post("/api/games/{game_id}/clicks")
def click(game_id: str, body: Click):
    now = time.time()

    def change(state):
        """(이미 끝났었나, 찾은 아이템 id, 이번 요청으로 끝났나)"""
        if game.expire_if_time_over(state, now):
            return True, None, True
        if state["status"] == game.FINISHED:
            return True, None, False
        item_id = game.apply_click(state, body.x, body.y, now)
        return False, item_id, state["status"] == game.FINISHED

    state, result = store.update(game_id, change)
    if state is None:
        raise _not_found()
    rejected, item_id, just_finished = result
    if just_finished:
        db.save_result(state)
    if rejected:
        raise HTTPException(status_code=409, detail="game already finished")
    return {"hit": item_id is not None, "item_id": item_id, "game": game.to_public(state, now)}
