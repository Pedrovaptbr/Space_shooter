import pygame
import json
import os

# --- Caminho Base para Recursos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')
ROOT_DIR = os.path.join(BASE_DIR, '..') # Acessa a pasta raiz do projeto
SETTINGS_FILE = os.path.join(ROOT_DIR, 'settings.json')

def carregar_settings():
    """Carrega as configurações de forma segura."""
    defaults = {'volume_musica': 0.5, 'volume_sfx': 0.5, 'resolucao': [1280, 720]}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                defaults.update(settings)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return defaults

class SoundManager:
    def __init__(self):
        self.sounds_loaded = False
        self._current_track = None  # 'menu' | 'in_game' | None — evita recarregar a mesma faixa
        self.settings = carregar_settings()
        self.volume_musica = self.settings.get('volume_musica', 0.5)
        self.volume_sfx = self.settings.get('volume_sfx', 0.5)

        try:
            # Usa caminhos absolutos para carregar os sons
            self.shoot_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "shoot.mp3"))
            self.shield_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "shield.mp3"))
            self.hit_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "hit.mp3"))
            self.victory_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "victory.mp3"))
            self.death_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "death.mp3"))
            
            self.sounds_loaded = True
            print("Efeitos sonoros carregados com sucesso.")
            
            self.set_sfx_volume(self.volume_sfx)
            pygame.mixer.music.set_volume(self.volume_musica)
            
        except pygame.error as e:
            print(f"Erro ao carregar os efeitos sonoros: {e}")
            self.sounds_loaded = False

    def set_sfx_volume(self, volume):
        if self.sounds_loaded:
            self.shoot_sound.set_volume(volume)
            self.shield_sound.set_volume(volume)
            self.hit_sound.set_volume(volume)
            self.victory_sound.set_volume(volume)
            self.death_sound.set_volume(volume)

    def play_shoot(self):
        if self.sounds_loaded: self.shoot_sound.play()

    def play_shield(self):
        if self.sounds_loaded: self.shield_sound.play()

    def play_hit(self):
        if self.sounds_loaded: self.hit_sound.play()

    def play_victory(self):
        if self.sounds_loaded:
            pygame.mixer.music.stop()
            self.victory_sound.play()

    def play_death(self):
        if self.sounds_loaded:
            pygame.mixer.music.stop()
            self.death_sound.play()

    def play_music_menu(self):
        """Toca a música do menu em loop. Idempotente: se já estiver tocando, não reinicia."""
        if not self.sounds_loaded:
            return
        if self._current_track == 'menu' and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "musica_menu.mp3"))
            pygame.mixer.music.set_volume(self.volume_musica)
            pygame.mixer.music.play(-1)
            self._current_track = 'menu'
        except pygame.error as e:
            print(f"Erro ao carregar a música do menu: {e}")

    def play_music_in_game(self):
        """Toca a música do jogo em loop. Idempotente: se já estiver tocando, não reinicia."""
        if not self.sounds_loaded:
            return
        if self._current_track == 'in_game' and pygame.mixer.music.get_b