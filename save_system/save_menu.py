import pygame
import logging
import os

logger = logging.getLogger(__name__)
class SaveLoadMenu:
    def __init__(self, screen, save_system):
        self.screen = screen
        self.save_system = save_system
        self.game_surface = pygame.Surface((1280, 720))  # Original game resolution
        self.font = pygame.font.SysFont(None, 36)
        self.active = False
        self.mode = None
        
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)

        # Load background
        self.load_menu_bg = pygame.image.load(os.path.join("assets", "menu", "load_menu.png")).convert_alpha()
        logger.debug("SaveLoadMenu initialized")

    def calculate_fullscreen_dimensions(self, screen_width, screen_height):
        """Calculate dimensions for proper scaling."""
        game_aspect_ratio = 1280 / 720
        screen_aspect_ratio = screen_width / screen_height
        
        if screen_aspect_ratio > game_aspect_ratio:
            game_height = screen_height
            game_width = int(game_height * game_aspect_ratio)
        else:
            game_width = screen_width
            game_height = int(game_width / game_aspect_ratio)
        
        x = (screen_width - game_width) // 2
        y = (screen_height - game_height) // 2
        
        return game_width, game_height, x, y

    def draw_button(self, rect, text, surface=None, hover=False):
        """Draw a button with text"""
        color = self.GRAY if hover else self.BLACK
        pygame.draw.rect(surface or self.game_surface, color, rect)
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        (surface or self.game_surface).blit(text_surface, text_rect)
        
    def show_menu(self, mode='save'):
        """Display the save/load menu"""
        logger.debug(f"Showing menu in {mode} mode")
        self.active = True
        self.mode = mode
        
        # Clear game surface
        self.game_surface.fill(self.BLACK)
        
        # Scale background to game surface size
        scaled_bg = pygame.transform.scale(self.load_menu_bg, (1280, 720))
        self.game_surface.blit(scaled_bg, (0, 0))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.game_surface.blit(overlay, (0, 0))
        
        # Create menu area in original coordinates
        menu_width = 400
        menu_height = 500
        menu_x = (1280 - menu_width) // 2
        menu_y = (720 - menu_height) // 2

        # Draw menu background with some transparency
        menu_bg = pygame.Surface((menu_width, menu_height))
        menu_bg.fill(self.WHITE)
        menu_bg.set_alpha(230)
        self.game_surface.blit(menu_bg, (menu_x, menu_y))
        
        # Draw menu background
        pygame.draw.rect(self.game_surface, self.WHITE, 
                        (menu_x, menu_y, menu_width, menu_height))
        
        # Draw title
        title = f"{'Save' if mode == 'save' else 'Load'} Game"
        title_surface = self.font.render(title, True, self.BLACK)
        self.game_surface.blit(title_surface, 
                            (menu_x + (menu_width - title_surface.get_width()) // 2, 
                             menu_y + 20))
        
        # Draw slot buttons
        buttons = []
        saves = self.save_system.list_saves()
        logger.debug(f"Available saves: {saves}")
        
        for i in range(3):  # 3 save slots
            save_info = next((s for s in saves if s["slot"] == i + 1), None)
            
            button_rect = pygame.Rect(menu_x + 50, 
                                    menu_y + 100 + (i * 80), 
                                    menu_width - 100, 
                                    60)
            
            text = f"Slot {i + 1} - {save_info['timestamp']}" if save_info else f"Empty Slot {i + 1}"
            self.draw_button(button_rect, text)
            buttons.append((button_rect, i + 1))
        
        # Draw back button
        back_button = pygame.Rect(menu_x + 50, 
                                menu_y + menu_height - 80, 
                                menu_width - 100, 
                                60)
        self.draw_button(back_button, "Back")
        buttons.append((back_button, "back"))

        # Scale and draw to screen
        screen_width, screen_height = self.screen.get_size()
        is_resized = screen_width != 1280 or screen_height != 720

        # Clear the main screen
        self.screen.fill(self.BLACK)

        if is_resized:
            game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
            scaled_surface = pygame.transform.scale(self.game_surface, (game_width, game_height))
            self.screen.blit(scaled_surface, (x, y))
        else:
            self.screen.blit(self.game_surface, (0, 0))
        
        return buttons

    def handle_click(self, pos, buttons, player, current_state):
        """Handle mouse clicks with proper coordinate conversion"""
        screen_width, screen_height = self.screen.get_size()
        is_resized = screen_width != 1280 or screen_height != 720
        
        if is_resized:
            # Convert click position to original coordinates
            game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
            scale_x = 1280 / game_width
            scale_y = 720 / game_height
            adjusted_pos = (
                (pos[0] - x) * scale_x,
                (pos[1] - y) * scale_y
            )
        else:
            adjusted_pos = pos
            
        for button, value in buttons:
            if button.collidepoint(adjusted_pos):
                if value == "back":
                    self.active = False
                    return None
                
                if self.mode == 'save':
                    success, message = self.save_system.save_game(player, current_state, value)
                    return {"success": success, "message": message}
                else:
                    success, message, save_data = self.save_system.load_game(value)
                    return {"success": success, "message": message, "save_data": save_data}
        return None