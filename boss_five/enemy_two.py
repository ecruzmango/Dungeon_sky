import pygame
import os
from sound_effects.bosses.boss_sound import SoundManager

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class EnemyTwoBeam:
    # Class constants
    ATTACK_FRAME_START = 13
    ATTACK_FRAME_END = 16
    HITBOX_X = 100
    HITBOX_Y = 420
    HITBOX_WIDTH = 1290
    HITBOX_HEIGHT = 50
    ACTIVATION_INTERVAL = 4000  # 4 seconds in milliseconds

    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.attack = False
        self.active = False

        # Initialize position
        self.x = 0
        self.y = 0

        self.sound_manager = SoundManager()

        # Animation properties
        self.animation_speed = 0.2
        self.frame_time = 0
        self.current_frame = 0
        
        # Load animations
        self.enemy_frames = self.load_animations()
        self.current_animation = self.enemy_frames
        
        # Initialize hitbox
        self.hitbox = pygame.Rect(self.HITBOX_X, self.HITBOX_Y, 
                                self.HITBOX_WIDTH, self.HITBOX_HEIGHT)
        
        # Timer initialization
        self.last_activation_time = pygame.time.get_ticks()
        self.activation_complete = False

    def load_animations(self):
        """Load animation frames with error handling"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        enemy_path = os.path.join(project_root, "animations", "boss_five_ani", "enemy.png")
        
        if not os.path.exists(enemy_path):
            print(f"[DEBUG] ERROR: Sprite sheet not found at {enemy_path}")
            return []
            
        try:
            sprite_sheet = pygame.image.load(enemy_path).convert_alpha()  # Added convert_alpha for better performance
            frames = []
            
            for i in range(21):  # Using the known frame count
                frame = sprite_sheet.subsurface(pygame.Rect(
                    i * SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT
                ))
                frames.append(frame)
                
            return frames
        except pygame.error as e:
            print(f"[DEBUG] ERROR loading sprite sheet: {e}")
            return []

    def activate(self):
        self.active = True
        self.frame_time = 0
        self.current_frame = 0
        self.activation_complete = False
        
    def deactivate(self):
        self.active = False
        self.activation_complete = True
            
    def check_hitbox(self):
        """Check if current frame should show hitbox and return it if active"""
        is_attack_frame = self.ATTACK_FRAME_START <= self.current_frame <= self.ATTACK_FRAME_END
        self.attack = is_attack_frame
        
        if is_attack_frame:
            # pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox, 2)
            return self.hitbox
            
        return None

    def update(self):
        """Update animation and hitbox state"""
        current_time = pygame.time.get_ticks()

        previous_frame = self.current_frame
        
        # Check if it's time to activate
        if not self.active and not self.activation_complete:
            if current_time - self.last_activation_time >= self.ACTIVATION_INTERVAL:
                self.activate()
                self.last_activation_time = current_time

        if self.active:
            # Update animation frame
            self.frame_time += self.animation_speed
            if self.enemy_frames:  # Only update if frames exist
                self.current_frame = int(self.frame_time) % len(self.enemy_frames)
                
                if self.current_frame == 1 and previous_frame != 1:
                    self.sound_manager.play_sound('beam')

                # If we've completed one full animation cycle
                if self.current_frame == len(self.enemy_frames) - 1:
                    self.deactivate()
                    
            self.check_hitbox()

    def draw(self, surface):  # Add surface parameter
        """Draw the enemy if active and frames are loaded"""
        if not self.active or not self.enemy_frames:
            return
            
        current_image = self.current_animation[self.current_frame]
        surface.blit(current_image, (self.x, self.y))  # Use surface instead of self.screen
