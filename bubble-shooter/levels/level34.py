"""
Level 34 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level34(LevelBase):
    """Level 34 - Thirty-fourth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 34
        self.name = "Level 34"

        # Game settings for Level 34
        self.grid_height = 13

        # Game state for Level 34
        self.max_shots = 1
        self.shots_remaining = 1
