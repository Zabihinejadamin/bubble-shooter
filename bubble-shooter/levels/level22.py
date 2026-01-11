"""
Level 22 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level22(LevelBase):
    """Level 22 - Twenty-second level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 22
        self.name = "Level 22"

        # Game settings for Level 22
        self.grid_height = 13

        # Game state for Level 22
        self.max_shots = 6
        self.shots_remaining = 6
