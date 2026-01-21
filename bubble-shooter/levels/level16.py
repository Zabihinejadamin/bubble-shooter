"""
Level 16 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level16(LevelBase):
    """Level 16 - Sixteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 16
        self.name = "Level 16"
        
        # Game settings for Level 16
        self.grid_height = 13
        
        # Game state for Level 16
        self.max_shots = 12
        self.shots_remaining = 12


