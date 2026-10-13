from BaseClasses import Item

from .naming import (
    FRAGMENT_ITEM_ID,
    FRAGMENT_ITEM_NAME,
    SHARD_LOCATION_COUNT,
    build_shard_tables,
)


class PrismaRoadItem(Item):
    game: str = "Prisma Road"

    def __init__(self, name, classification, code, player):
        super().__init__(name, classification, code, player)


# Shard *location* metadata only — the regions table feeds regions.py so each
# of the 211 shard locations gets attached to the correct sub-region for logic.
# The AP item every shard delivers is the single FRAGMENT_ITEM_NAME row in
# `item_table`; see __init__.create_items, which adds SHARD_LOCATION_COUNT
# copies of it to the pool.
_shard_locations, shard_location_regions = build_shard_tables()
assert len(_shard_locations) == SHARD_LOCATION_COUNT, (
    f"shard_internal_order.txt and SHARD_LOCATION_COUNT disagree: "
    f"{len(_shard_locations)} vs {SHARD_LOCATION_COUNT}"
)

# Boss drops (abilities). Stage 8 has no ability; "Victory" is the goal item.
_ability_items = {
    "Health": 77212,
    "Fire": 77213,
    "Speed": 77214,
    "Shield": 77215,
    "Ice": 77216,
    "Flight": 77217,
    "Power": 77218,
    "Stage 8 Clear": 77219,
    "Victory": 77220,
}

# `item_table` is what `PrismaRoadWorld.item_name_to_id` exposes to Archipelago.
# It only declares ONE shard item (Fragment); the item pool will hold many
# copies of that one item, which is what makes the room page collapse all
# fragments into one "Fragment N / M" row.
item_table = {FRAGMENT_ITEM_NAME: FRAGMENT_ITEM_ID, **_ability_items}
