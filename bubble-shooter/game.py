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

# Element types
FIRE = 0
WATER = 1
EARTH = 2
AIR = 3

# Element colors (RGB values 0-1) - Enhanced colors
ELEMENT_COLORS = {
    FIRE: (1.0, 0.4, 0.2),      # Orange/Red
    WATER: (0.2, 0.7, 1.0),     # Blue
    EARTH: (0.6, 0.4, 0.2),     # Brown
    AIR: (0.9, 0.95, 1.0)       # Light Blue/White
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
        
        # Load level configuration
        if level is None:
            # Default level if none provided
            from levels.level1 import Level1
            level = Level1()
        
        # Store level object for restart/next level functionality
        self.current_level = level
        level_config = level.get_config()
        
        # Game settings from level
        self.bubble_radius = level_config['bubble_radius']
        self.grid_width = level_config['grid_width']
        self.grid_height = level_config['grid_height']
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = level_config['grid_start_x']
        self.grid_start_y = level_config['grid_start_y']
        
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
        
        # Shooter
        self.shooter_x = 180  # Center of screen (360/2)
        self.shooter_y = 50  # Bottom of screen (rotated 180 degrees)
        self.aim_angle = 90  # Degrees (90 = straight up)
        self.current_bubble = None
        
        # Background image
        self.background_texture = None
        self.load_background_image()
        
        # Dynamite image
        self.dynamite_texture = None
        self.load_dynamite_image()
        
        # Mine image
        self.mine_texture = None
        self.load_mine_image()
        
        # Initialize
        self.initialize_grid()
        self.load_next_bubble()
        
        # Note: on_touch_down, on_touch_move, on_touch_up are automatically
        # connected by Kivy when using these method names
        
    def initialize_grid(self):
        """Create initial bubble grid - ensures no intersections"""
        self.grid_bubbles = []
        
        # Ensure grid spacing is sufficient (minimum 2 * radius)
        min_spacing = self.bubble_radius * 2.1  # Slightly more than 2 * radius
        if self.grid_spacing < min_spacing:
            self.grid_spacing = min_spacing
        
        # Check if level has custom pattern method
        has_custom_pattern = hasattr(self.current_level, 'should_place_bubble')
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # Check custom pattern if available
                if has_custom_pattern:
                    if not self.current_level.should_place_bubble(row, col):
                        continue  # Skip this position based on custom pattern
                
                # Offset every other row for hexagonal pattern
                x_offset = (self.grid_spacing * 0.5) if (row % 2 == 1) else 0
                x = self.grid_start_x + col * self.grid_spacing + x_offset
                y = self.grid_start_y - row * self.grid_spacing * 0.866
                
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
                
                # Set bubble position at shooter tip before shooting
                angle_rad = math.radians(self.aim_angle)
                shooter_length = 40
                self.current_bubble.x = self.shooter_x + math.cos(angle_rad) * shooter_length
                self.current_bubble.y = self.shooter_y + math.sin(angle_rad) * shooter_length
                
                # Normalize direction and set velocity
                speed = 400  # pixels per second
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
        
        # Panel dimensions (matching draw_ui)
        panel_width = 280
        panel_height = 200
        panel_x = center_x - panel_width / 2
        panel_y = center_y - panel_height / 2
        
        # Button dimensions and positions (EXACTLY matching draw_ui)
        button_width = 120
        button_height = 45
        button_spacing = 20
        button_y = panel_y + 30  # Match draw_ui exactly
        
        # Retry button position
        retry_x = center_x - button_width - button_spacing / 2
        
        # Next level button position (only show if won)
        next_level_x = center_x + button_spacing / 2
        
        won = len(self.grid_bubbles) == 0
        
        # Check retry button click - use larger hit area for better responsiveness
        hit_margin = 5  # Add margin for easier clicking
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
        self.game_active = True
        self.is_loading = False
        self.max_shots = level_config['max_shots']
        self.shots_remaining = level_config['shots_remaining']
        
        # Reset grid position from level config
        self.grid_start_x = level_config['grid_start_x']
        self.grid_start_y = level_config['grid_start_y']
        
        # Clear bubbles
        self.grid_bubbles = []
        self.shot_bubbles = []
        self.current_bubble = None
        
        # Reinitialize
        self.initialize_grid()
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
            # For now, restart Level 3 (can add more levels later)
            from levels.level3 import Level3
            self.current_level = Level3()
        else:
            # Default: restart current level
            pass
        
        self.restart_game()
    
    def update(self, dt):
        """Update game state (called every frame)"""
        # Update shooter position to bottom center of screen (rotated 180 degrees)
        if self.height > 0:
            self.shooter_y = 50  # Position near bottom
            self.shooter_x = self.width / 2  # Center horizontally
            # Don't override grid_start_x and grid_start_y - they should remain from level config
            # Only update if they haven't been set yet (initial load)
            if not hasattr(self, '_grid_position_initialized'):
                level_config = self.current_level.get_config()
                self.grid_start_x = level_config['grid_start_x']
                self.grid_start_y = level_config['grid_start_y']
                self._grid_position_initialized = True
        
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
                self.draw_ui()
            return
        
        # No longer need to update falling bubbles - disconnected bubbles are removed immediately
        
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
                self.grid_bubbles.remove(bubble)
                exploded_count += 1
        
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
                self.grid_bubbles.remove(bubble)
                exploded_count += 1
        
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
    
    def load_background_image(self):
        """Load background image texture"""
        background_path = r"C:\Users\aminz\OneDrive\Documents\GitHub\bubble-shooter\bubble-shooter\bubble-shooter\asset\grunge-white-surface-rough-background-textured.jpg"
        if os.path.exists(background_path):
            try:
                img = CoreImage(background_path)
                self.background_texture = img.texture
            except Exception as e:
                print(f"Error loading background image: {e}")
                self.background_texture = None
        else:
            print(f"Background image not found: {background_path}")
            self.background_texture = None
    
    def load_dynamite_image(self):
        """Load dynamite image texture with white background removed"""
        dynamite_path = r"C:\Users\aminz\OneDrive\Documents\GitHub\bubble-shooter\bubble-shooter\bubble-shooter\asset\istockphoto-1139873743-612x612.jpg"
        if os.path.exists(dynamite_path):
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
            print(f"Dynamite image not found: {dynamite_path}")
            self.dynamite_texture = None
    
    def load_mine_image(self):
        """Load mine image texture with white background removed"""
        mine_path = r"C:\Users\aminz\OneDrive\Documents\GitHub\bubble-shooter\bubble-shooter\bubble-shooter\asset\istockphoto-1474907248-612x612.jpg"
        if os.path.exists(mine_path):
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
            print(f"Mine image not found: {mine_path}")
            self.mine_texture = None
    
    def draw_background(self):
        """Draw game background using image"""
        if self.background_texture and self.width > 0 and self.height > 0:
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
        
        # Real bubbles are semi-transparent, so we'll use the color but with transparency
        
        # 1. Draw subtle shadow (real bubbles cast soft shadows)
        shadow_offset = 2
        Color(0, 0, 0, 0.15)  # Very subtle shadow
        Ellipse(pos=(x - radius + shadow_offset, y - radius - shadow_offset),
               size=(radius * 2, radius * 2))
        
        # 2. Draw main bubble body - semi-transparent with color tint
        # Real bubbles are mostly transparent with a slight color tint
        bubble_alpha = 0.3  # Transparency (lower = more transparent)
        Color(color[0], color[1], color[2], bubble_alpha)
        Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))
        
        # 3. Draw thin colored rim/edge (like real bubbles have)
        # Real bubbles have a thin colored edge
        rim_width = 1.5
        Color(color[0], color[1], color[2], 0.6)  # More opaque on edges
        Line(circle=(x, y, radius), width=rim_width)
        
        # 4. Draw subtle color rim (prismatic effect on edges)
        # Real bubbles can have color fringing
        Color(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, 0.4)
        Line(circle=(x, y, radius - 0.5), width=1)
        
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
                Line(points=[x, fuse_y, x, fuse_y + fuse_length], width=2)
                # Draw fuse tip (small circle)
                Color(1, 0.3, 0, 0.9)  # Orange-red for lit fuse
                Ellipse(pos=(x - 2, fuse_y + fuse_length - 2), size=(4, 4))
        
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
                Line(points=triangle_points, width=2, close=True)
                
                # Fill triangle slightly
                Color(1, 0.9, 0.3, 0.6)  # Lighter yellow fill
                # Draw filled triangle using multiple lines (simplified)
                for i in range(len(triangle_points) // 2 - 1):
                    Line(points=[x, y, triangle_points[i*2], triangle_points[i*2+1]], width=1)
                
                # Draw exclamation mark in center
                Color(1, 0.2, 0.2, 1)  # Red for exclamation
                # Exclamation mark line
                Line(points=[x, y - mine_size * 0.15, x, y + mine_size * 0.15], width=2)
                # Exclamation mark dot
                Ellipse(pos=(x - 2, y + mine_size * 0.2), size=(4, 4))
    
    def draw_shooter(self):
        """Draw shooter and current bubble with 3D effects"""
        x, y = self.shooter_x, self.shooter_y
        shooter_length = 40
        shooter_width = 8
        
        # Convert angle to radians
        angle_rad = math.radians(self.aim_angle)
        
        # Calculate shooter end point
        end_x = x + math.cos(angle_rad) * shooter_length
        end_y = y + math.sin(angle_rad) * shooter_length
        
        # Draw shooter base/cannon (circular base)
        Color(0.3, 0.3, 0.3)  # Dark gray
        Ellipse(pos=(x - 15, y - 15), size=(30, 30))
        
        # Draw shooter barrel (rotating)
        # Use PushMatrix/PopMatrix for rotation (simulated with line)
        Color(0.5, 0.5, 0.5)  # Medium gray
        Line(points=[x, y, end_x, end_y], width=shooter_width)
        
        # Draw shooter tip (small circle at end)
        Color(0.4, 0.4, 0.4)  # Slightly darker gray
        Ellipse(pos=(end_x - 5, end_y - 5), size=(10, 10))
        
        # Draw current bubble with 3D effect (positioned at shooter tip)
        if self.current_bubble and not self.current_bubble.attached:
            # Draw bubble at shooter tip position without modifying bubble properties
            self.draw_bubble_3d(self.current_bubble, x=end_x, y=end_y)
        
        # Draw aim line (shows current aim direction)
        aim_line_length = 100
        aim_end_x = x + math.cos(angle_rad) * aim_line_length
        aim_end_y = y + math.sin(angle_rad) * aim_line_length
        
        Color(1, 1, 1, 0.4)  # White, semi-transparent
        Line(points=[x, y, aim_end_x, aim_end_y], width=2)
    
    def draw_ui(self):
        """Draw UI elements with beautiful design"""
        if self.height > 0:
            # Ensure shots_remaining doesn't go below 0 for display
            display_shots = max(0, self.shots_remaining)
            
            # ===== SHOTS REMAINING (Bottom Left) =====
            shots_text = f'{display_shots}/{self.max_shots}'
            shots_label = CoreLabel(text=shots_text, 
                                  font_size=24, 
                                  color=(1, 1, 1, 1))
            shots_label.refresh()
            
            # Draw background panel with rounded corners effect
            panel_padding = 12
            panel_height = shots_label.texture.size[1] + panel_padding * 2
            panel_width = shots_label.texture.size[0] + panel_padding * 2 + 60  # Extra space for icon
            
            # Shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(15, 8), size=(panel_width, panel_height))
            
            # Main panel background (gradient effect with darker bottom)
            Color(0.15, 0.2, 0.3, 0.85)  # Dark blue-gray
            Rectangle(pos=(10, 10), size=(panel_width, panel_height))
            
            # Top highlight
            Color(0.3, 0.4, 0.5, 0.6)
            Rectangle(pos=(10, 10 + panel_height - 3), size=(panel_width, 3))
            
            # Draw icon circle (bullet/target icon representation)
            icon_x = 10 + panel_padding + 15
            icon_y = 10 + panel_height / 2
            Color(1, 0.7, 0.2, 0.9)  # Gold/orange
            Ellipse(pos=(icon_x - 12, icon_y - 12), size=(24, 24))
            Color(1, 0.9, 0.5, 1)  # Lighter gold
            Ellipse(pos=(icon_x - 8, icon_y - 8), size=(16, 16))
            
            # Draw shots text
            text_x = icon_x + 20
            text_y = 10 + panel_padding
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=shots_label.texture, 
                     pos=(text_x, text_y), 
                     size=shots_label.texture.size)
            
            # ===== LEVEL NUMBER (Above Score Box) =====
            level_text = f'Level {self.level}'
            level_label = CoreLabel(text=level_text, 
                                  font_size=18, 
                                  color=(1, 1, 1, 1))
            level_label.refresh()
            
            # ===== SCORE (Bottom Right) =====
            score_text = f'{self.score:,}'  # Add comma formatting
            score_label = CoreLabel(text=score_text, 
                                  font_size=24, 
                                  color=(1, 1, 1, 1))
            score_label.refresh()
            
            # Score panel dimensions
            score_panel_padding = 12
            score_panel_height = score_label.texture.size[1] + score_panel_padding * 2
            score_panel_width = score_label.texture.size[0] + score_panel_padding * 2 + 60 + 80  # Extra space for stars + 80  # Extra space for stars
            
            # Calculate position for bottom right
            score_panel_x = self.width - score_panel_width - 10
            
            # Level number position (above score box)
            level_y_offset = level_label.texture.size[1] + 5  # Space between level and score box
            level_panel_y = 10 + score_panel_height + level_y_offset
            
            # Draw level number background (small panel above score)
            level_panel_width = max(score_panel_width, level_label.texture.size[0] + 20)
            level_panel_height = level_label.texture.size[1] + 8
            
            # Level panel shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(score_panel_x + 5, level_panel_y - 2), size=(level_panel_width, level_panel_height))
            
            # Level panel background
            Color(0.2, 0.15, 0.3, 0.85)  # Same color as score panel
            Rectangle(pos=(score_panel_x, level_panel_y), size=(level_panel_width, level_panel_height))
            
            # Level panel top highlight
            Color(0.4, 0.3, 0.5, 0.6)
            Rectangle(pos=(score_panel_x, level_panel_y + level_panel_height - 3), size=(level_panel_width, 3))
            
            # Draw level text (centered in level panel)
            level_text_x = score_panel_x + (level_panel_width - level_label.texture.size[0]) / 2
            level_text_y = level_panel_y + 4
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=level_label.texture, 
                     pos=(level_text_x, level_text_y), 
                     size=level_label.texture.size)
            
            # Score box shadow
            Color(0, 0, 0, 0.3)
            Rectangle(pos=(score_panel_x + 5, 8), size=(score_panel_width, score_panel_height))
            
            # Score box main panel background
            Color(0.2, 0.15, 0.3, 0.85)  # Dark purple-gray
            Rectangle(pos=(score_panel_x, 10), size=(score_panel_width, score_panel_height))
            
            # Score box top highlight
            Color(0.4, 0.3, 0.5, 0.6)
            Rectangle(pos=(score_panel_x, 10 + score_panel_height - 3), size=(score_panel_width, 3))
            
            # Draw star/medal icon
            score_icon_x = score_panel_x + score_panel_padding + 15
            score_icon_y = 10 + score_panel_height / 2
            Color(1, 0.8, 0.2, 0.9)  # Gold
            # Draw star shape (simplified as diamond)
            star_points = [
                score_icon_x, score_icon_y + 10,  # Top
                score_icon_x - 8, score_icon_y,  # Left
                score_icon_x, score_icon_y - 10,  # Bottom
                score_icon_x + 8, score_icon_y,  # Right
            ]
            # Draw filled star using triangles (simplified as circle with highlight)
            Ellipse(pos=(score_icon_x - 10, score_icon_y - 10), size=(20, 20))
            Color(1, 0.95, 0.5, 1)  # Lighter gold
            Ellipse(pos=(score_icon_x - 6, score_icon_y - 6), size=(12, 12))
            
            # Draw score text
            score_text_x = score_icon_x + 20
            score_text_y = 10 + score_panel_padding
            Color(1, 1, 1, 1)  # White text
            Rectangle(texture=score_label.texture, 
                     pos=(score_text_x, score_text_y), 
                     size=score_label.texture.size)
            
            # Draw three achievement stars next to score
            stars_start_x = score_text_x + score_label.texture.size[0] + 15
            stars_y = 10 + score_panel_height / 2
            star_size = 16
            star_spacing = 20
            
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
                                    glow_points[(k+1)*2], glow_points[(k+1)*2+1]], width=3)
                    
                    # Gold star - main
                    Color(1, 0.85, 0.3, 1)  # Bright gold
                    Line(points=star_points, width=2, close=True)
                    # Fill star (simplified - draw lines to center)
                    for k in range(0, len(star_points), 2):
                        Line(points=[star_x, star_center_y, star_points[k], star_points[k+1]], width=1)
                    
                    # Gold star - highlight (inner glow)
                    Color(1, 0.95, 0.6, 0.8)  # Light gold
                    highlight_radius = inner_radius * 0.5
                    Ellipse(pos=(star_x - highlight_radius, star_center_y - highlight_radius), 
                           size=(highlight_radius * 2, highlight_radius * 2))
                else:
                    # Gray star - outer
                    Color(0.3, 0.3, 0.3, 0.5)  # Dark gray with transparency
                    Line(points=star_points, width=2, close=True)
                    # Fill star
                    for k in range(0, len(star_points), 2):
                        Line(points=[star_x, star_center_y, star_points[k], star_points[k+1]], width=1)
                    
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
                
                # Draw main panel background with shadow
                panel_width = 280
                panel_height = 200
                panel_x = center_x - panel_width / 2
                panel_y = center_y - panel_height / 2
                
                # Shadow
                Color(0, 0, 0, 0.5)
                Rectangle(pos=(panel_x + 5, panel_y - 5), size=(panel_width, panel_height))
                
                # Main panel background
                if won:
                    Color(0.1, 0.3, 0.2, 0.95)  # Dark green for win
                else:
                    Color(0.3, 0.1, 0.1, 0.95)  # Dark red for loss
                Rectangle(pos=(panel_x, panel_y), size=(panel_width, panel_height))
                
                # Panel border
                Color(1, 1, 1, 0.3)
                Line(rectangle=(panel_x, panel_y, panel_width, panel_height), width=2)
                
                # Top highlight
                if won:
                    Color(0.2, 0.6, 0.4, 0.8)
                else:
                    Color(0.6, 0.2, 0.2, 0.8)
                Rectangle(pos=(panel_x, panel_y + panel_height - 5), size=(panel_width, 5))
                
                # Draw title
                if won:
                    title_text = 'YOU WIN!'
                    title_color = (0.3, 1, 0.5, 1)  # Bright green
                else:
                    title_text = 'GAME OVER'
                    title_color = (1, 0.3, 0.3, 1)  # Bright red
                
                title_label = CoreLabel(text=title_text, 
                                      font_size=32, 
                                      color=title_color)
                title_label.refresh()
                title_x = center_x - title_label.texture.size[0] / 2
                title_y = panel_y + panel_height - 50
                Color(1, 1, 1, 1)
                Rectangle(texture=title_label.texture,
                         pos=(title_x, title_y),
                         size=title_label.texture.size)
                
                # Draw score display
                score_text = f'Final Score: {self.score:,}'
                score_label = CoreLabel(text=score_text,
                                      font_size=20,
                                      color=(1, 1, 1, 1))
                score_label.refresh()
                score_x = center_x - score_label.texture.size[0] / 2
                score_y = title_y - 35
                Color(1, 1, 1, 1)
                Rectangle(texture=score_label.texture,
                         pos=(score_x, score_y),
                         size=score_label.texture.size)
                
                # Draw buttons
                button_width = 120
                button_height = 45
                button_spacing = 20
                button_y = panel_y + 30
                
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
        
        # Draw loading panel
        panel_width = 250
        panel_height = 150
        panel_x = center_x - panel_width / 2
        panel_y = center_y - panel_height / 2
        
        # Shadow
        Color(0, 0, 0, 0.5)
        Rectangle(pos=(panel_x + 5, panel_y - 5), size=(panel_width, panel_height))
        
        # Main panel background
        Color(0.15, 0.15, 0.2, 0.95)  # Dark blue-gray
        Rectangle(pos=(panel_x, panel_y), size=(panel_width, panel_height))
        
        # Panel border
        Color(1, 1, 1, 0.3)
        Line(rectangle=(panel_x, panel_y, panel_width, panel_height), width=2)
        
        # Top highlight
        Color(0.3, 0.4, 0.6, 0.8)
        Rectangle(pos=(panel_x, panel_y + panel_height - 5), size=(panel_width, 5))
        
        # Draw "Loading..." text
        loading_label = CoreLabel(text='Loading...', 
                                 font_size=28, 
                                 color=(1, 1, 1, 1))
        loading_label.refresh()
        loading_x = center_x - loading_label.texture.size[0] / 2
        loading_y = panel_y + panel_height - 50
        Color(1, 1, 1, 1)
        Rectangle(texture=loading_label.texture,
                 pos=(loading_x, loading_y),
                 size=loading_label.texture.size)
        
        # Draw animated loading spinner (simple pulsing dots)
        spinner_y = panel_y + 60
        spinner_radius = 8
        spinner_spacing = 20
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
        Rectangle(pos=(x + 2, y - 2), size=(width, height))
        
        # Button background
        Color(color[0], color[1], color[2], color[3])
        Rectangle(pos=(x, y), size=(width, height))
        
        # Button border
        Color(1, 1, 1, 0.3)
        Line(rectangle=(x, y, width, height), width=2)
        
        # Top highlight
        Color(1, 1, 1, 0.2)
        Rectangle(pos=(x, y + height - 3), size=(width, 3))
        
        # Button text
        text_label = CoreLabel(text=text, font_size=20, color=(1, 1, 1, 1))
        text_label.refresh()
        text_x = x + (width - text_label.texture.size[0]) / 2
        text_y = y + (height - text_label.texture.size[1]) / 2
        Color(1, 1, 1, 1)
        Rectangle(texture=text_label.texture,
                 pos=(text_x, text_y),
                 size=text_label.texture.size)
