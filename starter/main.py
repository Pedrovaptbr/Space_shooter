import pygame
from config import *
from player import Player
from level import desenhar_cenario

def main():

    print("Servidor iniciando...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((HOST, PORT))
    except OSError as e:
        print(f"ERRO AO INICIAR O SERVIDOR: {e}")
        print(f"A porta {PORT} pode já estar em uso. Verifique seus processos ou aguarde um minuto.")
        return

    s.listen(2)
    print(f"Servidor ouvindo na porta {PORT}")

    jogador_id = 0
    while jogador_id < 2:
        conn, addr = s.accept()
        print(f"Conectado a: {addr}")
        threading.Thread(target=tratar_cliente, args=(conn, jogador_id)).start()
        jogador_id += 1

    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Multiplayer Starter")
    relogio = pygame.time.Clock()

    jogador1 = Player(100, 100, (0, 200, 255))
    jogador2 = Player(200, 100, (255, 100, 0))

    rodando = True
    while rodando:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        teclas = pygame.key.get_pressed()
        jogador1.mover(teclas, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        jogador2.mover(teclas, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        desenhar_cenario(tela)
        jogador1.desenhar(tela)
        jogador2.desenhar(tela)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
