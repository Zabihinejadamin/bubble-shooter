"""
Level 6 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level6(LevelBase):
    """Level 6 - Sixth level of the game (antique blue background, opaque bubbles)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 6
        self.name = "Level 6"
        
        # Game settings for Level 6
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 18  # More rows for increased difficulty
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Same horizontal position as Level 1
        
        # Game state for Level 6
        self.max_shots = 14  # Fewer shots for increased difficulty
        self.shots_remaining = 14
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 6
        Creates a spiral pattern
        """
        # Spiral pattern: bubbles form a spiral from center
        center_col = self.grid_width // 2
        center_row = self.grid_height // 2
        
        # Calculate distance from center
        row_dist = abs(row - center_row)
        col_dist = abs(col - center_col)
        
        # For odd rows, adjust column offset
        if row % 2 == 1:
            adjusted_col = col - 0.5
            col_dist = abs(adjusted_col - center_col)
        
        # Spiral pattern: allow bubbles in a spiral shape
        # Create a diamond that rotates
        max_dist = max(row_dist, col_dist)
        
        # Spiral effect: alternate between allowing and blocking
        spiral_phase = (row_dist + col_dist) % 3
        
        if spiral_phase == 0:
            # Allow bubbles within certain distance
            return max_dist <= min(center_row, center_col) + 2
        elif spiral_phase == 1:
            # Allow bubbles in middle range
            return 2 <= max_dist <= min(center_row, center_col) + 1
        else:
            # Allow bubbles in outer range
            return max_dist >= min(center_row, center_col) - 1

