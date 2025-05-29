import pygame
import logging
import os
import sys
from headers.classes import ControllerHandler


logger = logging.getLogger(__name__)

class GameMap:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.game_surface = pygame.Surface((1280, 720))
        
        # Animation timers
        self.animation_timer = 0
        self.animation_frame = 0
        self.animation_speed = 100
        self.bg_animation_timer = 0
        self.bg_animation_index = 0
        self.bg_frame_duration = 100
        self.animation_timer = 0  # Added for character animation
        self.idle_frame_count = 10
        self.walk_frame_count = 8
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.GOLD = (255, 215, 0)
        
        # Initialize player position and animation state
        self.player_x = 200  # Start at tutorial position
        self.player_y = 230  # Fixed Y position for walking
        self.player_direction = 1  # 1 for right, -1 for left
        self.current_animation = 'idle'

        # Map settings
        self.path_width = 90
        self.custom_path_widths = {
            ('boss_three', 'boss_four'): 45,
            ('boss_four', 'boss_five'): 45
        }
        self.node_radius = 100
        self.debug_mode = False
        self.level_proximity = 50
        self.movement_speed = 5
        
        # Initialize controller
        self.controller = ControllerHandler()
        
        # Level entry settings
        self.level_entry_cooldown = 500
        self.last_level_entry = 0
        self.can_enter_level = True
        self.show_entry_prompt = False
        
        # Level configurations
        self.levels = {
            'tutorial': {'completed': False, 'unlocked': True, 'x': 200, 'y': 200},
            'boss_one': {'completed': False, 'unlocked': False, 'x': 650, 'y': 240},
            'boss_three': {'completed': False, 'unlocked': False, 'x': 460, 'y': 550},
            'boss_four': {'completed': False, 'unlocked': False, 'x': 890, 'y': 650},
            'boss_five': {'completed': False, 'unlocked': False, 'x': 1180, 'y': 380}
        }
        
        self.current_level = 'tutorial'
        self.selected_level = None
        
        self.music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music", "world.mp3")
        # Load assets
        self.load_assets()
        

    def toggle_debug(self):
        """Toggle debug visualization"""
        self.debug_mode = not self.debug_mode
        
    def draw_debug_overlay(self):
        """Draw debug visualization of paths and hitboxes"""
        if not self.debug_mode:
            return
            
        # Draw node hitboxes
        for level_info in self.levels.values():
            if level_info['unlocked']:
                pygame.draw.circle(self.game_surface, (255, 0, 0), 
                                (level_info['x'], level_info['y']), 
                                self.node_radius, 2)
        
        # Draw path hitboxes
        level_connections = [
            ('tutorial', 'boss_one'),
            ('boss_one', 'boss_three'),
            ('boss_three', 'boss_four'),
            ('boss_four', 'boss_five')
        ]
        
        # Draw paths for all valid connections
        for start_level, end_level in level_connections:
            if (start_level in self.levels and end_level in self.levels):
                start = (self.levels[start_level]['x'], self.levels[start_level]['y'])
                end = (self.levels[end_level]['x'], self.levels[end_level]['y'])
                
                # Use custom width if defined, otherwise use default
                path_width = self.custom_path_widths.get((start_level, end_level), self.path_width)
                
                # Draw wide red line for path width
                pygame.draw.line(self.game_surface, (255, 0, 0), start, end, path_width * 2)
                # Draw thin green line for path center
                pygame.draw.line(self.game_surface, (0, 255, 0), start, end, 2)



    
    def play_music(self):
        """Force play world.mp3 every time we return to the map"""
        if os.path.exists(self.music_path):
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play(-1)
            except Exception as e:
                logger.error(f"Failed to play map music: {e}")
        else:
            logger.error(f"Map music not found at: {self.music_path}")

    def reset_state(self):
        """Reset map state when returning from a level"""
        self.selected_level = None
        self.show_enter_prompt = False
        # Clear all cooldown timers
        if hasattr(self, 'return_from_menu_time'):
            delattr(self, 'return_from_menu_time')
        if hasattr(self, 'return_from_pause_time'):
            delattr(self, 'return_from_pause_time')
        # Reset controller-related states
        self.can_enter_level = True
        self.last_level_entry = 0

    def load_assets(self):
        """Load all necessary game assets"""
        try:
            # Get the correct project root (the directory containing main.py)
            project_root = os.path.dirname(os.path.abspath(__file__))
            logger.debug(f"Project root path: {project_root}")
            
            # Load animated background frames
            map_path = os.path.join(project_root, "assets", "menu", "map_move.png")
            logger.debug(f"Loading map animation from: {map_path}")
            self.background_frames = self.load_frames(map_path, 12, 1280, 720)
            
            # Verify background frames loaded correctly
            if not self.background_frames:
                logger.error("Failed to load background frames, creating fallback background")
                fallback = pygame.Surface((1280, 720))
                fallback.fill((50, 50, 100))  # Dark blue background
                self.background_frames = [fallback]
            
            # Load fonts
            try:
                font_path = os.path.join(project_root, "fonts", "PixelFont.ttf")
                self.font = pygame.font.Font(font_path, 48)
                self.font_small = pygame.font.Font(font_path, 36)
            except:
                self.font = pygame.font.SysFont(None, 48)
                self.font_small = pygame.font.SysFont(None, 36)
            
            # Load character animations with correct paths
            animations_path = os.path.join(project_root, "animations", "user")
            logger.debug(f"Animations path: {animations_path}")
            
            idle_path = os.path.join(animations_path, "user_idle.png")
            logger.debug(f"Loading idle animation from: {idle_path}")
            self.idle_frames = self.load_frames(idle_path, 10, 160, 160)
            
            walk_path = os.path.join(animations_path, "user_walk.png")
            logger.debug(f"Loading walk animation from: {walk_path}")
            self.walk_frames = self.load_frames(walk_path, 8, 160, 160)
            
            # Create fallback character frames if loading fails
            if not self.idle_frames or not self.walk_frames:
                logger.error("Failed to load character animations, creating fallback sprites")
                fallback_sprite = pygame.Surface((160, 160), pygame.SRCALPHA)
                pygame.draw.circle(fallback_sprite, (255, 255, 255), (80, 80), 40)  # Simple white circle
                
                self.idle_frames = self.idle_frames if self.idle_frames else [fallback_sprite]
                self.walk_frames = self.walk_frames if self.walk_frames else [fallback_sprite]
                
        except Exception as e:
            logger.error(f"Error in load_assets: {e}")
            # Create fallback assets if loading fails completely
            fallback_sprite = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(fallback_sprite, (255, 255, 255), (80, 80), 40)
            
            self.idle_frames = [fallback_sprite]
            self.walk_frames = [fallback_sprite]
            self.font = pygame.font.SysFont(None, 48)
            self.font_small = pygame.font.SysFont(None, 36)
            
            # Load fonts
            try:
                font_path = os.path.join(project_root, "fonts", "PixelFont.ttf")
                self.font = pygame.font.Font(font_path, 48)
                self.font_small = pygame.font.Font(font_path, 36)
            except:
                self.font = pygame.font.SysFont(None, 48)
                self.font_small = pygame.font.SysFont(None, 36)
            
            # Load character animations
            sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_idle.png")
            self.idle_frames = self.load_frames(sprite_sheet_path, 10, 160, 160)
            
            walk_path = os.path.join(project_root, "animations", "user", "user_walk.png")
            self.walk_frames = self.load_frames(walk_path, 8, 160, 160)
            
            # Create fallback character frames if loading fails
            if not self.idle_frames or not self.walk_frames:
                logger.error("Failed to load character animations, creating fallback sprites")
                fallback_sprite = pygame.Surface((160, 160), pygame.SRCALPHA)
                pygame.draw.circle(fallback_sprite, (255, 255, 255), (80, 80), 40)  # Simple white circle
                
                self.idle_frames = self.idle_frames if self.idle_frames else [fallback_sprite]
                self.walk_frames = self.walk_frames if self.walk_frames else [fallback_sprite]
                

    def load_frames(self, path, num_frames, width, height):
        """Load animation frames from a sprite sheet"""
        frames = []
        try:
            logger.debug(f"Loading sprite sheet from path: {path}")
            if not os.path.exists(path):
                logger.error(f"Sprite sheet path does not exist: {path}")
                return frames

            sprite_sheet = pygame.image.load(path).convert_alpha()
            sprite_sheet_width = sprite_sheet.get_width()
            sprite_sheet_height = sprite_sheet.get_height()
            
            logger.debug(f"Sprite sheet dimensions: {sprite_sheet_width}x{sprite_sheet_height}")
            logger.debug(f"Expected frame dimensions: {width}x{height}")
            logger.debug(f"Number of frames to extract: {num_frames}")

            # Verify sprite sheet dimensions
            expected_width = width * num_frames
            if sprite_sheet_width < expected_width:
                logger.error(f"Sprite sheet width ({sprite_sheet_width}) is smaller than expected ({expected_width})")
                return frames
            
            for i in range(num_frames):
                frame_x = i * width
                # Check if we're still within the sprite sheet bounds
                if frame_x + width <= sprite_sheet_width:
                    try:
                        frame = sprite_sheet.subsurface((frame_x, 0, width, height))
                        frames.append(frame)
                        logger.debug(f"Successfully loaded frame {i+1}/{num_frames}")
                    except Exception as e:
                        logger.error(f"Error extracting frame {i}: {e}")
                else:
                    logger.error(f"Frame {i} extends beyond sprite sheet width")
                    break
            
            logger.debug(f"Successfully loaded {len(frames)} frames")
        except Exception as e:
            logger.error(f"Error loading sprite sheet: {e}")
        
        return frames

    def update_animation(self, dt):
        """Update character and background animation states"""
        # Update character animation
        self.animation_timer += dt * 1000
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            max_frames = self.idle_frame_count if self.current_animation == 'idle' else self.walk_frame_count
            self.animation_frame = (self.animation_frame + 1) % max_frames

        # Update background animation
        self.bg_animation_timer += dt * 1000
        if self.bg_animation_timer >= self.bg_frame_duration:
            self.bg_animation_timer = 0
            self.bg_animation_index = (self.bg_animation_index + 1) % len(self.background_frames)

    def draw_character(self):
        """Draw the character with current animation frame"""
        # Get the correct frame array and ensure animation frame is in bounds
        frames = self.walk_frames if self.current_animation == 'walk' else self.idle_frames
        max_frames = self.walk_frame_count if self.current_animation == 'walk' else self.idle_frame_count
        self.animation_frame = min(self.animation_frame, max_frames - 1)
        
        frame = frames[self.animation_frame]
        
        # Flip frame if facing left
        if self.player_direction == -1:
            frame = pygame.transform.flip(frame, True, False)
        
        # Center the character vertically and account for sprite size
        draw_x = self.player_x - frame.get_width() // 2
        draw_y = self.player_y - frame.get_height() // 2
        
        self.game_surface.blit(frame, (draw_x, draw_y))

    def draw_level_node(self, level_name, info):
        """Draw a level node with visual enhancements"""
        radius = 30
        x = info['x']
        y = info['y']
        
        # # Draw node
        # color = self.GOLD if info['unlocked'] else self.GRAY
        # pygame.draw.circle(self.game_surface, color, (x, y), radius)
        
        # if info['completed']:
        #     completion_text = self.font_small.render("✓", True, self.WHITE)
        #     text_rect = completion_text.get_rect(center=(x, y))
        #     self.game_surface.blit(completion_text, text_rect)
        
        # # Draw level name
        # name_text = self.font_small.render(level_name.replace('_', ' ').title(), True, self.WHITE)
        # name_rect = name_text.get_rect(center=(x, y + 50))
        # self.game_surface.blit(name_text, name_rect)
        
        # Draw connecting lines to previous level
        prev_level = self.get_previous_level(level_name)
        if prev_level and prev_level in self.levels:
            prev_x = self.levels[prev_level]['x']
            prev_y = self.levels[prev_level]['y']
            pass
            # pygame.draw.line(self.game_surface, self.GRAY, (prev_x, prev_y), (x, y), 3)

    def is_point_near_line(self, point, line_start, line_end, threshold):
        """Check if a point is within threshold distance of a line segment"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line start to end
        line_vec = (x2 - x1, y2 - y1)
        # Vector from line start to point
        point_vec = (x - x1, y - y1)
        
        # Length of line segment squared
        line_len_sq = line_vec[0] ** 2 + line_vec[1] ** 2
        
        if line_len_sq == 0:
            # Line segment is actually a point
            return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5 <= threshold
        
        # Calculate projection of point onto line
        t = max(0, min(1, (point_vec[0] * line_vec[0] + point_vec[1] * line_vec[1]) / line_len_sq))
        
        # Find nearest point on line segment
        proj_x = x1 + t * line_vec[0]
        proj_y = y1 + t * line_vec[1]
        
        # Calculate distance from point to nearest point on line segment
        dist = ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5
        
        return dist <= threshold

    def is_position_valid(self, x, y):
        """Check if a position is on a valid path or near a node"""
        # Check if position is near any node
        for level_info in self.levels.values():
            if level_info['unlocked']:
                node_x, node_y = level_info['x'], level_info['y']
                dist = ((x - node_x) ** 2 + (y - node_y) ** 2) ** 0.5
                if dist <= self.node_radius:
                    return True
        
        # Check if position is on any path between connected nodes
        level_connections = [
            ('tutorial', 'boss_one'),
            ('boss_one', 'boss_three'),
            ('boss_three', 'boss_four'),
            ('boss_four', 'boss_five')
        ]
        
        for start_level, end_level in level_connections:
            # Only check paths where both nodes are unlocked
            if (start_level in self.levels and end_level in self.levels and 
                self.levels[start_level]['unlocked'] and self.levels[end_level]['unlocked']):
                start = (self.levels[start_level]['x'], self.levels[start_level]['y'])
                end = (self.levels[end_level]['x'], self.levels[end_level]['y'])
                
                # Use custom width if defined, otherwise use default
                path_width = self.custom_path_widths.get((start_level, end_level), self.path_width)
                
                if self.is_point_near_line((x, y), start, end, path_width):
                    return True
        
        return False
    

    def handle_movement(self, keys):
        """Handle player movement on the map"""
        moving = False
        new_x, new_y = self.player_x, self.player_y
        
        # Handle controller movement
        if self.controller.is_connected():
            # Horizontal movement
            x_axis = self.controller.get_movement()
            if abs(x_axis) > 0:
                new_x += x_axis * self.movement_speed
                self.player_direction = 1 if x_axis > 0 else -1
                moving = True
            
            # Vertical movement
            y_axis = self.controller.controller.get_axis(1)
            if abs(y_axis) > self.controller.deadzone:
                new_y += y_axis * self.movement_speed
                moving = True
            
            # Level entry
            if self.controller.is_jumping():
                self.try_enter_level()

        # Handle keyboard movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= self.movement_speed
            self.player_direction = -1
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += self.movement_speed
            self.player_direction = 1
            moving = True

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= self.movement_speed
            moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += self.movement_speed
            moving = True

        # Update position if valid
        if self.is_position_valid(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

        # Check if near any level and update prompt visibility
        near_any_level = False
        for level_name, info in self.levels.items():
            if (abs(self.player_x - info['x']) < self.level_proximity and 
                abs(self.player_y - info['y']) < self.level_proximity and 
                info['unlocked']):
                near_any_level = True
                break

        self.show_entry_prompt = near_any_level

        # Level entry via keyboard
        if near_any_level and keys[pygame.K_e]:
            self.try_enter_level()

        self.current_animation = 'walk' if moving else 'idle'



    def handle_events(self):
        """Handle events for the map screen"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "pause"
                elif event.key == pygame.K_F3:  # Toggle debug mode
                    self.toggle_debug()
            elif event.type == pygame.JOYDEVICEADDED:
                self.controller.connect_controller()
            elif event.type == pygame.JOYDEVICEREMOVED:
                if self.controller.controller and event.instance_id == self.controller.controller.get_instance_id():
                    self.controller = ControllerHandler()
        
        # Check for controller pause
        if self.controller.is_connected():
            if self.controller.is_start_pressed():
                self.controller.clear_start_press()  # Clear the press state after handling it
                return "pause"
        
        return None

    def can_move_left(self):
        """Check if player can move left"""
        leftmost_level = min(level['x'] for level in self.levels.values())
        return self.player_x > leftmost_level - 50  # Add small buffer

    def can_move_right(self):
        """Check if player can move right"""
        rightmost_level = max(level['x'] for level in self.levels.values())
        return self.player_x < rightmost_level + 50  # Add small buffer

    def try_enter_level(self):
        current_time = pygame.time.get_ticks()

        """Try to enter a level with improved controller support"""

        for level_name, info in self.levels.items():
            if (abs(self.player_x - info['x']) < self.level_proximity and
                abs(self.player_y - info['y']) < self.level_proximity and
                info['unlocked']):
                self.show_entry_prompt = True  # trigger prompt when near unlocked level
                break

        # Check for input (either controller or keyboard)
        controller_input = self.controller.is_connected() and self.controller.is_jumping()
        keyboard_input = pygame.key.get_pressed()[pygame.K_e]

        

        # Don't check cooldown for initial entry after unlock
        if not (controller_input or keyboard_input):
            return None
        
        # Reset cooldown if enough time has passed
        if not self.can_enter_level and current_time - self.last_level_entry >= self.level_entry_cooldown:
            self.can_enter_level = True
        

        # Check proximity & unlocked state for each level
        for level_name, info in self.levels.items():
            if (abs(self.player_x - info['x']) < self.level_proximity and 
                abs(self.player_y - info['y']) < self.level_proximity and 
                info['unlocked']):
                
                # Allow entry if we can enter or if this is a newly unlocked level
                if self.can_enter_level or (not info['completed'] and info['unlocked']):
                    self.selected_level = level_name
                    self.last_level_entry = current_time
                    self.can_enter_level = False
                    return level_name
                
        self.show_entry_prompt = False
        return None
    def draw_ui_box(self, text_surface, center_pos, bg_color=(0, 0, 0, 180), border_color=None, border_thickness=2, padding=(30, 20)):
        """
        Draw a styled UI box centered at the given position.
        - `bg_color`: background color (can use RGBA if surface supports alpha).
        - `border_color`: None for no border, or a color tuple.
        - `padding`: tuple of (horizontal, vertical) padding around the text.
        """
        box_rect = text_surface.get_rect(center=center_pos)
        inflated_rect = box_rect.inflate(*padding)

        # Draw background (supporting transparency)
        surface = pygame.Surface(inflated_rect.size, pygame.SRCALPHA)
        surface.fill(bg_color)
        self.game_surface.blit(surface, inflated_rect.topleft)

        # Draw border if specified
        if border_color:
            pygame.draw.rect(self.game_surface, border_color, inflated_rect, border_thickness)

        # Blit text on top
        self.game_surface.blit(text_surface, box_rect)

    def draw(self):
        """Draw the map screen with all elements"""
        # Draw animated background
        if self.background_frames:  # Check if we have any frames
            current_bg_frame = self.background_frames[self.bg_animation_index % len(self.background_frames)]
            self.game_surface.blit(current_bg_frame, (0, 0))
        else:
            # Fallback to solid color if no frames are loaded
            self.game_surface.fill((50, 50, 100))  # Dark blue background
        
        # Draw level nodes
        for level_name, info in self.levels.items():
            self.draw_level_node(level_name, info)
            
        if self.show_entry_prompt:
            prompt_text = self.font_small.render("Enter Level? Press E", True, self.WHITE)
            prompt_rect = prompt_text.get_rect(center=(self.player_x, self.player_y - 100))
            pygame.draw.rect(self.game_surface, (0, 0, 0, 180), prompt_rect.inflate(30, 20))
            pygame.draw.rect(self.game_surface, self.GOLD, prompt_rect.inflate(30, 20), 2)
            self.game_surface.blit(prompt_text, prompt_rect)

        # Draw character
        self.draw_character()
        
        # Draw instructions
        # Draw instructions based on input method
        if self.controller.is_connected():
            instructions = self.font_small.render("Left Stick to move, A to enter level", True, self.WHITE)
        else:
            instructions = self.font_small.render("A/D to Move, E to Enter Level", True, self.WHITE)
            instructions_esc = self.font_small.render("esc to Exit", True, self.WHITE)
            

        self.draw_ui_box(instructions, (1050, 100), bg_color=(0, 0, 0), border_color=self.GOLD)
        self.draw_ui_box(instructions_esc, (1050, 50),bg_color=(0,0,0), border_color=self.GOLD )
            # Add after existing draw code:
        self.draw_debug_overlay()
        
        if self.debug_mode:
            debug_text = self.font_small.render("Debug Mode (F3)", True, (255, 0, 0))
            self.game_surface.blit(debug_text, (10, 10))
     


    def calculate_fullscreen_dimensions(self, screen_width, screen_height):
        """Calculate dimensions for fullscreen display"""
        game_aspect_ratio = 1280 / 720
        screen_aspect_ratio = screen_width / screen_height
        
        if screen_aspect_ratio > game_aspect_ratio:
            game_height = screen_height
            game_width = int(game_height * game_aspect_ratio)
        else:
            game_width = screen_width
            game_height = int(game_width / game_aspect_ratio)
        
        x = (screen_width - game_width) // 2
        y = (screen_height - game_height) // 2
        
        return game_width, game_height, x, y

    def run(self):
        """Main map loop"""
        self.play_music()
        last_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # Handle events
            result = self.handle_events()
            if result in ["quit", "pause"]:
                return result
                
            # Handle input if not in cooldown
            if not hasattr(self, 'return_from_menu_time') or \
            current_time - self.return_from_menu_time >= 1000:
                keys = pygame.key.get_pressed()
                self.handle_movement(keys)
            
            # Update and draw
            self.update_animation(dt)
            self.draw()
            
            # Screen scaling and display
            self.handle_screen_scaling()
            
            pygame.display.flip()
            self.clock.tick(60)
            
            # Check for level selection
            if self.selected_level and not hasattr(self, 'return_from_menu_time'):
                return self.selected_level

    def handle_screen_scaling(self):
        """Handle screen scaling and display"""
        screen_width, screen_height = self.screen.get_size()
        is_resized = screen_width != 1280 or screen_height != 720
        
        self.screen.fill(self.BLACK)
        
        if is_resized:
            game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
            scaled_surface = pygame.transform.scale(self.game_surface, (game_width, game_height))
            self.screen.blit(scaled_surface, (x, y))
        else:
            self.screen.blit(self.game_surface, (0, 0))

    def unlock_next_level(self, current_level):
        """Unlock the next level after completing current one"""
        level_order = ['tutorial', 'boss_one', 'boss_three', 'boss_four', 'boss_five']
        try:
            current_index = level_order.index(current_level)
            if current_index < len(level_order) - 1:
                next_level = level_order[current_index + 1]
                self.levels[next_level]['unlocked'] = True
                logger.debug(f"Unlocked level: {next_level}")
        except ValueError:
            logger.error(f"Invalid level: {current_level}")

    def mark_level_completed(self, level):
        """Mark a level as completed and unlock the next one"""
        if level in self.levels:
            if not self.levels[level]['completed']:  # Only if not already completed
                self.levels[level]['completed'] = True
                self.unlock_next_level(level)
                logger.debug(f"Marked level {level} as completed")
                
                # Only update position if level was just completed
                self.selected_level = None
                self.can_enter_level = False
                self.last_level_entry = pygame.time.get_ticks()

    def get_previous_level(self, level):
        """Get the previous level in the progression sequence"""
        level_order = ['tutorial', 'boss_one', 'boss_three', 'boss_four', 'boss_five']
        try:
            current_index = level_order.index(level)
            if current_index > 0:
                return level_order[current_index - 1]
        except ValueError:
            logger.error(f"Invalid level: {level}")
        return None

    def get_next_level(self, level):
        """Get the next level in the progression sequence"""
        level_order = ['tutorial', 'boss_one', 'boss_three', 'boss_four', 'boss_five']
        try:
            current_index = level_order.index(level)
            if current_index < len(level_order) - 1:
                return level_order[current_index + 1]
        except ValueError:
            logger.error(f"Invalid level: {level}")
        return None
        """Get data for saving"""
        return {
            "levels": self.levels,
            "current_level": self.current_level,
            "player_position": self.player_x
        }
    

    def load_save_data(self, data):
        """Load saved data"""
        if data:
            self.levels = data.get("levels", self.levels)
            self.current_level = data.get("current_level", self.current_level)
            self.player_x = data.get("player_position", self.player_x)