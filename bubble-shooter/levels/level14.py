"""
Level 14 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level14(LevelBase):
    """Level 14 - Fourteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 14
        self.name = "Level 14"
        
        # Game settings for Level 14
        self.grid_height = 13
        
        # Game state for Level 14
        self.max_shots = 14
        self.shots_remaining = 14

