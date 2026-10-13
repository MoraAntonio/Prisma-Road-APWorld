from BaseClasses import Location

from .naming import BOSS_CLEAR_LOCATION_TABLE, build_shard_tables


class PrismaRoadLocation(Location):
    game: str = "Prisma Road"

    def __init__(self, player, name, code, region):
        super().__init__(player, name, code, region)


# Locations remain individually named (one per shard pickup) so each check is
# distinct on the server. Items, by contrast, are collapsed into a single
# generic Fragment in items.py — see naming.FRAGMENT_ITEM_NAME.
_shard_locations, _shard_regions = build_shard_tables()

location_table = {**_shard_locations, **BOSS_CLEAR_LOCATION_TABLE}
