import pygame
import sys
import os
from headers.classes import Boss, Projectile, Player, ControllerHandler
# from menu_overlay import level_overlay
import random
import math
from enum import Enum
from headers.classes import Player
from sound_effects.bosses.boss_sound import SoundManager
from boss_four.raven import EnemyRaven  # Import the EnemyRaven class directly

class RavenState(Enum):
    IDLE = "idle"
    ATTACK = "attack"
    EXIT = "exit"

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_frame(sheet, frame, width, height, scale):
    img = sheet.subsurface((frame * width, 0, width, height)).convert_alpha()
    img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
    return img

class BossFourImplementation(Boss):
    def __init__(self, screen, clock, player, game_map=None):
        super().__init__(screen, clock)
        self.x = 850
        self.y = 290
        self.bx = 850
        self.by = 390
        self.player = player
        self.enemy = EnemyRaven(screen,clock, player)
        self.game_map = game_map
        self.controller = ControllerHandler()

        # Get screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.sound_manager = SoundManager()
        self.sound_laugh_400 = False
        self.sound_laugh_200 = False
        self.slam_sound_played = False

        # Modified state variables
        self.boss_state = 'walk'
        self.dir = 'right'
        self.is_walking = False
        self.current_walk_frame = 0
        self.should_attack = False
        self.magic_cooldown = 5000  # 5 seconds between curse attacks
        self.last_magic_time = pygame.time.get_ticks()

        # Add these new variables for position control
        self.min_x = 10
        self.max_x = 900
        self.move_speed = 5
        self.broom_speed = 3  # Reduced from 10 to 5 for slower movement
        self.base_broom_speed = 3  # Add this to track the base speed
        self.witch_dir = 'right'
        self.broom_dir = 'left'  # Or whatever initial direction you prefer

               # Broom dimensions (scaled)
        self.broom_width = 160  # Width after scaling (320 * 0.5)
        self.broom_height = 160  # Height after scaling (320 * 0.5)
        
        # Calculate broom boundaries considering sprite size
        self.broom_min_x = 0
        self.broom_max_x = self.screen_width - self.broom_width

        # self.healthbar()


        self.warning_flash = False
        self.is_damage_flashing = False
        self.flash_interval = 150
        self.flash_start_time = pygame.time.get_ticks()

        

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        curr_dir = os.path.join(project_root, "boss_four")
        sprite_directory = os.path.join(project_root, "animations", "boss_four_ani")

        # Load all sprite sheets and resources
        background_path = os.path.join(curr_dir, "boss_four_bk.png")
        broom_path = os.path.join(sprite_directory, "broom_spinning.png")
        walk_path = os.path.join(sprite_directory, "witch_walk.png")
        throw_path = os.path.join(sprite_directory, "witch_throw.png")
        punch_path = os.path.join(sprite_directory, "witch_punch.png")
        magic_path = os.path.join(sprite_directory, "magic.png")
        snake_projectile_path = os.path.join(sprite_directory, "snake_projectile.png")

        self.background_image = pygame.image.load(background_path).convert()
        self.broom_sheet = pygame.image.load(broom_path).convert_alpha()
        self.walk_sheet = pygame.image.load(walk_path).convert_alpha()
        self.throw_sheet = pygame.image.load(throw_path).convert_alpha()
        self.punch_sheet = pygame.image.load(punch_path).convert_alpha()
        self.magic_sheet = pygame.image.load(magic_path).convert_alpha()
        self.snake_projectile_sheet = pygame.image.load(snake_projectile_path).convert_alpha()

        self.music_path = os.path.join(project_root, "music", "purity_strictly.mp3")
        self.play_music()

        # Load animations
        self.walk_frames = [get_frame(self.walk_sheet, i, 320, 320, 1) for i in range(28)]
        self.throw_frames = [get_frame(self.throw_sheet, i, 320, 320, 1) for i in range(18)]
        self.punch_frames = [get_frame(self.punch_sheet, i, 320, 320, 1) for i in range(34)]
        self.magic_frames = [get_frame(self.magic_sheet, i, 320, 320, 1) for i in range(12)]
        self.projectiles_frames = [get_frame(self.broom_sheet, i, 320, 320, 0.5) for i in range(5)]
        self.snake_projectile_frames = [get_frame(self.snake_projectile_sheet, i, 160, 160, 1) for i in range(1)]

        # Animation state variables
        self.current_frame = 0
        self.current_attack_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.frame_duration = 100
        self.current_attack = None
        self.attack_damage_dealt = False

        # Combat timers
        self.last_attack_time = pygame.time.get_ticks()
        self.last_broom_attack = pygame.time.get_ticks()
        self.broom_duration = 1000
        self.attack_interval = 1000
        self.is_attacking = False

        # Health and state
        self.health = 700
        self.h_init = self.health
        self.color = (255, 255, 255)
        self.warning_flash = False
        self.is_damage_flashing = False
        self.flash_interval = 150

        # Hitboxes and collision
        self.ground = pygame.Rect(0, 650, 1290, 25)
        self.platforms = [self.ground]
        self.hazards = []
        self.broom_hitbox = pygame.Rect(self.bx + 90, self.by + 90, 90, 90)
        self.witch_hitbox = pygame.Rect(self.x + 100, self.y +100, 110, 200)
        self.snake_projectile_hitbox = pygame.Rect(self.x, self.y, 90, 90)

        # Projectiles
        self.projectiles = []  # Store active projectiles
        self.warning_flash_active = False
        self.flash_start_time = pygame.time.get_ticks()
        self.patterns = [
            'circle',    # Circular pattern
            'spiral',    # Spiral pattern
            'cross',     # Cross pattern
            'wave'       # Wave pattern
        ]
        self.current_pattern = 'circle'

                # !Health bar configuration
        self.max_health = self.health
        self.health_bar_width = 300
        self.health_bar_height = 20
        self.health_bar_x = 20
        self.health_bar_y = 50
        self.border_thickness = 4 

        # Smooth health bar animation
        self.visual_health = self.health  # This will be used for smooth animation
        self.health_animation_speed = 1  # Speed of health bar animation (higher = faster)


    def create_projectile_pattern(self):
        pattern = random.choice(self.patterns)
        projectiles = []
        
        # Calculate center position relative to witch position
        center_x = self.x + 105  # Center of witch
        center_y = self.y + 160
        
        if pattern == 'circle':
            num_projectiles = 8
            for i in range(num_projectiles):
                angle = (2 * math.pi * i) / num_projectiles
                speed = 7
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                projectiles.append({
                    'x': center_x,
                    'y': center_y,
                    'dx': dx,
                    'dy': dy,
                    'hitbox': pygame.Rect(center_x, center_y, 40, 40)
                })
                
        elif pattern == 'spiral':
            num_projectiles = 12
            for i in range(num_projectiles):
                angle = (2 * math.pi * i) / num_projectiles
                speed = 5 + (i % 3) * 2
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                projectiles.append({
                    'x': center_x,
                    'y': center_y,
                    'dx': dx,
                    'dy': dy,
                    'hitbox': pygame.Rect(center_x, center_y, 40, 40)
                })
                
        elif pattern == 'cross':
            speeds = [-8, -4, 4, 8]
            for speed in speeds:
                # Horizontal
                projectiles.append({
                    'x': center_x,
                    'y': center_y,
                    'dx': speed,
                    'dy': 0,
                    'hitbox': pygame.Rect(center_x, center_y, 40, 40)
                })
                # Vertical
                projectiles.append({
                    'x': center_x,
                    'y': center_y,
                    'dx': 0,
                    'dy': speed,
                    'hitbox': pygame.Rect(center_x, center_y, 40, 40)
                })
                
        elif pattern == 'wave':
            num_projectiles = 5
            spacing = 50
            base_height = center_y - 60
            for i in range(num_projectiles):
                speed = 6
                dx = speed
                dy = 0
                projectiles.append({
                    'x': center_x,
                    'y': base_height + (i * spacing),
                    'dx': dx,
                    'dy': dy,
                    'wave_offset': i * spacing,
                    'hitbox': pygame.Rect(center_x, base_height + (i * spacing), 40, 40)
                })
        
        return projectiles

    def update_projectiles(self):
        screen_rect = self.screen.get_rect()
        surviving_projectiles = []
        projectile_surface = self.snake_projectile_frames[0]
        flipped_projectile = pygame.transform.flip(projectile_surface, True, False)
        
        for proj in self.projectiles:
            # Update position
            proj['x'] += proj['dx']
            
            if 'wave_offset' in proj:
                proj['y'] += math.sin(proj['x'] / 50 + proj['wave_offset']) * 2
            else:
                proj['y'] += proj['dy']
            
            # Update hitbox with corrected offset
            if proj['dx'] < 0:  # Moving left
                proj['hitbox'].x = proj['x'] + 40
            else:  # Moving right
                proj['hitbox'].x = proj['x']
                
            proj['hitbox'].y = proj['y']
            
            # Check if projectile is within screen bounds
            if (0 <= proj['x'] <= screen_rect.width and 
                0 <= proj['y'] <= screen_rect.height):
                surviving_projectiles.append(proj)
                
                # Use pre-flipped surface based on direction
                surface_to_use = flipped_projectile if proj['dx'] < 0 else projectile_surface
                self.screen.blit(surface_to_use, (proj['x'], proj['y']))
                
            # Check player collision
            if proj['hitbox'].colliderect(self.player.hitbox) and not self.player.invincible:
                self.player.take_damage(15)
                
        self.projectiles = surviving_projectiles
            
    def update_pos(self):
        # Only update position if not attacking and in walking frames
        if not self.is_attacking and 2 < self.current_frame < 27:
            if self.witch_dir == 'right':
                self.x += self.move_speed
                if self.x >= self.max_x:
                    self.x = self.max_x
                    self.witch_dir = 'left'
            elif self.witch_dir == 'left':
                self.x -= self.move_speed
                if self.x <= self.min_x:
                    self.x = self.min_x
                    self.witch_dir = 'right'

        # Update hitbox after position is finalized
        self.witch_hitbox.x = self.x + 100
        self.witch_hitbox.y = self.y + 100


    def broom_pos(self):
        # Apply speed based on direction
        if self.broom_dir == 'right':
            self.bx += self.broom_speed
        else:  # left
            self.bx -= self.broom_speed
        
        # Check boundaries and reverse direction
        if self.bx >= self.screen_width - 160:  # 160 is broom width
            self.bx = self.screen_width - 160
            self.broom_dir = 'left'
        elif self.bx <= 0:
            self.bx = 0
            self.broom_dir = 'right'
        
        # Update hitbox position with adjusted margins
        self.broom_hitbox.x = self.bx + 40
        self.broom_hitbox.y = self.by + 40


    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time >= self.frame_duration:
            self.last_update_time = current_time
            
            if self.current_attack == 'punch':
                # Warning flash for punch
                if 1 <= self.current_attack_frame <= 8:
                    self.warning_flash = True
                    self.color = (253, 165, 15)
                else:
                    self.warning_flash = False
                    if not self.is_damage_flashing:
                        self.color = (255, 255, 255)
                
                # Process punch animation frame updates
                if self.current_attack_frame < len(self.punch_frames) - 1:  # Changed this condition
                    if self.current_attack_frame == 20:  # Check one frame before to prepare
                        if not self.slam_sound_played:
                            print(f"Playing slam sound at frame: {self.current_attack_frame + 1}")
                            # self.sound_manager.play_sound('slam')
                            self.slam_sound_played = True
                    
                    self.current_attack_frame += 1
                    
                    # Check for damage after frame increment
                    if 22 <= self.current_attack_frame <= 28:
                        if not self.attack_damage_dealt and self.witch_hitbox.colliderect(self.player.hitbox):
                            self.player.take_damage(50)
                            self.attack_damage_dealt = True
                else:
                    self.slam_sound_played = False
                    self.end_attack()
                
            elif self.current_attack == 'throw':
                if self.current_attack_frame < len(self.throw_frames):
                    # Warning flash during frames 1-8
                    if 1 <= self.current_attack_frame <= 8:
                        self.warning_flash = True
                        self.color = (253, 165, 15)  # Set warning color directly
                    else:
                        self.warning_flash = False
                        if not self.is_damage_flashing:
                            self.color = (255, 255, 255)
                    
                    if self.current_attack_frame == 9:
                        self.sound_manager.play_sound('magic')
                        self.projectiles.extend(self.create_projectile_pattern())
                    
                    self.current_attack_frame += 1
                    if self.current_attack_frame >= len(self.throw_frames) - 1:
                        self.end_attack()
            else:
                # Handle walking animation
                self.current_frame = (self.current_frame + 1) % 28
                
                # Increased attack chance from 60% to 90%
                if self.current_frame == 27:  # End of walk cycle
                    if random.random() < 0.9:  # 90% chance to attack
                        self.choose_attack()
                    else:
                        self.current_frame = 0  # Reset to first frame if no attack


    def update_warning_flash(self):
        if self.warning_flash and not self.is_damage_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start_time > self.flash_interval:
                self.color = (253, 165, 15) if self.color == (255, 255, 255) else (255, 255, 255)
                self.flash_start_time = current_time

    def play_music(self):
        if os.path.exists(self.music_path) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)

    def idle_animation(self):
        """Handles the idle animation of the boss."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time >= self.frame_duration:
            if not self.is_attacking:
                self.current_frame = (self.current_frame + 1) % len(self.idle_animation_frames)
                self.last_update_time = current_time
                if self.current_frame == 0:
                    self.idle_loops += 1
                if self.idle_loops >= self.max_idle_loops:
                    self.attack()
        if not self.is_attacking:
            self.screen.blit(self.idle_animation_frames[self.current_frame], (self.x, self.y))

    def attack(self):
        """Triggers attack animation."""
        current_time = pygame.time.get_ticks()
        if self.idle_loops >= self.max_idle_loops:
            if current_time - self.last_attack_time >= self.attack_interval:
                if not self.is_attacking:
                    self.is_attacking = True
                    self.attack_finished = False
                    self.current_attack_frame = 0
                    self.idle_loops = 0
                    self.last_attack_time = current_time

    def update_attack_animation(self):
        """Updates and renders the attack animation frames."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time >= self.frame_duration:
            self.current_attack_frame += 1
            self.last_update_time = current_time
            if self.current_attack_frame >= len(self.attack_animation_frames):
                self.is_attacking = False
                self.attack_finished = True
                self.current_attack_frame = 0
                return
        if self.is_attacking:
            self.screen.blit(self.attack_animation_frames[self.current_attack_frame], (self.x, self.y))

    def take_damage(self, damage):
        """Handle taking damage and flashing red to indicate being hit."""
        self.health -= damage
        self.color = (255, 0, 0)  # Set to red to indicate damage
        self.last_hit_time = pygame.time.get_ticks()
        
        # Play hit sound if you have a sound manager
        # self.sound_manager.play_sound('hit')  # Uncomment if you have sound manager
        
        if self.health <= 0:
            print("Boss is defeated!")
    
    def draw_health_bar(self):
        """Draw the boss health bar with smooth animation."""
        # Update visual health for smooth animation
        if self.visual_health > self.health:
            self.visual_health = max(self.health, self.visual_health - 2)  # Increased animation speed
        elif self.visual_health < self.health:
            self.visual_health = min(self.health, self.visual_health + 2)

        # Draw border
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (self.health_bar_x - self.border_thickness, 
                         self.health_bar_y - self.border_thickness,
                         self.health_bar_width + (self.border_thickness * 2), 
                         self.health_bar_height + (self.border_thickness * 2)))
        
        # Draw background
        pygame.draw.rect(self.screen, (169, 169, 169),
                        (self.health_bar_x, self.health_bar_y,
                         self.health_bar_width, self.health_bar_height))
        
        # Calculate health ratio and width
        health_ratio = max(self.visual_health / self.max_health, 0)
        current_health_width = int(self.health_bar_width * health_ratio)
        
        # Draw health bar
        if current_health_width > 0:
            pygame.draw.rect(self.screen, (255, 0, 0),
                           (self.health_bar_x, self.health_bar_y,
                            current_health_width, self.health_bar_height))
            
            # Add highlight for depth
            highlight_height = self.health_bar_height // 3
            pygame.draw.rect(self.screen, (255, 50, 50),
                           (self.health_bar_x, self.health_bar_y,
                            current_health_width, highlight_height))
            



    def update(self):
        if self.health > 0:
            # Phase control based on HP
            if self.health > 600:
                # Phase 1: Only witch and broom
                self.enemy.deactivate()  # Disable ravens
                self.can_curse = False
                self.broom_speed = 3  # Reset to base speed
                
            elif 400 < self.health <= 600:
                # Phase 2: Ravens appear, broom can curse
                self.enemy.activate()  # Enable ravens
                self.can_curse = True
                self.broom_speed = 3  # Keep base speed
                
            elif 200 < self.health <=400:
                if not self.sound_laugh_400:
                    self.sound_manager.play_sound('WL')
                    self.sound_laugh_400 = True
                # Phase 3: Broom speed increases but not too much
                if abs(self.broom_speed) < 6:  # Limit maximum speed
                    self.broom_speed = 4 
            else:
                if not self.sound_laugh_200:
                    self.sound_manager.play_sound('WL')
                    self.sound_laugh_200 = True
                # Phase 3: Broom speed increases but not too much
                if abs(self.broom_speed) < 6:  # Limit maximum speed
                    self.broom_speed = 6
                    
            self.update_animation()
            
            # Reset color after damage flash
            if self.color == (255, 0, 0):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_hit_time > 200:  # 200ms flash duration
                    self.color = (255, 255, 255)
            
            # Draw appropriate animation frame with color tint if damaged
            current_frame = None
            if self.is_attacking:
                if self.current_attack == 'punch':
                    current_frame = self.punch_frames[min(self.current_attack_frame, len(self.punch_frames)-1)]
                elif self.current_attack == 'throw':
                    current_frame = self.throw_frames[min(self.current_attack_frame, len(self.throw_frames)-1)]
            else:
                current_frame = self.walk_frames[self.current_frame]

            # Apply damage flash if needed
            if current_frame:
                frame_copy = current_frame.copy()
                if self.color == (255, 0, 0):
                    frame_copy.fill(self.color, special_flags=pygame.BLEND_MULT)
                self.screen.blit(frame_copy, (self.x, self.y))

            # Update broom animation continuously
            self.broom_pos()
            broom_frame = (pygame.time.get_ticks() // 200) % len(self.projectiles_frames)
            broom_surface = self.projectiles_frames[broom_frame].copy()
                    # Flip the broom sprite based on direction
            if self.broom_dir == 'left':
                broom_surface = pygame.transform.flip(broom_surface, True, False)

            
            # Color the broom based on phase and damage
            if self.color == (255, 0, 0):  # Damage flash takes priority
                broom_surface.fill(self.color, special_flags=pygame.BLEND_MULT)
            elif self.health <= 600:  # Curse phase - always purple unless damage flashing
                broom_surface.fill((128, 0, 128), special_flags=pygame.BLEND_MULT)  # Purple
                
            self.screen.blit(broom_surface, (self.bx, self.by))

            # Add projectile updates
            self.update_projectiles()

            # Draw hitboxes (for debugging)
            # pygame.draw.rect(self.screen, (255, 0, 0), self.witch_hitbox, 2)  # Red for witch hitbox
            # pygame.draw.rect(self.screen, (0, 255, 0), self.broom_hitbox, 2)  # Green for broom hitbox
            
    def choose_attack(self):
        if not self.is_attacking and pygame.time.get_ticks() - self.last_attack_time > self.attack_interval:
            attack_choice = random.choice(['punch', 'throw', None])
            if attack_choice:
                self.start_attack(attack_choice)

    def start_attack(self, attack_type):
        self.is_attacking = True
        self.current_attack = attack_type
        self.current_attack_frame = 0
        self.attack_damage_dealt = False
        self.last_attack_time = pygame.time.get_ticks()

    def end_attack(self):
        self.is_attacking = False
        self.current_attack = None
        self.current_frame = 0
        self.attack_damage_dealt = False
    
    def calculate_fullscreen_dimensions(self, screen_width, screen_height):
        """Calculate the dimensions and position for centered gameplay in fullscreen."""
        game_aspect_ratio = 1280 / 720
        screen_aspect_ratio = screen_width / screen_height
        
        if screen_aspect_ratio > game_aspect_ratio:
            # Screen is wider than the game - use pillarboxing
            game_height = screen_height
            game_width = int(game_height * game_aspect_ratio)
        else:
            # Screen is taller than the game - use letterboxing
            game_width = screen_width
            game_height = int(game_width / game_aspect_ratio)
        
        # Calculate position to center the game surface
        x = (screen_width - game_width) // 2
        y = (screen_height - game_height) // 2
        
        return game_width, game_height, x, y

  
    def window(self, player):
        """Main game loop with dynamic resizing support."""
        running = True
        game_surface = pygame.Surface((1280, 720))
        
        # Boss initial positions
        self.x = 1280 / 2 + 160
        self.y = 720 - 320
        self.bx = self.x + 200
        self.by = self.y + 75
        broom_dir = 'left'

        self.enemy.activate()
        
        while running:
            dt = self.clock.get_time() / 1000.0
            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return "map_menu"
                    elif event.key == pygame.K_x:
                        return "save"
                    elif event.key == pygame.K_z:
                        return "load"

            keys = pygame.key.get_pressed()
                # Update game logic
            player.move(keys, self.platforms, self.hazards, self.controller)
            player.attack(keys, self.controller)
            player.update_invincibility()
            player.update()


            # Handle player animations
            if player.is_cursed:
                if player.is_jumping:
                    player_frame = player.handle_action('jump', player.curse_jump_frames)
                elif player.is_falling:
                    player_frame = player.handle_action('fall', player.curse_fall_frames)
                elif keys[pygame.K_a] or keys[pygame.K_d]:
                    player_frame = player.handle_action('walk', player.curse_walk_frames)
                else:
                    player_frame = player.get_current_frame(self.controller)
            else:
                if player.is_jumping:
                    player_frame = player.handle_action('jump', player.jump_animation_frames)
                elif player.is_falling:
                    player_frame = player.handle_action('fall', player.fall_animation_frames)
                elif player.is_dashing:
                    player_frame = player.handle_action('dash', player.dash_animation_frames, is_dash=True)
                elif player.current_action == 'attack':
                    player_frame = player.handle_action('attack', player.attack_animation_frames)
                elif keys[pygame.K_a] or keys[pygame.K_d]:
                    player_frame = player.handle_action('walk', player.walk_animation_frames)
                else:
                    player_frame = player.get_current_frame(self.controller)

            # Clear and draw background to game surface
            game_surface.blit(self.background_image, (0, 0))

            # Update and draw ravens to game surface
            self.enemy.screen = game_surface  # Temporarily set game_surface as screen
            self.enemy.update(dt)
            self.enemy.draw()
            self.enemy.screen = self.screen  # Reset screen back to main screen

            # Check raven collisions
            for raven in self.enemy.ravens:
                if player.hitbox.colliderect(raven.hitbox):
                    if not player.invincible:
                        player.take_damage(15)
                        print("Raven hit player!")

            # Update boss position and animation
            self.update_pos()
            
            # Temporarily set game_surface as screen for boss updates
            original_screen = self.screen
            self.screen = game_surface
            self.update()
            self.screen = original_screen

            # Update broom position
            self.broom_pos()

            # Draw player
            if player_frame:
                player_surface = player_frame.copy()
                if player.color == (255, 0, 0):
                    player_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                game_surface.blit(player_surface, (player.x, player.y))

            # Check collisions and handle game states
            if player.hitbox.colliderect(self.witch_hitbox):
                if not player.damage_dealt:
                    self.take_damage(35)
                    print("HP IS AT: ", self.health)
                    player.damage_dealt = True

            if player.hitbox.colliderect(self.broom_hitbox) and pygame.time.get_ticks() - self.last_broom_attack >= self.broom_duration:
                if not player.invincible:
                    player.take_damage(10)
                    if self.health <= 600:
                        self.sound_manager.play_sound('magic')
                        player.curse()
                    self.last_broom_attack = pygame.time.get_ticks()

            if player.hitbox.colliderect(self.witch_hitbox) and self.is_attacking and pygame.time.get_ticks() - self.last_attack_time >= self.attack_interval:
                if not player.invincible:
                    self.last_attack_time = pygame.time.get_ticks()
                    player.take_damage(50)

            # Check game over conditions
            if player.healthbar <= 0:
                pygame.mixer.music.stop()
                self.enemy.deactivate()
                return "game_over"

            if self.health <= 0 and player.healthbar != 0:
                pygame.mixer.music.stop()
                self.enemy.deactivate()
                if self.game_map:
                    self.game_map.mark_level_completed('boss_four')
                    self.game_map.unlock_next_level('boss_four')
                return "map_menu"

            self.update_warning_flash()

            # Draw health bars to game surface
                            # Draw UI and health bars
            font = pygame.font.SysFont(None, 40)
            health_text = font.render(f"Player Health: {player.healthbar}", True, (0, 0, 0))
            boss_health_text = font.render(f"Boss Health: {self.health}", True, (0, 0, 0))
            game_surface.blit(health_text, (960, 20))
            game_surface.blit(boss_health_text, (20, 20))

            original_screen = self.screen
            self.screen = game_surface
            self.draw_health_bar()
            self.screen = original_screen

            player.draw_health_bar(game_surface)
            
            # Scale and display the game surface
            if is_fullscreen:
                game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                scaled_surface = pygame.transform.scale(game_surface, (game_width, game_height))
                self.screen.fill((0, 0, 0))
                self.screen.blit(scaled_surface, (x, y))
            else:
                self.screen.blit(game_surface, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        return "map_menu"