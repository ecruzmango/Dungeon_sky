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
        
        # Pre-calculate hitbox offset and size
        self.hitbox_offset = 70 if direction == "left" else 10
        self.hitbox = pygame.Rect(x + self.hitbox_offset, y, 80, 80)
        
        self.entrance_progress = 0
        self.entrance_speed = 2.0
        
        # Pre-calculate positions
        self.idle_x = 200 if direction == "right" else SCREEN_WIDTH - 280
        self.idle_y = y
        
        # Pre-calculate curve points and coefficients once
        self._initialize_curve()
        
    def _initialize_curve(self):
        """Pre-calculate curve points and coefficients"""
        self.p1 = (self.idle_x, self.idle_y)
        
        # Calculate control point (p2) based on direction
        center_offset = random.randint(-300, 300)
        target_x = SCREEN_WIDTH // 2 + center_offset
        target_y = SCREEN_HEIGHT - 100
        self.p2 = (target_x, target_y)
        
        # Calculate end point (p3) based on direction
        exit_x = -300 if self.direction == "right" else SCREEN_WIDTH + 300
        self.p3 = (exit_x, target_y + random.randint(-50, 50))
        
        # Pre-calculate quadratic coefficients
        self.quad_ax = self.p1[0] - 2 * self.p2[0] + self.p3[0]
        self.quad_bx = 2 * (self.p2[0] - self.p1[0])
        self.quad_cx = self.p1[0]
        self.quad_ay = self.p1[1] - 2 * self.p2[1] + self.p3[1]
        self.quad_by = 2 * (self.p2[1] - self.p1[1])
        self.quad_cy = self.p1[1]
        
    def get_quadratic_point(self, t):
        """Optimized quadratic curve calculation"""
        t2 = t * t
        x = (self.quad_ax * t2 + self.quad_bx * t + self.quad_cx)
        y = (self.quad_ay * t2 + self.quad_by * t + self.quad_cy)
        return x, y

    def update(self, dt):
        self.animation_timer += dt
        
        if self.state == RavenState.IDLE:
            if self.entrance_progress < 1.0:
                # Use linear interpolation for entrance
                self.entrance_progress = min(1.0, self.entrance_progress + dt * self.entrance_speed)
                self.x = self.x + (self.idle_x - self.x) * self.entrance_progress
                self.hitbox.x = self.x + self.hitbox_offset
                    
            # Update animation frame less frequently
            if self.animation_timer >= 0.1:
                self.current_frame = (self.current_frame + 1) % 3
                self.animation_timer = 0
            
            # Check for attack state
            if self.entrance_progress >= 1.0:
                self.attack_timer -= dt
                if self.attack_timer <= 0:
                    self.state = RavenState.ATTACK
                    self.attack_progress = 0
        
        elif self.state == RavenState.ATTACK:
            # Optimize attack movement
            self.attack_progress = min(1.0, self.attack_progress + dt * 0.65)
            self.x, self.y = self.get_quadratic_point(self.attack_progress)
            self.hitbox.x = self.x + self.hitbox_offset
            self.hitbox.y = self.y
            
            if self.attack_progress >= 1.0:
                self.state = RavenState.EXIT

class EnemyRaven:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.ravens = []
        
        # Pre-calculate spawn points
        self.spawn_points = {
            "right": {"x": -100, "idle_x": 200, "y_range": (50, 150)},
            "left": {"x": SCREEN_WIDTH + 100, "idle_x": SCREEN_WIDTH - 280, "y_range": (50, 150)}
        }
        
        self.spawn_timer = 0
        self.spawn_interval = 2.0
        self.max_ravens = 3
        
        # Initialize frames and cache them
        self.frames = self._initialize_frames()
        self._initialize_raven_pool()
        
        self.active = False
        
    def _initialize_frames(self):
        """Load and cache all frames at initialization"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raven_fly_path = os.path.join(project_root, "animations", "boss_four_ani", "raven_idle.png")
        raven_attack_path = os.path.join(project_root, "animations", "boss_four_ani", "raven_attack.png")
        
        frames = {}
        for direction in ["right", "left"]:
            frames[direction] = {
                "idle": [],
                "attack": []
            }
            
            # Load idle frames
            idle_sheet = pygame.image.load(raven_fly_path).convert_alpha()
            for i in range(3):
                frame = idle_sheet.subsurface((i * 160, 0, 160, 160))
                if direction == "left":
                    frame = pygame.transform.flip(frame, True, False)
                frames[direction]["idle"].append(frame)
            
            # Load attack frame
            attack_sheet = pygame.image.load(raven_attack_path).convert_alpha()
            frame = attack_sheet.subsurface((0, 0, 160, 160))
            if direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            frames[direction]["attack"].append(frame)
            
        return frames

    def _initialize_raven_pool(self):
        # Pre-calculate common raven parameters
        self.raven_pool = {
            "right": [],
            "left": []
        }
        # Create a pool of pre-initialized ravens for each direction
        for direction in ["right", "left"]:
            for _ in range(self.max_ravens * 2):  # Double the max for buffer
                spawn_info = self.spawn_points[direction]
                raven = Raven(spawn_info["x"], random.randint(*spawn_info["y_range"]), direction)
                self.raven_pool[direction].append(raven)

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        if not os.path.exists(sprite_sheet_path):
            raise FileNotFoundError(f"Sprite sheet not found: {sprite_sheet_path}")
            
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        return [sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height)) 
                for i in range(num_frames)]

    
    def activate(self):
        self.active = True
        self.spawn_timer = 0
    
    def deactivate(self):
        self.active = False
        self.ravens.clear()
        
    def update(self, dt):
        if not self.active:
            return
            
        # Spawn new ravens
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.ravens) < self.max_ravens:
            self.spawn_timer = 0
            self.spawn_raven()
        
        # Update existing ravens
        self.ravens = [raven for raven in self.ravens if raven.state != RavenState.EXIT]
        for raven in self.ravens:
            raven.update(dt)

    def spawn_raven(self):
        direction = random.choice(["left", "right"])
        
        # Get a pre-initialized raven from the pool
        if self.raven_pool[direction]:
            raven = self.raven_pool[direction].pop(0)
            # Reset raven position
            spawn_info = self.spawn_points[direction]
            raven.y = random.randint(*spawn_info["y_range"])
            raven.x = spawn_info["x"]
            raven.idle_x = spawn_info["idle_x"]
            raven.entrance_progress = 0
            raven.state = RavenState.IDLE
            self.ravens.append(raven)
            
            # Create a new raven for the pool to maintain size
            new_raven = Raven(spawn_info["x"], random.randint(*spawn_info["y_range"]), direction)
            self.raven_pool[direction].append(new_raven)

    def draw(self):
            """Optimized drawing method"""
            if not self.active:
                return
                
            for raven in self.ravens:
                frames = self.frames[raven.direction]
                frame = (frames["idle"][raven.current_frame] if raven.state == RavenState.IDLE 
                        else frames["attack"][0])
                self.screen.blit(frame, (raven.x, raven.y))