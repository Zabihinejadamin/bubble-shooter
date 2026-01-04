"""
Level 18 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level18(LevelBase):
    """Level 18 - Eighteenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 18
        self.name = "Level 18"
        
        # Game settings for Level 18
        self.grid_height = 13
        
        # Game state for Level 18
        self.max_shots = 10
        self.shots_remaining = 10

