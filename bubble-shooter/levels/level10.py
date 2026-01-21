"""
Level 10 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level10(LevelBase):
    """Level 10 - Tenth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 10
        self.name = "Level 10"
        
        # Game settings for Level 10
        # bubble_radius, grid_spacing, grid_start_x, grid_start_y are inherited from LevelBase (scaled for 1080x2424)
        self.grid_height = 13  # Maximum allowed rows
        
        # Game state for Level 10
        self.max_shots = 18
        self.shots_remaining = 18


