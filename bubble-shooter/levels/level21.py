"""
Level 21 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level21(LevelBase):
    """Level 21 - Twenty-first level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 21
        self.name = "Level 21"

        # Game settings for Level 21
        self.grid_height = 13

        # Game state for Level 21
        self.max_shots = 7
        self.shots_remaining = 7
