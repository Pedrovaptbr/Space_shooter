# starter/sound_manager.py
import pygame
import json
import os


class SoundManager:
    def __init__(self):
        """
        Inicializa o gestor de sons, carregando os efeitos e as configurações.
        """
        self.settings_file = "starter/settings.json"
        self.load_settings()

        try:
            # Carrega os efeitos sonoros
            self.shoot_sound = pygame.mixer.Sound("starter/sounds/shoot.mp3")
            self.shield_sound = pygame.mixer.Sound("starter/sounds/shield.mp3")
            self.hit_sound = pygame.mixer.Sound("starter/sounds/hit.mp3")
            self.victory_sound = pygame.mixer.Sound("starter/sounds/victory.mp3")
            self.death_sound = pygame.mixer.Sound("starter/sounds/death.mp3")

            # Ajusta o volume dos sons (0.0 a 1.0)
            self.set_effects_volume(self.effects_volume)

            print("Efeitos sonoros carregados com sucesso.")
            self.sounds_loaded = True
        except pygame.error as e:
            print(f"Erro ao carregar os efeitos sonoros: {e}")
            self.sounds_loaded = False

    def load_settings(self):
        """Carrega as configurações de um arquivo JSON."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.music_on = settings.get("music_on", True)
                self.effects_on = settings.get("effects_on", True)
                self.music_volume = settings.get("music_volume", 0.4)
                self.effects_volume = settings.get("effects_volume", 0.5)
        else:
            # Valores padrão se o arquivo não existir
            self.music_on = True
            self.effects_on = True
            self.music_volume = 0.4
            self.effects_volume = 0.5
            self.save_settings()

    def save_settings(self):
        """Guarda as configurações atuais no arquivo JSON."""
        settings = {
            "music_on": self.music_on,
            "effects_on": self.effects_on,
            "music_volume": self.music_volume,
            "effects_volume": self.effects_volume
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def toggle_music(self):
        """Ativa ou desativa a música."""
        self.music_on = not self.music_on
        if not self.music_on:
            pygame.mixer.music.stop()
        self.save_settings()

    def toggle_effects(self):
        """Ativa ou desativa os efeitos sonoros."""
        self.effects_on = not self.effects_on
        self.save_settings()

    def set_music_volume(self, volume):
        """Define o volume da música (0.0 a 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        self.save_settings()

    def set_effects_volume(self, volume):
        """Define o volume de todos os efeitos sonoros."""
        self.effects_volume = max(0.0, min(1.0, volume))
        if hasattr(self, 'shoot_sound'):  # Verifica se os sons foram carregados
            self.shoot_sound.set_volume(self.effects_volume)
            self.shield_sound.set_volume(self.effects_volume)
            self.hit_sound.set_volume(self.effects_volume)
            self.victory_sound.set_volume(self.effects_volume)
            self.death_sound.set_volume(self.effects_volume)
        self.save_settings()

    # --- Métodos para tocar os sons ---

    def play_shoot(self):
        if self.sounds_loaded and self.effects_on:
            self.shoot_sound.play()

    def play_shield(self):
        if self.sounds_loaded and self.effects_on:
            self.shield_sound.play()

    def play_hit(self):
        if self.sounds_loaded and self.effects_on:
            self.hit_sound.play()

    def play_victory(self):
        if self.sounds_loaded and self.effects_on:
            pygame.mixer.music.stop()
            self.victory_sound.play()

    def play_death(self):
        if self.sounds_loaded and self.effects_on:
            pygame.mixer.music.stop()
            self.death_sound.play()

    def play_music_in_menu(self):
        if self.sounds_loaded and self.music_on:
            if not pygame.mixer.music.get_busy() or "musica_menu" not in pygame.mixer.music.get_pos.__doc__:
                try:
                    pygame.mixer.music.load("starter/sounds/musica_menu.mp3")
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)
                except pygame.error as e:
                    print(f"Erro ao carregar a música do menu: {e}")

    def play_music_in_game(self):
        if self.sounds_loaded and self.music_on:
            try:
                pygame.mixer.music.load("starter/sounds/musica_jogo.mp3")
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"Erro ao carregar a música do jogo: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
