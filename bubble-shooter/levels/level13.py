"""
Level 13 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level13(LevelBase):
    """Level 13 - Thirteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 13
        self.name = "Level 13"
        
        # Game settings for Level 13
        self.grid_height = 13
        
        # Game state for Level 13
        self.max_shots = 15
        self.shots_remaining = 15

