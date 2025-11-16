# starter/level.py
import pygame
import random

# Lista para armazenar todas as estrelas
estrelas = []


def gerar_estrelas(largura, altura, quantidade):
    """
    Cria a lista inicial de estrelas com posições, tamanhos e velocidades aleatórias.
    """
    estrelas.clear()  # Limpa a lista caso o jogo seja reiniciado
    for _ in range(quantidade):
        x = random.randrange(0, largura)
        y = random.randrange(0, altura)

        # Escolhe um tamanho (1, 2 ou 3)
        tamanho = random.choice([1, 2, 3])

        # Define a velocidade com base no tamanho (estrelas maiores são mais rápidas)
        if tamanho == 1:
            velocidade = 1
        elif tamanho == 2:
            velocidade = 2
        else:
            velocidade = 3

        # Cria um retângulo para representar a estrela
        estrela = pygame.Rect(x, y, tamanho, tamanho)
        # Adiciona a estrela e sua velocidade à lista
        estrelas.append({'rect': estrela, 'vel': velocidade})


def desenhar_cenario(tela):
    """
    Desenha o fundo, move e desenha cada estrela para criar o efeito de paralaxe.
    """
    # Preenche o fundo com uma cor de espaço profundo
    tela.fill((10, 10, 20))

    largura_tela = tela.get_width()

    # Itera sobre cada estrela para movê-la e desenhá-la
    for estrela_info in estrelas:
        estrela_rect = estrela_info['rect']
        velocidade = estrela_info['vel']

        # Move a estrela para a esquerda
        estrela_rect.x -= velocidade

        # Se a estrela sair completamente pela esquerda, reposiciona-a na direita
        if estrela_rect.right < 0:
            estrela_rect.left = largura_tela
            estrela_rect.y = random.randrange(0, tela.get_height())  # Posição Y aleatória

        # Desenha a estrela (um pequeno quadrado branco)
        pygame.draw.rect(tela, (255, 255, 255), estrela_rect)
