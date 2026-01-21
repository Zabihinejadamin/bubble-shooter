"""
Level 29 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level29(LevelBase):
    """Level 29 - Twenty-ninth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 29
        self.name = "Level 29"

        # Game settings for Level 29
        self.grid_height = 13

        # Game state for Level 29
        self.max_shots = 1
        self.shots_remaining = 1

