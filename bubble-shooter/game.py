"""
Bubble Shooter Game - Main game logic with 3D-style graphics
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, PushMatrix, PopMatrix
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
import random
import math
import os
try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import graphics enhancer
try:
    from graphics_enhancer import GraphicsEnhancer
    GRAPHICS_ENHANCER_AVAILABLE = True
except ImportError:
    GRAPHICS_ENHANCER_AVAILABLE = False

# Element types
FIRE = 0
WATER = 1
EARTH = 2
AIR = 3

# Element colors (RGB values 0-1) - Enhanced colors
ELEMENT_COLORS = {
    FIRE: (1.0, 0.4, 0.2),      # Orange/Red
    WATER: (0.2, 0.7, 1.0),     # Blue
    EARTH: (1.0, 0.9, 0.2),     # Yellow (replaced brown)
    AIR: (0.6, 0.2, 0.9)        # Purple (replaced white/light blue)
}


class Bubble:
    """Represents a single bubble"""
    
    def __init__(self, x, y, element_type=None, radius=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.element_type = element_type if element_type is not None else random.randint(0, 3)
        self.color = ELEMENT_COLORS[self.element_type]
        self.vx = 0  # velocity x
        self.vy = 0  # velocity y
        self.attached = False  # Is bubble attached to grid?
        self.hit_count = 0  # For Earth bubbles (need 2 hits)
        self.has_dynamite = False  # Does this bubble contain dynamite?
        self.has_mine = False  # Does this bubble contain a mine?
        self.has_golden = False  # Is this a golden bubble? (extra score when shot directly)
        self.falling = False  # Is bubble falling (disconnected from top)?
        self.gravity = 300  # Gravity acceleration for falling bubbles
    
    def update(self, dt):
        """Update bubble position"""
        if self.falling:
            # Apply gravity to falling bubbles
            self.vy += self.gravity * dt
            self.y += self.vy * dt
        elif not self.attached:
            # Normal movement for shot bubbles
            self.x += self.vx * dt
            self.y += self.vy * dt
    
    def get_color(self):
        """Get color tuple for drawing"""
        return self.color
    
    def check_collision(self, other):
        """Check collision with another bubble"""
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        min_distance = self.radius + other.radius
        # Check if they're touching or overlapping (with small tolerance)
        return distance < min_distance + 1.0
    
    def matches_element(self, other):
        """Check if bubbles match element type"""
        return self.element_type == other.element_type


class BubbleShooterGame(Widget):
    """Main game widget with enhanced 3D graphics"""
    
    def __init__(self, level=None, **kwargs):
        super().__init__(**kwargs)
        
        # Base resolution for scaling (1080x2424)
        self.base_width = 1080
        self.base_height = 2424
        
        # Load level configuration
        if level is None:
            # Default level if none provided
            from levels.level1 import Level1
            level = Level1()
        
        # Store level object for restart/next level functionality
        self.current_level = level
        level_config = level.get_config()
        
        # Store base values from level (will be scaled in on_size)
        self.base_bubble_radius = level_config['bubble_radius']
        self.grid_width = level_config['grid_width']
        self.grid_height = level_config['grid_height']
        self.base_grid_spacing = level_config['grid_spacing']
        self.base_grid_start_x = level_config['grid_start_x']
        self.base_grid_start_y = level_config['grid_start_y']
        
        # Initialize scaled values (will be updated in on_size)
        # Start with base values - will be scaled when window size is known
        self.bubble_radius = self.base_bubble_radius
        self.grid_spacing = self.base_grid_spacing
        self.grid_start_x = self.base_grid_start_x
        self.grid_start_y = self.base_grid_start_y
        
        # Game state
        self.score = 0
        self.level = level_config['level_number']
        self.level_name = level_config['name']
        self.game_active = True
        self.max_shots = level_config['max_shots']
        self.shots_remaining = level_config['shots_remaining']
        self.is_loading = False  # Loading state for restart/level transition
        
        # Bubbles
        self.grid_bubbles = []  # Bubbles in grid
        self.shot_bubbles = []  # Currently shot bubble
        self.next_bubble = None  # Next bubble to shoot
        
        # Shooter (base values for 1080x2424)
        self.base_shooter_x = 540  # Center of screen (1080/2)
        self.base_shooter_y = 150  # Bottom of screen
        self.base_shooter_length = 120  # Shooter length
        self.base_bubble_speed = 1200  # Bubble shooting speed
        self.shooter_x = self.base_shooter_x  # Will be scaled in on_size
        self.shooter_y = self.base_shooter_y  # Will be scaled in on_size
        self.aim_angle = 90  # Degrees (90 = straight up)
        self.current_bubble = None
        
        # UI base values for 1080x2424
        self.base_panel_width = 840
        self.base_panel_height = 600
        self.base_button_width = 360
        self.base_button_height = 135
        self.base_button_spacing = 60
        self.base_font_size_large = 72
        self.base_font_size_medium = 54
        self.base_font_size_small = 42
        
        # Scale factor (will be calculated in on_size)
        self.scale = 1.0
        
        # Bind to size changes for responsive scaling
        self.bind(size=self.on_size, pos=self.on_size)
        
        # Background image
        self.background_texture = None
        self.load_background_image()
        
        # Dynamite image
        self.dynamite_texture = None
        self.load_dynamite_image()
        
        # Mine image
        self.mine_texture = None
        self.load_mine_image()
        
        # Gold bubble image
        self.gold_texture = None
        self.load_gold_image()
        
        # Enhanced graphics system
        self.graphics_enhancer = None
        self.bubble_textures = {}  # Cache for bubble textures
        if GRAPHICS_ENHANCER_AVAILABLE:
            self.graphics_enhancer = GraphicsEnhancer()
            self.graphics_enhancer.set_scale(self.scale)
        
        # Particle effects for explosions
        self.particles = []  # List of particle dictionaries
        
        # Call on_size immediately and also after a short delay to ensure window size is set
        # This ensures scaling works even if window size is already available
        self.on_size()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.on_size(), 0.1)
        
        # Note: on_touch_down, on_touch_move, on_touch_up are automatically
        # connected by Kivy when using these method names
    
    def on_size(self, *args):
        """Handle screen size changes - scale all game elements proportionally"""
        if self.width == 0 or self.height == 0:
            return
        
        # Calculate scale factors based on base resolution
        scale_x = self.width / self.base_width
        scale_y = self.height / self.base_height
        # Use minimum scale to maintain aspect ratio
        self.scale = min(scale_x, scale_y)
        
        # Scale bubble radius proportionally
        self.bubble_radius = self.base_bubble_radius * self.scale
        
        # Scale grid spacing proportionally
        self.grid_spacing = self.base_grid_spacing * self.scale
        
        # Scale positions based on actual screen dimensions
        # For X: center the grid on screen
        # Calculate grid width with scaled spacing
        grid_width_pixels = (self.grid_width - 1) * self.grid_spacing + self.grid_spacing * 0.5
        # Center the grid: start at (screen_width - grid_width) / 2
        # But account for bubble radius on left side
        self.grid_start_x = (self.width - grid_width_pixels) / 2 + self.bubble_radius
        
        # For Y: scale from base position (preserve relative position from level config)
        # This allows manual positioning adjustments to work correctly
        self.grid_start_y = self.base_grid_start_y * scale_y
        
        # Scale shooter position
        self.shooter_x = self.width / 2
        self.shooter_y = self.base_shooter_y * scale_y
        
        # Always reinitialize grid with scaled values
        # Store game state
        old_score = self.score
        old_shots = self.shots_remaining
        old_level = self.level
        old_level_name = self.level_name
        
        # Reinitialize grid with new scaled values
        self.initialize_grid()
        
        # Restore game state
        self.score = old_score
        self.shots_remaining = old_shots
        self.level = old_level
        self.level_name = old_level_name
        
        # Update existing shot bubbles' radius
        for bubble in self.shot_bubbles:
            if bubble:
                bubble.radius = self.bubble_radius
        
        # Update current and next bubble radius
        if self.current_bubble:
            self.current_bubble.radius = self.bubble_radius
        if self.next_bubble:
            self.next_bubble.radius = self.bubble_radius
        
        # Update graphics enhancer scale
        if self.graphics_enhancer:
            self.graphics_enhancer.set_scale(self.scale)
            # Clear texture cache to regenerate at new scale
            self.bubble_textures.clear()
        
        # Load next bubble if needed
        if self.next_bubble is None:
            self.load_next_bubble()
        
    def initialize_grid(self):
        """Create initial bubble grid - ensures no intersections"""
        self.grid_bubbles = []
        
        # Ensure grid spacing is sufficient (minimum 2 * radius)
        min_spacing = self.bubble_radius * 2.05  # Slightly more than 2 * radius (reduced for closer spacing)
        if self.grid_spacing < min_spacing:
            self.grid_spacing = min_spacing
        
        # Check if level has custom pattern method
        has_custom_pattern = hasattr(self.current_level, 'should_place_bubble')
        
        # Maximum number of bubbles limit (must be less than 140)
        MAX_BUBBLES = 139
        
        for row in range(self.grid_height):
            # Check bubble limit before processing each row
            if len(self.grid_bubbles) >= MAX_BUBBLES:
                break  # Stop if we've reached the maximum
            
            for col in range(self.grid_width):
                # Check bubble limit before processing each column
                if len(self.grid_bubbles) >= MAX_BUBBLES:
                    break  # Stop if we've reached the maximum
                
                # Check custom pattern if available
                if has_custom_pattern:
                    if not self.current_level.should_place_bubble(row, col):
                        continue  # Skip this position based on custom pattern
                
                # Offset every other row for hexagonal pattern
                x_offset = (self.grid_spacing * 0.5) if (row % 2 == 1) else 0
                x = self.grid_start_x + col * self.grid_spacing + x_offset
                y = self.grid_start_y - row * self.grid_spacing * 0.866
                
                # Skip bubbles that would extend beyond screen boundaries (only if width/height are known)
                if self.width > 0 and self.height > 0:
                    # Check left boundary (x - radius < 0)
                    if x - self.bubble_radius < 0:
                        continue
                    # Check right boundary (x + radius > width)
                    if x + self.bubble_radius > self.width:
                        continue
                    # Check bottom boundary (y - radius < 0)
                    if y - self.bubble_radius < 0:
                        continue
                    # Check top boundary (y + radius > height)
                    if y + self.bubble_radius > self.height:
                        continue
                
                element = random.randint(0, 3)
                bubble = Bubble(x, y, element, self.bubble_radius)
                bubble.attached = True
                
                # Randomly assign dynamite to ~8% of bubbles
                if random.random() < 0.08:
                    bubble.has_dynamite = True
                
                # Randomly assign mines to ~6% of bubbles (only for level > 2)
                # Mines and dynamite are mutually exclusive
                if self.level > 2 and not bubble.has_dynamite:
                    if random.random() < 0.06:
                        bubble.has_mine = True
                
                # Randomly assign golden bubbles to ~5% of bubbles (only for level > 5)
                # Golden bubbles are mutually exclusive with dynamite and mines
                if self.level > 5 and not bubble.has_dynamite and not bubble.has_mine:
                    if random.random() < 0.05:
                        bubble.has_golden = True
                
                # Verify no intersection before adding
                if not self.check_bubble_intersections(bubble):
                    self.grid_bubbles.append(bubble)
    
    def load_next_bubble(self):
        """Load next bubble to shoot"""
        if self.shooter_x is None or self.shooter_y is None:
            return
        element = random.randint(0, 3)
        self.next_bubble = Bubble(self.shooter_x, self.shooter_y, element, self.bubble_radius)
        self.current_bubble = self.next_bubble
    
    def on_touch_down(self, touch, *args):
        """Handle touch down - shoot bubble or handle button clicks"""
        try:
            # Check if game is over and handle button clicks
            if not self.game_active:
                return self.handle_game_over_click(touch)
            
            if self.current_bubble is None:
                return super().on_touch_down(touch)
            if self.current_bubble.attached:
                return super().on_touch_down(touch)
                
            # Calculate direction toward touch point
            dx = touch.x - self.shooter_x
            dy = touch.y - self.shooter_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 10:  # Minimum distance to shoot
                # Check if player has shots remaining
                if self.shots_remaining <= 0:
                    return super().on_touch_down(touch)
                
                # Update aim angle
                self.aim_angle = math.degrees(math.atan2(dy, dx))
                
                # Set bubble position at back of bazooka before shooting
                angle_rad = math.radians(self.aim_angle)
                base_radius = self.bubble_radius * 0.85  # Match the base radius used in drawing
                bubble_offset = base_radius * 0.8  # Position bubble slightly forward from base center
                self.current_bubble.x = self.shooter_x + math.cos(angle_rad) * bubble_offset
                self.current_bubble.y = self.shooter_y + math.sin(angle_rad) * bubble_offset
                
                # Normalize direction and set velocity (scaled)
                speed = self.base_bubble_speed * self.scale
                self.current_bubble.vx = (dx / distance) * speed
                self.current_bubble.vy = (dy / distance) * speed
                
                # Shoot the bubble
                bubble_to_shoot = self.current_bubble
                self.current_bubble = None
                self.shot_bubbles.append(bubble_to_shoot)
                self.shots_remaining -= 1  # Decrement shots remaining
                
                # Only load next bubble if game is still active and shots remain
                if self.shots_remaining > 0:
                    self.load_next_bubble()
                
                return True
        except Exception as e:
            print(f"Error in on_touch_down: {e}")
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch, *args):
        """Handle touch move - update aim angle (for visual feedback)"""
        dx = touch.x - self.shooter_x
        dy = touch.y - self.shooter_y
        self.aim_angle = math.degrees(math.atan2(dy, dx))
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch, *args):
        """Handle touch up - no action needed, shooting happens on touch_down"""
        return super().on_touch_up(touch)
    
    def handle_game_over_click(self, touch):
        """Handle button clicks on game over screen"""
        if self.height == 0:
            return False
        
        # Calculate button positions (EXACTLY matching draw_ui)
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Panel dimensions (matching draw_ui) - scaled
        panel_width = self.base_panel_width * self.scale
        panel_height = self.base_panel_height * self.scale
        panel_x = center_x - panel_width / 2
        panel_y = center_y - panel_height / 2
        
        # Button dimensions and positions (EXACTLY matching draw_ui) - scaled
        button_width = self.base_button_width * self.scale
        button_height = self.base_button_height * self.scale
        button_spacing = self.base_button_spacing * self.scale
        button_y = panel_y + 90 * self.scale  # 30 * 3
        
        # Retry button position
        retry_x = center_x - button_width - button_spacing / 2
        
        # Next level button position (only show if won)
        next_level_x = center_x + button_spacing / 2
        
        won = len(self.grid_bubbles) == 0
        
        # Check retry button click - use larger hit area for better responsiveness
        hit_margin = 15 * self.scale  # 5 * 3
        if (retry_x - hit_margin <= touch.x <= retry_x + button_width + hit_margin and
            button_y - hit_margin <= touch.y <= button_y + button_height + hit_margin):
            # Immediately show loading and start restart
            self.is_loading = True
            self.game_active = False
            self.start_restart()
            return True
        
        # Check next level button click (only if won) - use larger hit area
        if won and (next_level_x - hit_margin <= touch.x <= next_level_x + button_width + hit_margin and
                    button_y - hit_margin <= touch.y <= button_y + button_height + hit_margin):
            # Immediately show loading and start next level
            self.is_loading = True
            self.game_active = False
            self.start_next_level()
            return True
        
        return False
    
    def start_restart(self):
        """Start restart process - show loading screen immediately"""
        self.is_loading = True
        self.game_active = False  # Hide game over screen immediately
        # Schedule actual restart after a frame to show loading screen
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.restart_game(), 0.1)
    
    def start_next_level(self):
        """Start next level process - show loading screen immediately"""
        self.is_loading = True
        self.game_active = False  # Hide game over screen immediately
        # Schedule actual level transition after a frame to show loading screen
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.next_level(), 0.1)
    
    def restart_game(self):
        """Restart the current level"""
        level_config = self.current_level.get_config()
        
        # Reset game state
        self.score = 0
        self.level = level_config['level_number']  # Update level number
        self.level_name = level_config['name']  # Update level name
        self.game_active = True
        self.is_loading = False
        self.max_shots = level_config['max_shots']
        self.shots_remaining = level_config['shots_remaining']
        
        # Update base values from level config (in case level changed)
        self.base_bubble_radius = level_config['bubble_radius']
        self.grid_width = level_config['grid_width']
        self.grid_height = level_config['grid_height']
        self.base_grid_spacing = level_config['grid_spacing']
        self.base_grid_start_x = level_config['grid_start_x']
        self.base_grid_start_y = level_config['grid_start_y']
        
        # Clear bubbles
        self.grid_bubbles = []
        self.shot_bubbles = []
        self.current_bubble = None
        self.next_bubble = None
        
        # Recalculate scaling and reinitialize grid with scaled values
        # This ensures positions and sizes are correct
        self.on_size()
        
        # Load next bubble
        self.load_next_bubble()
    
    def next_level(self):
        """Advance to next level"""
        # Get current level number and advance to next level
        current_level_num = self.current_level.level_number
        
        if current_level_num == 1:
            # Advance to Level 2
            from levels.level2 import Level2
            self.current_level = Level2()
        elif current_level_num == 2:
            # Advance to Level 3
            from levels.level3 import Level3
            self.current_level = Level3()
        elif current_level_num == 3:
            # Advance to Level 4
            from levels.level4 import Level4
            self.current_level = Level4()
        elif current_level_num == 4:
            # Advance to Level 5
            from levels.level5 import Level5
            self.current_level = Level5()
        elif current_level_num == 5:
            # Advance to Level 6
            from levels.level6 import Level6
            self.current_level = Level6()
        elif current_level_num == 6:
            # Advance to Level 7
            from levels.level7 import Level7
            self.current_level = Level7()
        elif current_level_num == 7:
            # Advance to Level 8
            from levels.level8 import Level8
            self.current_level = Level8()
        elif current_level_num == 8:
            # Advance to Level 9
            from levels.level9 import Level9
            self.current_level = Level9()
        elif current_level_num == 9:
            # For now, restart Level 9 (can add more levels later)
            from levels.level9 import Level9
            self.current_level = Level9()
        else:
            # Default: restart current level
            pass
        
        self.restart_game()
    
    def update(self, dt):
        """Update game state (called every frame)"""
        # Update shooter position to bottom center of screen (rotated 180 degrees)
        if self.height > 0:
            # Shooter position is set in on_size, don't override it here
            self.shooter_x = self.width / 2  # Center horizontally
            # Grid positions are scaled in on_size, don't override them here
        
        if self.is_loading:
            # Show loading screen
            self.canvas.clear()
            with self.canvas:
                self.draw_background()
                self.draw_loading_screen()
            return
        
        if not self.game_active:
            # Still redraw even when game is over to show game over message
            self.canvas.clear()
            with self.canvas:
                self.draw_background()
                self.draw_grid()
                self.draw_shot_bubbles()
                self.draw_shooter()
                self.draw_particles()  # Draw particles on top
                self.draw_ui()
            return
        
        # No longer need to update falling bubbles - disconnected bubbles are removed immediately
        
        # Update particles
        self.update_particles(dt)
        
        # Update shot bubbles
        for bubble in self.shot_bubbles[:]:
            bubble.update(dt)
            
            # Check wall collisions
            if bubble.x - bubble.radius < 0:
                bubble.x = bubble.radius
                bubble.vx = -bubble.vx * 0.8  # Bounce with damping
            elif bubble.x + bubble.radius > self.width:
                bubble.x = self.width - bubble.radius
                bubble.vx = -bubble.vx * 0.8
            
            # Check top collision (bubble going above screen - bounce off top where bubbles are)
            if bubble.y + bubble.radius > self.height:
                bubble.y = self.height - bubble.radius
                bubble.vy = -bubble.vy * 0.8
            
            # Check bottom collision (bubble going below screen - remove it, shooter is at bottom)
            if bubble.y - bubble.radius < 0:
                self.shot_bubbles.remove(bubble)
                continue
            
            # Check collision with grid bubbles (prevent intersection)
            min_distance = float('inf')
            closest_bubble = None
            
            for grid_bubble in self.grid_bubbles:
                dx = bubble.x - grid_bubble.x
                dy = bubble.y - grid_bubble.y
                distance = math.sqrt(dx * dx + dy * dy)
                min_dist_needed = bubble.radius + grid_bubble.radius
                
                if distance < min_dist_needed:
                    # Bubble is too close - attach it
                    if distance < min_distance:
                        min_distance = distance
                        closest_bubble = grid_bubble
            
            if closest_bubble:
                self.attach_bubble(bubble, closest_bubble)
                break
            
            # Remove if below screen (bubble went off bottom where shooter is)
            if bubble.y - bubble.radius < 0:
                self.shot_bubbles.remove(bubble)
                continue
        
        # Check for game over condition: all shots used, bubbles still on screen, and no bubbles moving
        if self.shots_remaining <= 0 and len(self.grid_bubbles) > 0:
            if not self.has_moving_bubbles():
                self.game_active = False
        
        # Redraw
        self.canvas.clear()
        with self.canvas:
            self.draw_background()
            self.draw_grid()
            self.draw_shot_bubbles()
            self.draw_shooter()
            self.draw_particles()  # Draw particles on top
            self.draw_ui()
    
    def has_moving_bubbles(self):
        """Check if there are any bubbles currently moving (only shot bubbles, not falling ones)"""
        # Only check shot bubbles - falling bubbles don't prevent game over
        for bubble in self.shot_bubbles:
            # Check if bubble has significant velocity (above small threshold)
            speed = math.sqrt(bubble.vx * bubble.vx + bubble.vy * bubble.vy)
            if speed > 1.0:  # Threshold to account for floating point precision
                return True
        
        return False
    
    def attach_bubble(self, bubble, grid_bubble):
        """Attach shot bubble to grid at correct position without intersection"""
        bubble.attached = True
        bubble.falling = False  # Attached bubbles don't fall
        bubble.vx = 0
        bubble.vy = 0
        
        # Check if shot bubble attached directly to a golden bubble (extra score)
        golden_bonus_given = False
        if grid_bubble.has_golden:
            # Give extra score for shooting directly at golden bubble
            extra_score = 500  # Fixed bonus score of 500
            self.score += extra_score
            golden_bonus_given = True
            print(f"Golden bubble hit! Extra score: {extra_score}, Total score: {self.score}")
        
        # Find the best grid position near the collision point
        new_pos = self.find_nearest_empty_grid_position(bubble, grid_bubble)
        bubble.x = new_pos[0]
        bubble.y = new_pos[1]
        
        # Verify no intersections
        if not self.check_bubble_intersections(bubble):
            self.shot_bubbles.remove(bubble)
            self.grid_bubbles.append(bubble)
            # Check for matches
            self.check_matches(bubble)
        else:
            # If still intersecting, try alternative positions
            alt_pos = self.find_alternative_position(bubble, grid_bubble)
            bubble.x = alt_pos[0]
            bubble.y = alt_pos[1]
            
            if not self.check_bubble_intersections(bubble):
                self.shot_bubbles.remove(bubble)
                self.grid_bubbles.append(bubble)
                self.check_matches(bubble)
                # Print remaining bubbles after this shot is processed
                remaining_count = len(self.grid_bubbles)
                print(f"Remaining bubbles: {remaining_count}")
            else:
                # Last resort: remove the shot bubble if no valid position
                self.shot_bubbles.remove(bubble)
    
    def find_nearest_empty_grid_position(self, bubble, reference_bubble):
        """Find the nearest valid grid position that doesn't intersect"""
        # Calculate which grid cell the bubble should snap to
        min_distance = float('inf')
        best_pos = None
        
        # Check positions around the reference bubble (hexagonal grid pattern)
        # Try 6 adjacent positions in hexagonal pattern
        angles = [0, 60, 120, 180, 240, 300]
        distance = self.grid_spacing  # This should be >= 2 * radius
        
        for angle in angles:
            angle_rad = math.radians(angle)
            test_x = reference_bubble.x + math.cos(angle_rad) * distance
            test_y = reference_bubble.y + math.sin(angle_rad) * distance
            
            # Create temporary bubble at test position
            test_bubble = Bubble(test_x, test_y, bubble.element_type, bubble.radius)
            
            # Check if this position intersects with any existing bubbles
            if not self.check_bubble_intersections(test_bubble, exclude_bubble=bubble):
                # Check distance from original collision point
                dist = math.sqrt((test_x - bubble.x)**2 + (test_y - bubble.y)**2)
                if dist < min_distance:
                    min_distance = dist
                    best_pos = (test_x, test_y)
        
        # If no good adjacent position found, try snapping to exact grid
        if best_pos is None:
            # Snap to nearest grid cell
            col = round((reference_bubble.x - self.grid_start_x) / self.grid_spacing)
            row = round((self.grid_start_y - reference_bubble.y) / (self.grid_spacing * 0.866))
            
            x_offset = (self.grid_spacing * 0.5) if (row % 2 == 1) else 0
            x = self.grid_start_x + col * self.grid_spacing + x_offset
            y = self.grid_start_y - row * self.grid_spacing * 0.866
            
            test_bubble = Bubble(x, y, bubble.element_type, bubble.radius)
            if not self.check_bubble_intersections(test_bubble, exclude_bubble=bubble):
                best_pos = (x, y)
        
        # If still no valid position, use reference position (shouldn't happen with proper spacing)
        if best_pos is None:
            best_pos = (reference_bubble.x, reference_bubble.y + self.grid_spacing)
        
        return best_pos
    
    def find_alternative_position(self, bubble, reference_bubble):
        """Find alternative position if primary position intersects"""
        # Try positions further away
        distances = [self.grid_spacing * 1.5, self.grid_spacing * 2.0]
        
        for dist in distances:
            for angle in range(0, 360, 30):
                angle_rad = math.radians(angle)
                test_x = reference_bubble.x + math.cos(angle_rad) * dist
                test_y = reference_bubble.y + math.sin(angle_rad) * dist
                
                test_bubble = Bubble(test_x, test_y, bubble.element_type, bubble.radius)
                if not self.check_bubble_intersections(test_bubble, exclude_bubble=bubble):
                    return (test_x, test_y)
        
        # Fallback: position above reference
        return (reference_bubble.x, reference_bubble.y + self.grid_spacing)
    
    def check_bubble_intersections(self, bubble, exclude_bubble=None):
        """Check if a bubble intersects with any other bubbles in the grid"""
        for grid_bubble in self.grid_bubbles:
            if grid_bubble == exclude_bubble:
                continue
            
            dx = bubble.x - grid_bubble.x
            dy = bubble.y - grid_bubble.y
            distance = math.sqrt(dx * dx + dy * dy)
            min_distance = bubble.radius + grid_bubble.radius
            
            # If distance is less than sum of radii, they intersect
            # Use strict check: distance must be >= min_distance
            if distance < min_distance:
                return True
        
        return False
    
    def check_matches(self, bubble):
        """Check for matching bubbles"""
        matches = [bubble]
        self.find_connected_matches(bubble, matches, [])
        
        if len(matches) >= 3:
            # Check if any matched bubble has dynamite or mines
            has_dynamite_explosion = False
            dynamite_positions = []
            mine_positions = []
            
            # Count how many bubbles will be removed
            exploded_count = 0
            for match in matches:
                if match in self.grid_bubbles:
                    # Create particle effect for this bubble
                    self.create_explosion_particles(match.x, match.y, match.get_color())
                    
                    # Check for dynamite before removing
                    if match.has_dynamite:
                        has_dynamite_explosion = True
                        dynamite_positions.append((match.x, match.y))
                    # Check for mines before removing
                    if match.has_mine:
                        mine_positions.append((match.x, match.y))
                    self.grid_bubbles.remove(match)
                    exploded_count += 1
            
            # Calculate score: exploded bubbles * remaining shooting bubbles
            if exploded_count > 0:
                self.score += exploded_count * self.shots_remaining
            
            # Trigger dynamite explosions if any dynamite was found
            if has_dynamite_explosion:
                for dynamite_x, dynamite_y in dynamite_positions:
                    self.trigger_dynamite_explosion(dynamite_x, dynamite_y)
            
            # Trigger mine explosions if any mines were found
            if mine_positions:
                for mine_x, mine_y in mine_positions:
                    self.trigger_mine_explosion(mine_x, mine_y)
            
            # Check for floating bubbles
            self.check_floating_bubbles()
            
            # Check if all bubbles are cleared (win condition)
            if len(self.grid_bubbles) == 0:
                self.game_active = False  # Player wins!
    
    def get_dynamite_radius(self):
        """Get dynamite explosion radius in bubble diameters based on level"""
        if self.level <= 3:
            return 5  # Levels 1-3: radius of 5 bubbles
        elif self.level <= 6:
            return 4  # Levels 4-6: radius of 4 bubbles
        else:
            return 3  # Levels 7+: radius of 3 bubbles
    
    def trigger_dynamite_explosion(self, x, y):
        """Trigger dynamite explosion at position (x, y), removing all bubbles within level-based radius"""
        bubble_radius_count = self.get_dynamite_radius()
        explosion_radius = bubble_radius_count * self.bubble_radius * 2  # Convert to pixel radius (bubble diameters)
        
        bubbles_to_explode = []
        for bubble in self.grid_bubbles[:]:
            dx = bubble.x - x
            dy = bubble.y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # If bubble is within explosion radius, mark it for removal
            if distance <= explosion_radius:
                bubbles_to_explode.append(bubble)
        
        # Remove all bubbles in explosion radius
        exploded_count = 0
        for bubble in bubbles_to_explode:
            if bubble in self.grid_bubbles:
                # Create particle effect for this bubble
                self.create_explosion_particles(bubble.x, bubble.y, bubble.get_color())
                self.grid_bubbles.remove(bubble)
                exploded_count += 1
        
        # Create large explosion effect at dynamite position
        self.create_explosion_particles(x, y, (1.0, 0.5, 0.2), particle_count=30, speed_multiplier=2.0)
        
        # Calculate score: exploded bubbles * remaining shooting bubbles
        if exploded_count > 0:
            self.score += exploded_count * self.shots_remaining
        
        # Check for floating bubbles after explosion
        self.check_floating_bubbles()
        
        # Check if all bubbles are cleared (win condition)
        if len(self.grid_bubbles) == 0:
            self.game_active = False  # Player wins!
    
    def trigger_mine_explosion(self, x, y):
        """Trigger mine explosion at position (x, y), removing all bubbles in the same row"""
        # Find the row (y coordinate) of the mine
        mine_y = y
        
        # Tolerance for determining if bubbles are in the same row
        # Account for hexagonal grid where rows are spaced by grid_spacing * 0.866
        # Use half the row spacing as tolerance
        row_tolerance = self.grid_spacing * 0.4  # Allow tolerance for row detection
        
        bubbles_to_explode = []
        dynamite_to_trigger = []
        
        for bubble in self.grid_bubbles[:]:
            # Check if bubble is in the same row (within tolerance)
            if abs(bubble.y - mine_y) <= row_tolerance:
                bubbles_to_explode.append(bubble)
                # Check if this bubble has dynamite (will trigger after removal)
                if bubble.has_dynamite:
                    dynamite_to_trigger.append((bubble.x, bubble.y))
        
        # Remove all bubbles in the same row
        exploded_count = 0
        for bubble in bubbles_to_explode:
            if bubble in self.grid_bubbles:
                # Create particle effect for this bubble
                self.create_explosion_particles(bubble.x, bubble.y, bubble.get_color())
                self.grid_bubbles.remove(bubble)
                exploded_count += 1
        
        # Create large explosion effect at mine position
        self.create_explosion_particles(x, y, (1.0, 0.8, 0.0), particle_count=25, speed_multiplier=1.8)
        
        # Trigger dynamite explosions after removing bubbles (to avoid double processing)
        for dynamite_x, dynamite_y in dynamite_to_trigger:
            self.trigger_dynamite_explosion(dynamite_x, dynamite_y)
        
        # Calculate score: exploded bubbles * remaining shooting bubbles
        if exploded_count > 0:
            self.score += exploded_count * self.shots_remaining
        
        # Check for floating bubbles after mine explosion
        self.check_floating_bubbles()
        
        # Check if all bubbles are cleared (win condition)
        if len(self.grid_bubbles) == 0:
            self.game_active = False  # Player wins!
    
    def find_connected_matches(self, bubble, matches, visited):
        """Find all connected bubbles of same element"""
        visited.append(bubble)
        
        # Check neighbors within grid spacing (hexagonal pattern)
        neighbor_distance = self.grid_spacing * 1.1  # Slightly larger than grid spacing
        
        for other in self.grid_bubbles:
            if other not in visited and other != bubble:
                dx = bubble.x - other.x
                dy = bubble.y - other.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Check if they're neighbors (touching) and same element
                if distance < neighbor_distance and bubble.matches_element(other):
                    matches.append(other)
                    self.find_connected_matches(other, matches, visited)
    
    def create_explosion_particles(self, x, y, color, particle_count=15, speed_multiplier=1.0):
        """Create particle effects for bubble explosions"""
        if not self.graphics_enhancer or not PIL_AVAILABLE:
            return
        
        base_speed = 200 * speed_multiplier * self.scale
        
        for _ in range(particle_count):
            # Random angle for particle direction
            angle = random.uniform(0, 2 * math.pi)
            # Random speed variation
            speed = random.uniform(base_speed * 0.5, base_speed * 1.5)
            
            # Random lifetime (0.3 to 0.8 seconds)
            lifetime = random.uniform(0.3, 0.8)
            
            # Random size
            size = random.uniform(3 * self.scale, 8 * self.scale)
            
            # Slight color variation
            color_variation = random.uniform(0.8, 1.2)
            particle_color = (
                min(1.0, color[0] * color_variation),
                min(1.0, color[1] * color_variation),
                min(1.0, color[2] * color_variation)
            )
            
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': particle_color,
                'size': size,
                'lifetime': lifetime,
                'age': 0.0,
                'texture': None
            }
            
            # Create texture if graphics enhancer is available
            if self.graphics_enhancer:
                particle['texture'] = self.graphics_enhancer.create_particle_texture(
                    int(size * 2), particle_color, fade=True
                )
            
            self.particles.append(particle)
    
    def update_particles(self, dt):
        """Update particle positions and lifetimes"""
        for particle in self.particles[:]:
            # Update position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Apply gravity/friction
            particle['vy'] -= 300 * dt * self.scale  # Gravity
            particle['vx'] *= 0.98  # Friction
            
            # Update age
            particle['age'] += dt
            
            # Remove expired particles
            if particle['age'] >= particle['lifetime']:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            # Calculate alpha based on remaining lifetime
            remaining_life = 1.0 - (particle['age'] / particle['lifetime'])
            alpha = max(0.0, min(1.0, remaining_life))
            
            if particle['texture']:
                # Draw using texture
                size = particle['size'] * 2
                Color(1, 1, 1, alpha)
                Rectangle(texture=particle['texture'],
                         pos=(particle['x'] - size / 2, particle['y'] - size / 2),
                         size=(size, size))
            else:
                # Fallback: draw simple circle
                color = particle['color']
                Color(color[0], color[1], color[2], alpha)
                Ellipse(pos=(particle['x'] - particle['size'], particle['y'] - particle['size']),
                       size=(particle['size'] * 2, particle['size'] * 2))
    
    def check_floating_bubbles(self):
        """Check for bubbles not connected to topmost line and make them fall"""
        if len(self.grid_bubbles) == 0:
            return
        
        # Find all bubbles in the topmost line (at grid_start_y)
        # Only bubbles at the topmost line are considered "attached to top"
        top_threshold = self.grid_spacing * 0.5  # Tolerance for "top row" (half grid spacing)
        top_bubbles = []
        
        # Find all bubbles at the topmost line (at grid_start_y)
        for bubble in self.grid_bubbles:
            if abs(bubble.y - self.grid_start_y) <= top_threshold:
                top_bubbles.append(bubble)
        
        if not top_bubbles:
            # If no top bubbles found, all bubbles are disconnected - explode them all immediately
            disconnected_count = len(self.grid_bubbles)
            if disconnected_count > 0:
                # Calculate score before removing
                self.score += disconnected_count * self.shots_remaining
                # Remove all bubbles immediately
                self.grid_bubbles.clear()
                # Print remaining bubbles
                print(f"Remaining bubbles: 0")
            
            # Check if all bubbles are cleared (win condition)
            if len(self.grid_bubbles) == 0:
                self.game_active = False  # Player wins!
            return
        
        # Use BFS to find all bubbles connected to top bubbles
        connected_bubbles = set()
        queue = list(top_bubbles)
        
        for bubble in top_bubbles:
            connected_bubbles.add(bubble)
        
        # BFS traversal to find all connected bubbles
        while queue:
            current = queue.pop(0)
            
            # Find all neighbors of current bubble
            neighbor_distance = self.grid_spacing * 1.1  # Slightly larger than grid spacing
            
            for other in self.grid_bubbles:
                if other not in connected_bubbles:
                    dx = current.x - other.x
                    dy = current.y - other.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    # If bubbles are touching/neighbors, they're connected
                    if distance < neighbor_distance:
                        connected_bubbles.add(other)
                        queue.append(other)
        
        # Remove all bubbles that are NOT connected to the top (explode them immediately)
        disconnected_bubbles = []
        for bubble in self.grid_bubbles:
            if bubble not in connected_bubbles:
                disconnected_bubbles.append(bubble)
        
        # Remove disconnected bubbles immediately (explode them)
        disconnected_count = 0
        for bubble in disconnected_bubbles:
            if bubble in self.grid_bubbles:
                # Create particle effect for falling bubble
                self.create_explosion_particles(bubble.x, bubble.y, bubble.get_color())
                self.grid_bubbles.remove(bubble)
                disconnected_count += 1
        
        # Calculate score: all disconnected bubbles * remaining shooting bubbles
        if disconnected_count > 0:
            self.score += disconnected_count * self.shots_remaining
            # Print remaining bubbles after removing disconnected ones
            remaining_count = len(self.grid_bubbles)
            print(f"Remaining bubbles: {remaining_count}")
        
        # Check if all bubbles are cleared (win condition)
        if len(self.grid_bubbles) == 0:
            print(f"Remaining bubbles: 0")
            self.game_active = False  # Player wins!
    
    def get_asset_path(self, filename):
        """Get asset path that works on both desktop and Android"""
        # Try multiple possible paths
        possible_paths = [
            os.path.join("asset", filename),  # Relative path (works on Android)
            os.path.join(".", "asset", filename),  # Current directory
            os.path.join(os.path.dirname(__file__), "asset", filename),  # Same dir as game.py
            os.path.join(os.getcwd(), "asset", filename),  # Current working directory
        ]
        
        # On Windows, also try the original hardcoded path as fallback
        if os.name == 'nt':
            possible_paths.append(
                r"C:\Users\aminz\OneDrive\Documents\GitHub\bubble-shooter\bubble-shooter\bubble-shooter\asset\{}".format(filename)
            )
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def load_background_image(self):
        """Load background image texture"""
        background_path = self.get_asset_path("grunge-white-surface-rough-background-textured.jpg")
        if background_path and os.path.exists(background_path):
            try:
                img = CoreImage(background_path)
                self.background_texture = img.texture
            except Exception as e:
                print(f"Error loading background image: {e}")
                self.background_texture = None
        else:
            print(f"Background image not found: grunge-white-surface-rough-background-textured.jpg")
            self.background_texture = None
    
    def load_dynamite_image(self):
        """Load dynamite image texture with white background removed"""
        dynamite_path = self.get_asset_path("istockphoto-1139873743-612x612.jpg")
        if dynamite_path and os.path.exists(dynamite_path):
            try:
                if PIL_AVAILABLE:
                    # Use PIL to remove white background
                    pil_img = PILImage.open(dynamite_path)
                    # Convert to RGBA if not already
                    if pil_img.mode != 'RGBA':
                        pil_img = pil_img.convert('RGBA')
                    
                    # Get image data
                    data = pil_img.getdata()
                    # Create new image data with transparent white pixels
                    new_data = []
                    for item in data:
                        # If pixel is white or near-white (threshold for slight variations)
                        # Make it transparent
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0))  # Transparent
                        else:
                            new_data.append(item)  # Keep original
                    
                    pil_img.putdata(new_data)
                    
                    # Save to temporary file or use BytesIO
                    import io
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Load processed image
                    img = CoreImage(img_bytes, ext='png')
                    self.dynamite_texture = img.texture
                else:
                    # Fallback: load image without processing
                    img = CoreImage(dynamite_path)
                    self.dynamite_texture = img.texture
            except Exception as e:
                print(f"Error loading dynamite image: {e}")
                self.dynamite_texture = None
        else:
            print(f"Dynamite image not found: istockphoto-1139873743-612x612.jpg")
            self.dynamite_texture = None
    
    def load_mine_image(self):
        """Load mine image texture with white background removed"""
        mine_path = self.get_asset_path("istockphoto-1474907248-612x612.jpg")
        if mine_path and os.path.exists(mine_path):
            try:
                if PIL_AVAILABLE:
                    # Use PIL to remove white background
                    pil_img = PILImage.open(mine_path)
                    # Convert to RGBA if not already
                    if pil_img.mode != 'RGBA':
                        pil_img = pil_img.convert('RGBA')
                    
                    # Get image data
                    data = pil_img.getdata()
                    # Create new image data with transparent white pixels
                    new_data = []
                    for item in data:
                        # If pixel is white or near-white (threshold for slight variations)
                        # Make it transparent
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0))  # Transparent
                        else:
                            new_data.append(item)  # Keep original
                    
                    pil_img.putdata(new_data)
                    
                    # Save to temporary file or use BytesIO
                    import io
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Load processed image
                    img = CoreImage(img_bytes, ext='png')
                    self.mine_texture = img.texture
                else:
                    # Fallback: load image without processing
                    img = CoreImage(mine_path)
                    self.mine_texture = img.texture
            except Exception as e:
                print(f"Error loading mine image: {e}")
                self.mine_texture = None
        else:
            print(f"Mine image not found: istockphoto-1474907248-612x612.jpg")
            self.mine_texture = None
    
    def load_gold_image(self):
        """Load gold bubble image texture with background removed"""
        gold_path = self.get_asset_path("gold.jpg")
        if gold_path and os.path.exists(gold_path):
            try:
                if PIL_AVAILABLE:
                    # Use PIL to remove background
                    pil_img = PILImage.open(gold_path)
                    # Convert to RGBA if not already
                    if pil_img.mode != 'RGBA':
                        pil_img = pil_img.convert('RGBA')
                    
                    width, height = pil_img.size
                    
                    # Get corner pixels to determine background color
                    # Check all four corners
                    corners = [
                        pil_img.getpixel((0, 0)),  # Top-left
                        pil_img.getpixel((width-1, 0)),  # Top-right
                        pil_img.getpixel((0, height-1)),  # Bottom-left
                        pil_img.getpixel((width-1, height-1))  # Bottom-right
                    ]
                    
                    # Find the most common corner color (likely the background)
                    from collections import Counter
                    corner_colors = [tuple(c[:3]) for c in corners]  # RGB only
                    bg_color = Counter(corner_colors).most_common(1)[0][0]
                    
                    # Get image data
                    data = pil_img.getdata()
                    new_data = []
                    
                    # Threshold for background color matching (allow slight variations)
                    threshold = 30
                    
                    for item in data:
                        r, g, b = item[0], item[1], item[2]
                        bg_r, bg_g, bg_b = bg_color
                        
                        # Calculate distance from background color
                        color_distance = math.sqrt(
                            (r - bg_r) ** 2 + 
                            (g - bg_g) ** 2 + 
                            (b - bg_b) ** 2
                        )
                        
                        # Also check for very light colors (white/light backgrounds)
                        is_light = r > 240 and g > 240 and b > 240
                        
                        # If pixel is close to background color or very light, make it transparent
                        if color_distance < threshold or is_light:
                            new_data.append((255, 255, 255, 0))  # Transparent
                        else:
                            new_data.append(item)  # Keep original
                    
                    pil_img.putdata(new_data)
                    
                    # Save to temporary file or use BytesIO
                    import io
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Load processed image
                    img = CoreImage(img_bytes, ext='png')
                    self.gold_texture = img.texture
                else:
                    # Fallback: load image without processing
                    img = CoreImage(gold_path)
                    self.gold_texture = img.texture
            except Exception as e:
                print(f"Error loading gold image: {e}")
                self.gold_texture = None
        else:
            print(f"Gold image not found: {gold_path}")
            self.gold_texture = None
    
    def draw_background(self):
        """Draw game background using image"""
        # For levels 6-9, use antique blue background
        if self.level >= 6:
            # Antique blue background for levels 6-9
            Color(0.35, 0.45, 0.55, 1)  # Antique blue (muted blue-gray)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
        elif self.background_texture and self.width > 0 and self.height > 0:
            # Draw background image covering entire screen with darker tint
            Color(0.4, 0.4, 0.4, 1)  # Darker tint (0.4 = 40% brightness)
            Rectangle(texture=self.background_texture, 
                     pos=(0, 0), 
                     size=(self.width, self.height))
        else:
            # Fallback to solid color if image not loaded
            Color(0.1, 0.1, 0.15)  # Dark gray-blue
            Rectangle(pos=(0, 0), size=(self.width, self.height))
    
    def draw_grid(self):
        """Draw bubble grid with 3D effects"""
        for bubble in self.grid_bubbles:
            self.draw_bubble_3d(bubble)
    
    def draw_shot_bubbles(self):
        """Draw bubbles that are being shot with 3D effects"""
        for bubble in self.shot_bubbles:
            self.draw_bubble_3d(bubble)
    
    def draw_bubble_3d(self, bubble, x=None, y=None):
        """Draw a realistic bubble - transparent, glassy, with highlights like real soap bubbles"""
        if x is None:
            x = bubble.x
        if y is None:
            y = bubble.y
        radius = bubble.radius
        color = bubble.get_color()
        
        # Try to use enhanced graphics texture if available
        has_special = bubble.has_dynamite or bubble.has_mine or bubble.has_golden
        use_enhanced = self.graphics_enhancer and PIL_AVAILABLE
        
        if use_enhanced:
            # Create cache key for this bubble type
            cache_key = f"bubble_{bubble.element_type}_{int(radius)}_{has_special}"
            
            # Get or create texture
            texture = self.bubble_textures.get(cache_key)
            if texture is None:
                texture = self.graphics_enhancer.create_bubble_texture(
                    radius, color, bubble.element_type, has_special
                )
                if texture:
                    self.bubble_textures[cache_key] = texture
            
            # Draw using texture if available
            if texture:
                texture_size = texture.width / 2.5  # Account for 2.5x generation scale
                Color(1, 1, 1, 1)  # Full color
                Rectangle(texture=texture,
                         pos=(x - texture_size / 2, y - texture_size / 2),
                         size=(texture_size, texture_size))
            else:
                use_enhanced = False  # Fall back to basic drawing
        
        # Fallback to basic drawing if enhanced graphics not available
        if not use_enhanced:
            # Draw ball-like appearance with basic primitives
            
            # 1. Draw shadow (ball casts stronger shadow)
            shadow_offset = 3 * self.scale
            Color(0, 0, 0, 0.25)  # Stronger shadow for ball
            Ellipse(pos=(x - radius + shadow_offset, y - radius - shadow_offset),
                   size=(radius * 2, radius * 2))
            
            # 2. Draw main ball body - fully opaque solid ball
            Color(color[0], color[1], color[2], 1.0)  # Fully opaque
            Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))
            
            # 3. Draw darker bottom (simulate sphere shading)
            # Bottom half darker for depth
            bottom_darkness = 0.7
            Color(color[0] * bottom_darkness, color[1] * bottom_darkness, color[2] * bottom_darkness, 1.0)
            # Draw darker bottom half
            Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius))
            
            # 4. Draw highlight (bright spot at top-left for ball shine)
            highlight_radius = radius * 0.4
            highlight_x = x - radius * 0.3
            highlight_y = y + radius * 0.3
            Color(1, 1, 1, 0.5)  # White highlight
            Ellipse(pos=(highlight_x - highlight_radius, highlight_y - highlight_radius),
                   size=(highlight_radius * 2, highlight_radius * 2))
            
            # 5. Draw rim/edge (bright edge on lit side)
            rim_width = 2 * self.scale
            Color(color[0] * 1.3, color[1] * 1.3, color[2] * 1.3, 1.0)  # Brighter rim
            Line(circle=(x, y, radius), width=rim_width)
        
        # 5. Draw dynamite indicator if bubble has dynamite
        if bubble.has_dynamite:
            if self.dynamite_texture:
                # Draw dynamite image centered on bubble
                dynamite_size = radius * 2.5  # Much larger than bubble radius for better visibility
                Color(1, 1, 1, 1)  # Full color (no tinting)
                Rectangle(texture=self.dynamite_texture,
                         pos=(x - dynamite_size / 2, y - dynamite_size / 2),
                         size=(dynamite_size, dynamite_size))
            else:
                # Fallback: Draw simple dynamite stick if image not loaded
                stick_width = radius * 0.6
                stick_height = radius * 0.8
                stick_x = x - stick_width / 2
                stick_y = y - stick_height / 2
                
                # Draw dynamite stick (brown/red rectangle)
                Color(0.6, 0.2, 0.1, 0.9)  # Brown-red color
                Rectangle(pos=(stick_x, stick_y), size=(stick_width, stick_height))
                
                # Draw fuse on top (small line/circle)
                fuse_length = radius * 0.3
                fuse_y = stick_y + stick_height
                Color(0.8, 0.8, 0.3, 0.9)  # Yellow/light color for fuse
                Line(points=[x, fuse_y, x, fuse_y + fuse_length], width=6 * self.scale)  # 2 * 3
                # Draw fuse tip (small circle)
                Color(1, 0.3, 0, 0.9)  # Orange-red for lit fuse
                tip_size = 6 * self.scale  # 2 * 3
                Ellipse(pos=(x - tip_size, fuse_y + fuse_length - tip_size), size=(tip_size * 2, tip_size * 2))
        
        # 6. Draw mine indicator if bubble has a mine
        if bubble.has_mine:
            if self.mine_texture:
                # Draw mine image centered on bubble
                mine_size = radius * 2.5  # Much larger than bubble radius for better visibility
                Color(1, 1, 1, 1)  # Full color (no tinting)
                Rectangle(texture=self.mine_texture,
                         pos=(x - mine_size / 2, y - mine_size / 2),
                         size=(mine_size, mine_size))
            else:
                # Fallback: Draw simple mine symbol if image not loaded
                mine_size = radius * 1.8
                
                # Draw warning triangle (upside down triangle)
                triangle_points = [
                    x, y + mine_size * 0.4,  # Top point
                    x - mine_size * 0.5, y - mine_size * 0.3,  # Bottom left
                    x + mine_size * 0.5, y - mine_size * 0.3,  # Bottom right
                ]
                Color(1, 0.8, 0, 0.9)  # Yellow-orange warning color
                Line(points=triangle_points, width=6 * self.scale, close=True)  # 2 * 3
                
                # Fill triangle slightly
                Color(1, 0.9, 0.3, 0.6)  # Lighter yellow fill
                # Draw filled triangle using multiple lines (simplified)
                for i in range(len(triangle_points) // 2 - 1):
                    Line(points=[x, y, triangle_points[i*2], triangle_points[i*2+1]], width=3 * self.scale)  # 1 * 3
                
                # Draw exclamation mark in center
                Color(1, 0.2, 0.2, 1)  # Red for exclamation
                # Exclamation mark line
                Line(points=[x, y - mine_size * 0.15, x, y + mine_size * 0.15], width=6 * self.scale)  # 2 * 3
                # Exclamation mark dot
                dot_size = 6 * self.scale  # 2 * 3
                Ellipse(pos=(x - dot_size, y + mine_size * 0.2 - dot_size), size=(dot_size * 2, dot_size * 2))
        
        # 7. Draw golden bubble indicator if bubble is golden
        if bubble.has_golden:
            if self.gold_texture:
                # Draw gold image centered on bubble
                gold_size = radius * 1.6  # Slightly larger than bubble
                gold_x = x - gold_size / 2
                gold_y = y - gold_size / 2
                Color(1, 1, 1, 1)  # White to preserve image colors
                Rectangle(texture=self.gold_texture,
                         pos=(gold_x, gold_y),
                         size=(gold_size, gold_size))
            else:
                # Fallback: Draw golden glow/ring if image not loaded
                golden_ring_width = 9 * self.scale  # 3 * 3
                golden_ring_radius = radius + 6 * self.scale  # 2 * 3
                
                # Outer golden glow
                Color(1, 0.84, 0.0, 0.8)  # Gold color with transparency
                Line(circle=(x, y, golden_ring_radius), width=golden_ring_width)
                
                # Inner golden highlight
                Color(1, 0.9, 0.3, 0.9)  # Brighter gold
                Line(circle=(x, y, golden_ring_radius - 3 * self.scale), width=6 * self.scale)  # 2 * 3
                
                # Draw star symbol in center (simplified as small star)
                star_size = radius * 0.6
                star_points = []
                num_points = 5
                for i in range(num_points * 2):
                    angle = (i * math.pi / num_points) - math.pi / 2
                    if i % 2 == 0:
                        # Outer point
                        star_radius = star_size / 2
                    else:
                        # Inner point
                        star_radius = star_size / 4
                    px = x + star_radius * math.cos(angle)
                    py = y + star_radius * math.sin(angle)
                    star_points.extend([px, py])
                
                Color(1, 0.95, 0.5, 1)  # Bright gold for star
                Line(points=star_points, width=6 * self.scale, close=True)  # 2 * 3
    
    def draw_shooter(self):
        """Draw bazooka-style shooter with laser aim"""
        x, y = self.shooter_x, self.shooter_y
        # Scale bazooka size based on bubble radius (make it bigger)
        bubble_radius = self.bubble_radius
        shooter_length = bubble_radius * 3.0  # 3x bubble radius for length
        barrel_width = bubble_radius * 0.9  # Bigger barrel width (increased from 0.5)
        base_radius = bubble_radius * 0.85  # Base radius proportional to bubble
        tip_radius = bubble_radius * 0.3  # Tip radius proportional to bubble
        
        # Convert angle to radians
        angle_rad = math.radians(self.aim_angle)
        
        # Calculate shooter end point (tip of bazooka)
        end_x = x + math.cos(angle_rad) * shooter_length
        end_y = y + math.sin(angle_rad) * shooter_length
        
        # Calculate bubble position at the back of bazooka (near base, slightly forward)
        bubble_offset = base_radius * 0.8  # Position bubble slightly forward from base center
        bubble_x = x + math.cos(angle_rad) * bubble_offset
        bubble_y = y + math.sin(angle_rad) * bubble_offset
        
        # Calculate perpendicular vector for barrel width
        perp_x = -math.sin(angle_rad)
        perp_y = math.cos(angle_rad)
        half_width = barrel_width / 2
        
        # Draw bazooka base (larger, more detailed)
        # Base shadow
        Color(0, 0, 0, 0.3)
        Ellipse(pos=(x - base_radius + 2, y - base_radius - 2), size=(base_radius * 2, base_radius * 2))
        
        # Main base (dark metallic)
        Color(0.25, 0.25, 0.3, 1)  # Dark metallic gray
        Ellipse(pos=(x - base_radius, y - base_radius), size=(base_radius * 2, base_radius * 2))
        
        # Base highlight (top-left)
        Color(0.4, 0.4, 0.45, 0.6)
        highlight_radius = base_radius * 0.6
        highlight_x = x - base_radius * 0.3
        highlight_y = y + base_radius * 0.3
        Ellipse(pos=(highlight_x - highlight_radius, highlight_y - highlight_radius), 
               size=(highlight_radius * 2, highlight_radius * 2))
        
        # Base rim (metallic edge)
        Color(0.5, 0.5, 0.55, 0.8)
        Line(circle=(x, y, base_radius), width=3 * self.scale)
        
        # Draw bazooka barrel (cylindrical, metallic)
        # Barrel shadow
        barrel_points = [
            x + perp_x * half_width, y + perp_y * half_width,
            end_x + perp_x * half_width, end_y + perp_y * half_width,
            end_x - perp_x * half_width, end_y - perp_y * half_width,
            x - perp_x * half_width, y - perp_y * half_width
        ]
        Color(0, 0, 0, 0.2)
        # Draw shadow offset
        shadow_offset = 2
        shadow_points = [
            barrel_points[0] + shadow_offset, barrel_points[1] - shadow_offset,
            barrel_points[2] + shadow_offset, barrel_points[3] - shadow_offset,
            barrel_points[4] + shadow_offset, barrel_points[5] - shadow_offset,
            barrel_points[6] + shadow_offset, barrel_points[7] - shadow_offset
        ]
        # Simplified shadow drawing
        Line(points=[barrel_points[0], barrel_points[1], barrel_points[2], barrel_points[3]], width=barrel_width)
        
        # Main barrel body (metallic gray with gradient effect)
        Color(0.4, 0.4, 0.45, 1)  # Metallic gray
        Line(points=[x, y, end_x, end_y], width=barrel_width)
        
        # Barrel top highlight (brighter on top)
        Color(0.55, 0.55, 0.6, 0.8)
        top_line_width = barrel_width * 0.4
        top_offset = half_width * 0.6
        top_start_x = x + perp_x * top_offset
        top_start_y = y + perp_y * top_offset
        top_end_x = end_x + perp_x * top_offset
        top_end_y = end_y + perp_y * top_offset
        Line(points=[top_start_x, top_start_y, top_end_x, top_end_y], width=top_line_width)
        
        # Barrel bottom shadow (darker on bottom)
        Color(0.25, 0.25, 0.3, 0.8)
        bottom_offset = -top_offset
        bottom_start_x = x + perp_x * bottom_offset
        bottom_start_y = y + perp_y * bottom_offset
        bottom_end_x = end_x + perp_x * bottom_offset
        bottom_end_y = end_y + perp_y * bottom_offset
        Line(points=[bottom_start_x, bottom_start_y, bottom_end_x, bottom_end_y], width=top_line_width)
        
        # Barrel rim/edge lines
        Color(0.3, 0.3, 0.35, 0.9)
        Line(points=[x + perp_x * half_width, y + perp_y * half_width, 
                     end_x + perp_x * half_width, end_y + perp_y * half_width], width=2 * self.scale)
        Line(points=[x - perp_x * half_width, y - perp_y * half_width, 
                     end_x - perp_x * half_width, end_y - perp_y * half_width], width=2 * self.scale)
        
        # Draw bazooka tip/muzzle (larger, more detailed)
        # Tip shadow
        Color(0, 0, 0, 0.3)
        Ellipse(pos=(end_x - tip_radius + 1, end_y - tip_radius - 1), size=(tip_radius * 2, tip_radius * 2))
        
        # Main tip (dark metallic)
        Color(0.2, 0.2, 0.25, 1)  # Darker metallic
        Ellipse(pos=(end_x - tip_radius, end_y - tip_radius), size=(tip_radius * 2, tip_radius * 2))
        
        # Tip rim (metallic edge)
        Color(0.5, 0.5, 0.55, 0.9)
        Line(circle=(end_x, end_y, tip_radius), width=2 * self.scale)
        
        # Muzzle opening (dark center)
        muzzle_radius = tip_radius * 0.6
        Color(0.1, 0.1, 0.15, 1)  # Very dark
        Ellipse(pos=(end_x - muzzle_radius, end_y - muzzle_radius), size=(muzzle_radius * 2, muzzle_radius * 2))
        
        # Draw grip/handle (on the side of bazooka)
        grip_length = 40 * self.scale
        grip_width = 12 * self.scale
        grip_angle = angle_rad + math.pi / 2  # Perpendicular to barrel
        grip_x = x + math.cos(grip_angle) * (base_radius * 0.7)
        grip_y = y + math.sin(grip_angle) * (base_radius * 0.7)
        grip_end_x = grip_x + math.cos(angle_rad) * grip_length
        grip_end_y = grip_y + math.sin(angle_rad) * grip_length
        
        # Grip shadow
        Color(0, 0, 0, 0.2)
        Line(points=[grip_x + 1, grip_y - 1, grip_end_x + 1, grip_end_y - 1], width=grip_width)
        
        # Main grip
        Color(0.3, 0.25, 0.2, 1)  # Brown/dark wood color
        Line(points=[grip_x, grip_y, grip_end_x, grip_end_y], width=grip_width)
        
        # Grip highlight
        Color(0.4, 0.35, 0.3, 0.6)
        Line(points=[grip_x, grip_y, grip_end_x, grip_end_y], width=grip_width * 0.5)
        
        # Draw current bubble with 3D effect (positioned at back of bazooka)
        if self.current_bubble and not self.current_bubble.attached:
            # Draw bubble at the back of bazooka (near base) without modifying bubble properties
            self.draw_bubble_3d(self.current_bubble, x=bubble_x, y=bubble_y)
        
        # Draw laser that stops at the closest ball
        laser_start_x = end_x
        laser_start_y = end_y
        laser_dir_x = math.cos(angle_rad)
        laser_dir_y = math.sin(angle_rad)
        
        # Find the closest ball that the laser would hit using proper line-circle intersection
        min_distance = float('inf')
        hit_point_x = None
        hit_point_y = None
        
        # Check all grid bubbles to find the first one the laser hits
        for grid_bubble in self.grid_bubbles:
            # Vector from laser start to bubble center
            dx = grid_bubble.x - laser_start_x
            dy = grid_bubble.y - laser_start_y
            
            # Project bubble center onto laser direction
            proj_length = dx * laser_dir_x + dy * laser_dir_y
            
            # Only consider bubbles in front of the laser
            if proj_length < 0:
                continue
            
            # Closest point on laser ray to bubble center
            closest_x = laser_start_x + laser_dir_x * proj_length
            closest_y = laser_start_y + laser_dir_y * proj_length
            
            # Distance from bubble center to laser ray
            dist_to_line = math.sqrt((grid_bubble.x - closest_x)**2 + (grid_bubble.y - closest_y)**2)
            
            # Check if laser ray intersects the bubble
            if dist_to_line <= grid_bubble.radius:
                # Calculate the actual intersection point using line-circle intersection
                # Distance along the ray from closest point to intersection
                # Using Pythagorean theorem: radius^2 = dist_to_line^2 + offset^2
                offset = math.sqrt(grid_bubble.radius**2 - dist_to_line**2)
                
                # Intersection point is offset back along the ray from closest point
                # (towards laser start, so we get the first intersection)
                intersect_x = closest_x - laser_dir_x * offset
                intersect_y = closest_y - laser_dir_y * offset
                
                # Verify this point is in front of laser start (should be, but check)
                dist_to_intersect = math.sqrt((intersect_x - laser_start_x)**2 + (intersect_y - laser_start_y)**2)
                
                # Check if intersection is in the forward direction
                dot_product = (intersect_x - laser_start_x) * laser_dir_x + (intersect_y - laser_start_y) * laser_dir_y
                if dot_product > 0 and dist_to_intersect < min_distance:
                    min_distance = dist_to_intersect
                    hit_point_x = intersect_x
                    hit_point_y = intersect_y
        
        # If no bubble hit, extend laser to screen edge
        if hit_point_x is None:
            # Extend laser to screen edge
            max_length = max(self.width, self.height) * 2  # Long enough to reach edge
            hit_point_x = laser_start_x + laser_dir_x * max_length
            hit_point_y = laser_start_y + laser_dir_y * max_length
        
        # Draw laser target point/dot at hit location (no line, just the point)
        dot_size = 10 * self.scale
        # Outer glow of dot
        Color(1.0, 0.3, 0.5, 0.6)  # Pink-red glow
        Ellipse(pos=(hit_point_x - dot_size * 1.5, hit_point_y - dot_size * 1.5), 
               size=(dot_size * 3, dot_size * 3))
        
        # Main laser dot
        Color(1.0, 0.2, 0.4, 1.0)  # Bright pink-red
        Ellipse(pos=(hit_point_x - dot_size, hit_point_y - dot_size), 
               size=(dot_size * 2, dot_size * 2))
        
        # Inner bright core of dot
        Color(1.0, 0.5, 0.7, 1.0)  # Bright pink-white
        Ellipse(pos=(hit_point_x - dot_size * 0.5, hit_point_y - dot_size * 0.5), 
               size=(dot_size, dot_size))
    
    def draw_ui(self):
        """Draw UI elements with beautiful design"""
        if self.height > 0:
            # Ensure shots_remaining doesn't go below 0 for display
            display_shots = max(0, self.shots_remaining)
            
            # ===== SHOTS REMAINING (Bottom Left) =====
            shots_text = f'{display_shots}/{self.max_shots}'
            font_size = self.base_font_size_large * self.scale
            shots_label = CoreLabel(text=shots_text, 
                                  font_size=font_size, 
                                  color=(1, 1, 1, 1))
            shots_label.refresh()
            
            # Draw background panel with rounded corners effect
            panel_padding = 36 * self.scale  # 12 * 3
            panel_height = shots_label.texture.size[1] + panel_padding * 2
            panel_width = shots_label.texture.size[0] + panel_padding * 2 + 180 * self.scale  # Extra space for icon
            
            # Shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(45 * self.scale, 24 * self.scale), size=(panel_width, panel_height))
            
            # Main panel background (gradient effect with darker bottom)
            Color(0.15, 0.2, 0.3, 0.85)  # Dark blue-gray
            Rectangle(pos=(30 * self.scale, 30 * self.scale), size=(panel_width, panel_height))
            
            # Top highlight
            Color(0.3, 0.4, 0.5, 0.6)
            Rectangle(pos=(30 * self.scale, 30 * self.scale + panel_height - 9 * self.scale), size=(panel_width, 9 * self.scale))
            
            # Draw icon circle (bullet/target icon representation)
            icon_x = 30 * self.scale + panel_padding + 45 * self.scale
            icon_y = 30 * self.scale + panel_height / 2
            icon_radius = 36 * self.scale  # 12 * 3
            Color(1, 0.7, 0.2, 0.9)  # Gold/orange
            Ellipse(pos=(icon_x - icon_radius, icon_y - icon_radius), size=(icon_radius * 2, icon_radius * 2))
            Color(1, 0.9, 0.5, 1)  # Lighter gold
            inner_radius = 24 * self.scale  # 8 * 3
            Ellipse(pos=(icon_x - inner_radius, icon_y - inner_radius), size=(inner_radius * 2, inner_radius * 2))
            
            # Draw shots text
            text_x = icon_x + 60 * self.scale  # 20 * 3
            text_y = 30 * self.scale + panel_padding
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=shots_label.texture, 
                     pos=(text_x, text_y), 
                     size=shots_label.texture.size)
            
            # ===== LEVEL NUMBER (Above Score Box) =====
            level_text = f'Level {self.level}'
            level_font_size = self.base_font_size_medium * self.scale
            level_label = CoreLabel(text=level_text, 
                                  font_size=level_font_size, 
                                  color=(1, 1, 1, 1))
            level_label.refresh()
            
            # ===== SCORE (Bottom Right) =====
            score_text = f'{self.score:,}'  # Add comma formatting
            score_font_size = self.base_font_size_large * self.scale
            score_label = CoreLabel(text=score_text, 
                                  font_size=score_font_size, 
                                  color=(1, 1, 1, 1))
            score_label.refresh()
            
            # Score panel dimensions
            score_panel_padding = 24 * self.scale  # Reduced from 36
            score_panel_height = score_label.texture.size[1] + score_panel_padding * 2
            score_panel_width = score_label.texture.size[0] + score_panel_padding * 2 + 120 * self.scale + 160 * self.scale  # Reduced extra space for stars (from 180+240)
            
            # Calculate position for bottom right
            score_panel_x = self.width - score_panel_width - 30 * self.scale
            
            # Level number position (above score box)
            level_y_offset = level_label.texture.size[1] + 15 * self.scale  # Space between level and score box
            level_panel_y = 30 * self.scale + score_panel_height + level_y_offset
            
            # Draw level number background (small panel above score) - use only text width, not score panel width
            level_panel_width = level_label.texture.size[0] + 40 * self.scale  # Reduced from 60, and no longer matches score panel width
            level_panel_height = level_label.texture.size[1] + 18 * self.scale  # Reduced from 24
            
            # Level panel shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(score_panel_x + 15 * self.scale, level_panel_y - 6 * self.scale), size=(level_panel_width, level_panel_height))
            
            # Level panel background
            Color(0.2, 0.15, 0.3, 0.85)  # Same color as score panel
            Rectangle(pos=(score_panel_x, level_panel_y), size=(level_panel_width, level_panel_height))
            
            # Level panel top highlight
            Color(0.4, 0.3, 0.5, 0.6)
            Rectangle(pos=(score_panel_x, level_panel_y + level_panel_height - 9 * self.scale), size=(level_panel_width, 9 * self.scale))
            
            # Draw level text (centered in level panel)
            level_text_x = score_panel_x + (level_panel_width - level_label.texture.size[0]) / 2
            level_text_y = level_panel_y + 12 * self.scale
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=level_label.texture, 
                     pos=(level_text_x, level_text_y), 
                     size=level_label.texture.size)
            
            # Score box shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(score_panel_x + 15 * self.scale, 24 * self.scale), size=(score_panel_width, score_panel_height))
            
            # Score box main panel background
            Color(0.2, 0.15, 0.3, 0.85)  # Dark purple-gray
            Rectangle(pos=(score_panel_x, 30 * self.scale), size=(score_panel_width, score_panel_height))
            
            # Score box top highlight
            Color(0.4, 0.3, 0.5, 0.6)
            Rectangle(pos=(score_panel_x, 30 * self.scale + score_panel_height - 9 * self.scale), size=(score_panel_width, 9 * self.scale))
            
            # Draw star/medal icon
            score_icon_x = score_panel_x + score_panel_padding + 45 * self.scale
            score_icon_y = 30 * self.scale + score_panel_height / 2
            icon_radius = 30 * self.scale  # 10 * 3
            Color(1, 0.8, 0.2, 0.9)  # Gold
            # Draw filled star using circles (simplified)
            Ellipse(pos=(score_icon_x - icon_radius, score_icon_y - icon_radius), size=(icon_radius * 2, icon_radius * 2))
            Color(1, 0.95, 0.5, 1)  # Lighter gold
            inner_radius = 18 * self.scale  # 6 * 3
            Ellipse(pos=(score_icon_x - inner_radius, score_icon_y - inner_radius), size=(inner_radius * 2, inner_radius * 2))
            
            # Draw score text
            score_text_x = score_icon_x + 60 * self.scale  # 20 * 3
            score_text_y = 30 * self.scale + score_panel_padding
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=score_label.texture, 
                     pos=(score_text_x, score_text_y), 
                     size=score_label.texture.size)
            
            # Draw three achievement stars next to score
            stars_start_x = score_text_x + score_label.texture.size[0] + 45 * self.scale
            stars_y = 30 * self.scale + score_panel_height / 2
            star_size = 48 * self.scale  # 16 * 3
            star_spacing = 60 * self.scale  # 20 * 3
            
            for i in range(3):
                star_x = stars_start_x + i * star_spacing
                star_center_y = stars_y
                
                # Determine if star should be gold based on score thresholds
                thresholds = [500, 1000, 2000]
                is_gold = self.score > thresholds[i]
                
                # Draw star shape (5-pointed star)
                outer_radius = star_size / 2
                inner_radius = outer_radius * 0.4
                num_points = 5
                
                # Calculate star points
                star_points = []
                for j in range(num_points * 2):
                    angle = (j * math.pi / num_points) - math.pi / 2  # Start from top
                    if j % 2 == 0:
                        # Outer point
                        radius = outer_radius
                    else:
                        # Inner point
                        radius = inner_radius
                    px = star_x + radius * math.cos(angle)
                    py = star_center_y + radius * math.sin(angle)
                    star_points.extend([px, py])
                
                if is_gold:
                    # Gold star - outer glow
                    Color(1, 0.8, 0.2, 0.4)  # Gold glow with transparency
                    glow_points = []
                    for j in range(num_points * 2):
                        angle = (j * math.pi / num_points) - math.pi / 2
                        if j % 2 == 0:
                            radius = outer_radius + 2
                        else:
                            radius = inner_radius + 1
                        px = star_x + radius * math.cos(angle)
                        py = star_center_y + radius * math.sin(angle)
                        glow_points.extend([px, py])
                    # Draw glow (simplified as filled shape)
                    for k in range(len(glow_points) // 2 - 1):
                        Line(points=[glow_points[k*2], glow_points[k*2+1], 
                                    glow_points[(k+1)*2], glow_points[(k+1)*2+1]], width=9 * self.scale)  # 3 * 3
                    
                    # Gold star - main
                    Color(1, 0.85, 0.3, 1)  # Bright gold
                    Line(points=star_points, width=6 * self.scale, close=True)  # 2 * 3
                    # Fill star (simplified - draw lines to center)
                    for k in range(0, len(star_points), 2):
                        Line(points=[star_x, star_center_y, star_points[k], star_points[k+1]], width=3 * self.scale)  # 1 * 3
                    
                    # Gold star - highlight (inner glow)
                    Color(1, 0.95, 0.6, 0.8)  # Light gold
                    highlight_radius = inner_radius * 0.5
                    Ellipse(pos=(star_x - highlight_radius, star_center_y - highlight_radius), 
                           size=(highlight_radius * 2, highlight_radius * 2))
                else:
                    # Gray star - outer
                    Color(0.3, 0.3, 0.3, 0.5)  # Dark gray with transparency
                    Line(points=star_points, width=6 * self.scale, close=True)  # 2 * 3
                    # Fill star
                    for k in range(0, len(star_points), 2):
                        Line(points=[star_x, star_center_y, star_points[k], star_points[k+1]], width=3 * self.scale)  # 1 * 3
                    
                    # Gray star - inner
                    Color(0.5, 0.5, 0.5, 0.6)  # Lighter gray
                    inner_highlight_radius = inner_radius * 0.5
                    Ellipse(pos=(star_x - inner_highlight_radius, star_center_y - inner_highlight_radius), 
                           size=(inner_highlight_radius * 2, inner_highlight_radius * 2))
            
            # Draw beautiful game over screen with buttons
            if not self.game_active:
                # Check if won: either no bubbles left, or only falling bubbles (which are already scored)
                has_attached_bubbles = any(not bubble.falling for bubble in self.grid_bubbles)
                won = len(self.grid_bubbles) == 0 or not has_attached_bubbles
                center_x = self.width / 2
                center_y = self.height / 2
                
                # Draw dark overlay background
                Color(0, 0, 0, 0.75)  # Dark semi-transparent overlay
                Rectangle(pos=(0, 0), size=(self.width, self.height))
                
                # Draw main panel background with shadow - scaled
                panel_width = self.base_panel_width * self.scale
                panel_height = self.base_panel_height * self.scale
                panel_x = center_x - panel_width / 2
                panel_y = center_y - panel_height / 2
                
                # Shadow
                Color(0, 0, 0, 0.5)
                Rectangle(pos=(panel_x + 15 * self.scale, panel_y - 15 * self.scale), size=(panel_width, panel_height))
                
                # Main panel background
                if won:
                    Color(0.1, 0.3, 0.2, 0.95)  # Dark green for win
                else:
                    Color(0.3, 0.1, 0.1, 0.95)  # Dark red for loss
                Rectangle(pos=(panel_x, panel_y), size=(panel_width, panel_height))
                
                # Panel border
                Color(1, 1, 1, 0.3)
                Line(rectangle=(panel_x, panel_y, panel_width, panel_height), width=6 * self.scale)
                
                # Top highlight
                if won:
                    Color(0.2, 0.6, 0.4, 0.8)
                else:
                    Color(0.6, 0.2, 0.2, 0.8)
                Rectangle(pos=(panel_x, panel_y + panel_height - 15 * self.scale), size=(panel_width, 15 * self.scale))
                
                # Draw title
                if won:
                    title_text = 'YOU WIN!'
                    title_color = (0.3, 1, 0.5, 1)  # Bright green
                else:
                    title_text = 'GAME OVER'
                    title_color = (1, 0.3, 0.3, 1)  # Bright red
                
                title_font_size = 96 * self.scale  # 32 * 3
                title_label = CoreLabel(text=title_text, 
                                      font_size=title_font_size, 
                                      color=title_color)
                title_label.refresh()
                title_x = center_x - title_label.texture.size[0] / 2
                title_y = panel_y + panel_height - 150 * self.scale  # 50 * 3
                Color(1, 1, 1, 1)
                Rectangle(texture=title_label.texture,
                         pos=(title_x, title_y),
                         size=title_label.texture.size)
                
                # Draw score display
                score_text = f'Final Score: {self.score:,}'
                score_font_size = 60 * self.scale  # 20 * 3
                score_label = CoreLabel(text=score_text,
                                      font_size=score_font_size,
                                      color=(1, 1, 1, 1))
                score_label.refresh()
                score_x = center_x - score_label.texture.size[0] / 2
                score_y = title_y - 105 * self.scale  # 35 * 3
                Color(1, 1, 1, 1)
                Rectangle(texture=score_label.texture,
                         pos=(score_x, score_y),
                         size=score_label.texture.size)
                
                # Draw buttons - scaled
                button_width = self.base_button_width * self.scale
                button_height = self.base_button_height * self.scale
                button_spacing = self.base_button_spacing * self.scale
                button_y = panel_y + 90 * self.scale  # 30 * 3
                
                # Retry button
                retry_x = center_x - button_width - button_spacing / 2
                self.draw_button(retry_x, button_y, button_width, button_height, 
                               'RETRY', (0.2, 0.5, 0.8, 1))
                
                # Next level button (only if won)
                if won:
                    next_level_x = center_x + button_spacing / 2
                    self.draw_button(next_level_x, button_y, button_width, button_height,
                                   'NEXT', (0.2, 0.8, 0.4, 1))
    
    def draw_loading_screen(self):
        """Draw loading screen"""
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Draw dark overlay background
        Color(0, 0, 0, 0.85)  # Darker overlay for loading
        Rectangle(pos=(0, 0), size=(self.width, self.height))
        
        # Draw loading panel - scaled
        panel_width = 750 * self.scale  # 250 * 3
        panel_height = 450 * self.scale  # 150 * 3
        panel_x = center_x - panel_width / 2
        panel_y = center_y - panel_height / 2
        
        # Shadow
        Color(0, 0, 0, 0.5)
        Rectangle(pos=(panel_x + 15 * self.scale, panel_y - 15 * self.scale), size=(panel_width, panel_height))
        
        # Main panel background
        Color(0.15, 0.15, 0.2, 0.95)  # Dark blue-gray
        Rectangle(pos=(panel_x, panel_y), size=(panel_width, panel_height))
        
        # Panel border
        Color(1, 1, 1, 0.3)
        Line(rectangle=(panel_x, panel_y, panel_width, panel_height), width=6 * self.scale)
        
        # Top highlight
        Color(0.3, 0.4, 0.6, 0.8)
        Rectangle(pos=(panel_x, panel_y + panel_height - 15 * self.scale), size=(panel_width, 15 * self.scale))
        
        # Draw "Loading..." text
        loading_font_size = 84 * self.scale  # 28 * 3
        loading_label = CoreLabel(text='Loading...', 
                                 font_size=loading_font_size, 
                                 color=(1, 1, 1, 1))
        loading_label.refresh()
        loading_x = center_x - loading_label.texture.size[0] / 2
        loading_y = panel_y + panel_height - 150 * self.scale  # 50 * 3
        Color(1, 1, 1, 1)
        Rectangle(texture=loading_label.texture,
                 pos=(loading_x, loading_y),
                 size=loading_label.texture.size)
        
        # Draw animated loading spinner (simple pulsing dots) - scaled
        spinner_y = panel_y + 180 * self.scale  # 60 * 3
        spinner_radius = 24 * self.scale  # 8 * 3
        spinner_spacing = 60 * self.scale  # 20 * 3
        spinner_start_x = center_x - (spinner_spacing * 2)
        
        # Animate spinner based on time (simple pulsing effect)
        import time
        current_time = time.time()
        pulse_phase = int(current_time * 2) % 3  # Cycle through 0, 1, 2
        
        for i in range(3):
            dot_x = spinner_start_x + i * spinner_spacing
            # Pulse the current dot
            alpha = 1.0 if i == pulse_phase else 0.4
            Color(0.5, 0.7, 1, alpha)  # Light blue
            Ellipse(pos=(dot_x - spinner_radius, spinner_y - spinner_radius),
                   size=(spinner_radius * 2, spinner_radius * 2))
    
    def draw_button(self, x, y, width, height, text, color):
        """Draw a beautiful button"""
        # Shadow
        Color(0, 0, 0, 0.4)
        shadow_offset = 6 * self.scale  # 2 * 3
        Rectangle(pos=(x + shadow_offset, y - shadow_offset), size=(width, height))
        
        # Button background
        Color(color[0], color[1], color[2], color[3])
        Rectangle(pos=(x, y), size=(width, height))
        
        # Button border
        Color(1, 1, 1, 0.3)
        Line(rectangle=(x, y, width, height), width=6 * self.scale)  # 2 * 3
        
        # Top highlight
        Color(1, 1, 1, 0.2)
        Rectangle(pos=(x, y + height - 9 * self.scale), size=(width, 9 * self.scale))  # 3 * 3
        
        # Button text
        button_font_size = 60 * self.scale  # 20 * 3
        text_label = CoreLabel(text=text, font_size=button_font_size, color=(1, 1, 1, 1))
        text_label.refresh()
        text_x = x + (width - text_label.texture.size[0]) / 2
        text_y = y + (height - text_label.texture.size[1]) / 2
        Color(1, 1, 1, 1)
        Rectangle(texture=text_label.texture,
                 pos=(text_x, text_y),
                 size=text_label.texture.size)
