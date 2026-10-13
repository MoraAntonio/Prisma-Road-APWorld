"""
Display names for Archipelago locations/items.

Shard keys in GameMaker stay internal (e.g. Fields_room_2obj_...); the AP world
only uses numeric IDs on the wire. Names here are what players see in AP.
"""
from __future__ import annotations

import re
from collections import defaultdict
from importlib import resources

# All 211 shard pickups grant the SAME generic item: a single "Fragment" with
# a single AP item id. The item pool is built by adding 211 copies of it (see
# __init__.create_items). This is the standard AP pattern for fragment-collect
# games and is the only way to get the room page to render one summary row
# ("Fragment N / 211") instead of 211 separate rows — Archipelago's
# `item_name_to_id` is a dict[str, int] so 211 distinct (name, id) pairs
# cannot share the display name "Fragment".
#
# Locations stay individually named ("Fields room 5 shard #1", ...) so each
# pickup remains a distinct check; only the *item* delivered by every shard
# location is collapsed.
FRAGMENT_ITEM_NAME = "Fragment"
FRAGMENT_ITEM_ID = 77001

# Number of shard pickups the GameMaker side reports (= lines in
# shard_internal_order.txt = number of Fragment copies we put in the pool).
SHARD_LOCATION_COUNT = 211

# Parsed from internal GM save keys: ..._room_<room>obj_pickup_shard... or ..._room_<room>oCrystalFox...
_SHARD_ROOM_RE = re.compile(
    r"^([A-Za-z]+)_room_(.+?)(?:obj_pickup_shard|oCrystalFox)",
)

# Populated by build_shard_tables(): display names that need extra logic on top of region gates.
COAST_SHARD_FIRE_DISPLAYS: set[str] = set()
COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS: set[str] = set()

_COAST_FIRE_INTERNAL = "Coast_room_4obj_pickup_shard79174"
_COAST_DASH_FLIGHT_INTERNAL = "Coast_room_5obj_pickup_shard400111"


def _primary_room(room_part: str) -> int:
    """Leading integer of the room token (e.g. '11B' -> 11, '4' -> 4)."""
    m = re.match(r"^(\d+)", room_part)
    return int(m.group(1)) if m else 0


def _shard_region(stage: str, room_part: str) -> str:
    """
    Archipelago region for logic / reachability. Must match region names in regions.py.

    Mirrors design notes:
    - Fields / Desert: fully open within the stage.
    - City: Fire from room 3 onward (room 2 and earlier stay in City Start).
    - Forest: Dash (Speed) to enter; Fire from room 5 onward (Forest Deep).
    - Mountain: Speed from room 5 onward; Fire from room 8 onward.
    - Coast: Ice to enter; Fire from room 6 onward; Speed from room 14 onward.
    - Cave: Flight from room 6 onward; Ice from room 20 onward; Fire from room 21 onward.
    - Temple: Fire 8+, Speed 13+, Ice 23+, Flight 28+, Shield on room 37.
    """
    n = _primary_room(room_part)
    if stage == "Fields":
        return "Fields"
    if stage == "Desert":
        return "Desert"
    if stage == "City":
        return "City Start" if n < 3 else "City Deep"
    if stage == "Forest":
        return "Forest Start" if n < 5 else "Forest Deep"
    if stage == "Mountain":
        if n < 5:
            return "Mountain Start"
        if n < 8:
            return "Mountain Mid"
        return "Mountain High"
    if stage == "Coast":
        if n < 6:
            return "Coast Start"
        if n < 14:
            return "Coast Mid"
        return "Coast End"
    if stage == "Cave":
        if n < 6:
            return "Cave Start"
        if n < 20:
            return "Cave Mid"
        if n < 21:
            return "Cave Deep"
        return "Cave End"
    if stage == "Temple":
        if n < 8:
            return "Temple Start"
        if n < 13:
            return "Temple Room 8+"
        if n < 23:
            return "Temple Room 13+"
        if n < 28:
            return "Temple Room 23+"
        if n < 37:
            return "Temple Room 28+"
        return "Temple Room 37"
    raise ValueError(f"Unknown stage {stage!r}")


def _load_shard_internal_order() -> tuple[str, ...]:
    # importlib.resources: works when the world is loaded from a .apworld zip
    # (Path(__file__).parent / "…" does not — those paths are not real files).
    text = resources.files(__package__).joinpath("shard_internal_order.txt").read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) != 211:
        raise RuntimeError(f"shard_internal_order.txt: expected 211 lines, got {len(lines)}")
    return tuple(lines)


def _room_bucket_from_match(m: re.Match[str]) -> str:
    return f"{m.group(1)}_room_{m.group(2)}"


def _pretty_room_label(bucket: str) -> str:
    """Fields_room_2 -> 'Fields room 2'; Desert_room_11B -> 'Desert room 11B'."""
    stage, rest = bucket.split("_room_", 1)
    return f"{stage} room {rest}"


def _is_crystal_fox_shard(internal_key: str) -> bool:
    return "oCrystalFox" in internal_key


def build_shard_tables(start_id: int = 77001) -> tuple[dict[str, int], dict[str, str]]:
    """
    Returns (name_to_id, name_to_region) for the 211 shard *locations*.

    Regular shards: "<Stage> room <n> shard #<k>" per room.
    Crystal Fox pickups: global "shard crystal fox #1", "#2", ... in file order
    (independent of room).

    Note: these names are now used only for *location* registration. The
    *item* a player receives from any shard location is the single
    FRAGMENT_ITEM_NAME / FRAGMENT_ITEM_ID pair declared above; see items.py
    and __init__.create_items.
    """
    global COAST_SHARD_FIRE_DISPLAYS, COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS
    COAST_SHARD_FIRE_DISPLAYS = set()
    COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS = set()

    order = _load_shard_internal_order()
    counts: dict[str, int] = defaultdict(int)
    fox_n = 0
    names_to_ids: dict[str, int] = {}
    name_to_region: dict[str, str] = {}

    for i, internal in enumerate(order):
        vid = start_id + i
        m = _SHARD_ROOM_RE.match(internal)
        if not m:
            raise ValueError(f"Cannot parse shard key: {internal!r}")
        stage = m.group(1)
        room_part = m.group(2)
        region = _shard_region(stage, room_part)

        if _is_crystal_fox_shard(internal):
            fox_n += 1
            display = f"shard crystal fox #{fox_n}"
        else:
            bucket = _room_bucket_from_match(m)
            counts[bucket] += 1
            display = f"{_pretty_room_label(bucket)} shard #{counts[bucket]}"

        names_to_ids[display] = vid
        name_to_region[display] = region

        if internal == _COAST_FIRE_INTERNAL:
            COAST_SHARD_FIRE_DISPLAYS.add(display)
        if internal == _COAST_DASH_FLIGHT_INTERNAL:
            COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS.add(display)

    return names_to_ids, name_to_region


def build_shard_display_table(start_id: int = 77001) -> dict[str, int]:
    """Backward-compatible: only the name->id map (used by items.py)."""
    return build_shard_tables(start_id)[0]


# Boss *location* names (checks). IDs unchanged for GameMaker compatibility.
BOSS_CLEAR_LOCATION_TABLE: dict[str, int] = {
    "Stage 1 clear - health": 77212,
    "Stage 2 clear - fire": 77213,
    "Stage 3 clear - speed": 77214,
    "Stage 4 clear - shield": 77215,
    "Stage 5 clear - ice": 77216,
    "Stage 6 clear - flight": 77217,
    "Stage 7 clear - power": 77218,
    "Stage 8 clear": 77219,
    "Final Boss": 77220,
}
