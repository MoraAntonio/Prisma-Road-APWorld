from dataclasses import dataclass

from Options import DeathLink, PerGameCommonOptions, Range


class ShardsRequired(Range):
    """Number of Prisma shards required to defeat the final boss."""
    display_name = "Shards Required"
    range_start = 0
    range_end = 211
    default = 100


@dataclass
class PrismaRoadOptions(PerGameCommonOptions):
    shards_required: ShardsRequired
    death_link: DeathLink
