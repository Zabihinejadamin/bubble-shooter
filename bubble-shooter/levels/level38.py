"""
Level 38 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level38(LevelBase):
    """Level 38 - Thirty-eighth level of the game"""

    def __init__(self):
        super().__init__()

        self.level_number = 38
        self.name = "Level 38"

        # Game settings for Level 38
        self.grid_height = 13

        # Game state for Level 38
        self.max_shots = 1
        self.shots_remaining = 1

