"""
Base class for game levels

To create a new level:
1. Create a new file: levels/levelN.py (where N is the level number)
2. Import LevelBase: from .level_base import LevelBase
3. Create a class LevelN(LevelBase) and override __init__ to set level-specific values
4. Update levels/__init__.py to export your new level class
5. Update main.py to import and use your new level

Example:
    class Level2(LevelBase):
        def __init__(self):
            super().__init__()
            self.level_number = 2
            self.name = "Level 2"
            self.max_shots = 15  # Harder level with fewer shots
            self.grid_height = 15  # More rows
"""


class LevelBase:
    """Base class that all levels must inherit from"""
    
    def __init__(self):
        """Initialize level configuration"""
        self.level_number = 1
        self.name = "Level 1"
        
        # Game settings (base resolution: 1080x2424)
        # Scaled from original 360x640 design
        # Scale factors: width 1080/360=3.0, height 2424/640=3.7875
        self.bubble_radius = 60  # 20 * 3.0
        self.grid_width = 10
        self.grid_height = 12
        self.grid_spacing = 122  # Reduced for minimal gap between balls (minimum will be enforced to radius * 2.05 ≈ 123)
        self.grid_start_x = 300  # 100 * 3.0
        # grid_start_y positioned to minimize top margin (top bubble edge ~30px from top)
        # Top bubble center at grid_start_y, edge at grid_start_y + radius
        # For 2424 height: 2424 - 30 - 60 = 2334
        self.grid_start_y = 2334  # Minimized top margin (~30px from top of screen)
        
        # Game state
        self.max_shots = 20
        self.shots_remaining = 20
        
    def get_config(self):
        """Return level configuration as a dictionary"""
        return {
            'level_number': self.level_number,
            'name': self.name,
            'bubble_radius': self.bubble_radius,
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'grid_spacing': self.grid_spacing,
            'grid_start_x': self.grid_start_x,
            'grid_start_y': self.grid_start_y,
            'max_shots': self.max_shots,
            'shots_remaining': self.shots_remaining,
        }

