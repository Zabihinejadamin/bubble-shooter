"""
Level 28 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level28(LevelBase):
    """Level 28 - Twenty-eighth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 28
        self.name = "Level 28"

        # Game settings for Level 28
        self.grid_height = 13

        # Game state for Level 28
        self.max_shots = 1
        self.shots_remaining = 1
