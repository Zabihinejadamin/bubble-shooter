"""
Level 30 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level30(LevelBase):
    """Level 30 - Thirtieth and final level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 30
        self.name = "Level 30"

        # Game settings for Level 30
        self.grid_height = 13

        # Game state for Level 30
        self.max_shots = 1
        self.shots_remaining = 1
