from BaseClasses import Region, Entrance

from .items import shard_location_regions
from .locations import location_table, PrismaRoadLocation


def create_regions(multiworld, player):
    # 1. Menu = central hub.
    menu = Region("Menu", player, multiworld)
    multiworld.regions.append(menu)

    # 2. Stage sub-regions.
    stage_map = {
        "Fields": ["Fields"],
        "Desert": ["Desert"],
        "City": ["City Start", "City Deep"],
        "Forest": ["Forest Start", "Forest Deep"],
        "Mountain": ["Mountain Start", "Mountain Mid", "Mountain High"],
        "Coast": ["Coast Start", "Coast Mid", "Coast End"],
        "Cave": ["Cave Start", "Cave Mid", "Cave Deep", "Cave End"],
        "Temple": [
            "Temple Start",
            "Temple Room 8+",
            "Temple Room 13+",
            "Temple Room 23+",
            "Temple Room 28+",
            "Temple Room 37",
            "Temple Boss Zone",
        ],
    }

    regions_dict = {}
    for sub_regions in stage_map.values():
        for sub_name in sub_regions:
            new_reg = Region(sub_name, player, multiworld)
            regions_dict[sub_name] = new_reg
            multiworld.regions.append(new_reg)

    # 3. Auto-assign shard locations to their main region (display names:
    #    "Fields room 2 shard #1", etc.).
    boss_clear_locations = frozenset(
        {
            "Stage 1 clear - health",
            "Stage 2 clear - fire",
            "Stage 3 clear - speed",
            "Stage 4 clear - shield",
            "Stage 5 clear - ice",
            "Stage 6 clear - flight",
            "Stage 7 clear - power",
            "Stage 8 clear",
            "Final Boss",
        }
    )

    for loc_name, loc_id in location_table.items():
        if loc_name in boss_clear_locations:
            continue
        region_name = shard_location_regions[loc_name]
        region = regions_dict[region_name]
        region.locations.append(
            PrismaRoadLocation(player, loc_name, loc_id, region)
        )

    # 4. Boss clear locations, one per stage, in the region where that
    #    stage's boss actually is. Adjust these if your layout changes.
    clear_location_region = {
        "Stage 1 clear - health": "Fields",
        "Stage 2 clear - fire": "Desert",
        "Stage 3 clear - speed": "City Deep",
        "Stage 4 clear - shield": "Forest Deep",
        "Stage 5 clear - ice": "Mountain High",
        "Stage 6 clear - flight": "Coast End",
        "Stage 7 clear - power": "Cave End",
        "Stage 8 clear": "Temple Room 37",
        "Final Boss": "Temple Boss Zone",
    }
    for clear_name, region_name in clear_location_region.items():
        region = regions_dict[region_name]
        region.locations.append(
            PrismaRoadLocation(player, clear_name, location_table[clear_name], region)
        )

    # 5. Entrances (the "doors" rules.py gates).
    def connect(source, target, name):
        entrance = Entrance(player, name, source)
        source.exits.append(entrance)
        entrance.connect(target)

    # From Menu to each stage.
    connect(menu, regions_dict["Fields"], "Menu -> Fields")
    connect(menu, regions_dict["Desert"], "Menu -> Desert")
    connect(menu, regions_dict["City Start"], "Menu -> City")
    connect(menu, regions_dict["Forest Start"], "Menu -> Forest")
    connect(menu, regions_dict["Mountain Start"], "Menu -> Mountain")
    connect(menu, regions_dict["Coast Start"], "Menu -> Coast")
    connect(menu, regions_dict["Cave Start"], "Menu -> Cave")
    connect(menu, regions_dict["Temple Start"], "Menu -> Temple")

    # Internal stage connections.
    connect(regions_dict["City Start"], regions_dict["City Deep"], "City -> City Deep")
    connect(regions_dict["Forest Start"], regions_dict["Forest Deep"], "Forest -> Forest Deep")

    connect(regions_dict["Mountain Start"], regions_dict["Mountain Mid"], "Mountain -> Mountain Mid")
    connect(regions_dict["Mountain Mid"], regions_dict["Mountain High"], "Mountain -> Mountain High")

    connect(regions_dict["Coast Start"], regions_dict["Coast Mid"], "Coast -> Coast Area 2")
    connect(regions_dict["Coast Mid"], regions_dict["Coast End"], "Coast -> Coast Area 3")

    connect(regions_dict["Cave Start"], regions_dict["Cave Mid"], "Cave -> Cave Middle")
    connect(regions_dict["Cave Mid"], regions_dict["Cave Deep"], "Cave -> Cave Deep")
    connect(regions_dict["Cave Deep"], regions_dict["Cave End"], "Cave -> Cave End")

    # Temple path.
    connect(regions_dict["Temple Start"], regions_dict["Temple Room 8+"], "Temple -> Room 8+")
    connect(regions_dict["Temple Room 8+"], regions_dict["Temple Room 13+"], "Temple -> Room 13+")
    connect(regions_dict["Temple Room 13+"], regions_dict["Temple Room 23+"], "Temple -> Room 23+")
    connect(regions_dict["Temple Room 23+"], regions_dict["Temple Room 28+"], "Temple -> Room 28+")
    connect(regions_dict["Temple Room 28+"], regions_dict["Temple Room 37"], "Temple -> Room 37")
    connect(regions_dict["Temple Room 28+"], regions_dict["Temple Boss Zone"], "Temple -> Boss Access")
