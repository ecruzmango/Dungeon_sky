import pygame
import sys
import os
import logging
from headers.classes import Boss, Projectile, Player, ControllerHandler
# from menu_overlay import level_overlay
from tutorial import dummy

logger = logging.getLogger(__name__)


class Tutorial(Boss):
    def __init__(self, screen, clock, player, game_map=None):
        super().__init__(screen, clock)
        
        self.screen = screen
        self.game_surface = pygame.Surface((1280,720))
        self.clock = clock
        self.player = player
        self.game_map = game_map
        self.controller = ControllerHandler()
        
        # Setup paths and load sprite sheets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Load tutorial background
        self.tutorial_bg_path = os.path.join(project_root, "tutorial", "tutorial .png") 
        self.background_image = pygame.image.load(self.tutorial_bg_path).convert()


        # Initialize health-related attributes
        self.health = 100
        self.max_health = 100
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.health_bar_x = 50
        self.health_bar_y = 50
    

        # Load pixel font
        try:
            font_path = os.path.join(project_root, "fonts", "PixelFont.ttf")  # Adjust path as needed
            self.pixel_font = pygame.font.Font(font_path, 48)  # Larger size for controls
            self.pixel_font_small = pygame.font.Font(font_path, 36)  # Smaller size for other text
        except:
            # Fallback to system font if custom font fails to load
            self.pixel_font = pygame.font.SysFont("Arial", 48)
            self.pixel_font_small = pygame.font.SysFont("Arial", 36)

        # Music path
        self.music_path = os.path.join(project_root, "music", "tutorial.mp3")
        pygame.mixer.init()
        self.play_music()
            
        # platforms
        self.ground = pygame.Rect(0, 650, 1290, 25)
        self.PlatOne = pygame.Rect(0, 475, 100, 10)
        self.PlatTwo = pygame.Rect(310, 475, 200, 10)
        self.PlatThree = pygame.Rect(800, 390, 500, 10)
        
        self.platforms = [self.ground, self.PlatOne, self.PlatTwo, self.PlatThree]
        self.hazards = []

        # Initialize the dummy
        self.dummy = dummy.Enemy(screen, clock, player)

        # Enhanced control visualization settings
        self.controls = [
            {"key": "SPACE", "action": "JUMP", "pos": (1000, 50)},
            {"key": "A/D", "action": "MOVE", "pos": (1000, 120)},
            {"key": "S", "action": "DASH", "pos": (1000, 190)},
            {"key": "p", "action": "ATTACK", "pos": (1000, 260)}
        ]

        # Exit door position (adjust as needed)
        self.exit_door = pygame.Rect(1200, 200, 50, 100)  # Example position
        self.show_exit_prompt = False
         # ! Add these new attributes for state management
        self.completed = False
        self.exit_requested = False
        
    def play_music(self):
            """Play background music for the tutorial level."""
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(1.5)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            except pygame.error as e:
                print(f"Could not load or play music: {e}")
                pass
    def draw_controls(self):
        """Draw control information with medieval-style formatting"""
        # Center position calculation
        center_x = self.screen.get_width() // 2
        start_y = 50  # Starting Y position
        spacing = 80  # Vertical spacing between controls
        
        # Draw title
        title_text = self.pixel_font.render("CONTROLS", True, (255, 215, 0))  # Gold color
        title_rect = title_text.get_rect(center=(center_x, start_y))
        
        # Draw decorative line under title
        line_length = 300
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (center_x - line_length//2, start_y + 30),
                        (center_x + line_length//2, start_y + 30), 3)
        
        # Draw ornamental corners for title
        corner_size = 10
        pygame.draw.line(self.screen, (255, 215, 0), (title_rect.left, title_rect.top),
                        (title_rect.left + corner_size, title_rect.top), 3)
        pygame.draw.line(self.screen, (255, 215, 0), (title_rect.right, title_rect.top),
                        (title_rect.right - corner_size, title_rect.top), 3)
        
        self.screen.blit(title_text, title_rect)
        
        # Update control positions to be centered
        for i, control in enumerate(self.controls):
            y_pos = start_y + 60 + (i * spacing)
            
            # Create medieval-style box for key
            key_text = self.pixel_font.render(control['key'], True, (255, 223, 0))  # Golden yellow
            key_rect = key_text.get_rect(center=(center_x - 100, y_pos))
            
            # Draw ornate background for key
            box_padding = 20
            box_rect = key_rect.inflate(box_padding, box_padding)
            pygame.draw.rect(self.screen, (139, 69, 19), box_rect)  # Brown background
            pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 3)  # Gold border
            
            # Draw corner decorations
            corner_size = 8
            for corner in [(box_rect.topleft, (1, 1)), (box_rect.topright, (-1, 1)),
                        (box_rect.bottomleft, (1, -1)), (box_rect.bottomright, (-1, -1))]:
                pos, direction = corner
                pygame.draw.line(self.screen, (255, 215, 0),
                            pos,
                            (pos[0] + corner_size * direction[0], pos[1]), 3)
                pygame.draw.line(self.screen, (255, 215, 0),
                            pos,
                            (pos[0], pos[1] + corner_size * direction[1]), 3)
            
            # Draw key text
            self.screen.blit(key_text, key_rect)
            
            # Draw action text with medieval separator
            action_text = self.pixel_font_small.render(control['action'], True, (255, 223, 0))
            action_rect = action_text.get_rect(midleft=(center_x, y_pos))
            
            # Draw decorative separator
            separator_start = (center_x - 50, y_pos)
            separator_end = (center_x - 20, y_pos)
            pygame.draw.line(self.screen, (255, 215, 0), separator_start, separator_end, 2)
            
            self.screen.blit(action_text, action_rect)
            
    def check_exit_condition(self, player):
        """Check if player is near the exit door"""
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        return self.exit_door.colliderect(player_rect)
    
    def is_completed(self):
        """Check if tutorial is completed"""
        return self.completed
        
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
    
    def draw_ui_box(self, text_surface, center_pos, bg_color=(0, 0, 0, 180), border_color=(255, 215, 0), padding=(30, 20)):
        """
        Draws a gold/black UI box to the game surface, consistent with the world map theme.
        """
        rect = text_surface.get_rect(center=center_pos)
        box_rect = rect.inflate(*padding)

        # Draw background
        surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        surface.fill(bg_color)
        self.game_surface.blit(surface, box_rect.topleft)

        # Draw border
        if border_color:
            pygame.draw.rect(self.game_surface, border_color, box_rect, 2)

        # Draw text
        self.game_surface.blit(text_surface, rect)


    def window(self, player):
        """Main game loop with enhanced visuals"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    logger.debug(f"Key pressed in tutorial: {event.key}")
                    if event.key == pygame.K_ESCAPE:
                        return "pause"
                    elif event.key == pygame.K_p and self.check_exit_condition(player):
                        pygame.mixer.music.stop()
                        self.completed = True
                        if self.game_map:
                            self.game_map.mark_level_completed('tutorial')
                            self.game_map.unlock_next_level('tutorial')
                        return "map_menu"

                # Handle controller connection/disconnection
                elif event.type == pygame.JOYDEVICEADDED:
                    self.controller.connect_controller()
                elif event.type == pygame.JOYDEVICEREMOVED:
                    if self.controller.controller and event.instance_id == self.controller.controller.get_instance_id():
                        self.controller = ControllerHandler()

            # Handle controller logic
            if self.controller.is_connected():
                if self.controller.is_start_pressed():
                    self.controller.clear_start_press()
                    return "pause"
                
                if self.check_exit_condition(player) and self.controller.is_jumping():
                    pygame.mixer.music.stop()
                    self.completed = True
                    if self.game_map:
                        self.game_map.mark_level_completed('tutorial')
                        self.game_map.unlock_next_level('tutorial')
                    return "map_menu"

            keys = pygame.key.get_pressed()
            
            # Handle exit condition
            if self.check_exit_condition(player):
                self.show_exit_prompt = True
                if keys[pygame.K_e]:
                    pygame.mixer.music.stop()
                    self.completed = True
                    if self.game_map:
                        self.game_map.mark_level_completed('tutorial')
                        self.game_map.unlock_next_level('tutorial')
                    return "map_menu"
            else:
                self.show_exit_prompt = False


            # ! IMPORT

            # Get screen dimensions and check if fullscreen
            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720

            # Clear the main screen
            self.screen.fill((0, 0, 0))  # Black background for letterboxing/pillarboxing

            # Clear and prepare game surface
            self.game_surface.fill((0, 0, 0))
            self.game_surface.blit(self.background_image, (0, 0))

            # Update and draw dummy
            self.dummy.update(player)
            self.dummy.draw(self.game_surface)

            # Update player
            player.move(keys, self.platforms, self.hazards, self.controller)
            player.attack(keys, self.controller)
            player.update_invincibility()

            # Handle player animation
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
                
            # Draw player
            if player_frame:
                player_surface = player_frame.copy()
                if player.color == (255, 0, 0):
                    player_surface.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
                self.game_surface.blit(player_surface, (player.x, player.y))

            # Draw controls
            center_x = self.game_surface.get_width() // 2
            start_y = 50
            spacing = 80

            # Draw controls title
            title_text = self.pixel_font.render("CONTROLS", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(center_x, start_y))
            
            # Draw title decorations
            line_length = 300
            pygame.draw.line(self.game_surface, (255, 215, 0),
                            (center_x - line_length//2, start_y + 30),
                            (center_x + line_length//2, start_y + 30), 3)
            
            corner_size = 10
            pygame.draw.line(self.game_surface, (255, 215, 0),
                            (title_rect.left, title_rect.top),
                            (title_rect.left + corner_size, title_rect.top), 3)
            pygame.draw.line(self.game_surface, (255, 215, 0),
                            (title_rect.right, title_rect.top),
                            (title_rect.right - corner_size, title_rect.top), 3)
            
            self.game_surface.blit(title_text, title_rect)

            # Draw control buttons
            for i, control in enumerate(self.controls):
                y_pos = start_y + 60 + (i * spacing)
                
                # Key box
                key_text = self.pixel_font.render(control['key'], True, (255, 223, 0))
                key_rect = key_text.get_rect(center=(center_x - 100, y_pos))
                
                box_padding = 20
                box_rect = key_rect.inflate(box_padding, box_padding)
                pygame.draw.rect(self.game_surface, (139, 69, 19), box_rect)
                pygame.draw.rect(self.game_surface, (255, 215, 0), box_rect, 3)
                
                # Corner decorations for key box
                corner_size = 8
                for corner in [(box_rect.topleft, (1, 1)), (box_rect.topright, (-1, 1)),
                            (box_rect.bottomleft, (1, -1)), (box_rect.bottomright, (-1, -1))]:
                    pos, direction = corner
                    pygame.draw.line(self.game_surface, (255, 215, 0),
                                pos,
                                (pos[0] + corner_size * direction[0], pos[1]), 3)
                    pygame.draw.line(self.game_surface, (255, 215, 0),
                                pos,
                                (pos[0], pos[1] + corner_size * direction[1]), 3)
                
                self.game_surface.blit(key_text, key_rect)
                
                # Action text
                action_text = self.pixel_font_small.render(control['action'], True, (255, 223, 0))
                action_rect = action_text.get_rect(midleft=(center_x, y_pos))
                
                # Separator
                separator_start = (center_x - 50, y_pos)
                separator_end = (center_x - 20, y_pos)
                pygame.draw.line(self.game_surface, (255, 215, 0), separator_start, separator_end, 2)
                
                self.game_surface.blit(action_text, action_rect)

            # Draw exit prompt
            if self.show_exit_prompt:
                prompt_text = self.pixel_font.render("Ready to leave? Press E", True, (255, 255, 255))
                center_pos = (self.game_surface.get_width() // 2, 100)
                self.draw_ui_box(prompt_text, center_pos)


            # Update player
            player.update()

            # Final draw to screen
            if is_fullscreen:
                # Calculate dimensions for centered gameplay
                game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                
                
                # Scale and draw game surface
                scaled_game_surface = pygame.transform.scale(self.game_surface, (game_width, game_height))
                self.screen.blit(scaled_game_surface, (x, y))
            else:
                # Normal mode - draw directly
                self.screen.blit(self.game_surface, (0, 0))

            # Update display
            pygame.display.flip()
            self.clock.tick(60)