"""
Level 36 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level36(LevelBase):
    """Level 36 - Thirty-sixth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 36
        self.name = "Level 36"

        # Game settings for Level 36
        self.grid_height = 13

        # Game state for Level 36
        self.max_shots = 1
        self.shots_remaining = 1
