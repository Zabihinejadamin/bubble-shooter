"""
Level 9 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level9(LevelBase):
    """Level 9 - Ninth level of the game (antique blue background, opaque bubbles)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 9
        self.name = "Level 9"
        
        # Game settings for Level 9
        # bubble_radius, grid_spacing, grid_start_x, grid_start_y are inherited from LevelBase (scaled for 1080x2424)
        self.grid_height = 13  # Maximum allowed rows
        
        # Game state for Level 9
        self.max_shots = 11  # Fewest shots for maximum difficulty
        self.shots_remaining = 11
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 9
        Creates a complex maze-like pattern where each row has bubbles connected to the row above
        """
        # Maze pattern: alternating patterns but ensuring every row has bubbles
        # Creates a complex pattern that's challenging to clear
        
        # Pattern type based on row
        pattern_type = row % 4
        
        if pattern_type == 0:
            # Every fourth row: full row
            return True
        elif pattern_type == 1:
            # Second row: left side and center (ensures connectivity)
            return col < self.grid_width * 0.6 or (self.grid_width // 2 - 1 <= col < self.grid_width // 2 + 2)
        elif pattern_type == 2:
            # Third row: right side and center (ensures connectivity)
            return col >= self.grid_width * 0.4 or (self.grid_width // 2 - 1 <= col < self.grid_width // 2 + 2)
        else:
            # Fourth row: edges and center (ensures connectivity)
            return col < 3 or col >= self.grid_width - 3 or (self.grid_width // 2 - 2 <= col < self.grid_width // 2 + 2)

