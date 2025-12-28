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
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 12
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Shifted left by 50 (was 150)
        # grid_start_y is inherited from LevelBase (1015)
        
        # Game state for Level 1
        self.max_shots = 20  # Maximum number of bubbles to shoot
        self.shots_remaining = 20  # Remaining shots

