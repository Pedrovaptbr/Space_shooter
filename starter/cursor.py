# starter/cursor.py
import pygame
import os


class AnimatedCursor:
    def __init__(self):
        """
        Inicializa e carrega os frames para a animação do cursor.
        """
        self.frames = []
        self.frame_atual = 0
        self.velocidade_animacao = 100 # Troca de frame a cada 10 ciclos
        self.contador_animacao = 0
        self.carregado = False

        numero_de_frames = 3  # Altere para o número de imagens que você tem

        try:
            for i in range(numero_de_frames):
                nome_arquivo = f"cursor{i}.png"
                caminho = os.path.join("starter/imagens/cursor", nome_arquivo)
                imagem = pygame.image.load(caminho).convert_alpha()
                self.frames.append(imagem)

            pygame.mouse.set_visible(False)
            self.carregado = True
            print("Cursor animado carregado com sucesso.")
        except pygame.error as e:
            print(f"Erro ao carregar os frames do cursor: {e}")
            print("Verifique se a pasta 'imagens' existe na raiz do projeto e contém os arquivos 'cursorX.png'.")
            pygame.mouse.set_visible(True)  # Mostra o cursor do sistema se o personalizado falhar

    def update(self):
        """
        Avança o frame da animação do cursor.
        """
        if not self.carregado:
            return

        self.contador_animacao += 1
        if self.contador_animacao >= self.velocidade_animacao:
            self.contador_animacao = 0
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)

    def draw(self, tela):
        """
        Desenha o frame atual do cursor na posição do rato.
        """
        if not self.carregado:
            return

        imagem_do_cursor_atual = self.frames[self.frame_atual]
        posicao_mouse = pygame.mouse.get_pos()
        cursor_rect = imagem_do_cursor_atual.get_rect(center=posicao_mouse)
        tela.blit(imagem_do_cursor_atual, cursor_rect)
