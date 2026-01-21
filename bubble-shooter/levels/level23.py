"""
Level 23 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level23(LevelBase):
    """Level 23 - Twenty-third level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 23
        self.name = "Level 23"

        # Game settings for Level 23
        self.grid_height = 13

        # Game state for Level 23
        self.max_shots = 5
        self.shots_remaining = 5

