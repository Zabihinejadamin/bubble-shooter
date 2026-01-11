"""
Level 35 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level35(LevelBase):
    """Level 35 - Thirty-fifth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 35
        self.name = "Level 35"

        # Game settings for Level 35
        self.grid_height = 13

        # Game state for Level 35
        self.max_shots = 1
        self.shots_remaining = 1
