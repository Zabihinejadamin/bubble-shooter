"""
Level 32 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level32(LevelBase):
    """Level 32 - Thirty-second level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 32
        self.name = "Level 32"

        # Game settings for Level 32
        self.grid_height = 13

        # Game state for Level 32
        self.max_shots = 1
        self.shots_remaining = 1

