import pygame
import sys
import os
from . import enemy
from headers.classes import Boss, Projectile, Player, ControllerHandler

# from menu_overlay import level_overlay
# from classes import Boss
#! NEWW
from sound_effects.bosses.boss_sound import SoundManager

# collison floor, if touched, take damage
class BossOneImplementation(Boss):
    def __init__(self, screen, clock, player, game_map=None):
        super().__init__(screen, clock)

        self.enemy = enemy.Enemy(screen,clock, player)
        self.sound_manager = SoundManager()
        self.game_map = game_map
        self.controller = ControllerHandler()

        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Set the background color or image (temp background)
        self.background = os.path.join(project_root, "boss_one", "background_tree.png")  # Sky blue as temporary background
        self.background_image = pygame.image.load(self.background).convert()
        # self.healthbar()

        # Load idle animation frames
        sprite_sheet_path = os.path.join(project_root, "animations", "boss_one_ani", "tree_id.png")
        self.idle_animation_frames = self.load_frames(sprite_sheet_path, 12, 480, 480)

        # Load attack animation frames
        attack_sprite_sheet_path = os.path.join(project_root, "animations", "boss_one_ani", "tree_attack.png")
        self.attack_animation_frames = self.load_frames(attack_sprite_sheet_path, 16, 480, 480)

        # Load projectile image
        self.projectile_image_path = os.path.join(project_root, "animations", "boss_one_ani", "projectile.png")
        self.projectiles = []  # List to hold projectiles

        # TODO: load pahse 2!
        sprite_sheet_scence = os.path.join(project_root, "animations", "boss_one_ani", "tree_scene.png")
        self.scene_frames = self.load_frames(sprite_sheet_scence, 25, 480, 600) #! MIGHT CHANGE

        sprite_scene_bush = os.path.join(project_root,"animations", "boss_one_ani", "bush_walk.png")
        self.bush_frames = self.load_frames(sprite_scene_bush, 8, 480, 480) #! MIGHT CHANGE

        sprite_sheet_TreeIdleCry = os.path.join(project_root, "animations", "boss_one_ani", "tree_cry.png")
        self.TreeIdleCry = self.load_frames(sprite_sheet_TreeIdleCry, 5, 480, 480)

        sprite_sheet_CryTree = os.path.join(project_root, "animations", "boss_one_ani", "tree_cry_shoot.png")
        self.tree_cry_attack = self.load_frames(sprite_sheet_CryTree,7, 480, 480 )

        # ! Load in title
        # Add new attributes for title sequence
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.title_video_path = os.path.join(project_root, "animations", "title_ani", "title.mpeg")
        #self.title_sound_path = os.path.join(project_root, "music", "title_sound.wav")  # Add your sound file
        self.title_played = False
        self.alpha = 0  # For fade effect
        
        # ! PHASE TWO ATTR
        # Add phase two specific attributes
        self.phase_two = False
        self.bush_x = 100  # Starting X position for bush
        self.bush_direction = 1  # 1 for right, -1 for left
        self.bush_speed = 3
        self.bush_scale = .9
        self.bush_frames = [pygame.transform.scale(
            frame, 
            (int(480 * self.bush_scale), int(480 * self.bush_scale))
        ) for frame in self.bush_frames]
        # Adjust bush hitbox to match scaled size
        bush_width = int(100 * self.bush_scale)
        bush_height = int(80 * self.bush_scale)
        self.bush_y = 270
        self.bush_hitbox = pygame.Rect(900, 500, 195, 120)

        #self.bush_hitbox = pygame.Rect(self.bush_x, 230, 100, 80)  # Adjust size as needed
        
        # Bush walk animation
        self.current_bush_frame = 0
        self.last_bush_update = 0
        self.bush_frame_duration = 100
        
        # Phase two attack patterns
        self.cry_idle_loops = 0
        self.max_cry_idle_loops = 2
        self.current_cry_frame = 0
        self.current_cry_attack_frame = 0
        self.is_cry_attacking = False

        # Music path
        self.music_path = os.path.join(project_root, "music", "Scraper Sky High.mp3")
        self.play_music()

        # Timers
        self.last_attack_time = pygame.time.get_ticks()
        #self.attack_interval = 4000  # 4 seconds between attacks
        self.is_attacking = False
        self.attack_finished = False
   
        # Boss health and states
        self.health = 300  # Set boss health
        self.h_init = self.health
        self.last_scene_update_time = 0
        self.color = (255, 255, 255)  # Default color (white)
        self.is_cutscene_playing = False
        self.cutscene_played = False  # Ensure cutscene only plays once
        self.current_scene_frame = 0
        self.last_scene_update_time = 0
        self.scene_frame_duration = 100  # Duration for each frame of the cutscene

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

        self.hitbox = pygame.Rect(120, 250, 170, 375)  # Set boss hitbox (adjust as needed)

        # Frame durations and animations
        # Track animation cycles
        self.idle_loops = 0
        self.max_idle_loops = 2  # Number of idle cycles before attacking
        self.current_frame = 0
        self.current_attack_frame = 0
        self.is_attacking = False
        self.attack_finished = False
        self.last_update_time = pygame.time.get_ticks()
        self.frame_duration = 100  # Adjusted for debugging

        
        # platforms
        self.ground = pygame.Rect(0, 650, 1290, 25) # ! (x, y, width, height)
        self.platforms = [self.ground]
        self.hazards = []
        self.wall_barrier = 150 #x-cord limit

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

    def play_music(self):
        if os.path.exists(self.music_path)  and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(.5)
            pygame.mixer.music.play(-1)
        else:
            print(f"Error: Music file not found at {self.music_path}")

    def idle_animation(self, surface):
        """Handles the idle animation of the boss."""
        current_time = pygame.time.get_ticks()

        # Update frame based on frame duration
        if current_time - self.last_update_time >= self.frame_duration:
            if not self.is_attacking:  # Only update frames when not attacking
                self.current_frame = (self.current_frame + 1) % len(self.idle_animation_frames)
                self.last_update_time = current_time

                if self.current_frame == 0:  # Completed one loop of idle
                    self.idle_loops += 1
                    if self.idle_loops == 2:
                        self.attack()

        # Ensure idle is rendered if attack is not active
        if not self.is_attacking:
            surface.blit(self.idle_animation_frames[self.current_frame], (self.x, self.y))

    def draw_health_bar(self, surface):
        """Modified draw_health_bar to accept a surface parameter."""
        if self.visual_health > self.health:
            self.visual_health = max(self.health, self.visual_health - 2)
        elif self.visual_health < self.health:
            self.visual_health = min(self.health, self.visual_health + 2)

        pygame.draw.rect(surface, (0, 0, 0), 
                        (self.health_bar_x - self.border_thickness, 
                        self.health_bar_y - self.border_thickness,
                        self.health_bar_width + (self.border_thickness * 2), 
                        self.health_bar_height + (self.border_thickness * 2)))
        
        pygame.draw.rect(surface, (169, 169, 169),
                        (self.health_bar_x, self.health_bar_y,
                        self.health_bar_width, self.health_bar_height))
        
        health_ratio = max(self.visual_health / self.max_health, 0)
        current_health_width = int(self.health_bar_width * health_ratio)
        
        if current_health_width > 0:
            pygame.draw.rect(surface, (255, 0, 0),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, self.health_bar_height))
            
            highlight_height = self.health_bar_height // 3
            pygame.draw.rect(surface, (255, 50, 50),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, highlight_height))


    def attack(self):
        """Triggers attack animation and launches projectiles."""
        current_time = pygame.time.get_ticks()

        # Check if idle animation has looped twice before attacking
        if self.idle_loops >= self.max_idle_loops:
            # Check if enough time has passed since last attack
            if current_time - self.last_attack_time >= self.attack_interval:
                if not self.is_attacking:  # Prevent multiple projectile launches
                    self.is_attacking = True
                    self.attack_finished = False
                    self.current_attack_frame = 0  # Reset attack animation frame
                    self.last_attack_time = current_time
                    self.idle_loops = 0  # Reset idle loop counter
                    #print("[DEBUG] Starting attack animation after idle loops")
                    
    def update_attack_animation(self, surface):
        """Updates and renders the attack animation frames."""
        current_time = pygame.time.get_ticks()

        # Update animation frame based on frame duration
        if current_time - self.last_update_time >= self.frame_duration:
            self.current_attack_frame += 1
            self.last_update_time = current_time

            # If the current attack frame, create the projectile
            if self.current_attack_frame == 10 and not self.projectiles:  # Fire only one projectile
                projectile = Projectile(
                    x=self.x+75,  # Start from boss position
                    y=self.y+315,
                    speed=15,  # Increased speed from 8 to 15
                    image_path=self.projectile_image_path
                )
                self.projectiles.append(projectile)
                print("[DEBUG] Projectile fired at attack frame ", self.current_attack_frame)

            # If all attack frames are finished, return to idle
            if self.current_attack_frame >= len(self.attack_animation_frames):
                self.is_attacking = False
                self.attack_finished = True
                self.current_attack_frame = 0
                return

        # Draw the current attack frame if still attacking
        if self.is_attacking:
            surface.blit(self.attack_animation_frames[self.current_attack_frame], (self.x, self.y))


    def update_projectiles(self, surface):
        """Updates projectiles' positions and renders them."""
        for projectile in self.projectiles[:]:
            if projectile.is_off_screen(1280):  # Use fixed game width instead of screen width
                self.projectiles.remove(projectile)
            else:
                projectile.move()
                projectile.draw(surface)

    def take_damage(self, damage):
        """Handle taking damage and flashing red to indicate being hit."""
        self.health -= damage
        self.color = (255, 0, 0)  # Set to red to indicate damage
        self.last_hit_time = pygame.time.get_ticks()

        if self.health <= 0:
            print("Boss is defeated!")

    #! PHASE TWOOO ////////////////////////

    def handle_phase_transition(self):
        """Handle transition to phase two when health is 50% or lower"""
        if self.health <= 150 and not self.cutscene_played and not self.is_cutscene_playing:
            print(f"[DEBUG] Health: {self.health}, Triggering phase transition")
            print(f"[DEBUG] Starting cutscene with {len(self.scene_frames)} frames")
            self.is_cutscene_playing = True
            self.phase_two = False  # Don't enable phase two until cutscene is done
            self.current_scene_frame = 0  # Reset frame counter
            self.last_scene_update_time = pygame.time.get_ticks()  # Reset timer
            print(f"[DEBUG] Cutscene playing: {self.is_cutscene_playing}")

    def update_bush_movement(self):
        """Update bush position and animation"""
        if not self.phase_two:
            return
            
        # Update bush position
        self.bush_x += self.bush_speed * self.bush_direction
        
        # Proper screen boundary checks
        max_x = 1280 - (480 * self.bush_scale)  # Screen width minus bush width
        if self.bush_x <= 150:  # Use wall_barrier instead of 0
            self.bush_x = 150
            self.bush_direction = 1
        elif self.bush_x >= max_x:
            self.bush_x = max_x
            self.bush_direction = -1
            
        # Update bush hitbox position to follow the bush
        self.bush_hitbox.x = self.bush_x + 100
        
        # Update bush animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_bush_update >= self.bush_frame_duration:
            self.current_bush_frame = (self.current_bush_frame + 1) % len(self.bush_frames)
            self.last_bush_update = current_time

        # TODO: Draw bush hitbox for debugging
        # pygame.draw.rect(self.screen, (255, 0, 0), self.bush_hitbox, 2)


    def phase_two_idle_animation(self):
        """Handle the crying idle animation in phase two"""
        if not self.phase_two or self.is_cry_attacking:
            return
            
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_update_time >= self.frame_duration:
            self.current_cry_frame = (self.current_cry_frame + 1) % len(self.TreeIdleCry)
            self.last_update_time = current_time
            
            if self.current_cry_frame == 0:
                self.cry_idle_loops += 1
                if self.cry_idle_loops >= self.max_cry_idle_loops:
                    self.phase_two_attack()
                    self.cry_idle_loops = 0
                    
        self.screen.blit(self.TreeIdleCry[self.current_cry_frame], (self.x, self.y))
        
    def phase_two_attack(self):
        """Handle the crying attack animation and projectiles in phase two"""
        if not self.phase_two:
            return
            
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_attack_time >= self.attack_interval:
            if not self.is_cry_attacking:
                self.is_cry_attacking = True
                self.current_cry_attack_frame = 0
                self.last_attack_time = current_time
                
    def update_phase_two_attack(self):
        """Update the crying attack animation and projectiles"""
        if not self.is_cry_attacking or not self.phase_two:
            return
                
        current_time = pygame.time.get_ticks()
            
        if current_time - self.last_update_time >= self.frame_duration:
            self.current_cry_attack_frame += 1
            self.last_update_time = current_time
                
            # Fire projectile at frame 5
            if self.current_cry_attack_frame == 5 and not self.projectiles:
                projectile = Projectile(
                    x=self.x+140,
                    y=self.y+315,
                    speed=20,  # Increased speed for phase 2
                    image_path=self.projectile_image_path
                )
                self.projectiles.append(projectile)
                    
            if self.current_cry_attack_frame >= len(self.tree_cry_attack):
                self.is_cry_attacking = False
                self.current_cry_attack_frame = 0
                return
                    
        self.screen.blit(self.tree_cry_attack[self.current_cry_attack_frame], (self.x, self.y))

    def check_bush_collision(self, player):
        """Check for collision between player and bush"""
        if self.phase_two:
            player_rect = pygame.Rect(player.x + 40, player.y + 20, 75, 130)  # Match player's actual hitbox
            if self.bush_hitbox.colliderect(player_rect):
                if not player.invincible:
                    player.take_damage(10)  # Adjust damage as needed
                    player.invincible = True
                    player.invincible_start_time = pygame.time.get_ticks()



    # Modify the play_cutscene method to support fullscreen
    def play_cutscene(self, player):
        """Play the cutscene when boss reaches 50% HP."""
        if not self.scene_frames:
            print("[ERROR] No cutscene frames available!")
            self.is_cutscene_playing = False
            self.cutscene_played = True
            self.phase_two = True
            return
            
        current_time = pygame.time.get_ticks()
        player.x = 850
        
        # Update cutscene frame based on scene frame duration
        if current_time - self.last_scene_update_time >= self.scene_frame_duration:
            self.last_scene_update_time = current_time
            
            if self.current_scene_frame < len(self.scene_frames):
                try:
                    # Draw background to game surface first
                    game_surface = pygame.Surface((1280, 720))
                    game_surface.blit(self.background_image, (0, 0))
                    
                    # Draw cutscene frame centered
                    frame = self.scene_frames[self.current_scene_frame]
                    frame_x = (1280 - frame.get_width()) // 2
                    frame_y = (720 - frame.get_height()) // 2
                    game_surface.blit(frame, (frame_x, frame_y))
                    
                    # Handle fullscreen scaling
                    screen_width, screen_height = self.screen.get_size()
                    is_fullscreen = screen_width != 1280 or screen_height != 720
                    
                    if is_fullscreen:
                        game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                        scaled_surface = pygame.transform.scale(game_surface, (game_width, game_height))
                        self.screen.fill((0, 0, 0))
                        self.screen.blit(scaled_surface, (x, y))
                    else:
                        self.screen.blit(game_surface, (0, 0))
                    
                    pygame.display.flip()
                    
                except Exception as e:
                    print(f"[ERROR] Failed to draw frame {self.current_scene_frame}: {e}")
            
            self.current_scene_frame += 1
            
            if self.current_scene_frame >= len(self.scene_frames):
                print("[DEBUG] Cutscene finished, transitioning to phase two")
                self.is_cutscene_playing = False
                self.cutscene_played = True
                self.phase_two = True
                self.current_scene_frame = 0
                return


    def update(self, surface, player):
        """Updated main update function to include phase two logic"""
        if self.health > 0:
            # Check for phase transition
            if self.health <= 150 and not self.cutscene_played:
                self.handle_phase_transition()
            
            if self.phase_two:
                self.update_bush_movement()
                if self.is_cry_attacking:
                    self.update_phase_two_attack()
                else:
                    self.phase_two_idle_animation()
            else:
                if self.is_attacking:
                    self.update_attack_animation(surface)
                else:
                    self.idle_animation(surface)
                self.attack()
                
            self.update_projectiles(surface)
            
            if self.color == (255, 0, 0):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_hit_time > 200:
                    self.color = (255, 255, 255)
                    
        self.enemy.update(self.clock.get_time())
    
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
        """Main game loop to update and display the boss actions along with the player."""
        game_surface = pygame.Surface((1280, 720))
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return "map_menu"

                    
            self.controller.check_controller_events()


            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720

            # Handle phase transition check
            if self.health < 150 and not self.cutscene_played and not self.is_cutscene_playing:
                self.handle_phase_transition()

            # Draw background
            game_surface.blit(self.background_image, (0, 0))

            # Handle cutscene
            if self.is_cutscene_playing:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_scene_update_time >= self.scene_frame_duration:
                    self.last_scene_update_time = current_time
                    if self.current_scene_frame < len(self.scene_frames):
                        # Center the cutscene frame
                        frame = self.scene_frames[self.current_scene_frame]
                        frame_x = 0
                        frame_y = (720 - frame.get_height()) // 2
                        game_surface.blit(frame, (frame_x, frame_y))
                    
                    self.current_scene_frame += 1
                    if self.current_scene_frame >= len(self.scene_frames):
                        self.is_cutscene_playing = False
                        self.cutscene_played = True
                        self.phase_two = True
                        self.current_scene_frame = 0
                        player.x = 900
                else:
                    # Keep drawing current frame
                    if 0 <= self.current_scene_frame < len(self.scene_frames):
                        frame = self.scene_frames[self.current_scene_frame]
                        frame_x = 0
                        frame_y = (720 - frame.get_height()) // 2
                        game_surface.blit(frame, (frame_x, frame_y))
                        
            else:
                # Normal gameplay
                keys = pygame.key.get_pressed()
                if player.x < self.wall_barrier:
                    player.x = self.wall_barrier

                # Update game logic
                player.move(keys, self.platforms, self.hazards, self.controller)
                player.attack(keys, self.controller)
                player.update_invincibility()

                # Update and draw game elements
                self.update(game_surface, player)

                # Draw boss animations
                if not self.is_cutscene_playing:
                    if self.phase_two:
                        if self.is_cry_attacking:
                            boss_surface = self.tree_cry_attack[self.current_cry_attack_frame].copy()
                        else:
                            boss_surface = self.TreeIdleCry[self.current_cry_frame].copy()
                    else:
                        if self.is_attacking:
                            boss_surface = self.attack_animation_frames[self.current_attack_frame].copy()
                        else:
                            boss_surface = self.idle_animation_frames[self.current_frame].copy()
                            
                    if self.color == (255, 0, 0):
                        boss_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                    game_surface.blit(boss_surface, (self.x, self.y))

                # Handle combat
                if player.current_action == 'attack' and player.hitbox.colliderect(self.hitbox):
                    if not player.damage_dealt:
                        self.sound_manager.play_sound('hit')
                        self.take_damage(30)
                        player.damage_dealt = True
                elif player.current_action != 'attack':
                    player.damage_dealt = False

                # Draw player
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

                # Draw phase two elements
                if self.phase_two:
                    bush_surface = self.bush_frames[self.current_bush_frame]
                    if self.bush_direction == -1:
                        bush_surface = pygame.transform.flip(bush_surface, True, False)
                    game_surface.blit(bush_surface, (self.bush_x, self.bush_y))
                    self.check_bush_collision(player)

                # Handle projectiles and collisions
                for projectile in self.projectiles[:]:
                    if player.hitbox.colliderect(projectile.rect) and not player.invincible:
                        player.take_damage(50)
                        self.projectiles.remove(projectile)
                        break

                for projectile in self.enemy.projectiles[:]:
                    if player.hitbox.colliderect(projectile['hitbox']) and not player.invincible:
                        player.take_damage(50)
                        self.enemy.projectiles.remove(projectile)
                        break

                # Draw UI and health bars
                font = pygame.font.SysFont(None, 40)
                health_text = font.render(f"Player Health: {player.healthbar}", True, (0, 0, 0))
                boss_health_text = font.render(f"Boss Health: {self.health}", True, (0, 0, 0))
                game_surface.blit(health_text, (960, 20))
                game_surface.blit(boss_health_text, (20, 20))

                self.draw_health_bar(game_surface)
                player.draw_health_bar(game_surface)
                self.enemy.update(self.clock.get_time())
                self.enemy.draw(game_surface)

                # Check game over conditions
                if player.healthbar <= 0:
                    pygame.mixer.music.stop()
                    return "game_over"

                if self.health <= 0 and player.healthbar != 0:
                    pygame.mixer.music.stop()
                    if self.game_map:
                        self.game_map.mark_level_completed('boss_one')
                        self.game_map.unlock_next_level('boss_one')
                    return "map_menu"

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