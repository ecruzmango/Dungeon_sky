import pygame
import os
import random
from sound_effects.bosses.boss_sound import SoundManager

class Cloud:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.x = -100
        self.y = -300
        self.speed = 3
        self.lag_position = None
        self.update_lag_timer = 0
        self.lag_update_interval = 500  # Update target position every 500ms
        self.position_variance = 100  # Increased randomness in targeting


        self.width = 330 
        self.height = 1440
        self.active = False
        
        self.sound_manager = SoundManager()

        hitbox_width = 150  # Reduced from 330 to 150
        hitbox_x_offset = 120  # Center the smaller hitbox within the sprite
        self.hitbox = pygame.Rect(self.x + hitbox_x_offset, self.y + 1000, hitbox_width, 400)

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        idle_sprite_sheet_path = os.path.join(project_root, "animations", "boss_five_ani", "cloud.png")
        self.idle_animation_frames = self.load_frames(idle_sprite_sheet_path, 13, 320, 1440)

        bye_sprite_sheet_path = os.path.join(project_root, "animations", "boss_five_ani", "cloud_stop.png")
        self.bye_animation_frames = self.load_frames(bye_sprite_sheet_path, 13, 320, 1440)

        # Animation settings
        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = 100
        
        # State settings
        self.follow_duration = 6000  # How long to follow the player
        self.start_time = pygame.time.get_ticks()
        self.following = True  # Whether the cloud should follow the player

    def load_frames(self, sprite_sheet_path, num_frames, width, height):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            frames.append(frame)
        return frames
    
    def activate(self):
        """Activate the cloud and reset its position"""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.following = True
        self.x = -100  # Reset position
        self.y = -300
        
    def deactivate(self):
        self.active = False
        self.following = False
        
    def update(self):
        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.start_time
        previous_frame = self.animation_index

        # Update animation
        self.animation_timer += self.clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            if not self.following:
                # Play bye animation when not following
                self.animation_index = (self.animation_index + 1) % len(self.bye_animation_frames)
                print(f"Playing bye animation frame: {self.animation_index}")  # Debug print
            else:
                self.animation_index = (self.animation_index + 1) % len(self.idle_animation_frames)
        

        # Check if we should still be following the player
        if time_elapsed <= self.follow_duration:
            if self.following:
                # Update lagged position periodically
                self.update_lag_timer += self.clock.get_time()
                if self.lag_position is None or self.update_lag_timer >= self.lag_update_interval:
                    self.update_lag_timer = 0
                    self.lag_position = self.player.x + random.randint(-self.position_variance, self.position_variance)

                # Move towards lagged position
                if self.lag_position is not None:
                    target_x = self.lag_position - (self.width // 2)
                    if abs(self.x - target_x) > self.speed:
                        if self.x < target_x:
                            self.x += self.speed
                        else:
                            self.x -= self.speed
                if self.animation_index == 9 and previous_frame != 9:
                    self.sound_manager.play_sound('thunder')
        else:
            # Start bye animation and move off screen
            if self.following:
                print("Timer ended, starting bye animation")  # Debug print
                self.following = False
                self.animation_index = 0  # Reset animation index for bye animation
            
            # Move off screen while playing bye animation
            self.x += self.speed
            print(f"Moving off screen. X position: {self.x}")  # Debug print
            
            # Only deactivate when completely off screen
            if self.x > 1300:
                print("Cloud reached edge of screen, deactivating")  # Debug print
                self.active = False

        # Update hitbox position
        self.hitbox.x = self.x + 120
        self.hitbox.y = self.y + 600
        # print(f"Hitbox position: x={self.hitbox.x}, y={self.hitbox.y}")  # Debug print

    def draw(self, surface):  # Add surface parameter
            if not self.active:
                return
                    
            if not self.following:
                current_frame = self.bye_animation_frames[self.animation_index]
            else:
                current_frame = self.idle_animation_frames[self.animation_index]
            
            surface.blit(current_frame, (self.x, self.y))  # Use surface instead of self.screen
            
            # Debug visualization (if needed)
            # pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 2)
            
            # Debug text
            # font = pygame.font.Font(None, 36)
            # debug_text = f"State: {'Leaving' if not self.following else 'Following'}"
            # debug_surface = font.render(debug_text, True, (255, 0, 0))
            # surface.blit(debug_surface, (10, 10))

    def check_hitbox(self):
        # Only return hitbox if we're on frames 9-12 and still following
        is_attack_frame = 9 <= self.animation_index <= 12
        return self.hitbox if self.active and is_attack_frame and self.following else None