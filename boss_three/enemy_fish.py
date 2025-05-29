import os
import pygame

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class EnemyFish:
    def __init__(self, screen, clock, player, starting_x):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.x = starting_x  # Starting X position
        self.y = 700  # Y position at the bottom
        self.speed = 4.5  # Reduced from 9, but keep jump height
        self.jump_height = -300  # Increased for better jump height
        self.drop_speed = 5  # Slightly reduced from 10
        self.direction = "up"
        self.projectiles = []
        self.animation_timer = 0
        self.animation_delay = 7

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fish_jump_path = os.path.join(project_root, "animations", "boss_three_ani", "fish_jump.png")
        self.jump_animation_frames = self.load_frames(fish_jump_path, 13, 320, 320)
        fish_fall_path = os.path.join(project_root, "animations", "boss_three_ani", "fish_down.png")
        self.fall_animation_frames = self.load_frames(fish_fall_path, 1, 320, 320)

        self.active = False
        self.current_frame = 0
        self.current_animation = self.jump_animation_frames
        self.hitbox = pygame.Rect(self.x + 110, self.y + 90, 85, 180)


    def activate(self):
        """Activate the fish enemy"""
        self.active = True

    def deactivate(self):
        """Deactivate the fish enemy"""
        self.active = False

    def load_frames(self, sprite_sheet_path, num_frames, width, height):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            frames.append(frame)
        return frames

    def update(self):
        if not self.active:
            return

        # Update animation timing independently
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            
            # Ensure current_frame stays within bounds
            max_frame = len(self.current_animation) - 1
            
            # Only increment frame if we're not at a frame boundary we want to pause at
            if (self.direction == "up" and self.current_frame < 8) or (self.y <= 100 and self.current_frame < 12):
                self.current_frame = min(self.current_frame + 1, max_frame)

        # Handle movement
        if self.direction == "up":
            if self.y > 100:  # Still going up
                self.y -= self.speed
                # Limit to first 8 frames during upward movement
                if self.current_frame >= 8:
                    self.current_frame = 0
            else:  # Reached peak
                # Play frames 8-12 once at peak
                if self.current_frame < 8:
                    self.current_frame = 8
                elif self.current_frame >= 12:
                    # Once we've played the full jump animation, switch to falling
                    self.direction = "down"
                    self.current_animation = self.fall_animation_frames
                    self.current_frame = 0

        elif self.direction == "down":
            self.y += 5  # Using your new drop speed
            if self.y >= 600:
                # Reset for next jump
                self.direction = "up"
                self.current_animation = self.jump_animation_frames
                self.current_frame = 0
                self.y = 600
                # Add projectile at bottom
                self.projectiles.append({
                    "hitbox": pygame.Rect(self.x + 115, self.y + 90, 85, 180),
                    "y": self.y
                })

        # Ensure current_frame is always in bounds before drawing
        self.current_frame = min(self.current_frame, len(self.current_animation) - 1)
        
        # Update hitbox position
        self.hitbox.update(self.x + 110, self.y + 90, 85, 180)

    # Modify the draw method to accept a surface parameter
    def draw(self, surface):
        if not self.active:
            return
        # Draw the current frame of the fish
        current_image = self.current_animation[self.current_frame]
        surface.blit(current_image, (self.x, self.y))
        # Draw projectiles
        # for projectile in self.projectiles:
        #     pygame.draw.rect(self.screen, (255, 0, 0), projectile['hitbox'], 2)

    def handle_collisions(self):
        if not self.active:
            return
        # Handle projectile collisions with player
        for projectile in self.projectiles[:]: # create a copy of the list to safetly modify
            if self.player.hitbox.colliderect(projectile['hitbox']):  # Collision detected
                if not self.player.invincible:  # Only damage the player if they are not invincible
                    self.player.take_damage(5)  # Deal 50 damage
                    self.projectiles.remove(projectile)
