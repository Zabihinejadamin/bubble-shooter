"""
Level 24 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level24(LevelBase):
    """Level 24 - Twenty-fourth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 24
        self.name = "Level 24"

        # Game settings for Level 24
        self.grid_height = 13

        # Game state for Level 24
        self.max_shots = 4
        self.shots_remaining = 4
