"""
Level 27 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level27(LevelBase):
    """Level 27 - Twenty-seventh level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 27
        self.name = "Level 27"

        # Game settings for Level 27
        self.grid_height = 13

        # Game state for Level 27
        self.max_shots = 1
        self.shots_remaining = 1

