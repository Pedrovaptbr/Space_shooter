import pygame
import sys
import os
import subprocess
import socket
import atexit
from starter.cursor import AnimatedCursor
from starter.level import gerar_estrelas, desenhar_cenario
from starter.settings_menu import settings_main, carregar_settings
from starter.sound_manager import SoundManager
from starter import client as client_game
from starter.local_game import local_game_main
from starter.logger import log

# --- Gerenciamento do Servidor ---
server_process = None
def cleanup_server():
    global server_process
    if server_process and server_process.poll() is None:
        log("Encerrando processo do servidor...")
        server_process.terminate()
        server_process.wait()
atexit.register(cleanup_server)

def run_server():
    global server_process
    if server_process is None or server_process.poll() is not None:
        log("Iniciando processo do servidor...")
        server_path = os.path.join(os.path.dirname(__file__), 'starter', 'server.py')
        if sys.platform == "win32":
            server_process = subprocess.Popen([sys.executable, server_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            server_process = subprocess.Popen(['x-terminal-emulator', '-e', sys.executable, server_path])
        
        size = pygame.display.get_surface().get_size()
        flags = pygame.display.get_surface().get_flags()
        pygame.display.iconify()
        pygame.display.set_mode(size, flags, 32)

def get_local_ip():
    # Esta função ainda é útil para exibir o IP para outros jogadores
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except socket.error:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

# --- FUNÇÃO DO MENU ONLINE ---
def online_menu(tela, sounds):
    global server_process
    largura_tela, altura_tela = tela.get_size()
    cursor = AnimatedCursor()
    fonte_titulo = pygame.font.Font(None, 100)
    fonte_botao = pygame.font.Font(None, 60)
    fonte_label = pygame.font.Font(None, 40)
    fonte_input = pygame.font.Font(None, 50)
    fonte_status = pygame.font.Font(None, 45)
    branco, cinza, azul, verde = (255,255,255), (150,150,150), (0,150,255), (0,200,0)

    server_ip_display = get_local_ip() if server_process else ''
    active_field = None
    input_fields = {
        'host': {'label': 'IP do Servidor:', 'text': '127.0.0.1', 'rect': pygame.Rect(largura_tela/2 - 250, 350, 500, 50)},
        'port': {'label': 'Porta:', 'text': '5555', 'rect': pygame.Rect(largura_tela/2 - 250, 460, 240, 50)},
        'name': {'label': 'Seu Nome:', 'text': 'Jogador', 'rect': pygame.Rect(largura_tela/2 + 10, 460, 240, 50)}
    }
    btn_criar_servidor = pygame.Rect(largura_tela/2 - 250, 200, 500, 60)
    btn_conectar = pygame.Rect(largura_tela/2 - 150, 560, 300, 60)
    btn_voltar = pygame.Rect(largura_tela/2 - 100, 670, 200, 50)

    rodando = True
    while rodando:
        if server_process and server_process.poll() is not None:
            log("Processo do servidor foi encerrado externamente.")
            server_process = None

        mouse_pos = pygame.mouse.get_pos()
        desenhar_cenario(tela)
        titulo_texto = fonte_titulo.render("Modo Online", True, branco)
        tela.blit(titulo_texto, titulo_texto.get_rect(center=(largura_tela / 2, 100)))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_voltar.collidepoint(mouse_pos):
                    rodando = False
                elif btn_criar_servidor.collidepoint(mouse_pos) and server_process is None:
                    run_server()
                    server_ip_display = get_local_ip()
                    # --- CORREÇÃO LÓGICA ---
                    # Ao criar o servidor, o IP para se conectar é sempre 127.0.0.1
                    input_fields['host']['text'] = '127.0.0.1'
                    log(f"Servidor criado. IP de rede para outros: {server_ip_display}. IP de conexão local: 127.0.0.1")
                elif btn_conectar.collidepoint(mouse_pos):
                    try:
                        host = input_fields['host']['text']
                        porta = int(input_fields['port']['text'])
                        nome = input_fields['name']['text']
                        log(f"Tentando conectar a {host}:{porta} como '{nome}'")
                        client_game.main(tela, host, porta, nome)
                        sounds.play_music_menu()
                    except ValueError:
                        log("Erro de conexão: Porta inválida.")
                        input_fields['port']['text'] = ''
                active_field = None
                for name, field in input_fields.items():
                    if field['rect'].collidepoint(mouse_pos):
                        active_field = name; break
            if evento.type == pygame.KEYDOWN and active_field:
                if evento.key == pygame.K_BACKSPACE:
                    input_fields[active_field]['text'] = input_fields[active_field]['text'][:-1]
                else:
                    input_fields[active_field]['text'] += evento.unicode

        if server_process is None:
            pygame.draw.rect(tela, azul, btn_criar_servidor)
            texto_btn = fonte_botao.render("Criar Servidor", True, branco)
        else:
            pygame.draw.rect(tela, cinza, btn_criar_servidor)
            texto_btn = fonte_status.render(f"Servidor rodando em: {server_ip_display}", True, verde)
        tela.blit(texto_btn, texto_btn.get_rect(center=btn_criar_servidor.center))

        for name, field in input_fields.items():
            label_render = fonte_label.render(field['label'], True, cinza)
            tela.blit(label_render, (field['rect'].x, field['rect'].y - 30))
            cor_borda = azul if active_field == name else branco
            pygame.draw.rect(tela, cor_borda, field['rect'], 2)
            text_surface = fonte_input.render(field['text'], True, branco)
            tela.blit(text_surface, (field['rect'].x + 10, field['rect'].y + 10))

        pygame.draw.rect(tela, verde, btn_conectar)
        texto_conectar = fonte_botao.render("Conectar", True, branco)
        tela.blit(texto_conectar, texto_conectar.get_rect(center=btn_conectar.center))
        pygame.draw.rect(tela, cinza, btn_voltar)
        texto_voltar = fonte_label.render("Voltar", True, branco)
        tela.blit(texto_voltar, texto_voltar.get_rect(center=btn_voltar.center))
        
        cursor.update()
        cursor.draw(tela)
        pygame.display.flip()
    
    cleanup_server()

# --- FUNÇÃO DO MENU PRINCIPAL ---
def main_menu():
    settings = carregar_settings()
    resolucao = tuple(settings.get('resolucao', (1280, 720)))
    tela_cheia = settings.get('tela_cheia', True)
    
    pygame.init()
    pygame.mixer.init()
    
    flags = 0
    if tela_cheia:
        flags = pygame.FULLSCREEN
    tela = pygame.display.set_mode(resolucao, flags, 32)
    
    largura_tela, altura_tela = tela.get_size()
    pygame.display.set_caption("Space Shooter")

    sounds = SoundManager()
    sounds.play_music_menu()

    pygame.mouse.set_visible(False)  # usamos AnimatedCursor; evita cursor duplo do SO
    cursor = AnimatedCursor()
    gerar_estrelas(largura_tela, altura_tela, 200)
    
    fonte_titulo = pygame.font.Font(None, 120)
    fonte_botao = pygame.font.Font(None, 74)
    branco, cinza = (255, 255, 255), (150, 150, 150)
    titulo_texto = fonte_titulo.render("Space Shooter", True, branco)
    titulo_rect = titulo_texto.get_rect(center=(largura_tela / 2, altura_tela * 0.2))

    botoes = {
        'online': {'texto': "Jogar Online", 'rect': None, 'cor': branco},
        'local': {'texto': "2 Jogadores (Local)", 'rect': None, 'cor': branco},
        'settings': {'texto': "Configurações", 'rect': None, 'cor': branco},
        'sair': {'texto': "Sair", 'rect': None, 'cor': branco},
    }
    
    y_positions = [0.45, 0.60, 0.75, 0.90]
    keys = ['online', 'local', 'settings', 'sair']
    for i, key in enumerate(keys):
        botoes[key]['rect'] = fonte_botao.render(botoes[key]['texto'], True, branco).get_rect(center=(largura_tela / 2, altura_tela * y_positions[i]))

    rodando = True
    while rodando:
        mouse_pos = pygame.mouse.get_pos()
        desenhar_cenario(tela)
        tela.blit(titulo_texto, titulo_rect)

        for nome, botao in botoes.items():
            botao['cor'] = cinza if botao['rect'].collidepoint(mouse_pos) else branco
            texto_render = fonte_botao.render(botao['texto'], True, botao['cor'])
            tela.blit(texto_render, botao['rect'])

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botoes['online']['rect'].collidepoint(mouse_pos):
                    online_menu(tela, sounds)
                    sounds.play_music_menu()
                elif botoes['local']['rect'].collidepoint(mouse_pos):
                    local_game_main()
                    sounds.play_music_menu()
                elif botoes['settings']['rect'].collidepoint(mouse_pos):
                    settings_main(tela)
                    sounds.play_music_menu()
                elif botoes['sair']['rect'].collid