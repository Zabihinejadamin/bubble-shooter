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
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 16  # More rows for increased difficulty
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Same horizontal position as Level 1
        
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

