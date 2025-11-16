import socket
import threading
import pickle
import sys

try:
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
except (IndexError, ValueError):
    PORT = 5000

HOST = '0.0.0.0'

jogadores = {
    0: {'pos': (0, 0), 'bullets': [], 'escudo': False, 'vida': 3, 'conectado': False, 'vitorias': 0,
        'nome': 'Esperando...'},
    1: {'pos': (0, 0), 'bullets': [], 'escudo': False, 'vida': 3, 'conectado': False, 'vitorias': 0,
        'nome': 'Esperando...'}
}


def tratar_cliente(conn, jogador_id):
    global jogadores
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    jogadores[jogador_id]['conectado'] = True
    print(f"Enviando ID {jogador_id} para o cliente.")
    try:
        conn.send(pickle.dumps(jogador_id))
        conn.send(pickle.dumps(jogadores[jogador_id]))
    except (ConnectionResetError, BrokenPipeError):
        print(f"Falha ao enviar dados iniciais para o Jogador {jogador_id}.")
        jogadores[jogador_id]['conectado'] = False
        conn.close()
        return

    while True:
        try:
            dados = pickle.loads(conn.recv(2048))
            dados['conectado'] = True
            jogadores[jogador_id] = dados
            # A lógica de 'hit_power_up' é removida daqui
            conn.sendall(pickle.dumps(jogadores))
        except (ConnectionResetError, EOFError, pickle.UnpicklingError, BrokenPipeError):
            break

    print(f"Jogador {jogador_id} desconectado.")
    jogadores[jogador_id] = {'pos': (0, 0), 'bullets': [], 'escudo': False, 'vida': 3, 'conectado': False,
                             'vitorias': 0, 'nome': 'Desconectado'}
    conn.close()


def main(porta=PORT):
    print("Servidor iniciando...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, porta))
    except OSError as e:
        print(f"ERRO AO INICIAR O SERVIDOR NA PORTA {porta}: {e}")
        return

    s.listen(2)
    print(f"Servidor ouvindo na porta {porta}")

    # A thread de 'gerenciar_powerups' é removida daqui
    threads = []
    jogador_id_atual = 0
    while jogador_id_atual < 2:
        try:
            conn, addr = s.accept()
            print(f"Conectado a: {addr}")
            thread = threading.Thread(target=tratar_cliente, args=(conn, jogador_id_atual))
            thread.start()
            threads.append(thread)
            jogador_id_atual += 1
        except OSError:
            break

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()