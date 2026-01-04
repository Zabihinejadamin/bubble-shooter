"""
Level 8 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level8(LevelBase):
    """Level 8 - Eighth level of the game (antique blue background, opaque bubbles)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 8
        self.name = "Level 8"
        
        # Game settings for Level 8
        # bubble_radius, grid_spacing, grid_start_x, grid_start_y are inherited from LevelBase (scaled for 1080x2424)
        self.grid_height = 13  # Maximum allowed rows
        
        # Game state for Level 8
        self.max_shots = 12  # Fewer shots for increased difficulty
        self.shots_remaining = 12
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 8
        Creates a staircase pattern where each row has bubbles connected to the row above
        """
        # Staircase pattern: bubbles form steps going down
        # Each row has bubbles, but they shift position to create a staircase effect
        # Ensure every row has bubbles and they connect to the row above
        
        # Calculate shift based on row (creates diagonal staircase)
        # Shift alternates to create a staircase that ensures connectivity
        shift = (row // 2) % (self.grid_width // 2)
        
        # Calculate how many bubbles should be in this row
        # Ensure at least 7 bubbles per row for good connectivity
        min_bubbles = 7
        max_bubbles = self.grid_width
        bubbles_in_row = max(min_bubbles, max_bubbles - (row // 4))
        
        # Calculate starting column with shift
        # Ensure the pattern overlaps with previous row for connectivity
        start_col = shift
        
        # Ensure we don't go out of bounds
        if start_col + bubbles_in_row > self.grid_width:
            start_col = self.grid_width - bubbles_in_row
        
        # Ensure start_col is non-negative
        start_col = max(0, start_col)
        
        # Check if column is within the staircase for this row
        return start_col <= col < start_col + bubbles_in_row

