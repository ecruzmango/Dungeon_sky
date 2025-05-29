import os
import pygame
import random
import math
import sys
from headers.classes import Boss, Projectile, Player, ControllerHandler
from sound_effects.bosses.boss_sound import SoundManager
# from menu_overlay import level_overlay
from boss_one import enemy
from boss_three.enemy_fish import EnemyFish  # Changed to class name
from boss_three.enemy_duck import EnemyDuck  # Changed to class name

SCREEN_WIDTH = 1280

class BossThree(Boss):
    def __init__(self, screen, clock, player, game_map=None):
        super().__init__(screen, clock)

        self.enemy = enemy.Enemy(screen,clock, player)
        #create two fish enemies at different pos
        self.fish_left = EnemyFish(screen,clock, player, 250)
        self.fish_right = EnemyFish(screen, clock, player, 715)
        # create duck enemy
        self.duck_enemy = EnemyDuck(screen,clock, player)
        self.sound_manager = SoundManager()
        # self.healthbar()
        self.game_map = game_map

        self.controller = ControllerHandler()

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ! IMPORT

        # Set the background color or image (temp background)
        self.background = os.path.join(project_root, "boss_three", "background_frog.png")  # Sky blue as temporary background
        self.background_image = pygame.image.load(self.background).convert()
        
        # Load idle animation frames
        sprite_sheet_path = os.path.join(project_root, "animations", "boss_three_ani", "frog_idle.png")
        self.idle_animation_frames = self.load_frames(sprite_sheet_path, 12, 320, 320)

        # Load jump animation frames
        sprite_sheet_path_jump = os.path.join(project_root, "animations", "boss_three_ani", "frog_jump.png")
        self.jump_animation_frames = self.load_frames(sprite_sheet_path_jump, 26, 320, 320)

        #load call animtation frames
        sprite_sheet_path_call = os.path.join(project_root, "animations","boss_three_ani","frog_tongue.png")
        self.call_animation_frames = self.load_frames(sprite_sheet_path_call,19, 320,320)

        # Jump animation variables
        self.jump_start_y = 320  # Initial Y position
        self.jump_height = -200  # How high the frog jumps
        self.jump_progress = 0  # Progress through jump animation (0 to 1)
        self.is_attacking = False

        # !Health and position init
        self.max_health = 800
    
        self.health = self.max_health
        self.h_init = self.health
        self.boss_x = 50      # TODO: the desired cords for jumping are 50, 495, 940
        self.h_init = self.health
        self.boss_y = 320
        self.color = (255, 255, 255)
        self.current_frame = 0
        self.last_hit_time = 0


        # !Health bar configuration
        self.health_bar_width = 300
        self.health_bar_height = 20
        self.health_bar_x = 20
        self.health_bar_y = 50
        self.border_thickness = 4 

        # !Animation variables
        self.idle_played_count = 0
        self.is_jumping = False
        self.is_damage_flashing = False
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_frame_float = 0.0
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_duration = 100  # milliseconds per frame
        self.warning_flash = False
        self.flash_start_time = 0
        self.jump_height = -600
        self.flash_interval = 150  # milliseconds between flashes
        self.landing_positions = [50, 495, 940]
        self.target_x = self.boss_x
        self.jump_sound_played = False

        # !NEW MOVEMENT
        self.start_x = self.boss_x
        self.start_y = self.boss_y
        self.movement_time = 0
        self.total_movement_time = 1.0  # seconds

        # Movement damping
        self.damping = .5
        self.spring_strength = 1

        # Smooth interpolation helpers
        self.prev_x = self.boss_x
        self.prev_y = self.boss_y
        self.velocity_x = 0
        self.velocity_y = 0

        # Smooth health bar animation
        self.visual_health = self.health  # This will be used for smooth animation
        self.health_animation_speed = 1  # Speed of health bar animation (higher = faster)



        self.hitbox = pygame.Rect(self.boss_x+10, self.boss_y+75, 290, 220)  #! Set boss hitbox (adjust as needed)
        
        # platforms
        self.platforms = [
            pygame.Rect(50, 620, 300, 25), 
            pygame.Rect(510, 620, 300, 25), 
            pygame.Rect(950, 620, 300, 25)
        ]
        self.water = pygame.Rect(0, 645, 1290, 25)  # Water hazard
        self.hazards = [self.water]
        
        # Music path
        self.music_path = os.path.join(project_root, "music", "Sound of Night wind.mp3")
        self.play_music()


    def play_music(self):
        if os.path.exists(self.music_path)  and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(.5)
            pygame.mixer.music.play(-1)
        else:
            print(f"Error: Music file not found at {self.music_path}")

    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        """Load frames from a sprite sheet."""
        if not os.path.exists(sprite_sheet_path):
            print(f"Error: Sprite sheet not found at {sprite_sheet_path}")
            return []
        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path)
        except pygame.error as e:
            print(f"Error loading sprite sheet: {e}")
            return []

        frames = [
            sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            for i in range(num_frames)
        ]
        return frames

    def idle_animation(self):
        """Handles the idle animation of the boss."""
        current_time = pygame.time.get_ticks()
        frame_duration = 100  # Duration for each frame in milliseconds

        if current_time - self.last_update_time > frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.idle_animation_frames)
            self.last_update_time = current_time



    def draw_health_bar(self, surface):
        """Draw the boss health bar with thick border and smooth animation."""
        # Update visual health for smooth animation
        if self.visual_health > self.health:
            self.visual_health = max(self.health, self.visual_health - self.health_animation_speed)
        elif self.visual_health < self.health:
            self.visual_health = min(self.health, self.visual_health + self.health_animation_speed)

        # Draw the border (black rectangle) - now thicker
        pygame.draw.rect(surface, (0, 0, 0), 
                        (self.health_bar_x - self.border_thickness, 
                         self.health_bar_y - self.border_thickness,
                         self.health_bar_width + (self.border_thickness * 2), 
                         self.health_bar_height + (self.border_thickness * 2)))
        
        # Draw the background (gray rectangle)
        pygame.draw.rect(surface, (169, 169, 169),
                        (self.health_bar_x, self.health_bar_y,
                         self.health_bar_width, self.health_bar_height))
        
        # Calculate health ratios for current and visual health
        health_ratio = max(self.visual_health / self.max_health, 0)
        current_health_width = int(self.health_bar_width * health_ratio)
        
        # Draw the current health (red rectangle)
        if current_health_width > 0:
            # Draw the main health bar
            pygame.draw.rect(surface, (255, 0, 0),
                           (self.health_bar_x, self.health_bar_y,
                            current_health_width, self.health_bar_height))
            
            # Draw a lighter red highlight at the top of the health bar for depth
            highlight_height = self.health_bar_height // 3
            pygame.draw.rect(surface, (255, 50, 50),
                           (self.health_bar_x, self.health_bar_y,
                            current_health_width, highlight_height))


    def take_damage(self, damage):
        """Handle taking damage and flashing red to indicate being hit."""
        self.health = max(0, self.health - damage)  # Prevent negative health
        self.color = (255, 0, 0)  # Set to red to indicate damage
        self.last_hit_time = pygame.time.get_ticks()
        self.is_damage_flashing = True  # Add this flag to track damage flash state
        
    def update_damage_effects(self):
        """Update damage-related effects like color flashing."""
        if self.is_damage_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit_time > 200:  # Flash duration in milliseconds
                self.color = (255, 255, 255)  # Reset to normal color
                self.is_damage_flashing = False  # Reset damage flash state

                
    # starts fast and slows down at the end
    def ease_out_cubic(self, t):
            return 1 - math.pow(1 - t, 3)

    # starts slow, speeds up in the middle, and slows at the end
    def ease_in_out_quad(self, t):
        # 2 * t * t calculates acc (mult by 2 when it reaches .5, t= .5)
        # -2 * t + 2 transforms t to count down 
        return 2 * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 2) / 2

    # creates as smooth S-curve
    def smooth_step(self, t):
        return t * t * (2 - 1 * t)
    

    def execute_jump(self, delta_time):
        """Handle the jump execution physics and movement"""
        # Update movement time
        self.movement_time += delta_time / self.total_movement_time
        # Calculate progress with easing
        progress = self.ease_in_out_quad(min(1.0, self.movement_time))
        
        # Calculate target position with spring physics
        target_x = self.lerp(self.start_x, self.target_x, progress)
        
        # Calculate jump arc with enhanced smoothing
        self.jump_progress = self.smooth_step(progress)

        # math.sin creates the up and down motion 
        jump_height = self.jump_height * math.sin(progress * math.pi)

        # Calculate the peak in the middle of the jump 
        target_y = self.jump_start_y + jump_height * (1 - abs(2 * progress - 1))
        
        # Apply spring physics
        dx = target_x - self.boss_x
        dy = target_y - self.boss_y
        
        self.velocity_x += dx * self.spring_strength
        self.velocity_y += dy * self.spring_strength

        # Apply damping
        self.velocity_x *= self.damping
        self.velocity_y *= self.damping

        # Update position
        self.boss_x += self.velocity_x
        self.boss_y += self.velocity_y
        
        # Update hitbox
        self.hitbox.x = self.boss_x + 10
        self.hitbox.y = self.boss_y + 75

    def end_jump(self):
        """Reset all jump-related states"""
        self.current_animation = 'idle'
        self.animation_frame_float = 0
        self.animation_frame = 0
        self.is_attacking = False
        self.is_jumping = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.boss_x = self.target_x
        self.boss_y = self.jump_start_y
        self.warning_flash = False
        if not self.is_damage_flashing:
            self.color = (255, 255, 255)

    def update_animation_state(self):
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_frame_time) / 1000.0
            self.last_frame_time = current_time

            # Update floating-point frame counter for smoother transitions
            if self.current_animation == 'idle':
                self.animation_frame_float += delta_time * (1000 / self.frame_duration)
                self.animation_frame = int(self.animation_frame_float)

                # Only reset color if not damage flashing
                if not self.is_damage_flashing:
                    self.color = (255, 255, 255)
                    self.warning_flash = False

                # Handle idle animation cycling
                if self.animation_frame >= len(self.idle_animation_frames):
                    self.idle_played_count += 1
                    self.animation_frame_float -= len(self.idle_animation_frames)
                    self.animation_frame = int(self.animation_frame_float)

                # After 1 idle cycle, perform an action based on health
                if self.idle_played_count >= 1:
                    self.idle_played_count = 0
                    
                    # If HP > 500, can either jump or call duck
                    if self.health > 500:
                        if random.choice(['jump', 'call']) == 'jump':
                            self.initiate_jump()
                        else:
                            self.current_animation = 'call'
                            self.animation_frame_float = 0
                            self.animation_frame = 0
                    else:
                        # Below 500 HP, always jump after one idle animation
                        self.initiate_jump()

            elif self.current_animation == 'jump':
                self.handle_jump_animation(delta_time)

            elif self.current_animation == 'call':
                self.animation_frame_float += delta_time * (1000 / self.frame_duration)
                self.animation_frame = min(int(self.animation_frame_float), len(self.call_animation_frames) - 1)

                # Return to idle after call animation completes
                if self.animation_frame >= len(self.call_animation_frames) - 1:
                    self.current_animation = 'idle'
                    self.animation_frame_float = 0
                    self.animation_frame = 0

                
    def initiate_jump(self):
        self.current_animation = 'jump'
        self.animation_frame_float = 0
        self.animation_frame = 0
        self.target_x = random.choice([pos for pos in self.landing_positions if abs(pos - self.boss_x) > 100])
        self.is_jumping = True
        self.movement_time = 0
        self.start_x = self.boss_x
        self.start_y = self.boss_y
        self.jump_sound_played = False  # Reset the flag when starting a new jump



    def handle_jump_animation(self, delta_time):
        self.animation_frame_float += delta_time * (1000 / self.frame_duration)
        self.animation_frame = min(int(self.animation_frame_float), len(self.jump_animation_frames) - 1)
        
        # Warning flash phase
        if 5 <= self.animation_frame <= 12 and not self.is_damage_flashing:
            self.warning_flash = True
        else:
            self.warning_flash = False
            if not self.is_damage_flashing:
                self.color = (255, 255, 255)
            
            # Jump execution phase
            if self.animation_frame >= 14:
            # Only play the sound once when we first reach frame 14
                if not self.jump_sound_played:
                    self.sound_manager.play_sound('jump')
                    self.jump_sound_played = True
                self.execute_jump(delta_time)
            
            # Attack phase
            if self.animation_frame == 20:
                self.is_attacking = True
            
            # End jump animation
            if self.animation_frame >= 25:
                self.end_jump()
        # starts the movement between two points 0(start point), .5(halfway), 1(end point)
    def lerp(self, start, end, progress):
        return start + (end - start) * progress


    def update_warning_flash(self):
        if self.warning_flash and 5 <= self.animation_frame <= 12 and self.current_animation == 'jump' and not self.is_damage_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start_time > self.flash_interval:
                self.color = (253, 165, 15) if self.color == (255, 255, 255) else (255, 255, 255)
                self.flash_start_time = current_time

   # Add this new method from boss_one
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
        """Main game loop with fullscreen support."""
        running = True
        last_duck_spawn = pygame.time.get_ticks()
        game_surface = pygame.Surface((1280, 720))  # Create a fixed-size game surface
        duck_spawn_interval = 5000

        while running:
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

            # Get screen dimensions for fullscreen check
            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720

            # Clear game surface and draw background
            game_surface.blit(self.background_image, (0, 0))

            # Handle game state updates
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            # Update player
            player.move(keys, self.platforms, self.hazards, self.controller)
            player.attack(keys, self.controller)
            player.update_invincibility()

            # Update animations and states
            self.update_animation_state()
            self.update_warning_flash()
            self.update_damage_effects()

            # Draw boss with current animation frame
            if self.current_animation == 'jump':
                current_frames = self.jump_animation_frames
            elif self.current_animation == 'call':
                current_frames = self.call_animation_frames
            else:
                current_frames = self.idle_animation_frames

            if len(current_frames) > 0:
                current_frame = current_frames[self.animation_frame]
                boss_surface = current_frame.copy()
                if self.color != (255, 255, 255):
                    boss_surface.fill(self.color, special_flags=pygame.BLEND_MULT)
                game_surface.blit(boss_surface, (self.boss_x, self.boss_y))

            # Update and draw enemies
            self.enemy.update(self.clock.get_time())
            self.enemy.draw(game_surface)  # Update to draw on game_surface

            # Handle fish enemies
            if self.health < 600:
                self.fish_left.active = True
                self.fish_right.active = True
                self.fish_left.update()
                self.fish_right.update()
                self.fish_left.draw(game_surface)  # Update to draw on game_surface
                self.fish_right.draw(game_surface)  # Update to draw on game_surface

                if player.hitbox.colliderect(self.fish_left.hitbox) or \
                   player.hitbox.colliderect(self.fish_right.hitbox):
                    if not player.invincible:
                        player.take_damage(30)

            # Handle duck enemy
            if self.current_animation == 'call':
                if self.animation_frame == 13 and not self.duck_enemy.active:
                    self.sound_manager.play_sound('frog')
                    self.duck_enemy.setup_new_scenario()
                    self.sound_manager.play_sound('duck')
                    self.duck_enemy.activate()
            

            # Duck enemy drawing and collisions
            if self.duck_enemy.active:
                self.duck_enemy.update(self.clock.get_time())
                self.duck_enemy.draw(game_surface)  # Pass game_surface instead of self.screen
                
                # Check duck collisions with player's actual hitbox
                for duck in self.duck_enemy.ducks:
                    if player.hitbox.colliderect(duck['hitbox']):
                        if not player.invincible:
                            player.take_damage(30)

            # Fish enemies drawing and collisions
            if self.health < 600:
                self.fish_left.active = True
                self.fish_right.active = True
                self.fish_left.update()
                self.fish_right.update()
                self.fish_left.draw(game_surface)  # Pass game_surface
                self.fish_right.draw(game_surface)  # Pass game_surface
                # Check fish collisions with player
                if player.hitbox.colliderect(self.fish_left.hitbox) or \
                player.hitbox.colliderect(self.fish_right.hitbox):
                    if not player.invincible:
                        player.take_damage(30)
            
                
            # When health is below 500, spawn ducks every 5 seconds if not already active
            if self.health < 500 and not self.duck_enemy.active:
                if current_time - last_duck_spawn >= duck_spawn_interval:
                    self.sound_manager.play_sound('duck')
                    self.duck_enemy.setup_new_scenario()
                    self.duck_enemy.activate()
                    last_duck_spawn = current_time


            # Handle boss attack collision with player
            if self.is_attacking and self.hitbox.colliderect(player.hitbox):
                if not player.invincible:
                    player.take_damage(10)
            
            for projectile in self.enemy.projectiles[:]:
                    if player.hitbox.colliderect(projectile['hitbox']) and not player.invincible:
                        player.take_damage(50)
                        self.enemy.projectiles.remove(projectile)
                        break

            # Update and draw player
            if player.current_action == 'attack' and player.hitbox.colliderect(self.hitbox):
                if not player.damage_dealt:
                    self.take_damage(30)
                    player.damage_dealt = True

            # Draw player animation
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

            if player_frame:
                player_surface = player_frame.copy()
                if player.color == (255, 0, 0):
                    player_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                game_surface.blit(player_surface, (player.x, player.y))

            # Draw UI elements on game surface
            font = pygame.font.SysFont(None, 40)
            health_text = font.render(f"Player Health: {player.healthbar}", True, (0, 0, 0))
            game_surface.blit(health_text, (960, 20))
            boss_health_text = font.render(f"Boss Health: {self.health}", True, (0, 0, 0))
            game_surface.blit(boss_health_text, (20, 20))

            # Draw health bars on game surface
            self.draw_health_bar(game_surface)  # Update method to accept game_surface
            player.draw_health_bar(game_surface)  # Update method to accept game_surface

            # Handle fullscreen scaling
            if is_fullscreen:
                game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                scaled_surface = pygame.transform.scale(game_surface, (game_width, game_height))
                self.screen.fill((0, 0, 0))
                self.screen.blit(scaled_surface, (x, y))
            else:
                self.screen.blit(game_surface, (0, 0))

            # Check game over conditions
            if player.healthbar <= 0:
                pygame.mixer.music.stop()
                return "game_over"

            if self.health <= 0 and player.healthbar != 0:
                pygame.mixer.music.stop()
                if self.game_map:
                    self.game_map.mark_level_completed('boss_three')
                    self.game_map.unlock_next_level('boss_three')
                return "map_menu"

            pygame.display.flip()
            self.clock.tick(60)