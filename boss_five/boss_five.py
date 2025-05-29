import os
import pygame
import sys
import random
import math
from end import EndSequence
from headers.classes import Player, Projectile, Boss, ControllerHandler
from sound_effects.bosses.boss_sound import SoundManager
# from menu_overlay import level_overlay
from .enemy_one import EnemyOneChess
from .enemy_two import EnemyTwoBeam
from .cloud import Cloud
from .blob import Blob
from boss_three.enemy_duck import EnemyDuck




class BossFive(Boss):
    def __init__(self, screen, clock, player, game_map=None):
        super().__init__(screen, clock)
        # self.healthbar()
        self.health = 1000
        self.h_init = self.health
        self.max_health = self.health
        player.y = 200
        self.clock = clock
        self.screen = screen
        self.game_map = game_map

        self.enemy_one_1 = EnemyOneChess(screen,clock, player, 972, True)
        self.enemy_one_2 = EnemyOneChess(screen,clock, player, 230, False) 
        self.enemy_two = EnemyTwoBeam(screen,clock, player) #! MOSNTER
        self.enemy_three = Blob(screen,clock, player)
        self.enemy_cloud = Cloud(screen,clock, None)
        # create duck enemy
        self.duck_enemy = EnemyDuck(screen,clock, player)
        self.sound_manager = SoundManager()
        self.controller = ControllerHandler()


        # self.enemy_one = enemy_one.EnemyOne(screen,clock, player)
        # Animation initialization
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_frame = 0
        self.animation_frame_float = 0.0
        self.last_hit_time = 0
        self.is_damage_flashing = False
        self.visual_health = self.health
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_duration = 100  # milliseconds per frame
        self.current_animation = 'idle'

        # Attacks and timers
        self.idle_count = 0
        self.projectiles = []
        self.bouncing_balls = []
        self.thunder_start_time = 0
        self.thunder_duration = 8000  # 8 seconds in milliseconds

        # Add phase tracking
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.enemy_spawn_interval = 7000  # 7 seconds in milliseconds
        self.current_phase = 1  # Track current phase (1: 1000-800, 2: 800-600, 3: 600-300, 4: <300)
        self.raven_active = False



        # Position and color initialization
        self.pos_x = 370  # Adjust for frame width desired cords (250,350,500)
        self.pos_y = -70  # Adjust for frame height
        self.color = (255, 255, 255)

        # Smooth interpolation helpers
        self.prev_x = self.pos_x
        self.prev_y = self.pos_y
        self.velocity_x = 0
        self.velocity_y = 0

        # Movement variables
        self.moving = False
        self.target_x = self.pos_x
        self.start_x = self.pos_x
        self.movement_progress = 0
        self.movement_speed = 0.02

        # !Health bar configuration
        self.health_bar_width = 300
        self.health_bar_height = 20
        self.health_bar_x = 20
        self.health_bar_y = 50
        self.border_thickness = 4 

        # ! HEAD ATTACK
        self.attack_counter = 0
        self.head_x = 0
        self.head_active = False
        self.animation_sequence = 'idle'
        self.head_animation_state = None
        self.head_timer = 0
        self.laugh_timer = 0
        self.laugh_interval = 2000

        self.head_pass_count = 0
        self.head_direction = 1  # 1 for right, -1 for left
        self.is_head_attacking = False
        # self.enemy_three = None  # Initialize enemy_three reference
        

        # Smooth health bar animation
        self.visual_health = self.health  # This will be used for smooth animation
        self.health_animation_speed = 1  # Speed of health bar animation (higher = faster)
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load in the background
        # In __init__, load but don't scale the background
        background_path = os.path.join(project_root, "boss_five", "thunder_background.png")
        try:
            self.original_background = pygame.image.load(background_path).convert()  # Store original
            self.background_image = self.original_background  # Initial background
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.original_background = pygame.Surface((1280, 720))  # Use default game resolution
            self.original_background.fill((135, 206, 235))
            self.background_image = self.original_background

        # Load in the idle animation
        sprite_sheet_path_idle = os.path.join(project_root, "animations", "boss_five_ani", "thunder_idle.png")
        self.idle_animation_frames = self.load_frames(sprite_sheet_path_idle, 20, 570, 570)

        # load in slam animation
        sprite_sheet_path_slam = os.path.join(project_root, "animations", "boss_five_ani", "boss_slam.png")
        self.slam_animation_frames = self.load_frames(sprite_sheet_path_slam, 16, 570, 570)
        
        # load in the eye attack animation
        sprite_sheet_path_eye = os.path.join(project_root, "animations", "boss_five_ani", "thunder_eye.png")
        self.eye_animation_frames = self.load_frames(sprite_sheet_path_eye, 19, 570, 570)

        # load in ball animation
        sprite_sheet_path_ball = os.path.join(project_root, "animations", "boss_five_ani", "ball.png")
        self.ball_animation_frames = self.load_frames(sprite_sheet_path_ball, 10, 180, 180)

        # load in projectile throw animation
        sprite_sheet_path_thunder = os.path.join(project_root, "animations", "boss_five_ani", "boss_thunder.png")
        self.thunder_animation_frames = self.load_frames(sprite_sheet_path_thunder, 28, 570, 570)        

        # load in ball thunder(will shoot random projectiles)
        sprite_sheet_path_ThundBall = os.path.join(project_root, "animations", "boss_five_ani", "thunder_ball.png")
        self.ThundBall_animation_frames = self.load_frames(sprite_sheet_path_ThundBall, 6, 160, 160)

        # load in the boss's head
        sprite_sheet_path_ThundHead = os.path.join(project_root, "animations", "boss_five_ani", "thunder_head.png")
        self.ThundHead_animation_frames = self.load_frames(sprite_sheet_path_ThundHead, 6, 760, 760)

        # load in boss falling
        sprite_sheet_path_ThundFall = os.path.join(project_root, "animations", "boss_five_ani", "Boss_falls.png")
        self.ThundFall_animation_frames = self.load_frames(sprite_sheet_path_ThundFall, 11, 570, 570)

        sprite_sheet_path_ThundAppear = os.path.join(project_root, "animations", "boss_five_ani", "Thunder_appear.png")
        self.ThundAppear_animation_frames = self.load_frames(sprite_sheet_path_ThundAppear, 6, 570, 570)

        # load in Boss calling
        sprite_sheet_path_ThundCall = os.path.join(project_root, "animations", "boss_five_ani", "Boss_calls.png")
        self.ThundCall_animation_frames = self.load_frames(sprite_sheet_path_ThundCall, 13, 570, 570)

        # load in Boss intro play it in the beginning along with the audio/ also resize it to 1280 by 720
        sprite_sheet_path_ThundIntro = os.path.join(project_root, "animations", "boss_five_ani", "Boss_intro.png")
        self.intro_animation_frames = self.load_intro_frames(sprite_sheet_path_ThundIntro)
        self.sound_manager = SoundManager()
        self.play_intro_sequence()

        
        self.hitbox = pygame.Rect(self.pos_x+100, self.pos_y+75, 290, 600)  #! Set boss hitbox (adjust as needed)     
        self.ball_hitbox = pygame.Rect(60, 60, 100, 120)  #! Set boss hitbox (adjust as needed) 
        self.ThundBall_hitbox = pygame.Rect(5, 5, 60, 70)  #! Set boss hitbox (adjust as needed)     

        # Initialize platforms and hazards
        self.platforms = [
            pygame.Rect(230, 545, 822, 2)
        ]
        self.hazards = [
            pygame.Rect(0,715,1250,2)
        ]
                # Music path
        self.music_path = os.path.join(project_root, "music", "Night Walker.mp3")
        self.play_music()


    def play_music(self):
        if os.path.exists(self.music_path)  and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
        else:
            print(f"Error: Music file not found at {self.music_path}")
    

    def load_intro_frames(self, sprite_sheet_path):
        """Load and resize intro animation frames to 1280x720."""
        original_frames = self.load_frames(sprite_sheet_path, 108, 512, 288)
        resized_frames = []
        
        for frame in original_frames:
            resized_frame = pygame.transform.scale(frame, (1280, 720))
            resized_frames.append(resized_frame)
        
        return resized_frames


    # Fix for the play_intro_sequence method to support fullscreen
    def play_intro_sequence(self):
        """Play the intro animation and audio once at the beginning."""
        if not hasattr(self, 'intro_animation_frames'):
            print("Error: intro_animation_frames not initialized")
            return
            
        try:
            # Animation settings
            frame_duration = 100  # Milliseconds per frame
            current_frame = 0
            start_time = pygame.time.get_ticks()
            delay_frames = 12  # 30 frames = 0.5 seconds at 60 FPS
            audio_played = False
            
            # Create game surface for native resolution rendering
            game_surface = pygame.Surface((1280, 720))
            
            # Load intro audio
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            audio_path = os.path.join(project_root, "sound_effects", "bosses", "audio_intro.wav")
            try:
                intro_sound = pygame.mixer.Sound(audio_path)
            except Exception as e:
                print(f"Error loading intro audio: {e}")
                audio_played = True
            
            frame_counter = 0
            # Play intro animation
            while current_frame < len(self.intro_animation_frames):
                current_time = pygame.time.get_ticks()
                
                # Play audio after frame delay
                if not audio_played and frame_counter >= delay_frames:
                    intro_sound.play()
                    audio_played = True
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return
                
                # Update frame based on time
                if current_time - start_time >= frame_duration:
                    current_frame += 1
                    frame_counter += 1
                    start_time = current_time
                    
                if current_frame < len(self.intro_animation_frames):
                    # Clear game surface and draw current frame
                    game_surface.fill((0, 0, 0))
                    game_surface.blit(self.intro_animation_frames[current_frame], (0, 0))
                    
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
                    
                self.clock.tick(60)
        except Exception as e:
            print(f"Error during intro sequence: {e}")


    def load_frames(self, sprite_sheet_path, num_frames, frame_width, frame_height):
        """Load frames from a sprite sheet."""
        if not os.path.exists(sprite_sheet_path):
            print(f"Error: Sprite sheet not found at {sprite_sheet_path}")
            return [pygame.Surface((frame_width, frame_height))]
            
        try:
            sprite_sheet = pygame.image.load(sprite_sheet_path)
            frames = []
            for i in range(num_frames):
                frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frames.append(frame)
            return frames
        except pygame.error as e:
            print(f"Error loading sprite sheet: {e}")
            return [pygame.Surface((frame_width, frame_height))]
    
    def take_damage(self, damage):
        """Handle taking damage and flashing red to indicate being hit."""
        current_time = pygame.time.get_ticks()
        damage_cooldown = 500  # Milliseconds between possible damage hits
        
        # Only take damage if enough time has passed since last hit
        if current_time - self.last_hit_time >= damage_cooldown:
            self.health = max(0, self.health - damage)  # Prevent negative health
            self.color = (255, 0, 0)  # Set to red to indicate damage
            self.last_hit_time = current_time
            self.is_damage_flashing = True  # Add this flag to track damage flash state
            
            if self.health <= 0:
                print("Boss is defeated!")
                return True  # Return True if boss is defeated
        return False
    
    def update_damage_effects(self):
        """Update damage-related effects like color flashing."""
        if self.is_damage_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit_time > 200:  # Flash duration in milliseconds
                self.color = (255, 255, 255)  # Reset to normal color
                self.is_damage_flashing = False  # Reset damage flash state


    def draw_health_bar(self, surface):
        """Draw the boss health bar with smooth animation."""
        # Update visual health for smooth animation
        if self.visual_health > self.health:
            self.visual_health = max(self.health, self.visual_health - 2)  # Increased animation speed
        elif self.visual_health < self.health:
            self.visual_health = min(self.health, self.visual_health + 2)

        # Draw border
        pygame.draw.rect(surface, (0, 0, 0), 
                        (self.health_bar_x - self.border_thickness, 
                        self.health_bar_y - self.border_thickness,
                        self.health_bar_width + (self.border_thickness * 2), 
                        self.health_bar_height + (self.border_thickness * 2)))
        
        # Draw background
        pygame.draw.rect(surface, (169, 169, 169),
                        (self.health_bar_x, self.health_bar_y,
                        self.health_bar_width, self.health_bar_height))
        
        # Calculate health ratio and width
        health_ratio = max(self.visual_health / self.max_health, 0)
        current_health_width = int(self.health_bar_width * health_ratio)
        
        # Draw health bar
        if current_health_width > 0:
            pygame.draw.rect(surface, (255, 0, 0),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, self.health_bar_height))
            
            # Add highlight for depth
            highlight_height = self.health_bar_height // 3
            pygame.draw.rect(surface, (255, 50, 50),
                        (self.health_bar_x, self.health_bar_y,
                            current_health_width, highlight_height))

            

    def update_animation_state(self, player):
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_frame_time) / 1000.0
        self.last_frame_time = current_time

        previous_frame = self.animation_frame

        # Check phase transitions
        if self.health <= 500 and self.current_phase != 4:
            self.current_phase = 4
            self.raven_active = True
        elif self.health <= 600 and self.current_phase != 3:
            self.current_phase = 3
        elif self.health <= 800 and self.current_phase != 2:
            self.current_phase = 2

        # Update movement if boss is moving
        self.update_movement()

        # Handle animations based on current state
        if self.current_animation == 'idle':
            previous_frame
            self.animation_frame_float += delta_time * (1000 / self.frame_duration)
            self.animation_frame = int(self.animation_frame_float)

            if not self.is_damage_flashing:
                self.color = (255, 255, 255)



            if self.animation_frame >= len(self.idle_animation_frames):
                self.idle_count = getattr(self, 'idle_count', 0) + 1
                self.animation_frame_float -= len(self.idle_animation_frames)
                self.animation_frame = int(self.animation_frame_float)
            

                
                if self.idle_count >= 1 and not self.moving:
                    self.idle_count = 0
                    self.execute_phase_behavior()

        elif self.current_animation == 'slam':
            self.handle_slam_attack(delta_time, player)
        elif self.current_animation == 'projectile':
            self.handle_projectile_attack(delta_time, player)
        elif self.current_animation == 'ball':
            self.handle_ball_attack(delta_time)
        elif self.current_animation == 'head' and self.current_phase > 1:  # Only allow head in phase 2+
            self.handle_head_attack(delta_time)
        elif self.current_animation == 'call':
            # Handle call animation
            self.animation_frame_float += delta_time * (1000 / self.frame_duration)
            self.animation_frame = min(int(self.animation_frame_float), len(self.ThundCall_animation_frames) - 1)
            if self.animation_frame == 7 and previous_frame != 7: # check the current frame number
                self.sound_manager.play_sound('party')
            
            # When call animation completes, spawn appropriate enemies
            if self.animation_frame >= len(self.ThundCall_animation_frames) - 1:                
                self.current_animation = 'idle'
                self.animation_frame_float = 0
                self.animation_frame = 0

    def execute_phase_behavior(self):
        """Execute behavior based on current phase"""
        # Always start with random movement
        self.move_to_random_position()
        
        if self.current_phase == 1:
            # Phase 1 (1000-800 HP): Basic pattern only
            self.choose_random_attack()
            # Ensure enemies are deactivated in phase 1
            self.deactivate_all_enemies()
            
        elif self.current_phase == 2:
            # Phase 2 (800-600 HP): Add EnemyTwo spawning
            # Once EnemyTwo is activated, it stays active
            if not self.enemy_two.active:  # Only check if not already active
                choice = random.random()
                if choice < 0.3:  # 30% chance to activate EnemyTwo
                    self.enemy_two.activate()
            self.choose_random_attack()
            
        elif self.current_phase == 3:
            # Phase 3 (600-500 HP): Add EnemyOne spawning
            choice = random.random()
            
            # ! Activate EnemyOne pair if not already active
            if not self.duck_enemy.active:
                if choice < 0.2:  # 30% chance to activate both chess pieces
                    self.execute_call_duck()
                    self.duck_enemy.setup_new_scenario()
                    self.sound_manager.play_sound('duck')
                    self.duck_enemy.activate()
                else:  
                    self.choose_random_attack()
                
        else:  # Phase 4 (<500 HP): All enemies + increased frequency
            # Ensure all permanent enemies are active
            if not self.enemy_one_1.active:
                self.enemy_one_1.activate()
            if not self.enemy_one_2.active:
                self.enemy_one_2.activate()
            if not self.enemy_two.active:
                self.enemy_two.activate()
                
            choice = random.random()
            if choice < 0.2:  # 20% chance for normal attack
                self.choose_random_attack()
            elif choice < 0.5:  # 30% chance was used for ensuring enemies above
                pass
            elif choice < 0.8:  # 30% chance for cloud
                if not self.enemy_cloud.active:
                    self.execute_call()
            else:  # 20% chance for head
                self.current_animation = 'head'
                self.head_animation_state = 'falling'
                self.animation_frame_float = 0
                self.animation_frame = 0

    def deactivate_all_enemies(self):
        """Only deactivate all enemies in phase 1, otherwise just cloud"""
        if self.current_phase == 1:
            self.enemy_one_1.active = False
            self.enemy_one_2.active = False
            self.enemy_two.active = False
            self.enemy_cloud.active = False
        else:
            # Only deactivate cloud in other phases
            self.enemy_cloud.active = False


    def execute_call(self):
        """Execute the call action based on current phase"""
        self.current_animation = 'call'
        self.animation_frame_float = 0
        self.animation_frame = 0
        
        if self.current_phase >= 3:  # When HP <= 600
            self.enemy_cloud.activate()

    def execute_call_duck(self):
        """Execute the call action based on current phase"""
        self.current_animation = 'call'
        self.animation_frame_float = 0
        self.animation_frame = 0
    

    def choose_random_attack(self):
        """Choose and execute a random attack"""
        if self.current_phase == 1:
            # Phase 1: Only basic attacks, no head sequence
            attack_choice = random.choice(['slam', 'projectile', 'ball'])
            self.current_animation = attack_choice
            self.animation_frame_float = 0
            self.animation_frame = 0
        else:
            # Phase 2+: Include head sequence after 2 attacks
            if self.attack_counter >= 2:
                self.attack_counter = 0
                self.current_animation = 'head'
                self.head_animation_state = 'falling'
                self.animation_frame_float = 0
                self.animation_frame = 0
            else:
                self.attack_counter += 1
                attack_choice = random.choice(['slam', 'projectile', 'ball'])
                self.current_animation = attack_choice
                self.animation_frame_float = 0
                self.animation_frame = 0
        # ! HEAD ATTACKS
    def handle_head_attack(self, delta_time):
        """Handle the head attack animation and movement"""
        current_time = pygame.time.get_ticks()
        
        if not self.is_head_attacking:
            print("Starting head attack sequence")
            self.is_head_attacking = True
            self.head_pass_count = 0
            self.head_direction = 1
            self.animation_sequence = 'falling'
            self.animation_frame_float = 0
            self.animation_frame = 0
            self.head_laugh_timer = current_time  # Reset timer when starting head attack
            if self.enemy_three:
                self.enemy_three.activate()
        
        screen_width = self.screen.get_width()
        head_speed = 10
        
        if self.animation_sequence == 'falling':
            self.animation_frame_float += delta_time * (1000 / self.frame_duration)
            self.animation_frame = min(int(self.animation_frame_float), len(self.ThundFall_animation_frames) - 1)
            
            if self.animation_frame >= len(self.ThundFall_animation_frames) - 1:
                print("Transitioning to head sequence")
                self.animation_sequence = 'head'
                self.animation_frame_float = 0
                self.head_x = -700 if self.head_direction == 1 else screen_width
        
        elif self.animation_sequence == 'head':

            # Update animation at a constant rate
            animation_speed = 12  # Adjust this value to change animation speed
            self.animation_frame_float += delta_time * animation_speed
            self.hitbox = pygame.Rect(0,0,10,10)


            # Play laugh sound at regular intervals during head sequence
            if current_time - self.head_laugh_timer >= self.laugh_interval:
                self.sound_manager.play_sound('clown_laugh')
                self.head_laugh_timer = current_time  # Reset timer

            # pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox, 2)
            
            # Move head across screen
            if self.head_direction == 1:
                self.head_x += head_speed
                if self.head_x > screen_width:
                    # print("Reversing direction (right to left)")
                    self.head_x = screen_width
                    self.head_direction = -1
                    self.head_pass_count += 1
            else:
                self.head_x -= head_speed
                if self.head_x < -700:
                    # print("Reversing direction (left to right)")
                    self.head_x = -700
                    self.head_direction = 1
                    self.head_pass_count += 1
            
            if self.head_pass_count >= 4:
                print("Transitioning to appear sequence")
                self.animation_sequence = 'appear'
                self.animation_frame_float = 0
                self.animation_frame = 0
        
        elif self.animation_sequence == 'appear':
            self.animation_frame_float += delta_time * (1000 / self.frame_duration)
            self.animation_frame = min(int(self.animation_frame_float), len(self.ThundAppear_animation_frames) - 1)
            
            if self.animation_frame >= len(self.ThundAppear_animation_frames) - 1:
                print("Ending head attack sequence")
                self.current_animation = 'idle'
                self.hitbox = pygame.Rect(self.pos_x+100, self.pos_y+75, 290, 600)  #! Set boss hitbox (adjust as needed)   
                self.animation_frame_float = 0
                self.animation_frame = 0
                self.is_head_attacking = False
                if self.enemy_three:
                    self.enemy_three.deactivate()

    # ! SLAM ATACKKKKKKKKKKKKKKKKKKKKKKKKKKKKK!!!!!!!!!!!!!!!!!!!!!!!

    def handle_slam_attack(self, delta_time, player):
        previous_frame = self.animation_frame

        self.animation_frame_float += delta_time * (1000 / self.frame_duration)
        self.animation_frame = min(int(self.animation_frame_float), len(self.slam_animation_frames) - 1)

        if self.animation_frame == 9 and previous_frame != 9:
            self.sound_manager.play_sound('slam')

        # Check for damage frames (9-11)
        if 9 <= self.animation_frame <= 11:
            self.check_slam_collision(player)
            # Draw slam attack hitboxes for debugging
            self.draw_slam_hitboxes()

        # Return to idle after animation completes and move
        if self.animation_frame >= len(self.slam_animation_frames) - 1:
            self.move_to_random_position()
            self.current_animation = 'idle'
            self.animation_frame_float = 0
            self.animation_frame = 0

    def draw_slam_hitboxes(self):
        # Make hitboxes more visible with thicker borders
        # Curse effect hitbox
        curse_box = pygame.Rect(self.pos_x + 80, self.pos_y + 410, 380, 150)
        # pygame.draw.rect(self.screen, (255, 0, 255), curse_box, 3)  # Purple for curse, thicker border
        
        # Center damage hitbox
        damage_box = pygame.Rect(self.pos_x + 150, self.pos_y + 300, 200, 200)
        # pygame.draw.rect(self.screen, (255, 0, 0), damage_box, 3)  # Red, thicker border

    def check_slam_collision(self, player):
        # Define separate hitboxes for damage and curse effect
        curse_box = pygame.Rect(self.pos_x + 80, self.pos_y + 410, 380, 150)
        # damage_box = pygame.Rect(self.pos_x + 150, self.pos_y + 300, 200, 200)

        # Check for curse collision
        if player.hitbox.colliderect(curse_box):
            if not player.invincible:
                player.take_damage(50)
                # player.curse()  # Apply curse effect
        
        # # Check for damage collision
        # if player.hitbox.colliderect(damage_box):
        #     if not player.invincible:
        #         player.take_damage(20)

    # ! END OF SLAMMMMMMMMMMMMMMMMMMMMMMm

    def handle_projectile_attack(self, delta_time, player):  # Add player parameter
        MAX_PROJECTILES = 8
        PROJECTILE_SPAWN_CHANCE = 0.2

        previous_frame = self.animation_frame
        
        self.animation_frame_float += delta_time * (1000 / self.frame_duration)
        self.animation_frame = min(int(self.animation_frame_float), len(self.thunder_animation_frames) - 1)

    # Only play sound when we first enter frame 3
        if self.animation_frame == 3 and previous_frame != 3:
            self.sound_manager.play_sound('thunder')


            try:
                # actual_sound = self.sound_manager.sounds['thunder']  # Get the actual sound object
                # print(f"Thunder sound object: {actual_sound}")  # Debug
                self.sound_manager.play_sound('thunder')
            except Exception as e:
                print(f"Error playing thunder sound: {e}")  # Debug any errors


        # Spawn projectiles during frames 21-28 if we haven't reached max
        if 21 <= self.animation_frame <= 28:
            if len(self.projectiles) < MAX_PROJECTILES and random.random() < PROJECTILE_SPAWN_CHANCE:
                self.spawn_thunder_ball(player)  # Pass player to spawn_thunder_ball

        # Return to idle after animation completes
        if self.animation_frame >= len(self.thunder_animation_frames) - 1:
            self.move_to_random_position()
            self.current_animation = 'idle'
            self.animation_frame_float = 0
            self.animation_frame = 0


    def handle_ball_attack(self, delta_time):
        # Print debug info for animation state
        # print(f"Current animation frame: {self.animation_frame}")
        
        self.animation_frame_float += delta_time * (1000 / self.frame_duration)
        self.animation_frame = min(int(self.animation_frame_float), len(self.eye_animation_frames) - 1)


        # Debug print for ball spawn condition
        if self.animation_frame == 18:
            print("Reached spawn frame 18")
            if not getattr(self, 'ball_spawned', False):
                print("Spawning ball!")
                self.spawn_bouncing_ball()
                self.ball_spawned = True
        

        if self.animation_frame >= len(self.eye_animation_frames) - 1:
            self.ball_spawned = False
            self.move_to_random_position()
            self.current_animation = 'idle'
            self.animation_frame_float = 0
            self.animation_frame = 0



    def move_to_random_position(self):
        possible_positions = [250, 370, 500]
        if self.pos_x in possible_positions:
            possible_positions.remove(self.pos_x)
        self.target_x = random.choice(possible_positions)
        
        self.start_x = self.pos_x
        self.moving = True
        self.movement_progress = 0
        self.current_animation = 'idle'
        self.animation_frame_float = 0
        self.animation_frame = 0

    def update_movement(self):
        if self.moving:
            # Ease in/out movement
            self.movement_progress += 0.02
            progress = self.ease_in_out_quad(self.movement_progress)
            
            if self.movement_progress >= 1:
                self.pos_x = self.target_x
                self.moving = False
                self.movement_progress = 0
            else:
                # Smooth movement using easing function
                self.pos_x = self.lerp(self.start_x, self.target_x, progress)
            
            # Update hitbox position
            self.hitbox.x = self.pos_x + 100

    def ease_in_out_quad(self, t):
        # Quadratic easing for smooth movement
        if t < 0.5:
            return 2 * t * t
        else:
            t = 2 * t - 1
            return -0.5 * (t * (t - 2) - 1)

    def lerp(self, start, end, progress):
        """Linear interpolation between start and end points."""
        return start + (end - start) * progress



    def spawn_thunder_ball(self, player):  # Add player parameter
        spawn_x = random.randint(0, self.screen.get_width())
        spawn_y = -50
        
        # Calculate trajectory towards actual player position
        target_x = player.x + player.hitbox.width / 2  # Target player's center
        target_y = player.y + player.hitbox.height / 2
        
        # Calculate angle to player
        dx = target_x - spawn_x
        dy = target_y - spawn_y
        angle = math.atan2(dy, dx)
        
        speed = 10
        
        self.projectiles.append({
            'x': spawn_x,
            'y': spawn_y,
            'speed_x': math.cos(angle) * speed,
            'speed_y': math.sin(angle) * speed,
            'frame': 0,
            'active': True
        })




    def spawn_bouncing_ball(self):
        # Adjusted spawn position for 180x180 frame
        ball_x = self.pos_x + 200  # Initial spawn X
        ball_y = 445  # Initial spawn Y
        
        # Determine initial speed
        if self.pos_x == 370:  # Center
            speed_x = random.choice([-8, 8])
        elif self.pos_x == 250:  # Left
            speed_x = 8
        else:  # Right (500)
            speed_x = -8

        # print(f"Spawning ball at position ({ball_x}, {ball_y})")  # Debug print

        self.bouncing_balls.append({
            'x': ball_x,
            'y': ball_y,
            'speed_x': speed_x,
            'speed_y': 0,
            'gravity': 0.5,
            'active': True,
            'frame': 0,
            'frame_progress': 0.0,
            'bounces': 0,
            'state': 'compress',
            'previous_frame_index' : 0,
            'bounce_sounds_played': 0  # Add this counter
        })

    def draw(self, surface):
        """Draw the boss with current animation frame."""
        current_frame = None
        
        if self.current_animation == 'head':
            if hasattr(self, 'animation_sequence'):
                if self.animation_sequence == 'falling':
                    current_frame = self.ThundFall_animation_frames[self.animation_frame]
                elif self.animation_sequence == 'appear':
                    current_frame = self.ThundAppear_animation_frames[self.animation_frame]
        elif self.current_animation == 'idle' and self.idle_animation_frames:
            current_frame = self.idle_animation_frames[self.animation_frame % len(self.idle_animation_frames)]
        elif self.current_animation == 'slam' and self.slam_animation_frames:
            current_frame = self.slam_animation_frames[self.animation_frame % len(self.slam_animation_frames)]
        elif self.current_animation == 'projectile' and self.thunder_animation_frames:
            current_frame = self.thunder_animation_frames[self.animation_frame % len(self.thunder_animation_frames)]
        elif self.current_animation == 'ball' and self.eye_animation_frames:
            current_frame = self.eye_animation_frames[self.animation_frame % len(self.eye_animation_frames)]
        elif self.current_animation == 'call' and self.ThundCall_animation_frames:
            current_frame = self.ThundCall_animation_frames[self.animation_frame % len(self.ThundCall_animation_frames)]

        if current_frame:
            boss_surface = current_frame.copy()
            if self.color != (255, 255, 255):
                boss_surface.fill(self.color, special_flags=pygame.BLEND_MULT)
            surface.blit(boss_surface, (self.pos_x, self.pos_y))


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
        # Initialize projectiles and bouncing balls lists if they don't exist
        if not hasattr(self, 'projectiles'):
            self.projectiles = []
        if not hasattr(self, 'bouncing_balls'):
            self.bouncing_balls = []

        game_surface = pygame.Surface((1280,720))

        while True:
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

            # Get keyboard input
            keys = pygame.key.get_pressed()
            dt = self.clock.get_time() / 1000.0  # Convert to seconds
            
            # At the start of the game loop in window method, before drawing

            # Now draw the properly scaled background
            game_surface.blit(self.background_image, (0, 0))

            # Update and draw boss
            self.update_animation_state(player)  # Pass player to update_animation_state
            self.update_damage_effects()

            # Handle player movement and actions
            player.move(keys, self.platforms, self.hazards, self.controller)
            player.attack(keys, self.controller)
            player.update_invincibility()

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



            # ! ENEMIES:
            if self.enemy_cloud.player is None:
                self.enemy_cloud.player = player

            # Draw boss and its animations (except for the head)
            if self.current_animation == 'head' and self.animation_sequence == 'head':
                # Don't draw boss during head sequence
                pass
            else:
                self.draw(game_surface)


            # Draw player
            if player_frame:
                player_surface = player_frame.copy()
                if player.color == (255, 0, 0):
                    player_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                game_surface.blit(player_surface, (player.x, player.y))

            if self.current_phase >= 2:  # Phase 2+: EnemyTwo
                if self.enemy_two.active:
                    self.enemy_two.update()
                    self.enemy_two.draw(game_surface)

            if self.current_phase >= 3:  # Phase 3+: EnemyOne and Cloud
                if self.enemy_one_1.active:
                    self.enemy_one_1.update()
                    self.enemy_one_1.draw(game_surface)
                if self.enemy_one_2.active:
                    self.enemy_one_2.update()
                    self.enemy_one_2.draw(game_surface)
                if self.enemy_cloud.active:
                    self.enemy_cloud.update()
                    self.enemy_cloud.draw(game_surface)

            if self.health <= 800:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_enemy_spawn_time >= self.enemy_spawn_interval:
                    if not self.enemy_two.active:  # Only activate if not already active
                        self.enemy_two.activate()
                        self.enemy_two.update()
                        self.enemy_two.draw(game_surface)
                        self.last_enemy_spawn_time = current_time

            # ! Check collisions for active enemies
            enemy_hitbox = self.enemy_one_1.get_hitbox()
            if enemy_hitbox and player.hitbox.colliderect(enemy_hitbox):
                if not player.invincible:
                    damage = self.enemy_one_1.hit()
                    if damage != 0:
                        player.take_damage(damage)

            enemy_hitbox = self.enemy_one_2.get_hitbox()
            if enemy_hitbox and player.hitbox.colliderect(enemy_hitbox):
                if not player.invincible:
                    damage = self.enemy_one_2.hit()
                    if damage != 0:
                        player.take_damage(damage)

            cloud_hitbox = self.enemy_cloud.check_hitbox()
            if cloud_hitbox and player.hitbox.colliderect(cloud_hitbox):
                if not player.invincible:
                    player.take_damage(25)
            
            # In the window method, where other enemy collisions are checked:
            enemy_two_hitbox = self.enemy_two.check_hitbox()
            if enemy_two_hitbox and player.hitbox.colliderect(enemy_two_hitbox):
                if not player.invincible:
                    player.take_damage(25)

            if self.enemy_three and self.enemy_three.active:
                    self.enemy_three.update()
                    self.enemy_three.draw(game_surface)
                    blob_hitbox = self.enemy_three.check_hitbox()
                    if blob_hitbox and player.hitbox.colliderect(blob_hitbox):
                        if not player.invincible:
                            player.take_damage(20)
            

            # ! Update and draw active ducks
            if self.duck_enemy.active:
                self.duck_enemy.update(self.clock.get_time())
                
                # Check if all ducks are off screen
                all_ducks_off_screen = True
                for duck in self.duck_enemy.ducks:
                    if -100 <= duck['x'] <= 1100 + 100:
                        all_ducks_off_screen = False
                        break
                
                # Deactivate if all ducks are off screen
                if all_ducks_off_screen:
                    self.duck_enemy.active = False
                    self.duck_enemy.ducks.clear()
                else:
                    self.duck_enemy.draw(game_surface)
                    
                    # Check duck collisions with player
                    for duck in self.duck_enemy.ducks:
                        if player.hitbox.colliderect(duck['hitbox']):
                            if not player.invincible:
                                player.take_damage(30)


            # Draw ONLY the head attack animation on top of everything
            if self.current_animation == 'head' and self.animation_sequence == 'head':
                frame_index = int(self.animation_frame_float) % len(self.ThundHead_animation_frames)
                current_frame = self.ThundHead_animation_frames[frame_index]
                game_surface.blit(current_frame, (self.head_x, 0))



            # Update and draw projectiles
            for projectile in self.projectiles[:]:  # Use slice copy to safely modify list while iterating
                projectile['y'] += projectile['speed_y']
                projectile['x'] += projectile['speed_x']
                
                # Create projectile hitbox
                projectile_hitbox = pygame.Rect(projectile['x'], projectile['y'], 30, 30)  # Adjust size as needed
                
                # Check collision with player
                if projectile_hitbox.colliderect(player.hitbox) and not player.invincible:
                    player.take_damage(15)
                    self.projectiles.remove(projectile)
                elif projectile['y'] > game_surface.get_height() or projectile['x'] < 0 or projectile['x'] > game_surface.get_width():
                    self.projectiles.remove(projectile)
                else:
                    # Draw projectile
                    current_frame = self.ThundBall_animation_frames[int(projectile['frame'])]
                    game_surface.blit(current_frame, (projectile['x'], projectile['y']))
                    projectile['frame'] = (projectile['frame'] + 0.2) % len(self.ThundBall_animation_frames)

            #! Update and draw bouncing balls
            for ball in self.bouncing_balls[:]:
                    # Update ball physics

                    ball['speed_y'] += ball['gravity']
                    ball['y'] += ball['speed_y']
                    ball['x'] += ball['speed_x']

                    # Create hitbox (adjusted for 180x180 frame)
                    hitbox_width = 100
                    hitbox_height = 100
                    ball_hitbox = pygame.Rect(ball['x'] + 40, ball['y'] + 50, hitbox_width, hitbox_height)

                    # Platform collision
                    for platform in self.platforms:
                        if ball_hitbox.colliderect(platform):
                            if ball['speed_y'] > 0:  # Only bounce when moving downward
                                ball['y'] = platform.top - hitbox_height - 20
                                ball['speed_y'] = -12
                                ball['bounces'] += 1
                                ball['state'] = 'compress'
                                ball['frame'] = 0
                                ball['frame_progress'] = 0.0
                                # print(f"Ball bounced! Position: ({ball['x']}, {ball['y']})")

                    # Animation state machine
                    if ball['state'] == 'compress':
                        if ball['frame_progress'] < 1.0:
                            ball['frame_progress'] += 0.15
                        else:
                            ball['state'] = 'expand'
                            ball['frame'] = 1

                    elif ball['state'] == 'expand':
                        if ball['speed_y'] < 0:  # Moving upward
                            ball['frame'] = min(ball['frame'] + 0.15, 9)  # Changed to match 10 frames
                        else:
                            ball['frame'] = max(ball['frame'] - 0.15, 0)
                            if ball['frame'] <= 0:
                                ball['state'] = 'compress'
                                ball['frame_progress'] = 0.0

                    # ! Get current frame
                    frame_index = int(ball['frame']) % len(self.ball_animation_frames)
                    previous_frame_index = ball['previous_frame_index']
                    current_frame = self.ball_animation_frames[frame_index]

                    # Check for frame transition and bounce sound count
                    if frame_index == 1 and previous_frame_index !=  1 and ball['bounce_sounds_played'] < 2:
                        self.sound_manager.play_sound('bounce')
                        ball['bounce_sounds_played'] += 1

                    ball['previous_frame_index'] = frame_index

                    # Print debug info
                    # print(f"Ball state: {ball['state']}, Frame: {frame_index}, Position: ({ball['x']}, {ball['y']})")

                    # Remove ball conditions
                    if ball['bounces'] > 3 or ball['y'] > game_surface.get_height() or ball['x'] < -110 or ball['x'] > self.screen.get_width() :
                        self.bouncing_balls.remove(ball)
                        continue

                    # Check player collision
                    if ball_hitbox.colliderect(player.hitbox) and not player.invincible:
                        player.take_damage(20)

                    # Draw the ball
                    game_surface.blit(current_frame, (ball['x'], ball['y']))
                    
                    # Draw hitbox for debugging
                    # pygame.draw.rect(self.screen, (255, 0, 0), ball_hitbox, 2)
                    # # Draw center point of hitbox
                    # pygame.draw.circle(self.screen, (0, 255, 0), (int(ball_hitbox.centerx), int(ball_hitbox.centery)), 3)


            # Handle player attack collision with boss
            if player.current_action == 'attack' and player.hitbox.colliderect(self.hitbox):
                if not player.damage_dealt:
                    self.take_damage(25)
                    

            self.draw_health_bar(game_surface)
            player.draw_health_bar(game_surface)

            # Draw platforms
            # for platform in self.platforms:
            # pygame.draw.rect(self.screen, (0, 0, 0), platform)
            player.update()

            # Draw UI and health bars
            font = pygame.font.SysFont(None, 40)
            health_text = font.render(f"Player Health: {player.healthbar}", True, (0, 0, 0))
            boss_health_text = font.render(f"Boss Health: {self.health}", True, (0, 0, 0))
            game_surface.blit(health_text, (960, 20))
            game_surface.blit(boss_health_text, (20, 20))


                                # Check for game over
            if player.healthbar <= 0:
                pygame.mixer.music.stop()
                return "game_over"  # New return state for game over

            if self.health <= 0 and player.healthbar != 0:
                pygame.mixer.music.stop()
                if self.game_map:
                    self.game_map.mark_level_completed('boss_five')
                    self.game_map.unlock_next_level('boss_five')
                   # Show end cutscene instead of returning to map
                    end_sequence = EndSequence(self.screen, self.clock)
                    end_sequence.run()
            
               # Handle fullscreen scaling at the end of the frame
            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720

            if is_fullscreen:
                game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                scaled_surface = pygame.transform.scale(game_surface, (game_width, game_height))
                self.screen.fill((0, 0, 0))
                self.screen.blit(scaled_surface, (x, y))
            else:
                self.screen.blit(game_surface, (0, 0))


            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(60)