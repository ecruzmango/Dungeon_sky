import pygame
import os

class Enemy:
    def __init__(self, screen, clock, player):
        self.screen = screen
        self.clock = clock
        self.player = player
        self.x = 1000
        self.y = 500
        self.width = 160
        self.height = 160
        
        self.hitbox_offset_x = 40
        self.hitbox_offset_y = 40
        self.hitbox_width = 80
        self.hitbox_height = 80
        
        self.state = "idle"
        self.previous_state = "idle"  # Add this to track state changes
        self.color = (255, 255, 255)
        self.is_damage_flashing = False
        self.last_hit_time = 0
        self.hit_cooldown = False
        self.hit_cooldown_time = 0
        self.hit_cooldown_duration = 800

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load animations
        idle_sprite_sheet_path = os.path.join(project_root, "animations", "tutorial_ani", "Dummy_idle.png")
        self.idle_animation_frames = self.load_frames(idle_sprite_sheet_path, 1, 160, 160)

        talk_sprite_sheet_path = os.path.join(project_root, "animations", "tutorial_ani", "Dummy_talk.png")
        self.talk_animation_frames = self.load_frames(talk_sprite_sheet_path, 2, 160, 160)

        hit_sprite_sheet_path = os.path.join(project_root, "animations", "tutorial_ani", "Dummy_hit.png")
        self.hit_animation_frames = self.load_frames(hit_sprite_sheet_path, 8, 160, 160)

        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = 100
        
        # Animation state tracking
        self.current_animation_frames = self.idle_animation_frames

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        """Load frames from a sprite sheet with better error handling"""
        frames = []
        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            sheet_width = sprite_sheet.get_width()
            
            print(f"[DEBUG] Loading sprite sheet: {sprite_sheet_path}")
            print(f"[DEBUG] Sheet dimensions: {sheet_width}x{sprite_sheet.get_height()}")
            print(f"[DEBUG] Expected frames: {num_frames}")
            
            for frame in range(num_frames):
                x = frame * frame_width
                surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                surface.blit(sprite_sheet, (0, 0), (x, 0, frame_width, frame_height))
                frames.append(surface)
                
            print(f"[DEBUG] Successfully loaded {len(frames)} frames")
            return frames
        except Exception as e:
            print(f"[ERROR] Failed to load sprite sheet: {e}")
            return []

    def get_hitbox(self):
        """Get the hitbox for collision detection"""
        return pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height
        )

    def get_talk_range(self):
        """Get the range for talking detection"""
        hitbox = self.get_hitbox()
        return hitbox.inflate(150, 150)

    def is_player_in_range(self):
        """Check if player is in talking range"""
        player_rect = pygame.Rect(self.player.x + 40, self.player.y + 20, 75, 130)
        return self.get_talk_range().colliderect(player_rect)

    def check_hit(self):
        """Check if player's attack hits the dummy"""
        if not self.hit_cooldown and self.player.current_action == 'attack':
            if self.player.facing_right:
                attack_hitbox = pygame.Rect(
                    self.player.x + 60,
                    self.player.y,
                    90,
                    130
                )
            else:
                attack_hitbox = pygame.Rect(
                    self.player.x + 60,
                    self.player.y,
                    90,
                    130
                )
            
            if self.get_hitbox().colliderect(attack_hitbox):
                self.take_hit()
                return True
        return False

    def take_hit(self):
        """Handle being hit by the player"""
        if not self.hit_cooldown:
            print("Dummy hit!")
            self.state = "hit"
            self.animation_index = 0
            self.color = (255, 0, 0)
            self.is_damage_flashing = True
            self.last_hit_time = pygame.time.get_ticks()
            self.hit_cooldown = True
            self.hit_cooldown_time = pygame.time.get_ticks()

    def update(self, player):
        """Update dummy state and animations"""
        current_time = pygame.time.get_ticks()
        
        # Store previous state before updating
        self.previous_state = self.state
        
        # Check for hits
        self.check_hit()
        
        # Update damage flash effect
        if self.is_damage_flashing and current_time - self.last_hit_time > 200:
            self.color = (255, 255, 255)
            self.is_damage_flashing = False

        # Update hit cooldown
        if self.hit_cooldown and current_time - self.hit_cooldown_time > self.hit_cooldown_duration:
            self.hit_cooldown = False
            self.state = "idle"

        # Update state based on player proximity
        if self.state != "hit":
            if self.is_player_in_range():
                self.state = "talk"
            else:
                self.state = "idle"

        # Handle state transitions
        if self.previous_state != self.state:
            # Only reset animation index if we're transitioning to a new state
            self.animation_index = 0
            self.animation_timer = 0
            
            # Update current animation frames
            if self.state == "idle":
                self.current_animation_frames = self.idle_animation_frames
            elif self.state == "talk":
                self.current_animation_frames = self.talk_animation_frames
            elif self.state == "hit":
                self.current_animation_frames = self.hit_animation_frames

        # Update animation frame
        self.animation_timer += self.clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.current_animation_frames)
            
            # Check if hit animation is complete
            if self.state == "hit" and self.animation_index == 0:
                self.state = "idle"
                self.current_animation_frames = self.idle_animation_frames

    def draw(self, screen):
        """Draw the dummy with current animation frame and hitboxes"""
        hitbox = self.get_hitbox()
        talk_range = self.get_talk_range()
        
        # Draw the sprite
        if self.current_animation_frames and len(self.current_animation_frames) > 0:
            frame = self.current_animation_frames[self.animation_index].copy()
            
            if self.is_damage_flashing:
                frame.fill(self.color, special_flags=pygame.BLEND_MULT)
            
            screen.blit(frame, (self.x, self.y))

            # Draw speech bubble when talking
            if self.state == "talk":
                font = pygame.font.SysFont(None, 30)
                text = font.render("Hit me!", True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), 
                               (self.x, self.y - 40, text.get_width() + 20, 30))
                screen.blit(text, (self.x + 10, self.y - 35))