from BaseClasses import MultiWorld
from worlds.generic.Rules import add_rule

from .naming import COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS, COAST_SHARD_FIRE_DISPLAYS


def set_rules(world: MultiWorld, player: int, shards_needed: int):
    # =========================================================================
    # 1. Access rules for stages (entrances from Menu).
    # =========================================================================
    # City: first rooms are open; Fire is required only past City Start (see
    # "City -> City Deep" below), matching "fire from room 3 onward".
    add_rule(world.get_entrance("Menu -> Forest", player),
             lambda state: state.has("Speed", player))
    add_rule(world.get_entrance("Menu -> Coast", player),
             lambda state: state.has("Ice", player))
    # Temple: no ability required to enter; room 8+ onward is gated internally.

    # =========================================================================
    # 2. Internal sub-region logic.
    # =========================================================================
    add_rule(world.get_entrance("City -> City Deep", player),
             lambda state: state.has("Fire", player))

    add_rule(world.get_entrance("Forest -> Forest Deep", player),
             lambda state: state.has("Fire", player))

    add_rule(world.get_entrance("Mountain -> Mountain Mid", player),
             lambda state: state.has("Speed", player))
    add_rule(world.get_entrance("Mountain -> Mountain High", player),
             lambda state: state.has("Fire", player))

    add_rule(world.get_entrance("Coast -> Coast Area 2", player),
             lambda state: state.has("Fire", player))
    add_rule(world.get_entrance("Coast -> Coast Area 3", player),
             lambda state: state.has("Speed", player))

    add_rule(world.get_entrance("Cave -> Cave Middle", player),
             lambda state: state.has("Flight", player))
    add_rule(world.get_entrance("Cave -> Cave Deep", player),
             lambda state: state.has("Ice", player))
    add_rule(world.get_entrance("Cave -> Cave End", player),
             lambda state: state.has("Fire", player))

    add_rule(world.get_entrance("Temple -> Room 8+", player),
             lambda state: state.has("Fire", player))
    add_rule(world.get_entrance("Temple -> Room 13+", player),
             lambda state: state.has("Speed", player))
    add_rule(world.get_entrance("Temple -> Room 23+", player),
             lambda state: state.has("Ice", player))
    add_rule(world.get_entrance("Temple -> Room 28+", player),
             lambda state: state.has("Flight", player))
    add_rule(world.get_entrance("Temple -> Room 37", player),
             lambda state: state.has("Shield", player))

    # Coast: one early shard still needs Fire; another needs Speed or Flight
    # even when the surrounding sub-region is otherwise reachable.
    for loc_name in COAST_SHARD_FIRE_DISPLAYS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, pl=player: state.has("Fire", pl),
        )
    for loc_name in COAST_SHARD_DASH_OR_FLIGHT_DISPLAYS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, pl=player: state.has("Speed", pl) or state.has("Flight", pl),
        )

    # =========================================================================
    # 3. Final boss (Stage 9) condition.
    # =========================================================================
    add_rule(
        world.get_location("Final Boss", player),
        lambda state: state.count_group("Shards", player) >= shards_needed,
    )

    # Official victory condition: you have collected the Victory item
    # (locked on the Final Boss location, so you must actually beat it).
    world.completion_condition[player] = lambda state: state.has("Victory", player)
