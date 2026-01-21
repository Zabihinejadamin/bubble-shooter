"""
Level 33 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level33(LevelBase):
    """Level 33 - Thirty-third level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 33
        self.name = "Level 33"

        # Game settings for Level 33
        self.grid_height = 13

        # Game state for Level 33
        self.max_shots = 1
        self.shots_remaining = 1

