"""
Bubble Shooter Game - Main game logic with 3D-style graphics
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, PushMatrix, PopMatrix
from kivy.clock import Clock
import random
import math

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
    
    def update(self, dt):
        """Update bubble position"""
        if not self.attached:
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Game settings
        self.bubble_radius = 20
        self.grid_width = 10
        self.grid_height = 12
        # Grid spacing must be at least 2 * radius to prevent intersection
        self.grid_spacing = max(45, self.bubble_radius * 2.2)  # 2.2 * radius ensures no overlap
        self.grid_start_x = 50
        self.grid_start_y = 500
        
        # Game state
        self.score = 0
        self.level = 1
        self.game_active = True
        
        # Bubbles
        self.grid_bubbles = []  # Bubbles in grid
        self.shot_bubbles = []  # Currently shot bubble
        self.next_bubble = None  # Next bubble to shoot
        
        # Shooter
        self.shooter_x = 180  # Center of screen (360/2)
        self.shooter_y = 600  # Top of screen
        self.aim_angle = -90  # Degrees (-90 = straight down)
        self.current_bubble = None
        
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
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # Offset every other row for hexagonal pattern
                x_offset = (self.grid_spacing * 0.5) if (row % 2 == 1) else 0
                x = self.grid_start_x + col * self.grid_spacing + x_offset
                y = self.grid_start_y - row * self.grid_spacing * 0.866
                
                element = random.randint(0, 3)
                bubble = Bubble(x, y, element, self.bubble_radius)
                bubble.attached = True
                
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
        """Handle touch down - shoot bubble immediately"""
        try:
            if self.current_bubble is None:
                return super().on_touch_down(touch)
            if self.current_bubble.attached:
                return super().on_touch_down(touch)
                
            # Calculate direction toward touch point
            dx = touch.x - self.shooter_x
            dy = touch.y - self.shooter_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 10:  # Minimum distance to shoot
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
    
    def update(self, dt):
        """Update game state (called every frame)"""
        if not self.game_active:
            return
        
        # Update shooter position to top center of screen
        if self.height > 0:
            self.shooter_y = self.height - 50  # Position near top
            self.shooter_x = self.width / 2  # Center horizontally
        
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
            
            # Check top collision (bubble going above screen)
            if bubble.y + bubble.radius > self.height:
                bubble.y = self.height - bubble.radius
                bubble.vy = -bubble.vy * 0.8
            
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
            
            # Remove if below screen
            if bubble.y + bubble.radius < 0:
                self.shot_bubbles.remove(bubble)
        
        # Redraw
        self.canvas.clear()
        with self.canvas:
            self.draw_background()
            self.draw_grid()
            self.draw_shot_bubbles()
            self.draw_shooter()
            self.draw_ui()
    
    def attach_bubble(self, bubble, grid_bubble):
        """Attach shot bubble to grid at correct position without intersection"""
        bubble.attached = True
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
            # Remove matched bubbles
            for match in matches:
                if match in self.grid_bubbles:
                    self.grid_bubbles.remove(match)
                    self.score += 10
            
            # Check for floating bubbles
            self.check_floating_bubbles()
    
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
        """Check for bubbles not connected to top"""
        # Simplified: remove bubbles with no neighbors
        # Full implementation would use graph traversal
        pass
    
    def draw_background(self):
        """Draw game background - lighter for transparency visibility"""
        # Lighter background so transparent bubbles are visible
        Color(0.2, 0.25, 0.3)  # Light gray-blue
        Rectangle(pos=(0, 0), size=(self.width, self.height))
        
        # Subtle gradient for depth
        Color(0.25, 0.3, 0.35, 0.2)
        Rectangle(pos=(0, self.height * 0.7), size=(self.width, self.height * 0.3))
    
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
        """Draw UI elements"""
        # Score text would go here (using Label widget in full implementation)
        # For now, score is shown in console
        pass
