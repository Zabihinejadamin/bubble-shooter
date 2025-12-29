"""
Level 5 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level5(LevelBase):
    """Level 5 - Fifth level of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 5
        self.name = "Level 5"
        
        # Game settings for Level 5
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 17  # Even more rows for increased difficulty
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Same horizontal position as Level 1
        
        # Game state for Level 5
        self.max_shots = 15  # Even fewer shots for increased difficulty
        self.shots_remaining = 15
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 5
        Creates an hourglass/X pattern
        """
        # Hourglass pattern: wider at top and bottom, narrower in middle
        center_row = self.grid_height // 2
        
        # Calculate distance from center row
        distance_from_center = abs(row - center_row)
        
        # Calculate how many bubbles should be in this row
        # Top and bottom rows have more bubbles, middle has fewer
        # Create an hourglass shape
        if distance_from_center <= 2:
            # Middle rows: fewer bubbles (hourglass waist)
            bubbles_in_row = max(4, self.grid_width - 4)
        else:
            # Top and bottom rows: more bubbles
            bubbles_in_row = self.grid_width - (distance_from_center // 2)
        
        # Ensure minimum bubbles
        bubbles_in_row = max(3, min(bubbles_in_row, self.grid_width))
        
        # Calculate starting column to center the pattern
        start_col = (self.grid_width - bubbles_in_row) // 2
        
        # Check if column is within the hourglass shape for this row
        return start_col <= col < start_col + bubbles_in_row

