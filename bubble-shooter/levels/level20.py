"""
Level 20 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level20(LevelBase):
    """Level 20 - Twentieth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 20
        self.name = "Level 20"
        
        # Game settings for Level 20
        self.grid_height = 13
        
        # Game state for Level 20
        self.max_shots = 8
        self.shots_remaining = 8


