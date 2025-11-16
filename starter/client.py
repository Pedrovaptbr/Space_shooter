# --- IMPORTAÇÕES ---
import pygame
import socket
import pickle
import sys
import random
from starter.player import Player
from starter.level import desenhar_cenario, gerar_estrelas
from starter.bullet import Bullet
from starter.config import FPS
from starter.sound_manager import SoundManager
from starter.cursor import AnimatedCursor
from starter.powerup import PowerUp

# --- CONSTANTES GLOBAIS ---
LARGURA_JANELA, ALTURA_JANELA = 1280, 720


# --- FUNÇÕES AUXILIARES DE UI (INTERFACE DO USUÁRIO) ---
def desenhar_barra_de_poder(tela, poder_atual, poder_maximo, largura_tela, altura_tela):
    largura_total = largura_tela / 3
    pos_x = (largura_tela - largura_total) / 2
    pos_y = altura_tela - 30
    altura_barra = 20
    largura_atual = (poder_atual / poder_maximo) * largura_total
    pygame.draw.rect(tela, (50, 50, 50), (pos_x, pos_y, largura_total, altura_barra))
    if largura_atual > 0:
        pygame.draw.rect(tela, (0, 128, 255), (pos_x, pos_y, largura_atual, altura_barra))


def desenhar_hud(tela, vida, municao, vitorias_p0, vitorias_p1, largura_tela, altura_tela):
    margem = 15
    tamanho_vida = 25
    largura_municao = 30
    altura_municao = 12
    espacamento = 8

    y_pos_vida = altura_tela - margem - tamanho_vida
    for i in range(vida):
        pos_x = margem + (i * (tamanho_vida + espacamento))
        pygame.draw.rect(tela, (255, 0, 0), (pos_x, y_pos_vida, tamanho_vida, tamanho_vida))
        pygame.draw.rect(tela, (150, 0, 0), (pos_x, y_pos_vida, tamanho_vida, tamanho_vida), 2)

    y_pos_municao = altura_tela - margem - altura_municao
    for i in range(municao):
        pos_x = largura_tela - margem - (i * (largura_municao + espacamento)) - largura_municao
        pygame.draw.rect(tela, (255, 255, 0), (pos_x, y_pos_municao, largura_municao, altura_municao))
        pygame.draw.rect(tela, (150, 150, 0), (pos_x, y_pos_municao, largura_municao, altura_municao), 2)

    fonte_placar = pygame.font.Font(None, 60)
    texto_placar = f"{vitorias_p0}  -  {vitorias_p1}"
    placar_render = fonte_placar.render(texto_placar, True, (255, 255, 255))
    placar_rect = placar_render.get_rect(center=(largura_tela / 2, 40))
    tela.blit(placar_render, placar_rect)


def desenhar_botao_sair(tela):
    botao_rect = pygame.Rect(15, 15, 40, 40)
    pygame.draw.rect(tela, (200, 0, 0), botao_rect)
    pygame.draw.line(tela, (255, 255, 255), (20, 20), (50, 50), 4)
    pygame.draw.line(tela, (255, 255, 255), (50, 20), (20, 50), 4)
    return botao_rect


# --- FUNÇÃO DE CONEXÃO ---
def conectar(host, porta):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.connect((host, porta))
    return s


# --- FUNÇÃO PRINCIPAL DO JOGO ---
def main(host, porta, nome_jogador):
    # --- INICIALIZAÇÃO DO PYGAME E TELA ---
    pygame.init()
    pygame.mixer.init()
    info_tela = pygame.display.Info()
    LARGURA_TELA, ALTURA_TELA = info_tela.current_w, info_tela.current_h
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.FULLSCREEN)
    em_tela_cheia = True
    pygame.display.set_caption(f"Cliente Multiplayer - Conectado a {host}:{porta}")
    relogio = pygame.time.Clock()

    # --- CARREGAMENTO DE FONTES E ASSETS ---
    fonte_grande = pygame.font.Font(None, 100)
    fonte_media = pygame.font.Font(None, 74)
    fonte_espera = pygame.font.Font(None, 50)
    cursor = AnimatedCursor()
    gerar_estrelas(LARGURA_TELA, ALTURA_TELA, 200)
    sounds = SoundManager()
    sounds.play_music_in_game()

    # --- VARIÁVEIS DE ESTADO DO JOGO ---
    municao = 3
    poder_maximo = 100
    poder_atual = poder_maximo
    tempo_ativacao_escudo = 0
    outro_conectado = False
    vitorias_jogador = 0
    vitorias_outro = 0
    confirmando_saida = False
    power_up_ativo = None
    cronometro_powerup_iniciado = False
    tempo_referencia_powerup = 0
    INTERVALO_POWERUP = 15000
    fim_de_round = False
    tempo_fim_round = 0
    mensagem_round = ""
    fim_de_partida = False
    rodando = True
    mensagem_fim_jogo = ""
    botao_sair_rect = pygame.Rect(0, 0, 0, 0)
    botao_sim_rect = pygame.Rect(0, 0, 0, 0)
    botao_nao_rect = pygame.Rect(0, 0, 0, 0)
    botao_novo_round_rect = pygame.Rect(0, 0, 0, 0)
    botao_voltar_menu_rect = pygame.Rect(0, 0, 0, 0)

    # --- CONEXÃO COM O SERVIDOR ---
    try:
        conn = conectar(host, porta)
    except (ConnectionRefusedError, socket.gaierror):
        print(f"Erro: Não foi possível conectar ao servidor em {host}:{porta}.")
        tela.fill((20, 20, 20))
        texto_erro = fonte_grande.render("Servidor não encontrado", True, (255, 0, 0))
        tela.blit(texto_erro, texto_erro.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2)))
        pygame.display.flip()
        pygame.time.wait(3000)
        return

    # --- CONFIGURAÇÃO INICIAL DOS JOGADORES ---
    meu_id = pickle.loads(conn.recv(2048))
    print(f"Você é o Jogador {meu_id}")
    _ = pickle.loads(conn.recv(2048))
    id_outro = 1 if meu_id == 0 else 0
    jogador = Player(0, 0, meu_id, nome_jogador)
    outro = Player(0, 0, id_outro, "Oponente")

    # --- FUNÇÃO PARA RESETAR O ROUND ---
    def resetar_round():
        nonlocal poder_atual, municao, fim_de_round, mensagem_round
        poder_atual = poder_maximo
        municao = 3
        jogador.vida = 3
        jogador.bullets.clear()
        outro.bullets.clear()
        if meu_id == 0:
            jogador.rect.topleft = (100, ALTURA_TELA / 2)
        else:
            jogador.rect.topleft = (LARGURA_TELA - 100 - 40, ALTURA_TELA / 2)
        fim_de_round = False
        mensagem_round = ""

    resetar_round()

    # --- LOOP PRINCIPAL DO JOGO ---
    while rodando:
        # --- ATUALIZAÇÕES GERAIS A CADA FRAME ---
        relogio.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        jogador.animate()
        if outro_conectado:
            outro.animate()

        # --- TRATAMENTO DE EVENTOS (INPUTS DO USUÁRIO) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if confirmando_saida:
                    if botao_sim_rect.collidepoint(mouse_pos):
                        rodando = False
                    if botao_nao_rect.collidepoint(mouse_pos):
                        confirmando_saida = False
                        pygame.mixer.music.unpause()
                elif fim_de_partida:
                    if botao_novo_round_rect.collidepoint(mouse_pos):
                        vitorias_jogador = 0
                        try:
                            dados_para_enviar = {'pos': (jogador.rect.x, jogador.rect.y), 'bullets': [],
                                                 'escudo': False, 'vida': 3, 'vitorias': 0, 'nome': jogador.nome}
                            conn.send(pickle.dumps(dados_para_enviar))
                        except:
                            pass
                        resetar_round()
                        fim_de_partida = False
                        mensagem_fim_jogo = ""
                        sounds.play_music_in_game()
                    if botao_voltar_menu_rect.collidepoint(mouse_pos):
                        rodando = False
                elif botao_sair_rect.collidepoint(mouse_pos):
                    confirmando_saida = True
                    pygame.mixer.music.pause()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    em_tela_cheia = not em_tela_cheia
                    if em_tela_cheia:
                        info_tela = pygame.display.Info()
                        LARGURA_TELA, ALTURA_TELA = info_tela.current_w, info_tela.current_h
                        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.FULLSCREEN)
                    else:
                        LARGURA_TELA, ALTURA_TELA = LARGURA_JANELA, ALTURA_JANELA
                        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.RESIZABLE)
                    gerar_estrelas(LARGURA_TELA, ALTURA_TELA, 200)
                if fim_de_partida and evento.key == pygame.K_RETURN:
                    rodando = False
                elif not confirmando_saida and outro_conectado and not fim_de_round and not fim_de_partida:
                    if evento.key == pygame.K_c:
                        if not jogador.escudo_ativo and poder_atual >= poder_maximo:
                            jogador.escudo_ativo = True
                            tempo_ativacao_escudo = pygame.time.get_ticks()
                            sounds.play_shield()
            if not confirmando_saida and outro_conectado and evento.type == pygame.KEYUP and not fim_de_round and not fim_de_partida:
                if evento.key == pygame.K_SPACE:
                    if municao > 0:
                        jogador.atirar()
                        sounds.play_shoot()
                        municao -= 1
                if evento.key == pygame.K_r:
                    municao = 3

        # --- LÓGICA PRINCIPAL DO JOGO (MOVIMENTO, POWER-UPS, REDE, COLISÕES) ---
        if not confirmando_saida and not fim_de_partida:
            if outro_conectado and not cronometro_powerup_iniciado:
                cronometro_powerup_iniciado = True
                tempo_referencia_powerup = pygame.time.get_ticks()

            if cronometro_powerup_iniciado and power_up_ativo is None:
                agora = pygame.time.get_ticks()
                if agora - tempo_referencia_powerup >= INTERVALO_POWERUP:
                    tipo_escolhido = random.choice(['vida', 'escudo'])
                    pos_x = LARGURA_TELA / 2
                    pos_y = random.randint(100, ALTURA_TELA - 100)
                    power_up_ativo = PowerUp(pos_x, pos_y, tipo_escolhido)

            if power_up_ativo is not None:
                power_up_ativo.update()
                for tiro in jogador.bullets[:]:
                    if power_up_ativo.rect.colliderect(tiro.rect):
                        if power_up_ativo.type == 'vida' and jogador.vida < 3:
                            jogador.vida += 1
                        elif power_up_ativo.type == 'escudo':
                            poder_atual = poder_maximo
                        jogador.bullets.remove(tiro)
                        power_up_ativo = None
                        tempo_referencia_powerup = pygame.time.get_ticks()
                        break
                if power_up_ativo is not None:
                    for tiro_inimigo in outro.bullets[:]:
                        if power_up_ativo.rect.colliderect(tiro_inimigo.rect):
                            outro.bullets.remove(tiro_inimigo)
                            power_up_ativo = None
                            tempo_referencia_powerup = pygame.time.get_ticks()
                            break

            if not fim_de_round:
                teclas = pygame.key.get_pressed()
                jogador.mover(teclas, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, LARGURA_TELA, ALTURA_TELA)
                if outro_conectado and jogador.escudo_ativo:
                    tempo_decorrido = pygame.time.get_ticks() - tempo_ativacao_escudo
                    if tempo_decorrido > 3000:
                        jogador.escudo_ativo = False
                        poder_atual = 0
                    else:
                        poder_atual = poder_maximo - (tempo_decorrido / 3000) * poder_maximo
                else:
                    jogador.escudo_ativo = False
                    if poder_atual < poder_maximo:
                        poder_atual += 0.01
                for tiro in jogador.bullets[:]:
                    tiro.mover()
                    if tiro.rect.right < 0 or tiro.rect.left > LARGURA_TELA:
                        jogador.bullets.remove(tiro)

            try:
                pos_tiros = [(t.rect.x, t.rect.y) for t in jogador.bullets]
                dados_para_enviar = {
                    'pos': (jogador.rect.x, jogador.rect.y), 'bullets': pos_tiros,
                    'escudo': jogador.escudo_ativo, 'vida': jogador.vida, 'vitorias': vitorias_jogador,
                    'nome': jogador.nome
                }
                conn.send(pickle.dumps(dados_para_enviar))
                estado_jogo_servidor = pickle.loads(conn.recv(2048))

                for id_jogador_servidor, dados_jogador in estado_jogo_servidor.items():
                    if isinstance(id_jogador_servidor, int) and id_jogador_servidor != meu_id:
                        outro_conectado = dados_jogador['conectado']
                        outro.rect.x, outro.rect.y = dados_jogador['pos']
                        outro.escudo_ativo = dados_jogador['escudo']
                        outro.vida = dados_jogador['vida']
                        vitorias_outro = dados_jogador['vitorias']
                        outro.nome = dados_jogador['nome']
                        outro.bullets.clear()
                        for pos_tiro in dados_jogador['bullets']:
                            tiro_inimigo = Bullet(pos_tiro[0], pos_tiro[1], (255, 0, 0))
                            outro.bullets.append(tiro_inimigo)
            except (ConnectionResetError, EOFError, pickle.UnpicklingError) as e:
                print(f"Conexão com o servidor perdida: {e}")
                rodando = False
                break

            if outro_conectado and not fim_de_round:
                for tiro_inimigo in outro.bullets[:]:
                    if jogador.escudo_ativo:
                        if tiro_inimigo.rect.colliderect(jogador.rect.inflate(20, 20)):
                            outro.bullets.remove(tiro_inimigo)
                            sounds.play_hit()
                    else:
                        offset = (tiro_inimigo.rect.x - jogador.rect.x, tiro_inimigo.rect.y - jogador.rect.y)
                        if jogador.mask.overlap(tiro_inimigo.mask, offset):
                            outro.bullets.remove(tiro_inimigo)
                            jogador.vida -= 1
                            sounds.play_hit()
                for meu_tiro in jogador.bullets[:]:
                    if outro.escudo_ativo:
                        if meu_tiro.rect.colliderect(outro.rect.inflate(20, 20)):
                            jogador.bullets.remove(meu_tiro)
                    else:
                        offset = (meu_tiro.rect.x - outro.rect.x, meu_tiro.rect.y - outro.rect.y)
                        if outro.mask.overlap(meu_tiro.mask, offset):
                            jogador.bullets.remove(meu_tiro)
                            outro.vida -= 1
                            sounds.play_hit()

            if not fim_de_round:
                if jogador.vida <= 0:
                    fim_de_round = True
                    tempo_fim_round = pygame.time.get_ticks()
                    mensagem_round = "Round Perdido"
                elif outro_conectado and outro.vida <= 0:
                    vitorias_jogador += 1
                    fim_de_round = True
                    tempo_fim_round = pygame.time.get_ticks()
                    mensagem_round = "Round Vencido!"

            if fim_de_round:
                if pygame.time.get_ticks() - tempo_fim_round > 3000:
                    if vitorias_jogador >= 3:
                        if not mensagem_fim_jogo:
                            mensagem_fim_jogo = "Você Venceu!"
                            sounds.play_victory()
                        fim_de_partida = True
                    elif vitorias_outro >= 3:
                        if not mensagem_fim_jogo:
                            mensagem_fim_jogo = "Você Perdeu!"
                            sounds.play_death()
                        fim_de_partida = True
                    if not fim_de_partida:
                        resetar_round()

        # --- DESENHAR TUDO NO ECRÃ ---
        desenhar_cenario(tela)
        jogador.desenhar(tela)
        if power_up_ativo is not None:
            power_up_ativo.draw(tela)
        if outro_conectado:
            outro.desenhar(tela)
        else:
            texto_espera = fonte_espera.render("Esperando jogador...", True, (200, 200, 200))
            pos_x_espera = LARGURA_TELA * 0.75 if meu_id == 0 else LARGURA_TELA * 0.25
            pos_texto = texto_espera.get_rect(center=(pos_x_espera, ALTURA_TELA / 2))
            tela.blit(texto_espera, pos_texto)
        if meu_id == 0:
            vitorias_p0, vitorias_p1 = vitorias_jogador, vitorias_outro
        else:
            vitorias_p0, vitorias_p1 = vitorias_outro, vitorias_jogador
        desenhar_hud(tela, jogador.vida, municao, vitorias_p0, vitorias_p1, LARGURA_TELA, ALTURA_TELA)
        desenhar_barra_de_poder(tela, poder_atual, poder_maximo, LARGURA_TELA, ALTURA_TELA)
        botao_sair_rect = desenhar_botao_sair(tela)
        if confirmando_saida:
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            tela.blit(overlay, (0, 0))
            texto_confirma = fonte_media.render("Tem a certeza que quer sair?", True, (255, 255, 255))
            tela.blit(texto_confirma, texto_confirma.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 50)))
            texto_sim = fonte_media.render("Sim", True, (0, 255, 0))
            botao_sim_rect = texto_sim.get_rect(center=(LARGURA_TELA / 2 - 100, ALTURA_TELA / 2 + 50))
            tela.blit(texto_sim, botao_sim_rect)
            texto_nao = fonte_media.render("Não", True, (255, 0, 0))
            botao_nao_rect = texto_nao.get_rect(center=(LARGURA_TELA / 2 + 100, ALTURA_TELA / 2 + 50))
            tela.blit(texto_nao, botao_nao_rect)
        elif fim_de_round and not fim_de_partida:
            texto = fonte_grande.render(mensagem_round, True, (255, 255, 255))
            pos_texto = texto.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2))
            tela.blit(texto, pos_texto)
        elif fim_de_partida:
            texto = fonte_grande.render(mensagem_fim_jogo, True, (255, 255, 255))
            pos_texto = texto.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 100))
            tela.blit(texto, pos_texto)
            texto_novo_round = fonte_media.render("Jogar Novamente", True, (0, 255, 0))
            botao_novo_round_rect = texto_novo_round.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 50))
            tela.blit(texto_novo_round, botao_novo_round_rect)
            texto_voltar_menu = fonte_media.render("Voltar para o Menu", True, (255, 255, 255))
            botao_voltar_menu_rect = texto_voltar_menu.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 120))
            tela.blit(texto_voltar_menu, botao_voltar_menu_rect)

        cursor.draw(tela)
        pygame.display.flip()

    # --- FINALIZAÇÃO ---
    sounds.stop_music()
    conn.close()


# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    if len(sys.argv) < 4:
        host_arg = input("IP do servidor: ")
        port_arg = int(input("Porta do servidor: "))
        nome_arg = input("Seu nome: ")
    else:
        host_arg = sys.argv[1]
        port_arg = int(sys.argv[2])
        nome_arg = sys.argv[3]
    main(host_arg, port_arg, nome_arg)
    pygame.quit()