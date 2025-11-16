import pygame
import os


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.type = powerup_type
        self.frames = []
        self.load_frames()

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))

        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100

    def load_frames(self):
        """Carrega os sprites animados do power-up."""
        path = os.path.join('starter', 'imagens', "power_up", self.type)

        num_frames = 0
        if self.type == 'vida':
            num_frames = 5
        elif self.type == 'escudo':
            num_frames = 7

        try:
            for i in range(num_frames):
                filename = f"sprite_{i}.png"
                filepath = os.path.join(path, filename)
                frame = pygame.image.load(filepath).convert_alpha()
                self.frames.append(frame)
            print(f"Frames do power-up '{self.type}' carregados com sucesso.")
        except pygame.error as e:
            print(f"--- ERRO CRÍTICO ---")
            print(f"Não foi possível carregar as imagens do power-up em: '{path}'")
            print(f"Verifique se a pasta e os arquivos de imagem (ex: vida_0.png) existem.")
            print(f"Detalhe do erro do Pygame: {e}")
            raise SystemExit

    def update(self):
        """Atualiza a animação do power-up."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def draw(self, screen):
        """Desenha o power-up na tela."""
        screen.blit(self.image, self.rect)