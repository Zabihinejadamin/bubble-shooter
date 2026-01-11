"""
Level 40 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level40(LevelBase):
    """Level 40 - Fortieth and final level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 40
        self.name = "Level 40"

        # Game settings for Level 40
        self.grid_height = 13

        # Game state for Level 40
        self.max_shots = 1
        self.shots_remaining = 1
