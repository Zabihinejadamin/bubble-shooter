"""
Level 19 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level19(LevelBase):
    """Level 19 - Nineteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 19
        self.name = "Level 19"
        
        # Game settings for Level 19
        self.grid_height = 13
        
        # Game state for Level 19
        self.max_shots = 9
        self.shots_remaining = 9

