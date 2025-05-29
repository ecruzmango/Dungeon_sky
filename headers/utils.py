# headers/utils.py
import os
import sys
import pygame

def get_path(relative_path):
    """Return full path to resource, supports PyInstaller and dev mode."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# headers/utils.py
def load_sprite_frames(path, num_frames, frame_width, frame_height):
    frames = []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        for i in range(num_frames):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA).convert_alpha()
            frame.blit(sheet, (0, 0), rect)
            frames.append(frame)
    except Exception as e:
        print(f"[ERROR] Failed to load sprite sheet: {e}")
    return frames
