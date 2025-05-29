import sys
import os
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from boss_four import BossFourImplementation
from headers.classes import Player


def run_boss():
    # Initialize Pygame
    pygame.init()
    # Screen dimensions
    width = 1280
    height = 720

    # Create the screen object
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    # Set up a basic clock for FPS control
    clock = pygame.time.Clock()


    # Initialize the player
    player = Player(screen, clock)  # Use your player class

    boss_name = "Boss4"
    boss = BossFourImplementation(screen, clock)

    # Animation timer for witch
    animation = pygame.USEREVENT
    pygame.time.set_timer(animation, 100) # 10 times per second
    count = 0

    # State variables
    exit = False

    # Boss coords
    boss_x = width/2 - 160
    boss_y = height - 320

    broom_x = boss_x + 200
    broom_y = boss_y - 75
    broom_dir = 'left'

    while True:
        # screen.fill((62, 66, 75))
        screen.blit(boss.bg, (0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
            if event.type == animation:
                count += 1

                if count % 100 == 0:
                    boss.boss_state = "punch"
                elif count % 50 == 0:
                    boss.boss_state = "throw"
                else:
                    boss.boss_state = "walk"
                 
        if exit:
            break
        
        keys = pygame.key.get_pressed()
        # Update player movement
        player.move(keys, boss.platforms, boss.hazards)

        # Draw the player based on its state
        if player.is_jumping:
            frame_to_blit = player.animate(player.jump_animation_frames)
        elif player.is_dashing:
            frame_to_blit = player.animate(player.dash_animation_frames, is_dash=True)
        elif player.current_action == 'attack':
            frame_to_blit = player.animate(player.attack_animation_frames)
        elif player.is_falling:
            frame_to_blit = player.animate(player.fall_animation_frames)
        elif keys[pygame.K_a] or keys[pygame.K_d]:  # Walking left or right
            frame_to_blit = player.animate(player.walk_animation_frames)
        else:  # Idle
            frame_to_blit = player.animate(player.idle_animation_frames)

        # Blit player animation frame to screen
        screen.blit(frame_to_blit, (player.x, player.y))

        # Get boss animation
        if boss.boss_state == 'walk':
            # Update boss position
            boss_x, boss_y = boss.update_pos(boss_x, boss_y, width)
            screen.blit(boss.walk[count % 28], (boss_x, boss_y))
            screen.blit(boss.magic[count % 12], (boss_x, boss_y))
        elif boss.boss_state == 'throw':
            screen.blit(boss.throw[count % 18], (boss_x, boss_y))
        elif boss.boss_state == 'punch':
            screen.blit(boss.punch[count % 34], (boss_x, boss_y))

        # Update broom position
        broom_x, broom_y, broom_dir = boss.broom_pos(broom_x, broom_y, width, broom_dir)
        # Blit broom to screen
        screen.blit(boss.broom[count % 5], (broom_x, broom_y))

        if boss_x == player.x:
            boss.boss_state = 'throw'
            player.take_damage(20)
        
        # if boss:  # Ensure the boss is initialized
        #     result = boss.window(player)  # Pass the player to the boss window
        # if result == "Pass":
        #     return "Pass " + boss_name
        # Update the display
        pygame.display.update()
        
        # Control the frame rate
        clock.tick(60)

run_boss()