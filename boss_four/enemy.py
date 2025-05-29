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
        self.speed = 2  # Speed of the broom
        self.projectiles = []

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load projectile image
        projectile_image_path = os.path.join(project_root, "animations", "boss_four_ani", "broom_spinning.png")
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


        # Update projectiles
        self.update_projectiles()

    def reset_position(self):
        # Reset
        self.x = -100
        self.animation_index = 0



    def update_projectiles(self):
        # Update projectiles and safely remove them if off-screen
        for projectile in self.projectiles[:]:
            projectile['y'] += 7  # Move projectile down
            projectile['hitbox'].y = projectile['y']  # Update hitbox position

            # Remove projectile if it goes off-screen
            if projectile['y'] > SCREEN_HEIGHT:
                self.projectiles.remove(projectile)
