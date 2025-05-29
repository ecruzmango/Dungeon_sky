import sys
import os
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from boss_one import BossOneImplementation
from boss_three.boss_three import BossThree

sys.path.append(os.path.join(os.path.dirname(__file__), 'boss_five'))
from boss_five.boss_five import BossFive

from tutorial.tutorial import Tutorial
from headers.classes import Player
from boss_four.boss_class import BossFourImplementation
from save_system.save import SaveSystem
from save_system.save_menu import SaveLoadMenu

# Initialize Pygame
pygame.init()


# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

# Initialize save system
save_system = SaveSystem()
save_load_menu = SaveLoadMenu(screen, save_system)


# Define game states
STATE_MENU = "menu"
STATE_BOSS1 = "boss1"
STATE_BOSS3 = "boss3"
STATE_BOSS4 = "boss4"
STATE_BOSS5 = "boss5"
STATE_TUTORIAL = "tutorial"
game_state = STATE_MENU  # Start at the menu

# Set up a basic clock for FPS control
clock = pygame.time.Clock()

# Create an instance of the boss (initialized later when transitioning to the boss level)
boss = None

# Initialize the player
player = Player(screen, clock)

def map_menu():
    screen.fill(WHITE)
    
    
    font = pygame.font.SysFont(None, 48) 
    title_text = font.render("Select a Boss Level", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, 100))
    
    # Display options (buttons for boss levels)
    boss1_button = pygame.Rect(150, 300, 200, 50)
    boss3_button = pygame.Rect(450, 300, 200, 50)
    boss5_button = pygame.Rect(750, 300, 200, 50)
    boss4_button = pygame.Rect(750, 600, 200, 50)
    tutorial_button = pygame.Rect(970, 300, 200, 50)  # Changed from text surface to Rect
    
    pygame.draw.rect(screen, BLACK, boss1_button)
    pygame.draw.rect(screen, BLACK, boss3_button)
    pygame.draw.rect(screen, BLACK, boss4_button)
    pygame.draw.rect(screen, BLACK, boss5_button)
    pygame.draw.rect(screen, BLACK, tutorial_button)
    
    boss1_text = font.render("Boss 1", True, WHITE)
    boss3_text = font.render("Boss 3", True, WHITE)
    boss4_text = font.render("Boss 4", True, WHITE)
    boss5_text = font.render("Boss 5", True, WHITE)
    tutorial_text = font.render("Tutorial", True, WHITE)  # Changed variable name to tutorial_text
    
    screen.blit(boss1_text, (170, 310))
    screen.blit(boss3_text, (470, 310))
    screen.blit(boss4_text, (770, 610))
    screen.blit(boss5_text, (770, 310))
    screen.blit(tutorial_text, (990, 310))  # Using tutorial_text here

    # Return all button Rect objects
    return boss1_button, boss3_button, boss4_button, boss5_button, tutorial_button

# Main game loop
while True:
    # Get all events once at the start of each frame
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle keyboard shortcuts for save/load
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:  # Changed from K_0 to K_F5
                save_load_menu.show_menu('save')
            elif event.key == pygame.K_F9:
                save_load_menu.show_menu('load')

        # Handle mouse click in the menu
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == STATE_MENU:
                mouse_pos = pygame.mouse.get_pos()
                boss1_button, boss3_button, boss4_button, boss5_button, tutorial_button = map_menu()

                if boss1_button.collidepoint(mouse_pos):
                    game_state = STATE_BOSS1
                    boss = BossOneImplementation(screen, clock, player)
                elif boss3_button.collidepoint(mouse_pos):
                    game_state = STATE_BOSS3
                    boss = BossThree(screen, clock, player)
                elif boss4_button.collidepoint(mouse_pos):
                    game_state = STATE_BOSS4
                    boss = BossFourImplementation(screen, clock, player)
                elif boss5_button.collidepoint(mouse_pos):
                    game_state = STATE_BOSS5
                    boss = BossFive(screen, clock, player)
                elif tutorial_button.collidepoint(mouse_pos):
                    game_state = STATE_TUTORIAL
                    boss = Tutorial(screen, clock, player)
            
            # Handle save/load menu clicks
            elif save_load_menu.active:
                buttons = save_load_menu.show_menu(save_load_menu.mode)
                result = save_load_menu.handle_click(
                    pygame.mouse.get_pos(), 
                    buttons, 
                    player, 
                    game_state
                )
                if result:
                    if result.get("success"):
                        if save_load_menu.mode == 'load' and result.get("save_data"):
                            save_data = result["save_data"]
                            player.rect.x = save_data["player"]["position"][0]
                            player.rect.y = save_data["player"]["position"][1]
                            if hasattr(player, "health"):
                                player.health = save_data["player"]["health"]
                            game_state = save_data["game_state"]["current_boss"]

        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    # Update the game screen based on the current game state
    if game_state == STATE_MENU:
        map_menu()
    elif game_state in [STATE_BOSS1, STATE_BOSS3, STATE_BOSS5, STATE_BOSS4, STATE_TUTORIAL]:
        if boss:
            boss.window(player)

    # Draw save/load menu if active
    if save_load_menu.active:
        save_load_menu.show_menu(save_load_menu.mode)

    # Update the display
    pygame.display.flip()
    
    # Control the frame rate
    clock.tick(60)