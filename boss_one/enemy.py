import os
import pygame

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class Enemy:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.x = -100  # Starting X position off-screen
        self.y = 50  # Y position near the top
        self.speed = 2  # Speed of the mosquito
        self.state = "idle"  # Possible states: idle, dropping, no_apple
        self.projectiles = []
        self.debug_mode = True  # Add debug mode flag

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load idle animation frames
        idle_sprite_sheet_path = os.path.join(project_root, "animations", "boss_one_ani", "fly_idle.png")
        self.idle_animation_frames = self.load_frames(idle_sprite_sheet_path, 2, 160, 160)

        # Load attack animation frames (fly drop)
        drop_sprite_sheet_path = os.path.join(project_root, "animations", "boss_one_ani", "fly_drop.png")
        self.drop_animation_frames = self.load_frames(drop_sprite_sheet_path, 2, 160, 160)

        # Load no_apple animation frames
        no_apple_sprite_sheet_path = os.path.join(project_root, "animations", "boss_one_ani", "fly_no_apple.png")
        self.no_apple_animation_frames = self.load_frames(no_apple_sprite_sheet_path, 2, 160, 160)

        # Load projectile image
        projectile_image_path = os.path.join(project_root, "animations", "boss_one_ani", "apple_proj.png")
        self.projectile_image = pygame.image.load(projectile_image_path).convert_alpha()

        # Animation settings
        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = 100  # milliseconds per frame

    def load_frames(self, sprite_sheet_path, num_frames, width, height):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            frames.append(frame)
        return frames

    def update(self, delta_time):
        # Animation timing
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.current_animation())

        # Mosquito movement
        self.x += self.speed * (delta_time / 16)  # Adjust speed by delta time
        if self.x > SCREEN_WIDTH:  # Remove if off-screen
            self.reset_position()  # Reset and create new fly

        if self.state == "idle":
            # Check if aligned with the player
            if abs(self.x - self.player.x) < 10:
                self.state = "dropping"  # Start dropping the projectile

        elif self.state == "dropping":
            if self.animation_index == len(self.drop_animation_frames) - 1:  # Drop complete
                self.drop_projectile()
                self.state = "no_apple"

        # Update projectiles
        self.update_projectiles()

    def reset_position(self):
        # Reset the fly for reuse
        self.x = -100
        self.state = "idle"
        self.animation_index = 0

    def update_projectiles(self):
        # Update projectiles and safely remove them if off-screen
        for projectile in self.projectiles[:]:
            projectile['y'] += 7  # Move projectile down
            projectile['hitbox'].y = projectile['y'] + 90 # Update hitbox position

            # Remove projectile if it goes off-screen
            if projectile['y'] > SCREEN_HEIGHT:
                self.projectiles.remove(projectile)

    def drop_projectile(self):
        # Create a projectile with a hitbox of 75x75
        projectile = {
            'x': self.x,
            'y': self.y + 1,
            'hitbox': pygame.Rect(self.x+40, self.y + 90, 30, 50)
        }
        self.projectiles.append(projectile)

    def draw(self, surface):
        """Draw the enemy and its projectiles on the specified surface."""
        # Draw the current animation frame
        current_frame = self.current_animation()[self.animation_index]
        surface.blit(current_frame, (self.x, self.y))

        # Draw projectiles
        for projectile in self.projectiles:
            surface.blit(self.projectile_image, (projectile['x'], projectile['y']))
            
            # Draw debug hitboxes if debug mode is enabled
            # if self.debug_mode:
            #     pygame.draw.rect(surface, (255, 0, 0), projectile['hitbox'], 2)  # Red rectangle with 2px width
            
    def current_animation(self):
        if self.state == "idle":
            return self.idle_animation_frames
        elif self.state == "dropping":
            return self.drop_animation_frames
        elif self.state == "no_apple":
            return self.no_apple_animation_frames