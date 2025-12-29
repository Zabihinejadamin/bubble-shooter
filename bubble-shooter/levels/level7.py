"""
Level 7 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level7(LevelBase):
    """Level 7 - Seventh level of the game (antique blue background, opaque bubbles)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 7
        self.name = "Level 7"
        
        # Game settings for Level 7
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 19  # More rows for increased difficulty
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Same horizontal position as Level 1
        
        # Game state for Level 7
        self.max_shots = 13  # Fewer shots for increased difficulty
        self.shots_remaining = 13
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 7
        Creates a cross/X pattern
        """
        # Cross pattern: bubbles form a cross shape
        center_col = self.grid_width // 2
        center_row = self.grid_height // 2
        
        # Check if bubble is on the vertical line (center column)
        on_vertical = abs(col - center_col) <= 1
        
        # Check if bubble is on the horizontal line (center row)
        on_horizontal = abs(row - center_row) <= 1
        
        # Allow bubbles that are on either the vertical or horizontal line
        return on_vertical or on_horizontal

