import random

import pytest

from app import game

POOL = [{"id": i, "name": f"item{i}", "image": f"/assets/items/{i}.svg"} for i in range(1, 9)]
T0 = 1_000_000.0


def make_game(seed=0):
    return game.new_game("g1", POOL, T0, rng=random.Random(seed))


def center(item):
    return item["x"] + item["size"] / 2, item["y"] + item["size"] / 2


def find_empty_spot(state):
    for x in range(0, game.MAP_WIDTH, 10):
        for y in range(0, game.MAP_HEIGHT, 10):
            if game.find_hit(state, x, y) is None:
                return x, y
    raise AssertionError("no empty spot")


# 배치

@pytest.mark.parametrize("seed", range(50))
def test_place_items_inside_map_and_not_overlapping(seed):
    items = game.place_items(POOL, random.Random(seed))
    assert len(items) == 5
    assert len({i["id"] for i in items}) == 5
    for it in items:
        assert it["size"] == 64
        assert 0 <= it["x"] <= game.MAP_WIDTH - 64
        assert 0 <= it["y"] <= game.MAP_HEIGHT - 64
        assert set(it) == {"id", "name", "image", "x", "y", "size"}
    for a in range(5):
        for b in range(a + 1, 5):
            assert not game._overlaps(items[a], items[b])


# 판정

def test_hit_inside_and_on_boundary():
    s = make_game()
    it = s["items"][0]
    for x, y in [center(it), (it["x"], it["y"]), (it["x"] + 64, it["y"] + 64)]:
        assert game.find_hit(s, x, y) == it["id"]


def test_miss_just_outside():
    s = make_game()
    it = s["items"][0]
    hit = game.find_hit(s, it["x"] - 0.01, it["y"])
    assert hit != it["id"]


def test_click_miss_changes_nothing():
    s = make_game()
    x, y = find_empty_spot(s)
    assert game.apply_click(s, x, y, T0 + 1) is None
    assert s["found_item_ids"] == []
    assert s["status"] == game.PLAYING


def test_same_item_not_found_twice():
    s = make_game()
    it = s["items"][0]
    assert game.apply_click(s, *center(it), T0 + 1) == it["id"]
    assert game.apply_click(s, *center(it), T0 + 2) is None
    assert s["found_item_ids"] == [it["id"]]


# 시간

def test_remaining_sec_is_floored():
    s = make_game()
    assert game.remaining_sec(s, T0) == 600
    assert game.remaining_sec(s, T0 + 0.1) == 599
    assert game.remaining_sec(s, T0 + 599.9) == 0
    assert game.remaining_sec(s, T0 + 700) == 0


# 점수

def test_score_when_all_found_includes_time_bonus():
    s = make_game()
    for i, it in enumerate(s["items"]):
        game.apply_click(s, *center(it), T0 + 10 + i)
    # 마지막 클릭 T0+14.0 -> 남은 586초
    assert s["status"] == game.FINISHED
    assert s["score"] == 500 + 586
    assert s["ended_at"] == T0 + 14
    assert game.to_public(s, T0 + 100)["remaining_sec"] == 586


def test_score_bonus_floors_fractional_seconds():
    s = make_game()
    for it in s["items"]:
        game.apply_click(s, *center(it), T0 + 30.7)
    assert s["score"] == 500 + 569


def test_score_null_while_playing():
    s = make_game()
    game.apply_click(s, *center(s["items"][0]), T0 + 1)
    assert s["score"] is None
    assert game.to_public(s, T0 + 1)["score"] is None


# 시간 초과

def test_not_expired_before_limit():
    s = make_game()
    assert game.expire_if_time_over(s, T0 + 599.99) is False
    assert s["status"] == game.PLAYING


def test_expire_gives_only_base_points():
    s = make_game()
    game.apply_click(s, *center(s["items"][0]), T0 + 5)
    game.apply_click(s, *center(s["items"][1]), T0 + 6)
    assert game.expire_if_time_over(s, T0 + 600) is True
    assert s["status"] == game.FINISHED
    assert s["score"] == 200
    assert s["ended_at"] == T0 + 600
    assert game.remaining_sec(s, T0 + 9999) == 0


def test_expire_with_nothing_found_scores_zero():
    s = make_game()
    assert game.expire_if_time_over(s, T0 + 1000)
    assert s["score"] == 0


def test_expire_only_once():
    s = make_game()
    assert game.expire_if_time_over(s, T0 + 600)
    assert game.expire_if_time_over(s, T0 + 601) is False


def test_finished_game_does_not_expire_again():
    s = make_game()
    for it in s["items"]:
        game.apply_click(s, *center(it), T0 + 1)
    score = s["score"]
    assert game.expire_if_time_over(s, T0 + 700) is False
    assert s["score"] == score == 500 + 599


def test_public_shape():
    s = make_game()
    p = game.to_public(s, T0)
    assert set(p) == {
        "game_id", "status", "map", "time_limit_sec", "remaining_sec", "items", "found_item_ids", "score",
    }
    assert p["map"] == {"width": 1600, "height": 900}
    assert p["time_limit_sec"] == 600
    assert p["status"] == "playing"
