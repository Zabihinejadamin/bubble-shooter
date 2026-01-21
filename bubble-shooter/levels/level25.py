"""
Level 25 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level25(LevelBase):
    """Level 25 - Twenty-fifth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 25
        self.name = "Level 25"

        # Game settings for Level 25
        self.grid_height = 13

        # Game state for Level 25
        self.max_shots = 3
        self.shots_remaining = 3

