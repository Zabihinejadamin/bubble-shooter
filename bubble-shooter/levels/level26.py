"""
Level 26 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level26(LevelBase):
    """Level 26 - Twenty-sixth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 26
        self.name = "Level 26"

        # Game settings for Level 26
        self.grid_height = 13

        # Game state for Level 26
        self.max_shots = 2
        self.shots_remaining = 2
