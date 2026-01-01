"""
Level 1 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level1(LevelBase):
    """Level 1 - First level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 1
        self.name = "Level 1"
        
        # Game settings for Level 1
        # All values (bubble_radius, grid_spacing, grid_start_x, grid_start_y) 
        # are inherited from LevelBase (already scaled for 1080x2424)
        # No need to override - use base values
        # (grid_start_x = -600, grid_start_y = 915)
        
        # Game state for Level 1
        self.max_shots = 20  # Maximum number of bubbles to shoot
        self.shots_remaining = 20  # Remaining shots

