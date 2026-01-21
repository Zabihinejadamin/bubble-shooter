"""
Level 37 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level37(LevelBase):
    """Level 37 - Thirty-seventh level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 37
        self.name = "Level 37"

        # Game settings for Level 37
        self.grid_height = 13

        # Game state for Level 37
        self.max_shots = 1
        self.shots_remaining = 1

