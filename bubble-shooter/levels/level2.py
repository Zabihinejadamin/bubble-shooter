"""
Level 2 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level2(LevelBase):
    """Level 2 - Second level of the game (more challenging)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 2
        self.name = "Level 2"
        
        # Game settings for Level 2 - more challenging
        # bubble_radius, grid_spacing, grid_start_x, grid_start_y are inherited from LevelBase (scaled for 1080x2424)
        self.grid_height = 13  # Maximum allowed rows
        
        # Game state for Level 2 - same shots as Level 1
        self.max_shots = 20
        self.shots_remaining = 20
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 2
        Creates a diamond/pyramid shape pattern
        """
        # Diamond pattern: widest in the middle, narrower at top and bottom
        center_row = self.grid_height // 2
        
        # Calculate distance from center row
        distance_from_center = abs(row - center_row)
        
        # Calculate how many bubbles should be in this row
        # Center row has the most bubbles, edges have fewer
        # Start with full width, reduce by 1 for each row away from center
        max_bubbles = self.grid_width
        bubbles_in_row = max(3, max_bubbles - distance_from_center)
        
        # Calculate starting column to center the pattern
        start_col = (self.grid_width - bubbles_in_row) // 2
        
        # Check if column is within the diamond shape for this row
        return start_col <= col < start_col + bubbles_in_row
