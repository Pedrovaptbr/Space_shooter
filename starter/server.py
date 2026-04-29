import socket
import json
import select
import sys
import time
import os
from starter.logger import log

# --- CONFIGURAÇÕES DO SERVIDOR ---
PORT = 5555
HOST = '0.0.0.0'
MAX_JOGADORES = 2
BUFFER_SIZE = 4096
TICK_RATE = 60
TICK_INTERVAL = 1.0 / TICK_RATE

# --- LÓGICA DE JOGO NO SERVIDOR ---
PLAYER_SPEED = 5
BULLET_SPEED = 15
LARGURA_TELA, ALTURA_TELA = 1280, 720
PLAYER_W, PLAYER_H = 70, 70
BULLET_W, BULLET_H = 15, 5


def aabb_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    """Colisão AABB simples — evita depender de pygame no servidor."""
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def aplicar_acao(player, action, player_id, balas):
    """Aplica uma ação de input no estado do jogador. Retorna a nova bala se for tiro, senão None."""
    px, py = player['pos']
    if action == 'move_up':
        player['pos'] = (px, max(0, py - PLAYER_SPEED))
    elif action == 'move_down':
        player['pos'] = (px, min(ALTURA_TELA - PLAYER_H, py + PLAYER_SPEED))
    elif action == 'move_left':
        player['pos'] = (max(0, px - PLAYER_SPEED), py)
    elif action == 'move_right':
        player['pos'] = (min(LARGURA_TELA - PLAYER_W, px + PLAYER_SPEED), py)
    elif action == 'shoot':
        direction = 1 if player_id == 0 else -1
        bullet_pos = (player['pos'][0] + (35 * direction), player['pos'][1] + 35)
        balas.append({'pos': bullet_pos, 'owner_id': player_id, 'dir': direction})


def avancar_balas(balas):
    """Move balas e descarta as que saíram da tela. Retorna a lista filtrada."""
    sobreviventes = []
    for bala in balas:
        bx, by = bala['pos']
        bx += BULLET_SPEED * bala['dir']
        bala['pos'] = (bx, by)
        if 0 < bx < LARGURA_TELA:
            sobreviventes.append(bala)
    return sobreviventes


def processar_colisoes(balas, jogadores):
    """Aplica dano e remove balas que atingiram um jogador inimigo. Retorna a nova lista de balas."""
    sobreviventes = []
    for bala in balas:
        atingiu = False
        for player_id, player in jogadores.items():
            if bala['owner_id'] == player_id:
                continue
            px, py = player['pos']
            bx, by = bala['pos']
            if aabb_overlap(px, py, PLAYER_W, PLAYER_H, bx, by, BULLET_W, BULLET_H):
                player['vida'] -= 1
                log(f"Jogador {player_id} ({player['nome']}) atingido! Vida: {player['vida']}")
                atingiu = True
                break
        if not atingiu:
            sobreviventes.append(bala)
    return sobreviventes


def main():
    global PORT
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            log(f"Porta inválida em argv ('{sys.argv[1]}'). Usando padrão {PORT}.")

    if sys.platform == "win32":
        os.system(f"title Space Shooter - Servidor Autoritativo (Porta: {PORT})")

    log("========================================")
    log("  INICIANDO SERVIDOR AUTORITATIVO UDP")
    log("========================================")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    # NOTE: socket continua não-bloqueante para drenar a fila de uma vez
    sock.setblocking(False)

    log(f"Servidor ouvindo em {HOST}:{PORT}.")

    game_state = {'jogadores': {}, 'balas': []}
    clients = {}
    player_inputs = {}
    next_player_id = 0
    next_tick = time.time() + TICK_INTERVAL

    try:
        while True:
            # 1) Espera por pacote OU pelo deadline do próximo tick — sem busy-wait
            timeout = max(0.0, next_tick - time.time())
            ready, _, _ = select.select([sock], [], [], timeout)

            # 2) Drena tudo que chegou neste momento
            if ready:
                while True:
                    try:
                        data, addr = sock.recvfrom(BUFFER_SIZE)
                    except BlockingIOError:
                        break

                    try:
                        request = json.loads(data.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        log(f"Recebido pacote malformado de {addr}. Ignorando.")
                        continue

                    if addr not in clients:
                        if (len(clients) < MAX_JOGADORES
                                and isinstance(request, dict)
                                and request.get('action') == 'join'):
                            player_id = next_player_id
                            player_name = request.get('name', f'Jogador {player_id + 1}')

                            clients[addr] = player_id
                            game_state['jogadores'][player_id] = {
                                'pos': (100 if player_id == 0 else LARGURA_TELA - 140, ALTURA_TELA / 2),
                                'vida': 3, 'vitorias': 0, 'escudo': False, 'conectado': True,
                                'nome': player_name
                            }
                            player_inputs[player_id] = []
                            log(f"Novo cliente {addr} conectado como Jogador {player_id} (Nome: {player_name}).")
                            next_player_id += 1

                            id_packet = json.dumps({'type': 'id_assignment', 'id': player_id}).encode('utf-8')
                            sock.sendto(id_packet, addr)
                        else:
                            log(f"Pedido de conexão de {addr} recusado (Servidor cheio ou pedido inválido).")
                        continue

                    player_id = clients[addr]
                    if isinstance(request, list):
                        player_inputs[player_id] = request

            # 3) Tick (só quando o deadline chega)
            now = time.time()
            if now < next_tick:
                continue
            # Mantém cadência mesmo se o tick atrasar
            next_tick = max(now, next_tick + TICK_INTERVAL)

            # Aplica inputs
            for player_id, actions in player_inputs.items():
                player = game_state['jogadores'][player_id]
                for action in actions:
                    aplicar_acao(player, action, player_id, game_state['balas'])
                player_inputs[player_id] = []

            # Avança balas e processa colisões
            game_state['balas'] = avancar_balas(game_state['balas'])
            game_state['balas'] = processar_colisoes(game_state['balas'], game_state['jogadores'])

            # Broadcast do estado
            state_packet = json.dumps({
                'type': 'game_state',
                'data': game_state,
                'timestamp': now
            }).encode('utf-8')
            for addr in clients.keys():
                sock.sendto(state_packet, addr)

    except KeyboardInterrupt:
        log("Servidor encerrando via KeyboardInterrupt.")
    finally:
        sock.close()
        log("Socket do servidor fechado.")


if __name__ == "__main__":
    main()
