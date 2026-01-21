"""
Level 12 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level12(LevelBase):
    """Level 12 - Twelfth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 12
        self.name = "Level 12"
        
        # Game settings for Level 12
        self.grid_height = 13
        
        # Game state for Level 12
        self.max_shots = 16
        self.shots_remaining = 16


