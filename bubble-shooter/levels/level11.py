"""
Level 11 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level11(LevelBase):
    """Level 11 - Eleventh level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 11
        self.name = "Level 11"
        
        # Game settings for Level 11
        self.grid_height = 13
        
        # Game state for Level 11
        self.max_shots = 17
        self.shots_remaining = 17

