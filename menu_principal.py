# menu_principal.py
import pygame
import sys
import subprocess
import math
import threading

from starter.server import main as iniciar_servidor
from starter.client import main as iniciar_cliente
from starter.sound_manager import SoundManager
from starter.level import desenhar_cenario, gerar_estrelas
from starter.cursor import AnimatedCursor

# --- Configurações Iniciais ---
pygame.init()
pygame.mixer.init()

LARGURA_TELA = 1280
ALTURA_TELA = 720
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)

pygame.display.set_caption("Space Shooter - Menu")
clock = pygame.time.Clock()
FPS = 60

# --- Cores e Fontes ---
COR_FUNDO = (20, 20, 20)
COR_TEXTO = (255, 255, 255)
COR_DESTAQUE = (0, 255, 0)
COR_INPUT_ATIVO = (100, 249, 237)
COR_INPUT_INATIVO = (100, 149, 237)
fonte_titulo = pygame.font.Font(None, 100)
fonte_botao = pygame.font.Font(None, 70)
fonte_input = pygame.font.Font(None, 50)
fonte_media = pygame.font.Font(None, 74)


# --- Classes de UI ---
class Botao:
    def __init__(self, texto, pos, fonte):
        self.texto_str = texto
        self.fonte = fonte
        self.cor = COR_TEXTO
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.pos = pos

    def desenhar(self, tela_surface):
        brilho = int(150 + (math.sin(pygame.time.get_ticks() * 0.005) * 105))
        cor_final = (brilho, brilho, brilho) if self.cor == COR_DESTAQUE else self.cor
        texto_renderizado = self.fonte.render(self.texto_str, True, cor_final)
        self.rect = texto_renderizado.get_rect(center=self.pos)
        tela_surface.blit(texto_renderizado, self.rect)

    def verificar_hover(self, mouse_pos):
        self.cor = COR_DESTAQUE if self.rect.collidepoint(mouse_pos) else COR_TEXTO


class CaixaInput:
    def __init__(self, label, pos, texto_inicial="", largura=400):
        self.label_str = label
        self.texto = texto_inicial
        self.pos = pos
        self.largura = largura
        self.ativo = False
        self.rect = pygame.Rect(0, 0, 0, 0)

    def desenhar(self, tela_surface):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.largura, 50)
        label_renderizado = fonte_input.render(self.label_str, True, COR_TEXTO)
        tela_surface.blit(label_renderizado, (self.rect.x, self.rect.y - 40))
        cor_caixa = COR_INPUT_ATIVO if self.ativo else COR_INPUT_INATIVO
        pygame.draw.rect(tela_surface, cor_caixa, self.rect, 2)
        texto_renderizado = fonte_input.render(self.texto, True, COR_TEXTO)
        tela_surface.blit(texto_renderizado, (self.rect.x + 10, self.rect.y + 10))

    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.rect.collidepoint(evento.pos)
        if evento.type == pygame.KEYDOWN and self.ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            else:
                if len(self.texto) < 40:
                    self.texto += evento.unicode


# --- Funções dos Menus ---
def menu_principal(sounds, cursor):
    global tela, LARGURA_TELA, ALTURA_TELA
    titulo = fonte_titulo.render("Space Shooter", True, COR_TEXTO)
    botoes = [
        Botao("Jogar", (LARGURA_TELA // 2, ALTURA_TELA // 2 - 100), fonte_botao),
        Botao("Configurações", (LARGURA_TELA // 2, ALTURA_TELA // 2), fonte_botao),
        Botao("Sair", (LARGURA_TELA // 2, ALTURA_TELA // 2 + 100), fonte_botao)
    ]
    while True:
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        desenhar_cenario(tela)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 4)))
        for botao in botoes:
            botao.verificar_hover(mouse_pos)
            botao.desenhar(tela)
        cursor.draw(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return "sair_final"
            if evento.type == pygame.VIDEORESIZE:
                LARGURA_TELA, ALTURA_TELA = evento.size
                tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botoes[0].rect.collidepoint(mouse_pos): return "jogar"
                if botoes[1].rect.collidepoint(mouse_pos): return "configuracoes"
                if botoes[2].rect.collidepoint(mouse_pos): return "sair_final"
        pygame.display.update()
        clock.tick(FPS)


def menu_jogar(sounds, cursor):
    global tela, LARGURA_TELA, ALTURA_TELA
    botoes = [
        Botao("Hospedar Jogo", (LARGURA_TELA // 2, ALTURA_TELA // 2 - 100), fonte_botao),
        Botao("Entrar em Jogo", (LARGURA_TELA // 2, ALTURA_TELA // 2), fonte_botao),
        Botao("Voltar", (LARGURA_TELA // 2, ALTURA_TELA // 2 + 100), fonte_botao)
    ]
    while True:
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        desenhar_cenario(tela)
        for botao in botoes:
            botao.verificar_hover(mouse_pos)
            botao.desenhar(tela)
        cursor.draw(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                LARGURA_TELA, ALTURA_TELA = evento.size
                tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botoes[0].rect.collidepoint(mouse_pos): return "hospedar"
                if botoes[1].rect.collidepoint(mouse_pos): return "entrar"
                if botoes[2].rect.collidepoint(mouse_pos): return "principal"
        pygame.display.update()
        clock.tick(FPS)


def menu_configuracoes(sounds, cursor):
    global tela, LARGURA_TELA, ALTURA_TELA
    botoes = [
        Botao(f"Música: {'Ligada' if sounds.music_on else 'Desligada'}", (LARGURA_TELA // 2, ALTURA_TELA // 2 - 100),
              fonte_botao),
        Botao(f"Efeitos: {'Ligados' if sounds.effects_on else 'Desligados'}", (LARGURA_TELA // 2, ALTURA_TELA // 2),
              fonte_botao),
        Botao("Voltar", (LARGURA_TELA // 2, ALTURA_TELA - 150), fonte_botao)
    ]
    while True:
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        desenhar_cenario(tela)

        botoes[0].texto_str = f"Música: {'Ligada' if sounds.music_on else 'Desligada'}"
        botoes[1].texto_str = f"Efeitos: {'Ligados' if sounds.effects_on else 'Desligados'}"

        for botao in botoes:
            botao.verificar_hover(mouse_pos)
            botao.desenhar(tela)
        cursor.draw(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                LARGURA_TELA, ALTURA_TELA = evento.size
                tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botoes[0].rect.collidepoint(mouse_pos):
                    sounds.toggle_music()
                    if sounds.music_on: sounds.play_music_in_menu()
                if botoes[1].rect.collidepoint(mouse_pos):
                    sounds.toggle_effects()
                if botoes[2].rect.collidepoint(mouse_pos): return "principal"
        pygame.display.update()
        clock.tick(FPS)


def menu_configuracao_rede(tipo, cursor):
    global tela, LARGURA_TELA, ALTURA_TELA
    titulo_str = "Hospedar Jogo" if tipo == "hospedar" else "Entrar em Jogo"
    titulo = fonte_titulo.render(titulo_str, True, COR_TEXTO)

    y_topo = ALTURA_TELA // 4
    y_centro = ALTURA_TELA // 2
    x_esquerda = LARGURA_TELA // 4 - 200
    x_direita = LARGURA_TELA * 3 // 4 - 200
    x_centro = LARGURA_TELA // 2 - 200

    elementos = []
    if tipo == "hospedar":
        input_nome = CaixaInput("Seu Nome:", (x_direita, y_topo), "Anfitrião")
        input_porta = CaixaInput("Porta:", (x_esquerda, y_topo), "5000")
        elementos = [input_nome, input_porta]
    else:
        input_nome = CaixaInput("Seu Nome:", (x_direita, y_topo), "Jogador")
        input_porta = CaixaInput("Porta:", (x_esquerda, y_topo), "5000")
        input_ip = CaixaInput("IP do Servidor:", (x_centro, y_centro), "127.0.0.1")
        elementos = [input_nome, input_porta, input_ip]

    botoes = [
        Botao("Iniciar", (LARGURA_TELA // 2, ALTURA_TELA - 200), fonte_botao),
        Botao("Voltar", (LARGURA_TELA // 2, ALTURA_TELA - 100), fonte_botao)
    ]
    while True:
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        desenhar_cenario(tela)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, 100)))
        for elem in elementos: elem.desenhar(tela)
        for botao in botoes: botao.verificar_hover(mouse_pos); botao.desenhar(tela)
        cursor.draw(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                LARGURA_TELA, ALTURA_TELA = evento.size
                tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
            for elem in elementos: elem.tratar_evento(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botoes[0].rect.collidepoint(mouse_pos):
                    nome = elementos[0].texto or "Jogador"
                    porta = elementos[1].texto
                    ip = "127.0.0.1" if tipo == "hospedar" else elementos[2].texto
                    return ip, porta, nome
                if botoes[1].rect.collidepoint(mouse_pos): return None, None, None
        pygame.display.update()
        clock.tick(FPS)

# --- Loop Principal do Menu ---
if __name__ == "__main__":
    sounds = SoundManager()
    cursor = AnimatedCursor()
    gerar_estrelas(LARGURA_TELA, ALTURA_TELA, 200)

    estado_menu = "principal"
    while estado_menu != "sair_final":
        if not pygame.mixer.music.get_busy() and sounds.music_on:
            sounds.play_music_in_menu()

        if estado_menu == "principal":
            estado_menu = menu_principal(sounds, cursor)
        elif estado_menu == "jogar":
            estado_menu = menu_jogar(sounds, cursor)
        elif estado_menu == "configuracoes":
            estado_menu = menu_configuracoes(sounds, cursor)
        elif estado_menu == "hospedar":
            ip_cliente, porta_str, nome_jogador = menu_configuracao_rede("hospedar", cursor)
            if ip_cliente is not None:
                try:
                    porta_int = int(porta_str)
                    servidor_thread = threading.Thread(target=iniciar_servidor, args=(porta_int,), daemon=True)
                    servidor_thread.start()
                    pygame.time.wait(1000)
                    sounds.stop_music()
                    iniciar_cliente(ip_cliente, porta_int, nome_jogador)
                    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
                except Exception as e:
                    print(f"Erro ao hospedar o jogo: {e}")
                estado_menu = "jogar"
            else:
                estado_menu = "jogar"
        elif estado_menu == "entrar":
            ip_cliente, porta_str, nome_jogador = menu_configuracao_rede("entrar", cursor)
            if ip_cliente is not None:
                try:
                    porta_int = int(porta_str)
                    sounds.stop_music()
                    iniciar_cliente(ip_cliente, porta_int, nome_jogador)
                    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
                except Exception as e:
                    print(f"Erro ao entrar no jogo: {e}")
                estado_menu = "jogar"
            else:
                estado_menu = "jogar"

    pygame.quit()
    sys.exit()