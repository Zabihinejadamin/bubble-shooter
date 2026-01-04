"""
Level 15 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level15(LevelBase):
    """Level 15 - Fifteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 15
        self.name = "Level 15"
        
        # Game settings for Level 15
        self.grid_height = 13
        
        # Game state for Level 15
        self.max_shots = 13
        self.shots_remaining = 13

