import pygame
import os
import random
import math
from enum import Enum
from sound_effects.bosses.boss_sound import SoundManager

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class RavenState(Enum):
    IDLE = "idle"
    ATTACK = "attack"
    EXIT = "exit"

class Raven:
    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = RavenState.IDLE
        self.current_frame = 0
        self.animation_timer = 0
        self.attack_timer = random.uniform(2, 4)
        self.attack_progress = 0
        self.hitbox = pygame.Rect(x, y, 80, 80)
        
        # Add entrance animation variables
        self.entrance_progress = 0
        self.entrance_speed = 2.0  # Speed of entrance movement
        self.sound_manager = SoundManager()
        
        # Set actual idle position based on direction
        if direction == "right":
            self.idle_x = 200  # Further into screen from right
        else:
            self.idle_x = SCREEN_WIDTH - 280  # Further into screen from left
            
        self.idle_y = y  # Keep the same y position
        
        # Attack curve parameters
        self.start_pos = (self.idle_x, self.idle_y)  # Use idle position as start
        
        # Calculate target point near bottom-center of screen
        center_offset = random.randint(-300, 300)
        target_x = SCREEN_WIDTH // 2 + center_offset
        target_y = SCREEN_HEIGHT - 100
        
        # Calculate exit point based on direction
        if direction == "right":
            exit_x = -300
        else:
            exit_x = SCREEN_WIDTH + 300
            
        # Store points for quadratic curve
        self.p1 = (self.idle_x, self.idle_y)  # Start from idle position
        self.p2 = (target_x, target_y)
        self.p3 = (exit_x, target_y - random.randint(-50, 50))

    def get_quadratic_point(self, t):
        """Calculate point on quadratic curve at time t (0 to 1)"""
        x = (1-t)**2 * self.p1[0] + 2*(1-t)*t * self.p2[0] + t**2 * self.p3[0]
        y = (1-t)**2 * self.p1[1] + 2*(1-t)*t * self.p2[1] + t**2 * self.p3[1]
        return x, y

    def update(self, dt):
        self.animation_timer += dt
        
        if self.state == RavenState.IDLE:
            # Handle entrance movement
            if self.entrance_progress < 1.0:
                self.entrance_progress += dt * self.entrance_speed
                progress = min(self.entrance_progress, 1.0)
                
                # Lerp from spawn position to idle position
                if self.direction == "right":
                    self.x = self.x + (self.idle_x - self.x) * progress
                else:
                    self.x = self.x + (self.idle_x - self.x) * progress
                    
                # Update hitbox during entrance
                if self.direction == "right":
                    self.hitbox.x = self.x + 10
                else:
                    self.hitbox.x = self.x + 50
                    
            # Handle idle animation
            if self.animation_timer >= 0.1:
                self.current_frame = (self.current_frame + 1) % 3
                self.animation_timer = 0
            
            # Only start attack timer after entrance is complete
            if self.entrance_progress >= 1.0:
                self.attack_timer -= dt
                if self.attack_timer <= 0:
                    self.state = RavenState.ATTACK
                    self.sound_manager.play_sound('raven')
                    self.attack_progress = 0
        
        elif self.state == RavenState.ATTACK:
            self.attack_progress += dt * 0.65
            
            progress = min(self.attack_progress, 1.0)
            
            # Get position on quadratic curve
            self.x, self.y = self.get_quadratic_point(progress)
            
            # Update hitbox position with direction-based offset
            if self.direction == "right":
                self.hitbox.x = self.x + 10
            else:
                self.hitbox.x = self.x + 70
                
            self.hitbox.y = self.y
            
            if progress >= 1.0:
                self.state = RavenState.EXIT


    def draw(self, screen, idle_frames, attack_frames):
        """Draw the raven with appropriate animation frame"""
        if not idle_frames or not attack_frames:
            return
            
        frame = idle_frames[self.current_frame] if self.state == RavenState.IDLE else attack_frames[0]
        
        if self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)
        
        screen.blit(frame, (self.x, self.y))
        
        # Uncomment for hitbox debugging
        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)

class EnemyRaven:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.ravens = []
        
        self.spawn_timer = 0
        self.spawn_interval = 2.0
        self.max_ravens = 3
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raven_fly_path = os.path.join(project_root, "animations", "boss_four_ani", "raven_idle.png")
        raven_attack_path = os.path.join(project_root, "animations", "boss_four_ani", "raven_attack.png")
        
        print(f"Loading raven sprites from: {raven_fly_path}")
        
        self.raven_idle_frames = self.load_frames(raven_fly_path, 3, 160, 160)
        self.raven_attack_frames = self.load_frames(raven_attack_path, 1, 160, 160)
        
        self.active = False

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        if not os.path.exists(sprite_sheet_path):
            print(f"Warning: Sprite sheet not found at {sprite_sheet_path}")
            return []
            
        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            frames = []
            for i in range(num_frames):
                frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                frames.append(frame)
            return frames
        except Exception as e:
            print(f"Error loading frames: {e}")
            return []
    
    def activate(self):
        self.active = True
        self.spawn_timer = 0
    
    def deactivate(self):
        self.active = False
        self.ravens.clear()
        
    def update(self, dt):
        if not self.active:  # Don't update if ravens are deactivated
            return
            
        # Update spawn timer and create new ravens if needed
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.ravens) < self.max_ravens:
            self.spawn_timer = 0
            self.spawn_raven()
        
        # Update existing ravens and remove those that have exited
        updated_ravens = []
        for raven in self.ravens:
            raven.update(dt)
            if raven.state != RavenState.EXIT:
                updated_ravens.append(raven)
        
        self.ravens = updated_ravens
    
    def spawn_raven(self):
        direction = random.choice(["left", "right"])
        
        if direction == "right":
            x = 50
        else:
            x = SCREEN_WIDTH +50 
            
        y = random.randint(50, 150)  # Lower spawn height for better swooping
        
        raven = Raven(x, y, direction)
        self.ravens.append(raven)
    
    def draw(self):
        if not self.active:
            return
            
        for raven in self.ravens:
            raven.draw(self.screen, self.raven_idle_frames, self.raven_attack_frames)