import pygame
import os
import sys

class EndSequence:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.frames = []
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 200  # milliseconds

        self.game_surface = pygame.Surface((1280, 720))  # Add this for proper fullscreen scaling

        self.load_assets()
        self.play_music()

    def load_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        end_path = os.path.join(base_path, "assets", "menu", "end.png")
        sprite_sheet = pygame.image.load(end_path).convert()
        for i in range(10):
            frame = sprite_sheet.subsurface((i * 1280, 0, 1280, 720))
            self.frames.append(frame)

    def play_music(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(base_path, "music", "end.mp3")
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Couldn't play ending music.")

    def calculate_fullscreen_dimensions(self, screen_width, screen_height):
        """Calculate the dimensions and position for centered gameplay in fullscreen."""
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

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            # Update animation frame
            self.frame_timer += self.clock.tick(60)
            if self.frame_timer >= self.frame_duration:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.frame_timer = 0

            # Clear game surface and draw frame
            self.game_surface.fill((0, 0, 0))
            self.game_surface.blit(self.frames[self.frame_index], (0, 0))

            # Handle fullscreen drawing
            screen_width, screen_height = self.screen.get_size()
            is_fullscreen = screen_width != 1280 or screen_height != 720
            self.screen.fill((0, 0, 0))  # Pillarbox background

            if is_fullscreen:
                game_width, game_height, x, y = self.calculate_fullscreen_dimensions(screen_width, screen_height)
                scaled_surface = pygame.transform.scale(self.game_surface, (game_width, game_height))
                self.screen.blit(scaled_surface, (x, y))
            else:
                self.screen.blit(self.game_surface, (0, 0))

            pygame.display.flip()

        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()
