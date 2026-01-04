"""
Level 4 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level4(LevelBase):
    """Level 4 - Fourth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 4
        self.name = "Level 4"
        
        # Game settings for Level 4
        # bubble_radius, grid_spacing, grid_start_x, grid_start_y are inherited from LevelBase (scaled for 1080x2424)
        self.grid_height = 13  # Maximum allowed rows
        
        # Game state for Level 4
        self.max_shots = 16  # Fewer shots for increased difficulty
        self.shots_remaining = 16
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 4
        Creates a checkerboard/striped pattern
        """
        # Checkerboard pattern: alternate between having bubbles and empty spaces
        # Creates a diagonal stripe effect
        
        # Calculate pattern based on row and column
        pattern_type = (row + col) % 3
        
        # Pattern 0: full row
        # Pattern 1: left half
        # Pattern 2: right half
        if pattern_type == 0:
            # Full row
            return True
        elif pattern_type == 1:
            # Left half
            return col < self.grid_width // 2
        else:
            # Right half
            return col >= self.grid_width // 2

