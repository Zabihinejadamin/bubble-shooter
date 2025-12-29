"""
Level 3 configuration for Bubble Shooter game
"""

from .level_base import LevelBase


class Level3(LevelBase):
    """Level 3 - Third level of the game (introduces mines)"""
    
    def __init__(self):
        super().__init__()
        
        self.level_number = 3
        self.name = "Level 3"
        
        # Game settings for Level 3
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 15  # More rows for increased difficulty
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 100  # Same horizontal position as Level 1
        
        # Game state for Level 3
        self.max_shots = 18  # Slightly fewer shots than Level 1
        self.shots_remaining = 18
    
    def should_place_bubble(self, row, col):
        """
        Define custom bubble pattern for Level 3
        Creates a wave/zigzag pattern
        """
        # Wave pattern: bubbles form a wave that goes up and down
        # Each row alternates between having bubbles on left/right side
        
        # Calculate wave phase (0 to 1)
        wave_phase = (row % 4) / 4.0  # 4-row cycle
        
        # Determine which side of the grid should have bubbles
        if wave_phase < 0.25:
            # First quarter: left side
            return col < self.grid_width * 0.6
        elif wave_phase < 0.5:
            # Second quarter: center
            return self.grid_width * 0.2 <= col < self.grid_width * 0.8
        elif wave_phase < 0.75:
            # Third quarter: right side
            return col >= self.grid_width * 0.4
        else:
            # Fourth quarter: full width (top of wave)
            return True

