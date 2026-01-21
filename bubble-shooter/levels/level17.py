"""
Level 17 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level17(LevelBase):
    """Level 17 - Seventeenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 17
        self.name = "Level 17"
        
        # Game settings for Level 17
        self.grid_height = 13
        
        # Game state for Level 17
        self.max_shots = 11
        self.shots_remaining = 11


