import os 
import pygame
import random
from headers.utils import load_sprite_frames
from sound_effects.bosses.boss_sound import SoundManager

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class EnemyDuck:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.ducks = []  # List to store multiple ducks
        self.projectiles = []
        self.animation_timer = 0
        
        self.sound_manager = SoundManager()

        
        # setup paths and sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        duck_fly_path = os.path.join(project_root, "animations", "boss_three_ani", "duck_enemy.png")

        
        # load the attack animation for the duck
        self.duck_frames = load_sprite_frames(duck_fly_path, 4, 320, 320)


        self.current_frame = 0
        self.frame_duration = 100 

        # flags
        self.active = False
        self.scenario = None
        


    def setup_new_scenario(self):
        """Set up a random scenario when called"""
        self.scenario = random.choice([1, 2, 3])
        self.ducks.clear()
        
        if self.scenario == 1:  # Single fast duck
            duck = {
                'x': -100,
                'y': random.randint(100, 500),
                'speed': 12,
                'hitbox': pygame.Rect(-100, random.randint(100, 500), 170, 110)
            }
            self.ducks.append(duck)
            
        elif self.scenario == 2:  # Group of ducks
            for i in range(4):
                duck = {
                    'x': -100 - (i * 100),
                    'y': 420 + (i * 30),
                    'speed': 7,
                    'hitbox': pygame.Rect(-100 - (i * 100), 420 + (i * 30), 170, 110)
                }
                self.ducks.append(duck)
                
        else:  # Two ducks from different positions
            duck1 = {
                'x': -100,
                'y': 200,
                'speed': 8,
                'hitbox': pygame.Rect(-100, 200, 170, 110)
            }
            duck2 = {
                'x': SCREEN_WIDTH + 100,
                'y': 390,
                'speed': -8,
                'hitbox': pygame.Rect(SCREEN_WIDTH + 100, 390, 170, 110)
            }
            self.ducks.extend([duck1, duck2])




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
        self.active = True
        
    
    def deactivate(self):
        self.active = False
  
    
    def draw(self, surface):
        if not self.active:
            return
        
        if not self.duck_frames:
            print("[DEBUG] No duck frames available for drawing")
            return
            
        frame_count = len(self.duck_frames)
        if frame_count == 0:
            print("[DEBUG] Empty duck frames list")
            return
        
        self.current_frame = self.current_frame % frame_count
            
        # Draw each duck in the scenario
        for duck in self.ducks:
            current_image = self.duck_frames[self.current_frame]
            if duck['speed'] < 0:
                current_image = pygame.transform.flip(current_image, True, False)
            surface.blit(current_image, (duck['x'], duck['y']))


    def update(self, delta_time):
        if not self.active or not self.duck_frames:
            return
            
        # Animation timing
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.duck_frames)

        # Update duck positions
        all_ducks_off_screen = True
        for duck in self.ducks:
            duck['x'] += duck['speed'] * (delta_time / 16)
            duck['hitbox'].x = duck['x'] + 30
            duck['hitbox'].y = duck['y'] + 70
            
            if -200 <= duck['x'] <= SCREEN_WIDTH + 200:
                all_ducks_off_screen = False

        # If all ducks are off screen, just deactivate
        if all_ducks_off_screen:
            self.active = False
            self.ducks.clear()