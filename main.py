import sys
import os
import pygame
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# hello there
from headers.utils import get_path
from headers.classes import Player, ControllerHandler
from tutorial.tutorial import Tutorial  # Add this import
from boss_one.boss_one import BossOneImplementation
from boss_three.boss_three import BossThree
from boss_four.boss_class import BossFourImplementation
from boss_five.boss_five import BossFive

from save_system.save import SaveSystem
from save_system.save_menu import SaveLoadMenu
from map import GameMap


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

def main():
    game = Game()
    game.run()


class GameState:
    MAIN_MENU = "main_menu"
    GAME_MENU = "game_menu"
    TUTORIAL = "tutorial"
    MAP_MENU = "map_menu"
    BOSS_ONE = "boss_one"
    BOSS_THREE = "boss_three"
    BOSS_FOUR = "boss_four"
    BOSS_FIVE = "boss_five"



class AnimatedMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Setup paths
        menu_sprite_sheet_path = get_path(os.path.join("assets", "menu", "main_menu.png"))
        load_menu_path = get_path(os.path.join("assets", "menu", "load_menu.png"))

        pre_menu_sprite_sheet_path = get_path(os.path.join("assets", "menu", "pre_main_menu.png"))
        
        


        # Load animation frames
        self.menu_frames = self.load_frames(menu_sprite_sheet_path, 6, 1280, 720)
        self.pre_menu_frames = self.load_frames(pre_menu_sprite_sheet_path,17, 1280, 720)

        # Load load menu background
        self.load_menu_bg = pygame.image.load(load_menu_path).convert_alpha()
        
        # Animation settings
        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = 100  # milliseconds per frame
        self.any_key_pressed = False
        last_start_press = False

        self.pre_intro_done = False
        self.pre_animation_index = 0
        self.played_pre_intro_sound = False

        # load pre intro sound
        self.pre_intro_sound = pygame.mixer.Sound(get_path((os.path.join("sound_effects","pre_intro.wav"))))


    def load_frames(self, sprite_sheet_path, num_frames, width, height):
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            frames.append(frame)
        return frames

    def update(self, dt):
        if not self.any_key_pressed:
            if not self.pre_intro_done:
                self.animation_timer += dt * 1000
                if not self.played_pre_intro_sound:
                    self.pre_intro_sound.play()
                    self.played_pre_intro_sound = True

                if self.animation_timer >= self.frame_duration:
                    self.animation_timer = 0
                    self.pre_animation_index += 1
                    if self.pre_animation_index >= len(self.pre_menu_frames):
                        self.pre_intro_done = True
            else:
                self.animation_timer += dt * 1000
                if self.animation_timer >= self.frame_duration:
                    self.animation_timer = 0
                    self.animation_index = (self.animation_index + 1) % len(self.menu_frames)

    def draw(self, surface):
        if not self.any_key_pressed:
            if not self.pre_intro_done:
                current_frame = self.pre_menu_frames[self.pre_animation_index]
            else:
                current_frame = self.menu_frames[self.animation_index]
            surface.blit(current_frame, (0, 0))
        else:
            surface.blit(self.load_menu_bg, (0, 0))


# Then, update the Game class's __init__ method
class Game:
    def __init__(self):
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.is_fullscreen = False

        self.paused = False

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Boss Battle Game")
        
        # Store original game surface
        self.game_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.controller = ControllerHandler()
        self.last_selected_pos = (640, 360)

        # Initialize fonts
        project_root = os.path.dirname(os.path.abspath(__file__))
        try:
            font_path = os.path.join(project_root, "fonts", "PixelFont.ttf")
            self.pixel_font = pygame.font.Font(font_path, 36)
            self.font_small = pygame.font.Font(font_path, 24)  # Smaller size for instructions
        except Exception as e:
            print(f"Could not load custom font: {e}")
            self.pixel_font = pygame.font.SysFont("Arial", 36)

        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        
        # Add animated menu
        self.animated_menu = AnimatedMenu(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.last_time = pygame.time.get_ticks()  # Initialize last_time
        self.last_level = None
        
        # Initialize game state
        self.current_state = GameState.MAIN_MENU
        
        self.clock = pygame.time.Clock()
        
        self.map = GameMap(self.screen, self.clock)
        
        # Font for non-medieval buttons
        self.font = pygame.font.SysFont(None, 48)
        
        # Initialize player and game objects
        self.player = None
        self.boss = None
        self.tutorial_completed = False
        
        # Add pause menu state
        self.paused = False

        # Add warning state
        self.show_warning = False
        self.warning_confirmed = False

# Get the correct project root (where the game folder is)
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.music_paths = {
            GameState.MAIN_MENU: get_path(os.path.join(project_root, "music", "title.mp3")),
            GameState.MAP_MENU: get_path(os.path.join(project_root, "music", "world.mp3"))
        }

        self.current_music = None

        
        
        logger.debug("Game initialized")
    
    def handle_pause_input(self):
        """Handle pause menu input with improved controller support"""
        if self.controller.is_start_pressed():
            self.controller.clear_start_press()
            if not self.show_warning:
                self.paused = not self.paused
                if self.paused:
                    self.last_selected_pos = (640, 360)  # Reset selection position
        
    def draw_styled_text(self, surface, text, center_pos, font, color, shadow_color=(0, 0, 0), shadow_offset=(2, 2)):
        """Draw bold-looking text with a shadow for depth and readability."""
        shadow = font.render(text, True, shadow_color)
        shadow_rect = shadow.get_rect(center=(center_pos[0] + shadow_offset[0], center_pos[1] + shadow_offset[1]))
        surface.blit(shadow, shadow_rect)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        surface.blit(text_surface, text_rect)

    def draw_pause_menu(self):
        """Draw the pause menu overlay with different options based on current state and controller selection"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.game_surface.blit(overlay, (0, 0))
        
        if self.show_warning:
            return self.draw_warning_menu()
        
        # Menu dimensions
        menu_width = 400
        menu_height = 300 if self.current_state != GameState.MAP_MENU else 200
        menu_x = (1280 - menu_width) // 2
        menu_y = (720 - menu_height) // 2
        
        # Draw menu background
        pygame.draw.rect(self.game_surface, self.WHITE, 
                        (menu_x, menu_y, menu_width, menu_height))
        
        # Draw "Paused" text
        self.draw_styled_text(
            self.game_surface,
            "Paused",
            (640, menu_y + 40),
            self.pixel_font,
            (182, 47, 54),  # B62F36
            (0, 0, 0)
        )

        buttons = {}
        mouse_pos = self.adjust_mouse_position(pygame.mouse.get_pos())
        
        # Continue button (always present)
        continue_rect = pygame.Rect(menu_x + 50, menu_y + 80, menu_width - 100, 50)
        is_selected = continue_rect.collidepoint(self.last_selected_pos)
        self.draw_medieval_button(continue_rect, "Continue", 
                                hover=continue_rect.collidepoint(mouse_pos),
                                selected=is_selected)
        buttons['continue'] = continue_rect
        
        if self.current_state != GameState.MAP_MENU:
            # Map Menu button (only in levels)
            map_rect = pygame.Rect(menu_x + 50, menu_y + 150, menu_width - 100, 50)
            is_selected = map_rect.collidepoint(self.last_selected_pos)
            self.draw_medieval_button(map_rect, "Return to Map", 
                                    hover=map_rect.collidepoint(mouse_pos),
                                    selected=is_selected)
            buttons['map'] = map_rect
            
            # Title Screen button
            title_rect = pygame.Rect(menu_x + 50, menu_y + 220, menu_width - 100, 50)
            is_selected = title_rect.collidepoint(self.last_selected_pos)
            self.draw_medieval_button(title_rect, "Title Screen", 
                                    hover=title_rect.collidepoint(mouse_pos),
                                    selected=is_selected)
            buttons['title'] = title_rect
        else:
            # Title Screen button (only option besides continue in map menu)
            title_rect = pygame.Rect(menu_x + 50, menu_y + 150, menu_width - 100, 50)
            is_selected = title_rect.collidepoint(self.last_selected_pos)
            self.draw_medieval_button(title_rect, "Title Screen", 
                                    hover=title_rect.collidepoint(mouse_pos),
                                    selected=is_selected)
            buttons['title'] = title_rect
        
        # Draw controller instruction if controller is connected

        
        return buttons


    def draw_warning_menu(self):
            """Draw warning message about losing progress"""
            menu_width = 400
            menu_height = 250
            menu_x = (1280 - menu_width) // 2
            menu_y = (720 - menu_height) // 2
            
            # Draw menu background
            pygame.draw.rect(self.game_surface, self.WHITE, 
                            (menu_x, menu_y, menu_width, menu_height))
            
            # Draw warning text
            warning_text = ["Warning!", 
                        "Returning to title screen will", 
                        "reset all progress.",
                        "Are you sure?"]
            
            current_y = menu_y + 40
            for line in warning_text:
                self.draw_styled_text(
                    self.game_surface,
                    line,
                    (640, current_y),
                    self.pixel_font,
                    (182, 47, 54) if line == "Warning!" else (111, 124, 144),  # B62F36 or 6F7C90
                    (0, 0, 0)
                )
                current_y += 40

            
            buttons = {}
            mouse_pos = self.adjust_mouse_position(pygame.mouse.get_pos())
            
            # Yes button
            yes_rect = pygame.Rect(menu_x + 50, menu_y + 180, (menu_width - 150) // 2, 50)
            is_selected = yes_rect.collidepoint(self.last_selected_pos)
            self.draw_medieval_button(yes_rect, "Yes", 
                                    hover=yes_rect.collidepoint(mouse_pos),
                                    selected=is_selected)
            buttons['yes'] = yes_rect
            
            # No button
            no_rect = pygame.Rect(menu_x + 100 + (menu_width - 150) // 2, menu_y + 180, (menu_width - 150) // 2, 50)
            is_selected = no_rect.collidepoint(self.last_selected_pos)
            self.draw_medieval_button(no_rect, "No", 
                                    hover=no_rect.collidepoint(mouse_pos),
                                    selected=is_selected)
            buttons['no'] = no_rect

            # Draw controller instruction if controller is connected

            
            return buttons

    def initialize_game_state(self, state):
        """Initialize the game state and create necessary objects"""
        logger.debug(f"Initializing game state: {state}")
        
        # Reset states
        self.paused = False
        if self.map:
            self.map.reset_state()
            # Clear any cooldown timers
            if hasattr(self.map, 'return_from_menu_time'):
                delattr(self.map, 'return_from_menu_time')
        
        # Clear controller states when changing states
        if self.controller:
            self.controller.check_controller_events()
            self.controller.clear_all_button_states()
        
        # Set the current state first
        self.current_state = state
        
        # Stop any existing music before playing new music
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Add this line to fully unload current music
        self.play_music(state)
        
        # Initialize player if needed
        if self.player is None:
            self.player = Player(self.screen, self.clock)
            self.player.x = 500
            self.player.y = 480
            logger.debug("Player initialized at default spawn position (500, 480)")

        try:
            # Reset boss and initialize new one based on state
            self.boss = None  # Clear existing boss
            if state == GameState.TUTORIAL:
                self.boss = Tutorial(self.screen, self.clock, self.player, self.map)
            elif state == GameState.BOSS_ONE:
                self.boss = BossOneImplementation(self.screen, self.clock, self.player, self.map)
            elif state == GameState.BOSS_THREE:
                self.boss = BossThree(self.screen, self.clock, self.player, self.map)
            elif state == GameState.BOSS_FOUR:
                self.boss = BossFourImplementation(self.screen, self.clock, self.player, self.map)
            elif state == GameState.BOSS_FIVE:
                self.boss = BossFive(self.screen, self.clock, self.player, self.map)
               # Set appropriate spawn position after boss initialization
            if state == GameState.BOSS_FIVE:
                self.player.x = 500  # Keep default X
                self.player.y = 200  # Higher platform for boss 5
            else:
                # Use default spawn position for all other levels
                self.player.x = 500
                self.player.y = 480
            
            logger.debug(f"Successfully initialized state: {state}")
        except Exception as e:
            logger.error(f"Error initializing state {state}: {e}")
            self.current_state = GameState.MAIN_MENU

    def play_music(self, state):
            """Play music for the current state"""
            # Don't change music if we're already playing the correct track
            if self.current_music == self.music_paths.get(state):
                return
                
            music_path = self.music_paths.get(state)
            if not music_path:
                logger.debug(f"No music defined for state: {state}")
                return
                
            if not os.path.exists(music_path):
                logger.error(f"Music file not found: {music_path}")
                return
                
            try:
                # Always stop and unload current music first
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                
                # Load and play new music
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.7)  # Set to 70% volume
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.current_music = music_path
                logger.debug(f"Now playing: {os.path.basename(music_path)}")
            except Exception as e:
                logger.error(f"Error playing music ({os.path.basename(music_path)}): {e}")
                self.current_music = None


    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Switch back to windowed
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        
        # Update background scale for fullscreen
        if self.is_fullscreen:
            screen_width, screen_height = self.screen.get_size()
            self.scaled_background = pygame.transform.scale(self.background, (screen_width, screen_height))
    

    def draw_button(self, rect, text, hover=False):
        """Helper function to draw buttons"""
        mouse_pos = pygame.mouse.get_pos()
        # Adjust mouse position for centered game surface in fullscreen
        if self.is_fullscreen:
            screen_width, screen_height = self.screen.get_size()
            mouse_pos = (mouse_pos[0] - (screen_width - self.SCREEN_WIDTH) // 2,
                        mouse_pos[1] - (screen_height - self.SCREEN_HEIGHT) // 2)
        
        hover = rect.collidepoint(mouse_pos)
        color = self.GRAY if hover else self.BLACK
        pygame.draw.rect(self.game_surface, color, rect)
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.game_surface.blit(text_surface, text_rect)
        return rect

    
# Add these methods to your Game class

    def draw_medieval_button(self, rect, text, surface=None, hover=False, selected=False):
        """Draw a gold-and-black button matching the map's UI style."""
        if surface is None:
            surface = self.game_surface

        # Colors
        GOLD = (255, 215, 0)
        HIGHLIGHT = (255, 165, 0) if selected else GOLD
        BG_COLOR = (0, 0, 0, 180)  # Semi-transparent black

        # Create transparent surface for button background
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        button_surface.fill(BG_COLOR)
        surface.blit(button_surface, rect.topleft)

        # Border
        pygame.draw.rect(surface, HIGHLIGHT, rect, 3)

        # Text rendering with shadow
        font = self.pixel_font
        text_surface = font.render(text, True, HIGHLIGHT)
        shadow_surface = font.render(text, True, (0, 0, 0))

        text_rect = text_surface.get_rect(center=rect.center)
        shadow_rect = text_rect.copy().move(2, 2)

        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)

        
    
    def main_menu(self):
        """Draw the main menu with only New Game button"""
        self.animated_menu.draw(self.game_surface)
        
        buttons = {}
        
        if self.animated_menu.any_key_pressed:
            center_x = 1280 // 2
            center_y = 720 // 2
            
            button_width = 300
            button_height = 70
            # Draw ornate title decoration
            line_length = 400
            
            # # Title
            # self.draw_styled_text(
            #     self.game_surface,
            #     "DUNGEON IN THE SKY",
            #     (center_x, center_y - 200),
            #     self.pixel_font,
            #     (182, 47, 54),  # B62F36
            #     (0, 0, 0)
            # )
        # pygame.draw.line(self.game_surface, (111, 124, 144),  # 6F7C90
        #                     (center_x - line_length//2, center_y - 160),
        #                     (center_x + line_length//2, center_y - 160), 3)

            
            # New Game button
            new_game_rect = pygame.Rect(
                center_x - button_width//2,
                center_y - button_height//2,
                button_width,
                button_height
            )
            
            mouse_pos = self.adjust_mouse_position(pygame.mouse.get_pos())
            
            self.draw_medieval_button(new_game_rect, "New Game",
                                    hover=new_game_rect.collidepoint(mouse_pos))
            
            buttons['new_game'] = new_game_rect
        
            return buttons



        # Modify the map_menu method to properly handle level selection:
    def map_menu(self):
        """Handle map menu state"""
        if self.current_state == GameState.MAP_MENU:
            if self.controller:
                self.controller.check_controller_events()
            
            result = self.map.run()
            if result == "quit":
                return False
            elif result == "menu":
                self.current_state = GameState.MAIN_MENU
            elif result == "pause":
                return "pause"
            elif result:  # Handle level selection
                level_map = {
                    'tutorial': GameState.TUTORIAL,
                    'boss_one': GameState.BOSS_ONE,
                    'boss_three': GameState.BOSS_THREE,
                    'boss_four': GameState.BOSS_FOUR,
                    'boss_five': GameState.BOSS_FIVE
                }
                
                if result in level_map:
                    self.last_level = result
                    new_state = level_map[result]
                    self.current_state = new_state
                    self.initialize_game_state(new_state)

        return True
                
    def reset_progress(self):
        """Reset all game progress"""
        logger.debug("Resetting game progress")
        self.player = None
        self.boss = None
        self.current_state = GameState.MAIN_MENU
        self.tutorial_completed = False
        self.last_level = None  # Reset last level tracking
        
        # Reset map progress - make sure to reset ALL level states
        if self.map:
            # Reset all levels to their initial state
            self.map.levels = {
                'tutorial': {'completed': False, 'unlocked': True, 'x': 200, 'y': 200},
                'boss_one': {'completed': False, 'unlocked': False, 'x': 650, 'y': 240},
                'boss_three': {'completed': False, 'unlocked': False, 'x': 460, 'y': 550},
                'boss_four': {'completed': False, 'unlocked': False, 'x': 890, 'y': 650},
                'boss_five': {'completed': False, 'unlocked': False, 'x': 1180, 'y': 380}
            }
            # Reset map state
            self.map.current_level = 'tutorial'
            self.map.selected_level = None
            # Reset player position to tutorial start position
            self.map.player_x = 200  # Tutorial node position
            self.map.player_y = 230  # Fixed Y position for walking
        
        # Reset animated menu state
        self.animated_menu.any_key_pressed = False
        self.animated_menu.animation_index = 0
        self.animated_menu.animation_timer = 0
        
        # Stop any playing music
        pygame.mixer.music.stop()
        
        logger.debug("Game progress reset complete")
                
    def handle_menu_controller(self):
        """Enhanced controller input handling for menus"""
        if not self.controller.is_connected():
            return

        # Get menu navigation with cooldown
        x, y = self.controller.get_menu_navigation()
        
        # Reset last_selected_pos if not set
        if not hasattr(self, 'last_selected_pos'):
            self.last_selected_pos = (640, 360)
        
        # Get current buttons based on menu state
        if self.paused:
            buttons = self.draw_pause_menu() if not self.show_warning else self.draw_warning_menu()
        elif self.current_state == GameState.MAIN_MENU and self.animated_menu.any_key_pressed:
            buttons = self.main_menu()
        else:
            buttons = None

        if not buttons:
            return

        # Convert buttons dict to list for navigation
        button_list = list(buttons.items())
        
        # If no button is currently selected, select the first one
        if not any(rect.collidepoint(self.last_selected_pos) for _, rect in button_list):
            self.last_selected_pos = button_list[0][1].center

        # Find currently selected button
        selected_index = 0
        for i, (name, rect) in enumerate(button_list):
            if rect.collidepoint(self.last_selected_pos):
                selected_index = i
                break

        # Update selection based on navigation
        if y != 0:  # Vertical navigation
            selected_index = (selected_index - y) % len(button_list)
            self.last_selected_pos = button_list[selected_index][1].center
            logger.debug(f"Selected menu option: {button_list[selected_index][0]}")

        # Handle button press (A button)
        if self.controller.is_menu_confirm():
            if self.show_warning:
                if button_list[selected_index][0] == 'yes':
                    self.reset_progress()
                    self.current_state = GameState.MAIN_MENU
                    self.paused = False
                    self.show_warning = False
                elif button_list[selected_index][0] == 'no':
                    self.show_warning = False
            elif self.paused:
                button_name = button_list[selected_index][0]
                if button_name == 'continue':
                    self.paused = False
                elif button_name == 'map':
                
                    self.current_state = GameState.MAP_MENU
                    self.paused = False
                    if hasattr(self, 'map'):
                        self.map.return_from_menu_time = pygame.time.get_ticks()

                elif button_name == 'title':
                    self.show_warning = True
            elif self.current_state == GameState.MAIN_MENU:
                if button_list[selected_index][0] == 'new_game':
                    self.reset_progress()
                    self.current_state = GameState.TUTORIAL
                    self.initialize_game_state(GameState.TUTORIAL)

        # Handle B button (cancel)
        if self.controller.is_menu_cancel():
            if self.show_warning:
                self.show_warning = False
            elif self.paused:
                self.paused = False

    def handle_events(self):
        """Updated handle_events method with fixed pause control"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time
        
        if self.current_state == GameState.MAIN_MENU:
            self.animated_menu.update(dt)
        
        # Check controller state and handle Start button for pause
        if self.controller.is_connected():
                # Handle pause toggling
                if self.controller.is_start_pressed():
                    self.controller.clear_start_press()  # Clear state immediately
                    if not self.show_warning and self.current_state in [GameState.TUTORIAL, GameState.BOSS_ONE, 
                                            GameState.BOSS_THREE, GameState.BOSS_FOUR, 
                                            GameState.BOSS_FIVE, GameState.MAP_MENU]:
                        self.paused = not self.paused
                        if self.paused:
                            self.last_selected_pos = (640, 360)  # Reset selection position


        for event in pygame.event.get():
            # Handle controller connection/disconnection
            if event.type == pygame.JOYDEVICEADDED:
                self.controller.connect_controller()
                logger.debug("Controller connected")
            elif event.type == pygame.JOYDEVICEREMOVED:
                if self.controller.controller and event.instance_id == self.controller.controller.get_instance_id():
                    self.controller = ControllerHandler()
                    logger.debug("Controller disconnected")
            
            # Handle window quit
            if event.type == pygame.QUIT:
                return False
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                # Title screen key press
                if self.current_state == GameState.MAIN_MENU and not self.animated_menu.any_key_pressed:
                    self.animated_menu.any_key_pressed = True
                    logger.debug("Key pressed in main menu - showing buttons")
                
                # Handle escape key for pause/unpause
                if event.key == pygame.K_ESCAPE:
                    if self.current_state in [GameState.TUTORIAL, GameState.BOSS_ONE, 
                                            GameState.BOSS_THREE, GameState.BOSS_FOUR, 
                                            GameState.BOSS_FIVE, GameState.MAP_MENU]:
                        if self.show_warning:
                            self.show_warning = False
                        else:
                            self.paused = not self.paused
                # Toggle fullscreen
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                # Toggle debug mode
                elif event.key == pygame.K_F3:
                    if hasattr(self.map, 'toggle_debug'):
                        self.map.toggle_debug()
            
            # Handle mouse input
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_input(event)

                # Handle controller input for menus
            if self.controller.is_connected():
                if self.current_state == GameState.MAIN_MENU and not self.animated_menu.any_key_pressed:
                    if self.controller.is_menu_confirm() or self.controller.is_menu_cancel():
                        self.animated_menu.any_key_pressed = True
                        
                if self.paused or (self.current_state == GameState.MAIN_MENU and self.animated_menu.any_key_pressed):
                    self.handle_menu_controller()
            
            # Handle map pause
            if self.current_state == GameState.MAP_MENU and not self.paused:
                if self.controller.is_start_pressed():
                    self.paused = True
                    return True
            
            # Handle controller button states
            if self.paused:
                if self.controller.is_menu_confirm():
                    selected_button = self.get_selected_button()
                    if selected_button:
                        self.handle_button_press(selected_button)
                elif self.controller.is_menu_cancel():
                    if self.show_warning:
                        self.show_warning = False
                    else:
                        self.paused = False
        
        return True

    def get_selected_button(self):
        """Helper method to get the currently selected button"""
        if self.paused:
            buttons = self.draw_pause_menu() if not self.show_warning else self.draw_warning_menu()
        elif self.current_state == GameState.MAIN_MENU and self.animated_menu.any_key_pressed:
            buttons = self.main_menu()
        else:
            return None

        if not buttons:
            return None

        for button_name, button_rect in buttons.items():
            if button_rect.collidepoint(self.last_selected_pos):
                return button_name
        
        return None


    def handle_button_press(self, button_name):
        """Helper method to handle button press actions"""
        if self.show_warning:
            if button_name == 'yes':
                self.reset_progress()
                self.current_state = GameState.MAIN_MENU
                self.paused = False
                self.show_warning = False
            elif button_name == 'no':
                self.show_warning = False
        elif self.paused:
            if button_name == 'continue':
                self.paused = False
            elif button_name == 'map':
                # Stop any playing music
                pygame.mixer.music.stop()
                
                # Update position in map
                if self.map and self.last_level in self.map.levels:
                    node_x = self.map.levels[self.last_level]['x']
                    node_y = self.map.levels[self.last_level]['y']
                    self.map.player_x = node_x - 50
                    self.map.player_y = node_y
                
                # Clear any previous level selection
                self.map.selected_level = None
                
                # Reset relevant states
                self.paused = False
                self.current_state = GameState.MAP_MENU
                
            elif button_name == 'title':
                self.show_warning = True
        elif self.current_state == GameState.MAIN_MENU:
            if button_name == 'new_game':
                self.reset_progress()
                self.current_state = GameState.TUTORIAL
                self.initialize_game_state(GameState.TUTORIAL)

    def handle_mouse_input(self, event):
        """Handle mouse input for menus"""
        mouse_pos = self.adjust_mouse_position(event.pos)
        
        if self.current_state == GameState.MAIN_MENU and not self.animated_menu.any_key_pressed:
            self.animated_menu.any_key_pressed = True
            logger.debug("Mouse clicked in main menu - showing buttons")
        
        if self.paused:
            if self.show_warning:
                buttons = self.draw_warning_menu()
                if 'yes' in buttons and buttons['yes'].collidepoint(mouse_pos):
                    self.reset_progress()
                    self.current_state = GameState.MAIN_MENU
                    self.paused = False
                    self.show_warning = False
                elif 'no' in buttons and buttons['no'].collidepoint(mouse_pos):
                    self.show_warning = False
            else:
                buttons = self.draw_pause_menu()
                if 'continue' in buttons and buttons['continue'].collidepoint(mouse_pos):
                    self.paused = False
                elif 'map' in buttons and buttons['map'].collidepoint(mouse_pos):
                    self.current_state = GameState.MAP_MENU
                    self.paused = False
                elif 'title' in buttons and buttons['title'].collidepoint(mouse_pos):
                    self.show_warning = True
        
        elif self.current_state == GameState.MAIN_MENU and self.animated_menu.any_key_pressed:
            buttons = self.main_menu()
            if buttons and 'new_game' in buttons and buttons['new_game'].collidepoint(mouse_pos):
                logger.debug("New Game button clicked")
                self.reset_progress()
                self.current_state = GameState.TUTORIAL
                self.initialize_game_state(GameState.TUTORIAL)
        
    def load_game_state(self, save_data):
        """Load a saved game state"""
        if save_data:
            logger.debug("Loading game state from save data")
            if self.player is None:
                self.player = Player(self.screen, self.clock)
            
            # Always set to default spawn position regardless of saved position
            # self.player.x = 500  # Default spawn x
            # self.player.y = 480  # Default spawn y
            
            self.player.healthbar = save_data["player"]["health"]  # Load health
            
            # Initialize game state
            new_state = save_data["game_state"]["current_boss"]
            self.initialize_game_state(new_state)
            logger.debug(f"Game state loaded: {new_state}")
            logger.debug(f"Player spawned at default position: (500, 480)")

    def get_save_data(self):
        """Get the current game state for saving"""
        return {
            "player": {
                "health": self.player.healthbar,
                # Always save default spawn position instead of current position
                "position": [500, 480]
            },
            "game_state": {
                "current_boss": self.current_state,
                "bosses_defeated": [],  # Add if you're tracking this
                "unlocked_levels": []   # Add if you're tracking this
            }
        }

    def handle_map_selection(self, direction):
        """Handle map menu selection"""
        if direction == 'left':
            self.initialize_game_state(GameState.TUTORIAL)
        elif direction == 'stay':
            self.initialize_game_state(GameState.BOSS_ONE)
        elif direction == 'right':
            self.initialize_game_state(GameState.BOSS_THREE)


# Add this method to the Game class
    def calculate_fullscreen_dimensions(self, screen_width, screen_height):
        """Calculate dimensions and position for centered gameplay in fullscreen."""
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
    
    def adjust_mouse_position(self, mouse_pos):
        """Convert screen mouse position to game surface coordinates"""
        screen_width, screen_height = self.screen.get_size()
        is_resized = screen_width != 1280 or screen_height != 720

        if is_resized:
            game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
            
            # Convert mouse position to game coordinates
            game_x = ((mouse_pos[0] - x) * 1280) // game_width
            game_y = ((mouse_pos[1] - y) * 720) // game_height
            
            return (game_x, game_y)
        return mouse_pos


    def update(self):
        """Update game state"""
        self.game_surface.fill((0, 0, 0))

        if self.current_state == GameState.MAIN_MENU:
            self.play_music(GameState.MAIN_MENU)
            self.main_menu()
        elif self.current_state == GameState.MAP_MENU:
            self.play_music(GameState.MAP_MENU)
            if not self.paused:  # Only run the map menu if not paused
                result = self.map_menu()
                if result == "pause":
                    self.paused = True
        elif self.current_state in [GameState.TUTORIAL, GameState.BOSS_ONE, GameState.BOSS_THREE, 
                                    GameState.BOSS_FOUR, GameState.BOSS_FIVE]:
            if self.boss:
                if not self.paused:
                    result = self.boss.window(self.player)
                    if result == "game_over":
                        self.reset_progress()  # This will now fully reset everything
                        self.player = None
                        self.current_state = GameState.MAIN_MENU
                        pygame.mixer.music.stop()
                    elif result == "map_menu":
                        if not self.map.levels['tutorial']['completed']:  # If tutorial isn't completed
                            # Reset to tutorial position
                            self.map.player_x = 200
                            self.map.player_y = 230
                        elif self.map and self.last_level in self.map.levels:
                            # For completed tutorial, position near the last level node
                            node_x = self.map.levels[self.last_level]['x']
                            node_y = self.map.levels[self.last_level]['y']
                            self.map.player_x = node_x - 50
                            self.map.player_y = node_y
                        
                        self.map.selected_level = None
                        self.current_state = GameState.MAP_MENU
                    elif result == "menu":
                        self.current_state = GameState.MAIN_MENU
                    elif result == "pause":
                        self.paused = True

        
        # Draw pause menu if game is paused
        if self.paused:
            self.draw_pause_menu()

        # Handle screen scaling
        screen_width, screen_height = self.screen.get_size()
        is_resized = screen_width != 1280 or screen_height != 720

        self.screen.fill(self.BLACK)

        if is_resized:
            game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
            scaled_game_surface = pygame.transform.scale(self.game_surface, (game_width, game_height))
            self.screen.blit(scaled_game_surface, (x, y))
        else:
            self.screen.blit(self.game_surface, (0, 0))

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
