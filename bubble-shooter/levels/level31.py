"""
Level 31 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level31(LevelBase):
    """Level 31 - Thirty-first level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 31
        self.name = "Level 31"

        # Game settings for Level 31
        self.grid_height = 13

        # Game state for Level 31
        self.max_shots = 1
        self.shots_remaining = 1
