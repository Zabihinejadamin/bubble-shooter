"""
Enhanced Graphics Module - 2D graphics with depth using PIL/Pillow
Creates procedural textures, gradients, and lighting effects for better visual depth
"""

import math
import os
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class GraphicsEnhancer:
    """Creates enhanced graphics with depth and detail"""
    
    def __init__(self):
        self.texture_cache = {}
        self.scale_factor = 1.0
        
    def set_scale(self, scale):
        """Set scale factor for texture generation"""
        self.scale_factor = scale
    
    def create_bubble_texture(self, radius, color, element_type, has_special=False):
        """Create a high-quality bubble texture with depth and lighting"""
        if not PIL_AVAILABLE:
            return None
        
        # Scale radius for texture generation (higher resolution for better quality)
        tex_radius = int(radius * 2.5)  # Generate at 2.5x for crisp rendering
        size = tex_radius * 2 + 20  # Add padding for shadows/glow
        center = size // 2
        
        # Create RGBA image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Draw stronger shadow (ball casts more defined shadow)
        shadow_offset = int(4 * self.scale_factor)
        shadow_radius = tex_radius + int(3 * self.scale_factor)
        shadow_alpha = 80  # Stronger shadow for ball
        shadow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.ellipse(
            [center - shadow_radius + shadow_offset, 
             center - shadow_radius - shadow_offset,
             center + shadow_radius + shadow_offset,
             center + shadow_radius - shadow_offset],
            fill=(0, 0, 0, shadow_alpha)
        )
        # Blur the shadow more for realistic ball shadow
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=6 * self.scale_factor))
        img = Image.alpha_composite(img, shadow_img)
        
        # 2. Draw ball body with spherical shading (3D sphere lighting)
        # Light direction (from top-left, slightly forward)
        light_dir_x = -0.5
        light_dir_y = -0.5
        light_dir_z = 0.7  # Slight forward direction for depth
        
        # Normalize light direction
        light_len = math.sqrt(light_dir_x**2 + light_dir_y**2 + light_dir_z**2)
        light_dir_x /= light_len
        light_dir_y /= light_len
        light_dir_z /= light_len
        
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= tex_radius:
                    # Calculate 3D position on sphere surface
                    # Normalize to unit sphere
                    nx = dx / tex_radius
                    ny = dy / tex_radius
                    # Calculate z using sphere equation: x^2 + y^2 + z^2 = 1
                    z_squared = 1.0 - (nx*nx + ny*ny)
                    if z_squared < 0:
                        continue  # Outside sphere
                    nz = math.sqrt(z_squared)  # Normal vector z component
                    
                    # Calculate dot product with light direction (Lambertian shading)
                    dot_product = nx * light_dir_x + ny * light_dir_y + nz * light_dir_z
                    
                    # Clamp dot product to [0, 1] for lighting
                    dot_product = max(0.0, min(1.0, dot_product))
                    
                    # Ambient light (minimum brightness)
                    ambient = 0.3
                    
                    # Diffuse lighting (main lighting)
                    diffuse = dot_product * 0.7
                    
                    # Total brightness
                    brightness = ambient + diffuse
                    
                    # Darken bottom of sphere (ambient occlusion effect)
                    if ny > 0.3:  # Bottom half
                        bottom_darkening = (ny - 0.3) * 0.4  # Darken by up to 40%
                        brightness *= (1.0 - bottom_darkening)
                    
                    # Darken edges slightly for depth
                    edge_factor = 1.0 - (dist / tex_radius) ** 2 * 0.1
                    brightness *= edge_factor
                    
                    # Apply color with lighting
                    r = min(1.0, color[0] * brightness)
                    g = min(1.0, color[1] * brightness)
                    b = min(1.0, color[2] * brightness)
                    
                    # Fully opaque for solid ball
                    alpha = 255
                    
                    img.putpixel((x, y), (
                        int(r * 255),
                        int(g * 255),
                        int(b * 255),
                        alpha
                    ))
        
        # 3. Add specular highlight (shiny ball reflection)
        # Highlight position (top-left, slightly forward)
        highlight_offset_x = -tex_radius * 0.35
        highlight_offset_y = -tex_radius * 0.35
        highlight_center_x = center + highlight_offset_x
        highlight_center_y = center + highlight_offset_y
        highlight_radius = int(tex_radius * 0.35)
        
        for y in range(size):
            for x in range(size):
                dx = x - highlight_center_x
                dy = y - highlight_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= highlight_radius:
                    # Check if this point is on the visible side of the sphere
                    sphere_dx = x - center
                    sphere_dy = y - center
                    sphere_dist = math.sqrt(sphere_dx*sphere_dx + sphere_dy*sphere_dy)
                    
                    if sphere_dist <= tex_radius:
                        # Calculate highlight intensity (stronger at center)
                        highlight_intensity = 1.0 - (dist / highlight_radius)
                        highlight_intensity = highlight_intensity ** 1.5  # Sharper highlight
                        
                        # Make highlight more intense
                        highlight_strength = highlight_intensity * 0.6  # 60% white overlay
                        
                        r, g, b, a = img.getpixel((x, y))
                        
                        # Add white specular highlight
                        r = min(255, int(r + (255 - r) * highlight_strength))
                        g = min(255, int(g + (255 - g) * highlight_strength))
                        b = min(255, int(b + (255 - b) * highlight_strength))
                        
                        img.putpixel((x, y), (r, g, b, a))
        
        # 4. Add rim lighting (bright edge where light hits the sphere edge)
        rim_width = int(3 * self.scale_factor)
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Draw rim on the lit side (top-left edge)
                if tex_radius - rim_width <= dist <= tex_radius:
                    # Check if this is on the lit edge
                    angle = math.atan2(dy, dx)
                    # Lit edge is around 135 degrees (top-left)
                    lit_angle = math.radians(135)
                    angle_diff = abs(angle - lit_angle)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    
                    # Only add rim lighting on the lit side
                    if angle_diff < math.radians(60):  # Within 60 degrees of lit edge
                        rim_intensity = 1.0 - abs(dist - tex_radius) / rim_width
                        rim_intensity *= (1.0 - angle_diff / math.radians(60))  # Fade with angle
                        
                        r, g, b, a = img.getpixel((x, y))
                        
                        # Brighten edge significantly
                        r = min(255, int(r + rim_intensity * 120))
                        g = min(255, int(g + rim_intensity * 120))
                        b = min(255, int(b + rim_intensity * 120))
                        
                        img.putpixel((x, y), (r, g, b, a))
        
        # 5. Add outer glow for special bubbles
        if has_special:
            glow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_img)
            glow_radius = tex_radius + int(5 * self.scale_factor)
            glow_draw.ellipse(
                [center - glow_radius, center - glow_radius,
                 center + glow_radius, center + glow_radius],
                fill=(int(color[0]*255), int(color[1]*255), int(color[2]*255), 60)
            )
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=6 * self.scale_factor))
            img = Image.alpha_composite(img, glow_img)
        
        # Convert to Kivy texture
        return self._pil_to_kivy_texture(img)
    
    def create_shooter_texture(self, length, width, base_radius):
        """Create enhanced shooter/cannon texture"""
        if not PIL_AVAILABLE:
            return None
        
        # Create texture for shooter base
        size = int(base_radius * 2.5)
        center = size // 2
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw metallic base with gradient
        base_radius_int = int(base_radius * 1.2)
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= base_radius_int:
                    # Metallic gradient (darker at edges, lighter in center)
                    norm_dist = dist / base_radius_int
                    brightness = 0.4 + 0.6 * (1 - norm_dist)
                    
                    # Metallic gray color
                    gray = int(brightness * 180)
                    img.putpixel((x, y), (gray, gray, gray, 255))
        
        # Add highlight
        highlight_radius = int(base_radius_int * 0.5)
        highlight_center_x = center - int(base_radius_int * 0.3)
        highlight_center_y = center - int(base_radius_int * 0.3)
        
        for y in range(size):
            for x in range(size):
                dx = x - highlight_center_x
                dy = y - highlight_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= highlight_radius:
                    intensity = 1.0 - (dist / highlight_radius)
                    r, g, b, a = img.getpixel((x, y))
                    bright = min(255, int(r + intensity * 60))
                    img.putpixel((x, y), (bright, bright, bright, a))
        
        return self._pil_to_kivy_texture(img)
    
    def create_panel_texture(self, width, height, style='default'):
        """Create enhanced UI panel texture with depth"""
        if not PIL_AVAILABLE:
            return None
        
        # Scale for quality
        tex_width = int(width * 2)
        tex_height = int(height * 2)
        
        img = Image.new('RGBA', (tex_width, tex_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw panel with gradient
        corner_radius = int(8 * self.scale_factor)
        
        # Main panel gradient (darker at bottom)
        for y in range(tex_height):
            brightness = 0.7 + 0.3 * (y / tex_height)  # Darker at bottom
            color_val = int(brightness * 60)
            alpha = int(brightness * 220)
            
            # Draw rounded rectangle row
            for x in range(tex_width):
                # Check if in rounded corners
                in_corner = False
                if x < corner_radius and y < corner_radius:
                    dist = math.sqrt((x - corner_radius)**2 + (y - corner_radius)**2)
                    in_corner = dist > corner_radius
                elif x >= tex_width - corner_radius and y < corner_radius:
                    dist = math.sqrt((x - (tex_width - corner_radius))**2 + (y - corner_radius)**2)
                    in_corner = dist > corner_radius
                elif x < corner_radius and y >= tex_height - corner_radius:
                    dist = math.sqrt((x - corner_radius)**2 + (y - (tex_height - corner_radius))**2)
                    in_corner = dist > corner_radius
                elif x >= tex_width - corner_radius and y >= tex_height - corner_radius:
                    dist = math.sqrt((x - (tex_width - corner_radius))**2 + (y - (tex_height - corner_radius))**2)
                    in_corner = dist > corner_radius
                
                if not in_corner:
                    if style == 'default':
                        img.putpixel((x, y), (color_val, color_val + 10, color_val + 20, alpha))
                    else:
                        img.putpixel((x, y), (color_val, color_val, color_val, alpha))
        
        # Add top highlight
        highlight_height = int(6 * self.scale_factor)
        for y in range(highlight_height):
            for x in range(tex_width):
                r, g, b, a = img.getpixel((x, y))
                bright = min(255, int(r + 40))
                img.putpixel((x, y), (bright, bright, bright, a))
        
        return self._pil_to_kivy_texture(img)
    
    def create_particle_texture(self, size, color, fade=True):
        """Create particle texture for explosion effects"""
        if not PIL_AVAILABLE:
            return None
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        center = size // 2
        
        # Create soft circular particle
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= size // 2:
                    if fade:
                        intensity = 1.0 - (dist / (size // 2))
                        intensity = intensity ** 1.5  # Softer falloff
                    else:
                        intensity = 1.0 if dist <= size // 2 else 0.0
                    
                    r = int(color[0] * 255 * intensity)
                    g = int(color[1] * 255 * intensity)
                    b = int(color[2] * 255 * intensity)
                    a = int(255 * intensity)
                    
                    img.putpixel((x, y), (r, g, b, a))
        
        return self._pil_to_kivy_texture(img)
    
    def create_bazooka_texture(self, length, width, base_radius, tip_radius, angle_rad=0):
        """Create a beautiful high-quality bazooka texture with depth and detail"""
        if not PIL_AVAILABLE:
            return None
        
        # Scale for high quality rendering
        scale = 2.0
        tex_length = int(length * scale)
        tex_width = int(width * scale)
        tex_base_radius = int(base_radius * scale)
        tex_tip_radius = int(tip_radius * scale)
        
        # Create image with padding
        padding = int(tex_base_radius * 1.5)
        img_width = tex_length + padding * 2
        img_height = max(tex_base_radius * 2, tex_width) + padding * 2
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate positions (bazooka pointing right)
        start_x = padding
        start_y = img_height // 2
        end_x = start_x + tex_length
        end_y = start_y
        
        # Draw bazooka base (circular metallic base)
        base_center_x = start_x
        base_center_y = start_y
        
        # Base metallic gradient with 3D effect
        for y in range(img_height):
            for x in range(img_width):
                dx = x - base_center_x
                dy = y - base_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= tex_base_radius:
                    # Calculate 3D position on sphere
                    nx = dx / tex_base_radius
                    ny = dy / tex_base_radius
                    z_squared = 1.0 - (nx*nx + ny*ny)
                    if z_squared < 0:
                        continue
                    nz = math.sqrt(z_squared)
                    
                    # Lighting from top-left
                    light_dir_x = -0.5
                    light_dir_y = -0.5
                    light_dir_z = 0.7
                    light_len = math.sqrt(light_dir_x**2 + light_dir_y**2 + light_dir_z**2)
                    light_dir_x /= light_len
                    light_dir_y /= light_len
                    light_dir_z /= light_len
                    
                    dot_product = nx * light_dir_x + ny * light_dir_y + nz * light_dir_z
                    dot_product = max(0.0, min(1.0, dot_product))
                    
                    # Metallic gray with lighting
                    ambient = 0.25
                    diffuse = dot_product * 0.75
                    brightness = ambient + diffuse
                    
                    # Metallic color (dark gray to light gray)
                    gray = int(brightness * 200)
                    img.putpixel((x, y), (gray, gray, int(gray * 1.1), 255))
        
        # Add base rim highlight
        rim_width = int(3 * scale)
        for y in range(img_height):
            for x in range(img_width):
                dx = x - base_center_x
                dy = y - base_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if tex_base_radius - rim_width <= dist <= tex_base_radius:
                    # Bright rim on top-left
                    angle = math.atan2(dy, dx)
                    if angle < -math.pi/4 and angle > -3*math.pi/4:
                        r, g, b, a = img.getpixel((x, y))
                        bright = min(255, int(r + 80))
                        img.putpixel((x, y), (bright, bright, bright, a))
        
        # Draw bazooka barrel (cylindrical with metallic finish)
        half_width = tex_width // 2
        
        # Draw barrel body with cylindrical shading
        for y in range(img_height):
            for x in range(img_width):
                # Check if point is within barrel rectangle
                if start_x <= x <= end_x:
                    # Calculate distance from barrel center line
                    dist_from_center = abs(y - start_y)
                    
                    if dist_from_center <= half_width:
                        # Calculate position along barrel (0 to 1)
                        barrel_pos = (x - start_x) / tex_length
                        
                        # Cylindrical shading (brighter on top, darker on bottom)
                        vertical_pos = (y - (start_y - half_width)) / tex_width
                        brightness = 0.4 + 0.6 * (1.0 - vertical_pos)  # Brighter at top
                        
                        # Add barrel segments/rings
                        segment_factor = 1.0
                        if int(barrel_pos * 4) % 2 == 0:
                            segment_factor = 0.95  # Slightly darker segments
                        
                        brightness *= segment_factor
                        
                        # Metallic gray color
                        gray = int(brightness * 180)
                        img.putpixel((x, y), (gray, gray, int(gray * 1.05), 255))
        
        # Add barrel top highlight
        highlight_width = int(tex_width * 0.3)
        for y in range(start_y - half_width, start_y - half_width + highlight_width):
            for x in range(start_x, end_x):
                r, g, b, a = img.getpixel((x, y))
                bright = min(255, int(r + 60))
                img.putpixel((x, y), (bright, bright, bright, a))
        
        # Add barrel reinforcement bands
        band_positions = [0.2, 0.6]
        for band_pos in band_positions:
            band_x = int(start_x + tex_length * band_pos)
            band_width = int(4 * scale)
            for y in range(start_y - half_width, start_y + half_width):
                for x in range(band_x - band_width, band_x + band_width):
                    if 0 <= x < img_width and 0 <= y < img_height:
                        r, g, b, a = img.getpixel((x, y))
                        dark = max(0, int(r - 40))
                        img.putpixel((x, y), (dark, dark, dark, a))
        
        # Draw bazooka tip/muzzle
        tip_center_x = end_x
        tip_center_y = start_y
        
        # Tip metallic circle
        for y in range(img_height):
            for x in range(img_width):
                dx = x - tip_center_x
                dy = y - tip_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= tex_tip_radius:
                    # 3D sphere shading
                    nx = dx / tex_tip_radius
                    ny = dy / tex_tip_radius
                    z_squared = 1.0 - (nx*nx + ny*ny)
                    if z_squared < 0:
                        continue
                    nz = math.sqrt(z_squared)
                    
                    # Lighting
                    light_dir_x = -0.5
                    light_dir_y = -0.5
                    light_dir_z = 0.7
                    light_len = math.sqrt(light_dir_x**2 + light_dir_y**2 + light_dir_z**2)
                    light_dir_x /= light_len
                    light_dir_y /= light_len
                    light_dir_z /= light_len
                    
                    dot_product = nx * light_dir_x + ny * light_dir_y + nz * light_dir_z
                    dot_product = max(0.0, min(1.0, dot_product))
                    
                    ambient = 0.2
                    diffuse = dot_product * 0.8
                    brightness = ambient + diffuse
                    
                    # Darker metallic for tip
                    gray = int(brightness * 150)
                    img.putpixel((x, y), (gray, gray, int(gray * 1.1), 255))
        
        # Muzzle opening (dark center)
        muzzle_radius = int(tex_tip_radius * 0.55)
        for y in range(img_height):
            for x in range(img_width):
                dx = x - tip_center_x
                dy = y - tip_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= muzzle_radius:
                    # Very dark center
                    img.putpixel((x, y), (20, 20, 25, 255))
        
        # Add inner muzzle rim
        rim_radius = int(muzzle_radius * 0.9)
        for y in range(img_height):
            for x in range(img_width):
                dx = x - tip_center_x
                dy = y - tip_center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if rim_radius - 2 <= dist <= rim_radius:
                    img.putpixel((x, y), (80, 80, 90, 255))
        
        return self._pil_to_kivy_texture(img)
    
    def _pil_to_kivy_texture(self, pil_image):
        """Convert PIL Image to Kivy Texture"""
        # Convert PIL image to bytes
        img_data = pil_image.tobytes()
        
        # Create Kivy texture
        texture = Texture.create(size=(pil_image.width, pil_image.height), colorfmt='rgba')
        texture.blit_buffer(img_data, colorfmt='rgba', bufferfmt='ubyte')
        
        return texture
    
    def get_cached_texture(self, cache_key):
        """Get texture from cache"""
        return self.texture_cache.get(cache_key)
    
    def cache_texture(self, cache_key, texture):
        """Cache texture for reuse"""
        self.texture_cache[cache_key] = texture

