import os # Used for file path management (load animation files)
import pygame
from sound_effects.user.user_sound import SoundManager
import cv2
# import cv2
import numpy as np
#from ..sprites import *


class Player:
    
    def __init__(self, screen, clock):
        self.healthbar = 500
        self.max_health = self.healthbar
        self.screen = screen
        self.clock = clock
        self.inventory = {"Gold": 0, "Health_potions": 1, "Jump_potions": 0, "Speed_potions": 0}
        self.curr_slot = [1] # Any of 1, 2, or 3
        self.press_delay = 0 # Used for ensuring only 1 instance of key press registered
        self.sound_manager = SoundManager()
    

        # Player's dimensions and position
        self.width = 125  
        self.height = 320
        self.x = 500
        self.y = 480
        
        # Initial player movement and state values
        self.new_x = self.x
        self.velocity = 8
        self.jump_speed = -19
        self.gravity = .8
        self.y_velocity = 0
        self.is_jumping = False
        self.is_falling = False
        self.is_dashing = False
        self.facing_right = True
        self.dash_cooldown = 700
        self.last_dash_time = 0
        self.dash_velocity = 12
        self.dash_duration = 500
        self.dash_start_time = 0

        # Action and state management
        self.current_action = 'idle'
        self.action_in_progress = False
        self.damage_dealt = False
        self.healthbar = 500
        self.projectiles = []
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 300  # 100 ms of invincibility
        self.color = (255, 255, 255)  # Default color (white)
        self.attack_on_cooldown = False
        self.attack_start_time = 0  # Track the start time of the attack animation


        # Animation timing variables
        self.current_frame = 0  
        self.last_update_time = pygame.time.get_ticks()
        self.frame_duration = 100
        self.dash_frame_duration = 100  # Faster animation for dashing
        self.attack_frame_duration = 50 # faster animation for attack

        # Health bar configuration
        self.health_bar_width = 300
        self.health_bar_height = 20
        self.health_bar_x = 960
        self.health_bar_y = 50
        self.border_thickness = 4 
        # Smooth health bar animation
        self.visual_health = self.healthbar  # This will be used for smooth animation
        self.health_animation_speed = 1  # Speed of health bar animation (higher = faster)



        # Setup paths and load sprite sheets for user
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        crop_rect = pygame.Rect(0,0, 169, 160)  # Cropping to the visible user area (x-pos,y-pos, x, y)

        # Load idle animation frames with cropping
        sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_idle.png")
        self.idle_animation_frames = self.load_frames(sprite_sheet_path, 10, 160, 160)

        # Load walking animation frames
        walk_sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_walk.png")
        self.walk_animation_frames = self.load_frames(walk_sprite_sheet_path, 8, 160, 160)

        # Load jumping animation frames
        jump_sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_jump.png")
        self.jump_animation_frames = self.load_frames(jump_sprite_sheet_path, 7, 160, 160)

        # Load fall animation frames
        fall_sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_fall.png")
        self.fall_animation_frames = self.load_frames(fall_sprite_sheet_path, 5, 160, 160)

        # Load dashing animation frames
        dash_sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_dash.png")
        self.dash_animation_frames = self.load_frames(dash_sprite_sheet_path, 13, 160, 160)

        # Load attacking animation frames
        attack_sprite_sheet_path = os.path.join(project_root, "animations", "user", "user_attack.png")
        self.attack_animation_frames = self.load_frames(attack_sprite_sheet_path, 9, 160, 160)

        # ! Load curse animation frames
        curse_idle_path = os.path.join(project_root, "animations", "user", "curse_idle.png")
        self.curse_idle_frames = self.load_frames(curse_idle_path, 10, 160, 160)
        
        curse_walk_path = os.path.join(project_root, "animations", "user", "curse_walk.png")
        self.curse_walk_frames = self.load_frames(curse_walk_path, 8, 160, 160)
        
        curse_jump_path = os.path.join(project_root, "animations", "user", "curse_jump.png")
        self.curse_jump_frames = self.load_frames(curse_jump_path, 7, 160, 160)
        
        curse_fall_path = os.path.join(project_root, "animations", "user", "curse_fall.png")
        self.curse_fall_frames = self.load_frames(curse_fall_path, 1, 160, 160)

        # Curse state variables
        self.is_cursed = False
        self.last_curse_time = pygame.time.get_ticks()
        self.original_velocity = self.velocity

        # Hitbox for collision detection (adjusted for the cropped frame size)
        self.hitbox = pygame.Rect(self.x+40, self.y+20, 75, 130)  # Match the crop size here

    def autopass(self, screen):
        ### For devs: Auto pass the levels with a hidden hitbox in bottom right corner ###
        mouse_pos = pygame.mouse.get_pos()
        box = pygame.Rect(750, 650, 500, 100)
        # pygame.draw.rect(screen, (0, 255, 0), box, 2)
        if box.collidepoint(mouse_pos):
            (pressed, z1, z2) = pygame.mouse.get_pressed(num_buttons=3)
            if(pressed):
                return "SudoPass"

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height, crop_rect=None):
        """Load frames from a sprite sheet, optionally cropping each frame to the specified area."""
        if not os.path.exists(sprite_sheet_path):
            print(f"Error: Sprite sheet not found at {sprite_sheet_path}")
            return []

        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path)
            # print(f"Loaded sprite sheet: {sprite_sheet_path}")
        except pygame.error as e:
            print(f"Error loading sprite sheet: {e}")
            return []

        frames = []
        
        # Slice the sprite sheet into individual frames and crop if crop_rect is provided
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            
            if crop_rect:
                frame = frame.subsurface(crop_rect)  # Crop to the desired area

            frames.append(frame)

        # print(f"Loaded {len(frames)} frames from {sprite_sheet_path}")
        return frames
    
        # Add this new method
    def curse(self):
        """Apply curse effect to player"""
        if not self.is_cursed:
            self.is_cursed = True
            self.last_curse_time = pygame.time.get_ticks()
            self.curse_timer = 7000  # Convert to milliseconds
            self.velocity = self.original_velocity / 2
            self.is_dashing = False  # End any ongoing dash
            self.current_action = 'idle'  # Reset to idle animation

    # Modify get_current_frame method to use curse animations
    def get_current_frame(self, controller=None):
        """Get the current animation frame based on player state and curse status"""
        # Check for movement from either keyboard or controller
        keys = pygame.key.get_pressed()
        is_moving = any(keys[key] for key in [pygame.K_a, pygame.K_d])
        
        # Add controller movement check
        if controller and controller.is_connected():
            stick_x = controller.get_movement()
            is_moving = is_moving or abs(stick_x) > controller.deadzone

        if self.is_cursed:
            if self.is_jumping:
                return self.animate(self.curse_jump_frames)
            elif self.is_falling:
                return self.animate(self.curse_fall_frames)
            elif is_moving:  # Use the combined movement check
                return self.animate(self.curse_walk_frames)
            else:
                return self.animate(self.curse_idle_frames)
        else:
            if self.is_jumping:
                return self.animate(self.jump_animation_frames)
            elif self.is_falling:
                return self.animate(self.fall_animation_frames)
            elif self.is_dashing:
                return self.animate(self.dash_animation_frames, True)
            elif self.current_action == 'attack':
                return self.animate(self.attack_animation_frames)
            elif is_moving:  # Use the combined movement check
                return self.animate(self.walk_animation_frames)
            else:
                return self.animate(self.idle_animation_frames)


    def flip_frame(self, frame):
        """Flip the frame if the player is facing left."""
        if not self.facing_right:
            return pygame.transform.flip(frame, True, False)
        return frame

    def animate(self, action_frames, is_dash=False):
        if not action_frames:
            print("Error: No frames available for this animation.")
            return None

        if self.current_frame >= len(action_frames):
            self.current_frame = 0  # Ensure it resets if out of range

        now = pygame.time.get_ticks()
        
        # Determine frame duration based on action type
        if self.current_action == 'attack':
            frame_duration = 50  # Faster animation for attacks (adjust this value to make it faster/slower)
        elif is_dash:
            frame_duration = self.dash_frame_duration
        else:
            frame_duration = self.frame_duration

        if now - self.last_update_time > frame_duration:
            self.current_frame = (self.current_frame + 1) % len(action_frames)
            self.last_update_time = now

        frame = action_frames[self.current_frame]
        return self.flip_frame(frame)
    

    def take_damage(self, damage):
        """Handle taking damage and becoming invincible for a duration."""
        if not self.invincible:
            self.sound_manager.play_sound('damage')
            self.healthbar -= damage
            self.invincible = True
            self.invincible_start_time = pygame.time.get_ticks()

            # Turn player red to indicate damage
            self.color = (255, 0, 0)
            # print(f"Player took {damage} damage! Health is now {self.healthbar}.")
            # if self.healthbar <= 0:
            #     print("Player is dead!")

    def update_invincibility(self):
        """Check if the invincibility duration has passed and reset it."""
        if self.invincible:
            current_time = pygame.time.get_ticks()
            # Flash once at the start of invincibility
            if current_time - self.invincible_start_time < 200:
                self.color = (255, 0, 0)
            else:
                self.color = (255, 255, 255)

            # Check if invincibility duration is over
            if current_time - self.invincible_start_time >= self.invincible_duration:
                self.invincible = False
                self.color = (255, 255, 255)  # Reset player color after invincibility ends

    def move(self, keys, platforms, hazards, controller=None):
            """Handle horizontal movement, jumping, falling, dashing, with collision detection."""
            current_time = pygame.time.get_ticks()

            # Get game surface dimensions instead of screen dimensions for boundary checks
            GAME_WIDTH = 1280  # Fixed game width
            GAME_HEIGHT = 720  # Fixed game height

            # Get input from either keyboard or controller
            moving_left = keys[pygame.K_a]
            moving_right = keys[pygame.K_d]
            jumping = keys[pygame.K_SPACE]
            dashing = keys[pygame.K_s]
            
            # Add controller input if available
            if controller and controller.is_connected():
                stick_x = controller.get_movement()
                if stick_x < 0:
                    moving_left = True
                elif stick_x > 0:
                    moving_right = True
                
                if controller.is_jumping():
                    jumping = True
                if controller.is_dashing():
                    dashing = True

            # Prevent dashing while cursed
            if not self.is_cursed:
                if dashing and not self.is_dashing and current_time - self.last_dash_time > self.dash_cooldown:
                    self.is_dashing = True
                    self.sound_manager.play_sound('dash')
                    self.dash_start_time = current_time
                    self.last_dash_time = current_time
                    self.is_jumping = False
                    self.is_falling = False

            # Handle dashing
            if self.is_dashing and not self.is_cursed:
                # Move player during dash
                if current_time - self.dash_start_time < self.dash_duration:
                    if self.facing_right:
                        self.x += self.dash_velocity
                    else:
                        self.x -= self.dash_velocity
                else:
                    self.is_dashing = False
                    self.is_falling = True
            
            # If cursed, immediately end any ongoing dash
            if self.is_cursed and self.is_dashing:
                self.is_dashing = False
                self.is_falling = True

            # Horizontal movement (no dashing)
            if not self.is_dashing:
                if moving_left:
                    self.x -= self.velocity
                    self.facing_right = False
                elif moving_right:
                    self.x += self.velocity
                    self.facing_right = True

            # Use fixed game dimensions for boundary checks instead of screen dimensions
            if self.x < 0:
                self.x = 0
            elif self.x + self.width > GAME_WIDTH:
                self.x = GAME_WIDTH - self.width

            # Jumping
            if jumping and not self.is_jumping and not self.is_falling and not self.is_dashing:
                self.is_jumping = True
                self.sound_manager.play_sound('jump')
                self.y_velocity = self.jump_speed

            # Apply gravity when jumping or falling
            if self.is_jumping or self.is_falling:
                self.y_velocity += self.gravity
                self.y += self.y_velocity

                if self.y_velocity > 0:
                    self.is_falling = True
                    self.is_jumping = False

                # Check if player lands on a platform
                on_platform = False
                for platform in platforms:
                    # Calculate the bottom of the player's hitbox and the distance to the platform's top
                    player_bottom = self.y + self.hitbox.height
                    distance_to_platform = abs(player_bottom - platform.top)
                    
                    # Check if player is within horizontal bounds of the platform
                    horizontally_aligned = (
                        self.hitbox.right > platform.left and 
                        self.hitbox.left < platform.right
                    )
                    
                    # Only allow landing if:
                    # 1. Player is falling (y_velocity >= 0)
                    # 2. Player's feet are close to the platform (within 10 pixels)
                    # 3. Player is horizontally aligned with the platform
                    if (self.y_velocity >= 0 and 
                        distance_to_platform <= 30 and 
                        horizontally_aligned):
                        
                        self.y = platform.top - self.hitbox.height  # Position player on top of platform
                        self.y_velocity = 0
                        self.is_falling = False
                        self.is_jumping = False
                        on_platform = True
                        break

                # If player is not on any platform, keep falling
                if not on_platform:
                    self.is_falling = True

                # Check collision with hazards
                for hazard in hazards:
                    if self.hitbox.colliderect(hazard):
                        self.take_damage(10)
                        self.y_velocity = -18
                        self.is_falling = True

            # Update falling state if not jumping or dashing
            if not self.is_jumping and not self.is_dashing:
                on_platform = False
                for platform in platforms:
                    # Check if the player's feet are still on a platform
                    player_bottom = self.y + self.hitbox.height
                    distance_to_platform = abs(player_bottom - platform.top)
                    horizontally_aligned = (
                        self.hitbox.right > platform.left and 
                        self.hitbox.left < platform.right
                    )
                    
                    if distance_to_platform <= 10 and horizontally_aligned:
                        on_platform = True
                        break
                        
                if not on_platform:
                    self.is_falling = True

            # Update hitbox after all movement
            self.hitbox.update(self.x + 40, self.y + 20, 75, 130)
        
    def check_collision(self, enemy_projectiles):
        """Check if the player collides with any enemy projectiles or enemies."""
        for projectile in enemy_projectiles:
            if self.hitbox.colliderect(projectile):  # Check collision directly with the pygame.Rect
                self.take_damage(20)  # Example damage value

    def draw(self, screen):
        """Draw the player on the screen with the current color."""
        current_frame = self.get_current_frame()  # Assuming you have a function to get the current animation frame
        frame_surface = current_frame.copy()  # Make a copy of the current frame to apply color changes

        if self.color == (255, 0, 0):  # If the player is supposed to be red (indicating damage)
            # You can apply a red tint to the frame surface here
            frame_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)

        screen.blit(frame_surface, (self.x, self.y))  # Draw the current frame with the color


        # Draw curse timer
        if self.is_cursed:
            font = pygame.font.Font(None, 36)
            timer_text = font.render(str(max(0, self.curse_timer // 1000)), True, (255, 0, 0))
            screen.blit(timer_text, (self.x + self.width // 2, self.y - 30))



    def attack(self, keys, controller=None):
        """Handle the attack action with both keyboard and controller support."""
        current_time = pygame.time.get_ticks()
        
        if self.is_cursed:  # Prevent attack while cursed
            return
            
        # Check if attack cooldown is over
        if self.attack_on_cooldown:
            if current_time - self.attack_start_time > 800:  # 400ms cooldown
                self.attack_on_cooldown = False
        
        # Check for attack input from either keyboard or controller
        attacking = keys[pygame.K_p]
        if controller and controller.is_connected():
            attacking = attacking or controller.is_attacking()
                
        # Start new attack if attack button is pressed and not on cooldown
        if attacking and not self.attack_on_cooldown:
            if not self.is_jumping and not self.is_falling:
                self.current_action = 'attack'
                self.sound_manager.play_sound('woosh')
                self.current_frame = 0
                self.action_in_progress = True
                self.attack_start_time = current_time
                self.damage_dealt = False
                self.attack_on_cooldown = True

    def draw_health_bar(self, surface):
        """Draw the player health bar with thick border and smooth animation."""
        # Update visual health for smooth animation
        if self.visual_health > self.healthbar:
            self.visual_health = max(self.healthbar, self.visual_health - self.health_animation_speed)
        elif self.visual_health < self.healthbar:
            self.visual_health = min(self.healthbar, self.visual_health + self.health_animation_speed)

        # Draw the border (black rectangle) - now thicker
        pygame.draw.rect(surface, (0, 0, 0), 
                        (self.health_bar_x - self.border_thickness, 
                        self.health_bar_y - self.border_thickness,
                        self.health_bar_width + (self.border_thickness * 2), 
                        self.health_bar_height + (self.border_thickness * 2)))
        
        # Draw the background (gray rectangle)
        pygame.draw.rect(surface, (169, 169, 169),
                        (self.health_bar_x, self.health_bar_y,
                        self.health_bar_width, self.health_bar_height))
        
        # Calculate health ratios for current and visual health
        health_ratio = max(self.visual_health / self.max_health, 0)
        current_health_width = int(self.health_bar_width * health_ratio)
        
        # Draw the current health (blue rectangle)
        if current_health_width > 0:
            # Draw the main health bar
            pygame.draw.rect(surface, (21, 145, 234),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, self.health_bar_height))
            
            # Draw a lighter blue highlight at the top of the health bar for depth
            highlight_height = self.health_bar_height // 3
            pygame.draw.rect(surface, (44, 172, 236),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, highlight_height))

    def gethealth(self):
        return self.healthbar
    
    def handle_action(self, action, action_frames, is_dash=False):
        """Handle animation frames for the specified action."""
        # Handle attack action
        if self.current_action == 'attack':
            frame = self.animate(self.attack_animation_frames)
            
            # Only reset action when animation completes
            if self.current_frame >= len(self.attack_animation_frames) - 1:
                self.action_in_progress = False
                self.current_action = 'idle'
                
            return frame

        # Handle other actions
        if not self.action_in_progress or self.current_action != action:
            self.current_action = action
            self.current_frame = 0
            self.action_in_progress = True

        frame = self.animate(action_frames, is_dash=is_dash)

        if self.current_frame == len(action_frames) - 1:
            self.action_in_progress = False

        return frame

    def animate(self, action_frames, is_dash=False):
        if not action_frames:
            print("Error: No frames available for this animation.")
            return None

        if self.current_frame >= len(action_frames):
            self.current_frame = 0  # Ensure it resets if out of range

        now = pygame.time.get_ticks()
        
        # Determine frame duration based on action type
        if self.current_action == 'attack':
            frame_duration = 50  # Faster animation for attacks (adjust this value to make it faster/slower)
        elif is_dash:
            frame_duration = self.dash_frame_duration
        else:
            frame_duration = self.frame_duration

        if now - self.last_update_time > frame_duration:
            self.current_frame = (self.current_frame + 1) % len(action_frames)
            self.last_update_time = now

        frame = action_frames[self.current_frame]
        return self.flip_frame(frame)

    def update(self):
        """Update player state, including curse duration"""
        current_time = pygame.time.get_ticks()
        # Check if curse should end
        if self.is_cursed:

            if current_time - self.last_curse_time >= self.curse_timer:
                # Reset curse state
                self.is_cursed = False
                self.velocity = self.original_velocity  # Restore original speed
                # print("Curse ended!")  # Debug message
                
        # Update invincibility
        self.update_invincibility()
        
        # Update hitbox position
        self.hitbox.update(self.x + 40, self.y + 20, 75, 130)

    # ! POTIONS
    def health_pot(self, num):
        if (num == 1):
            self.healthbar += 25
        if (num==2):
            self.healthbar += 50
        if (num == 3):
            self.healthbar +=100
    
    def speed_pot(self):
        self.velocity += 4

    def jump_pot(self):
        self.y_velocity -= .3
    
    def sheild_pot(self):
        self.invincible_duration =+ 9900  # 10 s of invincibility
    
    
        
    
    # def speed_pot(self, num):
    #     if (num == 1):


class ControllerHandler:
    def __init__(self):
        # Initialize the joystick module
        pygame.joystick.init()
        self.controller = None
        self.deadzone = 0.2  # Analog stick deadzone
        
        # Add menu navigation cooldown
        self.menu_cooldown = 200  # milliseconds
        self.last_menu_input = 0
        self.button_cooldown = 300  # milliseconds
        self.last_button_press = 0
        self.level_entry_cooldown = 500  # milliseconds
        self.last_level_entry = 0
        
        self.start_button_pressed = False
        self.last_start_state = False
        self.a_button_pressed = False
        self.last_a_state = False
        # Try to connect to the first available controller
        self.connect_controller()
            
    def connect_controller(self):
        """Attempt to connect to the first available controller."""
        try:
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                # Reset all button states
                self.start_button_pressed = False
                self.last_start_state = False
                self.a_button_pressed = False
                self.last_a_state = False
                # Reset cooldowns
                self.last_button_press = pygame.time.get_ticks()
                self.last_menu_input = pygame.time.get_ticks()
                self.last_level_entry = pygame.time.get_ticks()
                print(f"Controller connected: {self.controller.get_name()}")
                return True
        except pygame.error:
            self.controller = None
            print("Failed to connect controller")
        return False
    
    def is_connected(self):
        """Check if a controller is connected."""
        return self.controller is not None and self.controller.get_init()
    
    def get_movement(self):
        """Get horizontal movement from left analog stick."""
        if not self.is_connected():
            return 0
            
        x_axis = self.controller.get_axis(0)  # Left stick X-axis
        # Apply deadzone
        if abs(x_axis) < self.deadzone:
            return 0
        return x_axis
    
    def is_jumping(self):
        """Check if jump button is pressed (A button on Xbox controller)."""
        if not self.is_connected():
            return False
        return self.controller.get_button(0)  # Button 0 is typically A on Xbox controllers
    
    def is_dashing(self):
        """Check if dash button is pressed (B button on Xbox controller)."""
        if not self.is_connected():
            return False
        return self.controller.get_button(1)  # Button 1 is typically B on Xbox controllers
    
    def is_attacking(self):
        """Check if attack button is pressed (X button on Xbox controller)."""
        if not self.is_connected():
            return False
        return self.controller.get_button(2)  # Button 2 is typically X on Xbox controllers
    
    def is_menu_confirm(self):
        """Check if menu confirm button is pressed (A button) with proper button press tracking."""
        if not self.is_connected():
            return False
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_button_press < self.button_cooldown:
            return False
            
        # Get current A button state
        current_state = self.controller.get_button(3)  # A button
        
        # Check for button press (transition from not pressed to pressed)
        if current_state and not self.last_a_state:
            self.last_button_press = current_time
            self.last_a_state = current_state
            return True
            
        self.last_a_state = current_state
        return False
        
    def is_menu_cancel(self):
        """Check if menu cancel button is pressed (B button)."""
        if not self.is_connected():
            return False
        return self.controller.get_button(1)
    
    def is_start_pressed(self):
        """Check if start button is pressed and handle toggling."""
        if not self.is_connected():
            return False
            
        # Get current start button state
        current_state = self.controller.get_button(6)  # Using button 6 for Start
        
        # Check for button press (transition from not pressed to pressed)
        if current_state and not self.last_start_state:
            self.start_button_pressed = True
            self.last_start_state = current_state
            return True
        
        # Update last state
        self.last_start_state = current_state
        return False
        
    def clear_start_press(self):
            """Clear the start button pressed state after it's been handled."""
            self.start_button_pressed = False

    def get_button_press(self):
        """Debug method to check which button is being pressed"""
        if not self.is_connected():
            return
        
        for i in range(self.controller.get_numbuttons()):
            if self.controller.get_button(i):
                print(f"Button {i} pressed")

    def get_menu_navigation(self):
        """Get menu navigation input with cooldown. Returns (x, y) for direction."""
        if not self.is_connected():
            return (0, 0)
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_menu_input < self.menu_cooldown:
            return (0, 0)
            
        # Check D-pad
        x = 0
        y = 0
        try:
            hat = self.controller.get_hat(0)  # D-pad
            x, y = hat
        except:
            pass  # Some controllers might not have hat/d-pad
            
        # If no d-pad input, check analog stick
        if x == 0 and y == 0:
            x_axis = self.controller.get_axis(0)  # Left stick X
            y_axis = self.controller.get_axis(1)  # Left stick Y
            
            if abs(x_axis) > self.deadzone:
                x = 1 if x_axis > 0 else -1
            if abs(y_axis) > self.deadzone:
                y = 1 if y_axis > 0 else -1
        
        if x != 0 or y != 0:
            self.last_menu_input = current_time
            
        return (x, y)
    def clear_all_button_states(self):
        """Clear all button states"""
        self.clear_start_press()
        self._menu_confirm = False
        self._menu_cancel = False
        self._jumping = False
    
    def check_controller_events(self):
        """Process controller connection/disconnection events."""
        # Only attempt to connect if we don't have a controller
        if pygame.joystick.get_count() > 0 and not self.controller:
            self.connect_controller()
            print("Controller connected")
        elif pygame.joystick.get_count() == 0 and self.controller:
            self.controller = None
            self.start_button_pressed = False
            self.last_start_state = False
            self.a_button_pressed = False
            self.last_a_state = False
            print("Controller disconnected")

class Map:
  def __init__(self, width, height, clock):
        self.screen = pygame.display.set_mode((width, height))
        self.clock = clock

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)
    
    def update(self, target):
        x = int(self.width / 2) - 16
        y = int(self.height / 2) - 16

        self.camera = pygame.Rect(x, y, self.width, self.height)

class Boss:
    def __init__(self, screen, clock):
        
        self.screen = screen
        self.clock = clock
        self.x = 0
        self.y = 180
        self.width = 640
        self.height = 640
        self.health = 1500
        self.speed = 3
        self.direction = 1
        self.phase = 1
        self.idle_animation_frames = []
        self.current_frame = 0
        self.idle_time = 0
        self.last_update_time = pygame.time.get_ticks()
        self.frame_duration = 100
        
        self.projectiles = []
        self.attack_interval = 400
        self.last_attack_time = pygame.time.get_ticks()

    def get_frame(self, sheet, frame, width, height, scale):
        img = sheet.subsurface((0, frame * height, width, height)).convert_alpha()
        # img.blit(sheet, (0,0), ((frame * width), 0, width, height))
        img = pygame.transform.scale(img, (width * scale, height * scale))

        return img

    # def healthbar(self):
    #     # Function to establish / load sprite sheet for healthbar
    #     # Healthbar size is 128x16
    #     project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #     filepath = os.path.join(project_root, "sprites/boss_healthbar_update.png")
    #     hbar = pygame.image.load(filepath)
    #     self.h_init = self.health
    #     self.bar = {}
    #     for i in range(0, 26):   # 9 total frames
    #         self.bar[i] = self.get_frame(hbar, i, 128, 16, 5)

    # def load_healthbar(self, h):
    #     # Blit healthbar to screen based on boss health
    #     val = self.h_init / 25
    #     index = 25
    #     if val != 0:
    #         # health = self.health
    #         index = 25 - ((int)(h / val)) # 'boss health / 25' for specific number at end
    #         # print(f"health is: {h}, index: {index}, val: {val}")
    #     self.screen.blit(self.bar[index], (self.width/2 - 300, 8))


def play_title_sequence(self):
        """Play the title sequence with a fade-in effect"""
        current_time = pygame.time.get_ticks()

        # Check if enough time has passed for the next frame
        if current_time - self.last_frame_time >= self.frame_time:
            self.last_frame_time = current_time
            ret, frame = self.cap.read()

            if ret:
                # Convert frame to Pygame surface with correct orientation
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 0)  # Flip the frame vertically
                frame = np.rot90(frame, k=-1)  # Rotate frame 90 degrees clockwise
                frame = pygame.surfarray.make_surface(frame)

                # Resize the frame to fit the screen if necessary
                frame = pygame.transform.scale(frame, (self.screen.get_width(), self.screen.get_height()))

                # Draw the frame
                self.screen.blit(frame, (0, 0))

                # Create a black overlay surface for fade-in effect
                overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                overlay.set_alpha(255 - self.alpha)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                # Increase alpha value for fade-in effect
                if self.alpha < 255:
                    self.alpha += 5  # Adjust the increment for fade-in speed
                else:
                    self.alpha = 255  # Ensure alpha doesn't exceed 255

                pygame.display.update()
            else:
                # Video finished
                self.cap.release()
                self.title_played = True
                return True

        return False


class Projectile:
    def __init__(self, x, y, speed, image_path):
        self.x = x
        self.y = y
        self.speed = speed
        
        # Load the image
        self.full_image = pygame.image.load(image_path)

        # Crop the image to only include the acorn (100x100 area at the top-left)
        #acorn_rect = pygame.Rect(260, 360, 100, 100)  # Define the region of the acorn in the full image
        acorn_rect = pygame.Rect(0, 0, 75, 75)
        self.image = self.full_image.subsurface(acorn_rect)  # Crop the image to this region
        
        # Create the rect for collision purposes based on the cropped image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        #self.image = pygame.transform.scale(self.image, (60, 60))  # Resize to 100x100

    def move(self):
        # Move the projectile horizontally
        self.x += self.speed
        self.rect.x = self.x  # Update the rect's position for collision detection

    def draw(self, screen):
        # Draw the projectile on the screen at its current position
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self, screen_width):
        # Check if the projectile is off the screen
        return self.x > screen_width + self.rect.width


