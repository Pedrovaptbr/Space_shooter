# starter/player.py
import pygame
import os
from starter.bullet import Bullet


class Player:
    def __init__(self, x, y, player_id, nome="Jogador"):
        self.id = player_id
        self.nome = nome
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel = 5
        self.cor = (0, 200, 255) if self.id == 0 else (255, 100, 0)
        self.bullets = []
        self.escudo_ativo = False
        self.vida = 3
        self.fonte_nome = pygame.font.Font(None, 24)

        self.frames = []
        self.load_frames()

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.mask = pygame.mask.from_surface(self.image)

        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 80



    def mover(self, teclas, cima, baixo, esquerda, direita, largura_tela, altura_tela):
        if teclas[cima]: self.rect.y -= self.vel
        if teclas[baixo]: self.rect.y += self.vel
        if teclas[esquerda]: self.rect.x -= self.vel
        if teclas[direita]: self.rect.x += self.vel

        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > altura_tela: self.rect.bottom = altura_tela

        meio_da_tela = largura_tela / 2
        if self.id == 0:
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > meio_da_tela: self.rect.right = meio_da_tela
        else:
            if self.rect.left < meio_da_tela: self.rect.left = meio_da_tela
            if self.rect.right > largura_tela: self.rect.right = largura_tela

    def atirar(self):
        if self.id == 0:
            novo_tiro = Bullet(self.rect.centerx, self.rect.centery, (0, 150, 255))
        else:
            novo_tiro = Bullet(self.rect.centerx, self.rect.centery, (255, 0, 0))
            novo_tiro.vel *= -1
        self.bullets.append(novo_tiro)
    def load_frames(self):
        """Carrega os 5 frames da animação da nave correta (azul ou vermelha)."""
        ship_color = "nave_azul" if self.id == 0 else "nave_vermelha"
        path = os.path.join('starter', 'imagens', 'naves', ship_color)

        try:
            for i in range(5):  # Carrega os 5 sprites
                filename = f"sprite_{i}.png"
                filepath = os.path.join(path, filename)
                frame = pygame.image.load(filepath).convert_alpha()
                frame = pygame.transform.scale(frame, (70, 70))
                self.frames.append(frame)
            print(f"Animação da '{ship_color}' carregada com sucesso.")
        except pygame.error as e:
            print(
                f"--- ERRO --- Não foi possível carregar a animação da nave em '{path}'. Verifique o caminho e os nomes dos arquivos.")
            fallback_surface = pygame.Surface((40, 40))
            color = (0, 200, 255) if self.id == 0 else (255, 100, 0)
            fallback_surface.fill(color)
            self.frames.append(fallback_surface)

    def animate(self):
        """Atualiza o frame da animação da nave."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

            self.mask = pygame.mask.from_surface(self.image)

    def desenhar(self, tela):
        tela.blit(self.image, self.rect)

        if self.escudo_ativo:
            superficie_escudo = pygame.Surface((self.rect.width * 2, self.rect.height * 2), pygame.SRCALPHA)
            pygame.draw.circle(superficie_escudo, (0, 255, 0, 100), superficie_escudo.get_rect().center,
                               self.rect.width * 0.8)
            pos_x = self.rect.centerx - self.rect.width
            pos_y = self.rect.centery - self.rect.height
            tela.blit(superficie_escudo, (pos_x, pos_y))

        # Desenha o nome do jogador
        texto_nome = self.fonte_nome.render(self.nome, True, (255, 255, 255))
        pos_texto = texto_nome.get_rect(center=(self.rect.centerx, self.rect.top - 15))
        tela.blit(texto_nome, pos_texto)

        for tiro in self.bullets:
            tiro.desenhar(tela)
