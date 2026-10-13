from worlds.AutoWorld import World, WebWorld
from BaseClasses import ItemClassification, Tutorial

from .items import PrismaRoadItem, item_table
from .locations import PrismaRoadLocation, location_table
from .naming import (
    BOSS_CLEAR_LOCATION_TABLE,
    FRAGMENT_ITEM_NAME,
    SHARD_LOCATION_COUNT,
)
from .options import PrismaRoadOptions
from .rules import set_rules
from .regions import create_regions


# Items granted by beating a stage's boss. Stage 1-8 items are shuffled
# into the pool; "Victory" is locked on the Final Boss location.
ABILITY_ITEMS = {"Health", "Fire", "Speed", "Shield", "Ice", "Flight", "Power"}
STAGE_8_ITEM = "Stage 8 Clear"
GOAL_ITEM_NAME = "Victory"
GOAL_LOCATION_NAME = "Final Boss"

# Items used as logic gates in rules.py. These MUST be classified as
# progression so the collection state tracks them.
PROGRESSION_ABILITIES = {"Fire", "Speed", "Shield", "Ice", "Flight"}

# Stage prefixes used to bucket shard locations into per-stage groups for the
# tracker. Each shard location's display name starts with one of these tokens
# (see naming.py: "Fields room 2 shard #1", "Mountain room 5B shard #1", etc.).
# Crystal Fox shards live in their own bucket because their names don't start
# with a stage prefix ("shard crystal fox #1" ...).
_SHARD_STAGE_PREFIXES = (
    "Fields", "Desert", "City", "Forest", "Mountain", "Coast", "Cave", "Temple",
)

_BOSS_CLEAR_LOCATIONS = frozenset(BOSS_CLEAR_LOCATION_TABLE.keys())
_ALL_SHARD_LOCATIONS = frozenset(
    name for name in location_table if name not in _BOSS_CLEAR_LOCATIONS
)


class PrismaRoadWeb(WebWorld):
    tutorials = [Tutorial(
        "Prisma Road Setup Guide",
        "A guide to setting up the Prisma Road randomizer.",
        "English",
        "setup_en.md",
        "setup/en",
        ["YourName"],
    )]


class PrismaRoadWorld(World):
    """
    Prisma Road es un juego de plataformas y accion donde exploras diversos
    stages desbloqueando poderes y recolectando fragmentos de prisma.
    """
    game = "Prisma Road"
    web = PrismaRoadWeb()

    options_dataclass = PrismaRoadOptions
    options: PrismaRoadOptions

    item_name_to_id = item_table
    location_name_to_id = location_table

    # Only one shard item now (FRAGMENT_ITEM_NAME). The rules logic uses
    # `state.count_group("Shards", player)`, which counts every copy of every
    # name in this set the player owns — so a single-name group still totals
    # all 211 Fragment copies the world generates.
    item_name_groups = {
        "Shards": {FRAGMENT_ITEM_NAME},
    }

    # location_name_groups is what the Archipelago tracker / web room page
    # uses to render the "Group: X / Y" summary lines. Without this, every
    # shard is a separate row and players have to count them by hand to see
    # how far along they are. We expose:
    #   * "Shards"             -> all 211 shard locations rolled up
    #   * "<Stage> Shards"     -> per-stage subtotal so progress within a
    #                             single area is visible at a glance
    #   * "Crystal Fox Shards" -> the handful of pickups whose display names
    #                             don't follow the "<Stage> room ..." pattern
    #   * "Boss Clears"        -> the 9 stage-clear / Final Boss checks
    location_name_groups = {
        "Shards": set(_ALL_SHARD_LOCATIONS),
        "Crystal Fox Shards": {
            name for name in _ALL_SHARD_LOCATIONS if name.startswith("shard crystal fox")
        },
        "Boss Clears": set(_BOSS_CLEAR_LOCATIONS),
        **{
            f"{stage} Shards": {
                name for name in _ALL_SHARD_LOCATIONS if name.startswith(f"{stage} ")
            }
            for stage in _SHARD_STAGE_PREFIXES
        },
    }

    def create_regions(self):
        create_regions(self.multiworld, self.player)

        # The goal item is locked on the final boss location: beating the
        # boss is the only way to obtain it.
        goal_item = PrismaRoadItem(
            GOAL_ITEM_NAME,
            ItemClassification.progression,
            item_table[GOAL_ITEM_NAME],
            self.player,
        )
        self.multiworld.get_location(GOAL_LOCATION_NAME, self.player).place_locked_item(goal_item)

    def create_items(self):
        item_pool = []

        # Abilities + the dummy Stage 8 item. The Victory item is locked on
        # the Final Boss location in create_regions and is intentionally NOT
        # added to the pool here.
        for name, code in item_table.items():
            if name == GOAL_ITEM_NAME:
                continue
            if name == FRAGMENT_ITEM_NAME:
                # Handled in the bulk-add below; only one row in item_table
                # but SHARD_LOCATION_COUNT copies in the pool.
                continue

            if name in PROGRESSION_ABILITIES:
                classification = ItemClassification.progression
            elif name in ABILITY_ITEMS or name == STAGE_8_ITEM:
                # Abilities that no rule references (Health, Power) and the
                # dummy Stage 8 item. Still nice to find; not required.
                classification = ItemClassification.useful
            else:
                classification = ItemClassification.useful

            item_pool.append(PrismaRoadItem(name, classification, code, self.player))

        # Shards: a single AP item type (Fragment) multiplied to fill every
        # shard *location*. Each copy is its own Item instance with the same
        # name+id, which is what makes `state.count_group("Shards", ...)`
        # return the player's running shard total in rules.py and what makes
        # the AP web tracker show one collapsed "Fragment N / M" row.
        #
        # `progression_skip_balancing` keeps each copy progression-relevant
        # (so the generator places enough of them in reachable spots for the
        # final boss gate) without forcing the progression balancer to thread
        # 211 individually-tagged items.
        for _ in range(SHARD_LOCATION_COUNT):
            item_pool.append(
                PrismaRoadItem(
                    FRAGMENT_ITEM_NAME,
                    ItemClassification.progression_skip_balancing,
                    item_table[FRAGMENT_ITEM_NAME],
                    self.player,
                )
            )

        self.multiworld.itempool += item_pool

    def set_rules(self):
        set_rules(self.multiworld, self.player, self.options.shards_required.value)

    def fill_slot_data(self) -> dict:
        """Data sent to the GameMaker client on connect."""
        return {
            "shards_required": self.options.shards_required.value,
            "death_link": self.options.death_link.value,
        }
