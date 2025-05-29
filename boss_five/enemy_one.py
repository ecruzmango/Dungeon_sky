import pygame
import os
from sound_effects.bosses.boss_sound import SoundManager

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class EnemyOneChess:
    def __init__(self, screen, clock, player, x, going_right):
        self.animation_index = 0
        self.screen = screen
        self.clock = clock
        self.player = player
        self.active = False

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        enemy_path = os.path.join(project_root, "animations", "boss_five_ani", "friend.png")

        # load the attack animation
        self.idle_animation_frames = self.load_frames(enemy_path, 10, 160, 160)

        self.wait_durration = 600
        self.last_attack_time = 0
        self.attack_duration = 0
        self.startx = x
        self.x = x
        self.y = -100
        self.direction = going_right
        self.frame_duration = 50
        self.state = "Waiting"
        self.hitbox = pygame.Rect(self.x+10, self.y+18, 70, 110)
        self.timer = pygame.time.get_ticks()
        self.animation_timer = pygame.time.get_ticks()

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        """Load frames from a sprite sheet."""
        if not os.path.exists(sprite_sheet_path):
            #print(f"[DEBUG] ERROR: Sprite sheet not found at {sprite_sheet_path}")
            return []
        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path)
            #print("[DEBUG] Successfully loaded sprite sheet")
        except pygame.error as e:
            #print(f"[DEBUG] ERROR loading sprite sheet: {e}")
            return []

        frames = [
            sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            for i in range(num_frames)
        ]
        return frames
    
    def activate(self):
        """Activate the enemy and reset its position"""
        self.active = True
        self.reset_position()
        self.state = "Dropping"
        self.timer = pygame.time.get_ticks()
        
    def deactivate(self):
        self.active = False
        self.state = "Waiting"

    def update(self):
        if not self.active:
            return
        if self.state == "Waiting":
            if pygame.time.get_ticks() - self.timer >= self.wait_durration:
                self.reset_position()
        if self.state == "Dropping":
            self.y += 10
            if self.y > 415:
                self.state = "Moving"
                self.animation_timer = pygame.time.get_ticks()
        elif self.state == "Moving":
            if pygame.time.get_ticks() - self.animation_timer >= self.frame_duration:
                self.animation_index = (self.animation_index + 1) % len(self.idle_animation_frames)
                self.animation_timer = pygame.time.get_ticks()
            if self.direction == True:
                self.x -= 7 #speed
            else:
                self.x += 7
            if self.x > 1052 or self.x < 150:
                self.state = "Dropping2"
        elif self.state == "Dropping2":
            self.y += 10
            if self.y > 720: 
                self.state = "Waiting"
        
    def hit(self)->int:
            if pygame.time.get_ticks() - self.last_attack_time >= self.attack_duration:
                self.last_hit_time = pygame.time.get_ticks()
                return 30
            return 0

    def get_hitbox(self):
        return self.hitbox

    def reset_position(self):
        # Reset for reuse
        self.x = self.startx
        self.y = -100
        self.state = "Dropping"
        self.timer = pygame.time.get_ticks()
        self.animation_index = 0


    def draw(self, surface):  # Add surface parameter
        if not self.active:
            return
        # Draw the current animation frame
        if self.state == "Dropping" or self.state == "Dropping2":
            current_frame = self.idle_animation_frames[0].copy()
        if self.state == "Moving":
            current_frame = self.idle_animation_frames[self.animation_index].copy()

        if self.state != "Waiting":
            surface.blit(current_frame, (self.x, self.y))  # Use surface instead of self.screen
            self.hitbox = pygame.Rect(self.x+10, self.y+18, 70, 110)
            # pygame.draw.rect(surface, (209, 209, 209), self.hitbox)  # Updated for debugging



