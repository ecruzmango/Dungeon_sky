import pygame
import os
import random

class Blob:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        
        # Position and movement
        self.x = 160
        self.y = 400  # Fixed y coordinate
        self.speed = 3
        self.active = False
        self.width = 320
        self.height = 1920
        
        # Animation settings
        self.facing_right = True
        self.initial_animation = True
        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = 100
        self.current_animation = 'idle'
        self.is_leaving = False
        
        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        attack_sprite_sheet_path = os.path.join(project_root, "animations", "boss_five_ani", "blob.png")
        self.attack_animation_frames = self.load_frames(attack_sprite_sheet_path, 6, 320, 320)

        hi_sprite_sheet_path = os.path.join(project_root, "animations", "boss_five_ani", "blob_hi.png")
        self.hi_animation_frames = self.load_frames(hi_sprite_sheet_path, 11, 320, 320)

        bye_sprite_sheet_path = os.path.join(project_root, "animations", "boss_five_ani", "blob_bye.png")
        self.bye_animation_frames = self.load_frames(bye_sprite_sheet_path, 11, 320, 320)


        # Tracking settings
        self.lag_position = None
        self.update_lag_timer = 0
        self.lag_update_interval = 400  # Update target position every 400ms
        self.position_variance = 50

        # Hitbox
        self.hitbox = pygame.Rect(self.x+40, self.y+20, 110, 140)

    def load_frames(self, sprite_sheet_path, num_frames, width, height):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            frames.append(frame)
        return frames
    
    
    def activate(self):
        """Activate the blob and set its initial position"""
        self.active = True
        self.x = 300
        self.y = 400
        self.is_leaving = False
        self.current_animation = 'hi'
        self.animation_index = 0
        self.initial_animation = True
        self.facing_right = True
        
    def deactivate(self):
        """Start the leaving animation sequence"""
        if self.active and not self.is_leaving:
            self.is_leaving = True
            self.current_animation = 'bye'
            self.animation_index = 0

   
    def update(self):
        if not self.active:
            return

        # Update animation timing
        self.animation_timer += self.clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            
            if self.is_leaving:
                # Handle bye animation
                self.animation_index = (self.animation_index + 1) % len(self.bye_animation_frames)
                if self.animation_index >= len(self.bye_animation_frames) - 1:
                    self.active = False
                    return
            elif self.initial_animation:
                # Handle initial hi animation
                self.animation_index = (self.animation_index + 1) % len(self.hi_animation_frames)
                if self.animation_index >= len(self.hi_animation_frames) - 1:
                    self.initial_animation = False
                    self.current_animation = 'idle'
                    self.animation_index = 0
            else:
                # Handle idle animation
                self.animation_index = (self.animation_index + 1) % len(self.attack_animation_frames)

        if not self.is_leaving and not self.initial_animation:
            # Update lag position for smoother following
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
                        self.facing_right = True
                    else:
                        self.x -= self.speed
                        self.facing_right = False

        # Update hitbox position
        self.hitbox.x = self.x + 40
        self.hitbox.y = self.y + 20

        
    def draw(self, surface):  # Add surface parameter
        if not self.active:
            return

        current_frame = None
        if self.is_leaving:
            current_frame = self.bye_animation_frames[self.animation_index]
        elif self.initial_animation:
            current_frame = self.hi_animation_frames[self.animation_index]
        else:
            current_frame = self.attack_animation_frames[self.animation_index]

        if current_frame:
            draw_x = self.x
            
            if not self.facing_right:
                current_frame = pygame.transform.flip(current_frame, True, False)
                offset = 180
                draw_x = self.hitbox.x - offset
                
                # Debug text (if needed)
                # font = pygame.font.Font(None, 36)
                # debug_info = f"X: {self.x}, Hitbox X: {self.hitbox.x}, Draw X: {draw_x}"
                # debug_surface = font.render(debug_info, True, (255, 0, 0))
                # surface.blit(debug_surface, (10, 50))
            
            surface.blit(current_frame, (draw_x, self.y))  # Use surface instead of self.screen
            
        # Debug hitbox visualization (if needed)
        # pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 2)

    def check_hitbox(self):
        """Return the hitbox if active and not in leaving animation"""
        return self.hitbox if self.active and not self.is_leaving else None