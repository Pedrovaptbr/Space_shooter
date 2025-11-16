# starter/bullet.py
import pygame

pygame.init()

class Bullet:
    def __init__(self, x, y, cor):
        """
        Inicializa o projétil.
        x, y: Posição inicial do tiro.
        cor: A cor do projétil.
        """
        self.image = pygame.Surface((15, 5))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 10
        self.mask = pygame.mask.from_surface(self.image)

    def mover(self):
        """
        Move o projétil para a direita.
        """
        self.rect.x += self.vel

    def desenhar(self, tela):
        """
        Desenha o projétil na tela.
        """
        tela.blit(self.image, self.rect)