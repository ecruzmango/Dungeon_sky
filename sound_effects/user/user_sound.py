import os
import pygame
from headers.utils import get_path
class SoundManager:
    def __init__(self):
        # Get the absolute path to the project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sounds = {}
        self._load_sounds()
    
    def _load_sounds(self):
        
        # Load all sound effects using absolute paths
        self.sounds['jump'] = pygame.mixer.Sound(get_path(os.path.join('sound_board', 'button_1_click.wav')))
        self.sounds['damage'] = pygame.mixer.Sound(get_path(os.path.join('sound_board', 'user_damage.wav')))
        self.sounds['damage'].set_volume(.6)
        self.sounds['woosh'] = pygame.mixer.Sound(get_path(os.path.join('sound_board', 'sword_woosh.wav')))
        self.sounds['dash'] = pygame.mixer.Sound(get_path(os.path.join('sound_board', 'dash.wav')))
        self.sounds['dash'].set_volume(1.5)
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()