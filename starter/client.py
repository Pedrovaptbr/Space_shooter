import pygame
import socket
import json
import sys
import time
from starter.player import Player
from starter.level import desenhar_cenario
from starter.bullet import Bullet
from starter.config import FPS
from starter.sound_manager import SoundManager
from starter.cursor import AnimatedCursor
from starter.logger import log

# --- CONSTANTES ---
BUFFER_SIZE = 4096

# --- FUNÇÕES DE UI ---
def draw_status(tela, mensagem, cursor):
    fonte_status = pygame.font.Font(None, 50)
    texto_render = fonte_status.render(mensagem, True, (255, 255, 255))
    rect = texto_render.get_rect(center=(tela.get_width() / 2, tela.get_height() / 2))
    
    desenhar_cenario(tela)
    tela.blit(texto_render, rect)
    cursor.update()
    cursor.draw(tela)
    pygame.display.flip()

def desenhar_hud_online(tela, meu_id, jogadores_server):
    largura_tela, altura_tela = tela.get_size()
    fonte_placar = pygame.font.Font(None, 60)
    margem, tamanho_vida, espacamento = 15, 25, 8

    p1_data = jogadores_server.get(0, {})
    p2_data = jogadores_server.get(1, {})
    vitorias_p1, vitorias_p2 = p1_data.get('vitorias', 0), p2_data.get('vitorias', 0)
    vida_p1, vida_p2 = p1_data.get('vida', 0), p2_data.get('vida', 0)

    texto_placar = f"{vitorias_p1}  -  {vitorias_p2}"
    placar_render = fonte_placar.render(texto_placar, True, (255, 255, 255))
    tela.blit(placar_render, placar_render.get_rect(center=(largura_tela / 2, 40)))

    vida_local, cor_vida = (vida_p1, (0, 150, 255)) if meu_id == 0 else (vida_p2, (255, 50, 50))
    pos_x_base = margem if meu_id == 0 else largura_tela - margem - tamanho_vida
    for i in range(vida_local):
        x_pos = pos_x_base + (i * (tamanho_vida + espacamento)) * (1 if meu_id == 0 else -1)
        pygame.draw.rect(tela, cor_vida, (x_pos, altura_tela - margem - tamanho_vida, tamanho_vida, tamanho_vida))

# --- FUNÇÃO PRINCIPAL DO JOGO ---
def main(tela, host, porta, nome_jogador):
    LARGURA_TELA, ALTURA_TELA = tela.get_size()
    pygame.display.set_caption(f"Space Shooter - {nome_jogador}")
    relogio = pygame.time.Clock()
    cursor = AnimatedCursor()
    sounds = SoundManager()
    sounds.stop_music()
    sounds.play_music_in_game()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (host, porta)
    sock.setblocking(False)

    meu_id = None
    join_request = {'action': 'join', 'name': nome_jogador}
    
    connect_start_time = time.time()
    status_message = f"Conectando a {host}:{porta}..."
    log(f"Enviando pedido de conexão para {server_address}...")
    
    while time.time() - connect_start_time < 5 and meu_id is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: log("Conexão cancelada pelo usuário."); return

        draw_status(tela, status_message, cursor)
        sock.sendto(json.dumps(join_request).encode('utf-8'), server_address)

        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            response = json.loads(data.decode('utf-8'))
            if response.get('type') == 'id_assignment':
                meu_id = response['id']
                log(f"Conexão bem-sucedida! Recebido ID: {meu_id}")
                status_message = "Conectado! Sincronizando..."
                draw_status(tela, status_message, cursor)
                time.sleep(0.5)
                break
        except (BlockingIOError, json.JSONDecodeError, UnicodeDecodeError, ConnectionResetError) as e:
            log(f"Aguardando resposta do servidor... ({type(e).__name__})")
            pass
        time.sleep(0.5)
    
    if meu_id is None:
        log("Falha ao conectar: Servidor não respondeu a tempo.")
        draw_status(tela, "Falha ao conectar. Servidor não respondeu.", cursor)
        time.sleep(2)
        return

    jogadores_sprites = {0: Player(100, ALTURA_TELA / 2, 0, "P1"), 1: Player(LARGURA_TELA - 140, ALTURA_TELA / 2, 1, "P2")}
    balas_sprites = []
    server_state = {}

    rodando = True
    while rodando:
        relogio.tick(FPS)
        actions = []
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w]: actions.append('move_up')
        if teclas[pygame.K_s]: actions.append('move_down')
        if teclas[pygame.K_a]: actions.append('move_left')
        if teclas[pygame.K_d]: actions.append('move_right')
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE): rodando = False
            if evento.type == pygame.KEYUP and evento.key == pygame.K_SPACE: actions.append('shoot'); sounds.play_shoot()
        
        sock.sendto(json.dumps(actions).encode('utf-8'), server_address)

        try:
            while True:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                try:
                    packet = json.loads(data.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                if packet.get('type') == 'game_state':
                    server_state = packet['data']
                    # JSON converte chaves int em str — converter de volta para int
                    if 'jogadores' in server_state:
                        server_state['jogadores'] = {int(k): v for k, v in server_state['jogadores'].items()}
        except (BlockingIOError, ConnectionResetError): pass

        for player_id, player_data in server_state.get('jogadores', {}).items():
            sprite = jogadores_sprites[player_id]
            sprite.nome = player_data['nome']
            if player_id == meu_id:
                sprite.rect.x += (player_data['pos'][0] - sprite.rect.x) * 0.1
                sprite.rect.y += (player_data['pos'][1] - sprite.rect.y) * 0.1
            else:
                sprite.rect.x, sprite.rect.y = player_data['pos']
            sprite.vida = player_data['vida']
        
        balas_sprites.clear()
        for bala_data in server_state.get('balas', []):
            cor = (0, 150, 255) if bala_data['owner_id'] == 0 else (255, 50, 50)
            balas_sprites.append(Bullet(bala_data['pos'][0], bala_data['pos'][1], cor))

        desenhar_cenario(tela)
        for sprite in jogadores_sprites.values(): sprite.animate(); sprite.desenhar(tela)
        for bala in balas_sprites: bala.desenhar(tela)
      