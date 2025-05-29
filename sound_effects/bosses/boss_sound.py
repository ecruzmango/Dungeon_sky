import os
import pygame
from pygame import mixer
import wave
import audioop

class SoundManager:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # print(f"Project root: {self.project_root}")
        self.sounds = {}
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)
        self._load_sounds()
    
    def _trim_wave_file(self, input_path, output_path, start_sec, end_sec):
        """Trim a wave file to specified start and end times in seconds."""
        # print(f"Attempting to open: {input_path}")
        with wave.open(input_path, 'rb') as wave_file:
            params = wave_file.getparams()
            framerate = wave_file.getframerate()
            start_frame = int(start_sec * framerate)
            end_frame = int(end_sec * framerate)
            wave_file.setpos(start_frame)
            frames = wave_file.readframes(end_frame - start_frame)
            
            with wave.open(output_path, 'wb') as outfile:
                outfile.setparams(params)
                outfile.setnframes(end_frame - start_frame)
                outfile.writeframes(frames)

    def _amplify_wave_file(self, input_path, output_path, boost_factor=8):
        """Amplify the volume of a wave file."""
        with wave.open(input_path, 'rb') as wave_file:
            params = wave_file.getparams()
            frames = wave_file.readframes(wave_file.getnframes())
            amplified_frames = audioop.mul(frames, wave_file.getsampwidth(), boost_factor)
            
            with wave.open(output_path, 'wb') as outfile:
                outfile.setparams(params)
                outfile.writeframes(amplified_frames)

    def _load_sounds(self):
        temp_dir = os.path.join(self.project_root, 'temp_audio')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Process duck sound
        duck_path = os.path.join(self.project_root, 'bosses', 'Duck_quack.wav')
        trimmed_duck_path = os.path.join(temp_dir, 'trimmed_duck.wav')
        self._trim_wave_file(duck_path, trimmed_duck_path, 15, 18)
        self.sounds['duck'] = pygame.mixer.Sound(trimmed_duck_path)
        self.sounds['duck'].set_volume(0.5)

        # Process frog sound
        frog_path = os.path.join(self.project_root, 'bosses', 'FrogSound.wav')
        trimmed_frog_path = os.path.join(temp_dir, 'trimmed_frog.wav')
        if not os.path.exists(frog_path):
            raise FileNotFoundError(f"Could not find audio file at: {frog_path}")
        self._trim_wave_file(frog_path, trimmed_frog_path, 1, 2)
        self.sounds['frog'] = pygame.mixer.Sound(trimmed_frog_path)
        self.sounds['frog'].set_volume(0.5)

        # Process jump sound with amplification
        jump_path = os.path.join(self.project_root, 'bosses', 'FrogJumps.wav')
        amplified_jump_path = os.path.join(temp_dir, 'amplified_jump.wav')
        self._amplify_wave_file(jump_path, amplified_jump_path, boost_factor=8)
        self.sounds['jump'] = pygame.mixer.Sound(amplified_jump_path)
        self.sounds['jump'].set_volume(1.0)

        # Process hit sound
        hit_path = os.path.join(self.project_root, 'bosses', 'Hit.wav')
        self.sounds['hit'] = pygame.mixer.Sound(hit_path)
        self.sounds['hit'].set_volume(0.5)

        #! BOSS four
        
        slam_path = os.path.join(self.project_root, 'bosses', 'GroundSlam.wav')
        trimmed_slam_path = os.path.join(temp_dir, 'trimmed_GroundSlam.wav')
        amplified_slam_path = os.path.join(temp_dir, 'amplified_GroundSlam.wav')

        # first trim
        self._trim_wave_file(slam_path, trimmed_slam_path, 3, 5)

        self._amplify_wave_file(slam_path, amplified_slam_path, boost_factor=8)
        self.sounds['slam'] = pygame.mixer.Sound(amplified_slam_path)

        self.sounds['slam'].set_volume(1)        

        # process raven sound 
        raven_path = os.path.join(self.project_root, 'bosses', 'raven.wav')
        self.sounds['raven'] = pygame.mixer.Sound(raven_path)

        # process magic
        magic_path = os.path.join(self.project_root, 'bosses', 'magic.wav')
        self.sounds['magic'] = pygame.mixer.Sound(magic_path)
        
        magic_path = os.path.join(self.project_root, 'bosses', 'witch_laugh.wav')
        self.sounds['WL'] = pygame.mixer.Sound(magic_path)

        #! FInal boss:

        intro_path = os.path.join(self.project_root, 'bosses', 'audio_intro.wav')
        self.sounds['Intro'] = pygame.mixer.Sound(intro_path)

        party_path = os.path.join(self.project_root, 'bosses', 'party_horn.wav')
        self.sounds['party'] = pygame.mixer.Sound(party_path)

        beam_path = os.path.join(self.project_root, 'bosses', 'beam.wav')
        self.sounds['beam'] = pygame.mixer.Sound(beam_path)
        self.sounds['beam'].set_volume(.5)

        clown_laugh_path = os.path.join(self.project_root, 'bosses', 'clown_laughing.wav')
        self.sounds['clown_laugh'] = pygame.mixer.Sound(clown_laugh_path)
        self.sounds['clown_laugh'].set_volume(1)

        thunder_path = os.path.join(self.project_root, 'bosses', 'thunder.wav')
        # print(f"Loading thunder sound from: {thunder_path}")  # Debug print
        self.sounds['thunder'] = pygame.mixer.Sound(thunder_path)
        self.sounds['thunder'].set_volume(1.9)

        
        slam_path = os.path.join(self.project_root, 'bosses', 'slam.wav')
        self.sounds['slam'] = pygame.mixer.Sound(slam_path)

        slam_path = os.path.join(self.project_root, 'bosses', 'bounce.wav')
        self.sounds['bounce'] = pygame.mixer.Sound(slam_path)

        




    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()