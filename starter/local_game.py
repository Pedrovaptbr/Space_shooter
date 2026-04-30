# --- IMPORTAÇÕES ---
import pygame
import sys
import random
from starter.player import Player
from starter.level import desenhar_cenario, gerar_estrelas
from starter.bullet import Bullet
from starter.config import FPS
from starter.sound_manager import SoundManager
from starter.cursor import AnimatedCursor
from starter.powerup import PowerUp
from starter.scoring import decidir_vencedor_round


# --- CONSTANTES DO JOGO LOCAL ---
DURACAO_ESCUDO_MS = 3000
INTERVALO_POWERUP_MS = 15000
ROUNDS_PARA_VENCER = 3
DURACAO_FIM_DE_ROUND_MS = 3000
MUNICAO_MAXIMA = 3
PODER_MAXIMO = 100
TAXA_REGEN_PODER = 0.05


# --- TELA DE ENTRADA DE NOMES ---
def get_player_names(tela):
    LARGURA_TELA, ALTURA_TELA = tela.get_size()
    cursor = AnimatedCursor()
    fonte_titulo = pygame.font.Font(None, 80)
    fonte_label = pygame.font.Font(None, 50)
    fonte_input = pygame.font.Font(None, 50)

    input_fields = {
        'p1': {'label': 'Nome Jogador 1 (WASD):', 'text': 'Player 1', 'rect': pygame.Rect(LARGURA_TELA/2 - 200, 250, 400, 50), 'active': True},
        'p2': {'label': 'Nome Jogador 2 (Setas):', 'text': 'Player 2', 'rect': pygame.Rect(LARGURA_TELA/2 - 200, 410, 400, 50), 'active': False}
    }

    botao_iniciar_rect = pygame.Rect(LARGURA_TELA/2 - 100, 550, 200, 60)

    rodando = True
    while rodando:
        desenhar_cenario(tela)
        titulo_render = fonte_titulo.render("Modo 1 vs 1 Local", True, (255, 255, 255))
        tela.blit(titulo_render, titulo_render.get_rect(center=(LARGURA_TELA/2, 150)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_iniciar_rect.collidepoint(event.pos):
                    return input_fields['p1']['text'], input_fields['p2']['text']
                for field in input_fields.values():
                    field['active'] = field['rect'].collidepoint(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_fields['p1']['text'], input_fields['p2']['text']
                for field in input_fields.values():
                    if field['active']:
                        if event.key == pygame.K_BACKSPACE:
                            field['text'] = field['text'][:-1]
                        else:
                            field['text'] += event.unicode

        for field in input_fields.values():
            label_render = fonte_label.render(field['label'], True, (200, 200, 200))
            tela.blit(label_render, (field['rect'].x, field['rect'].y - 40))
            pygame.draw.rect(tela, (255, 255, 255) if field['active'] else (100, 100, 100), field['rect'], 2)
            text_surface = fonte_input.render(field['text'], True, (255, 255, 255))
            tela.blit(text_surface, (field['rect'].x + 10, field['rect'].y + 10))

        pygame.draw.rect(tela, (0, 200, 0), botao_iniciar_rect)
        iniciar_texto = fonte_label.render("Iniciar", True, (255, 255, 255))
        tela.blit(iniciar_texto, iniciar_texto.get_rect(center=botao_iniciar_rect.center))
        cursor.update(); cursor.draw(tela); pygame.display.flip()


# --- FUNÇÕES AUXILIARES DE UI ---
def desenhar_barra_de_poder(tela, poder_atual, poder_maximo, pos_x, pos_y, largura_total, altura_barra, cor):
    largura_atual = (poder_atual / poder_maximo) * largura_total
    pygame.draw.rect(tela, (50, 50, 50), (pos_x, pos_y, largura_total, altura_barra))
    if largura_atual > 0:
        pygame.draw.rect(tela, cor, (pos_x, pos_y, largura_atual, altura_barra))


def desenhar_hud_local(tela, p1, p2, vitorias_p1, vitorias_p2, municao_p1, municao_p2, poder_p1, poder_p2, largura_tela, altura_tela):
    margem = 15; tamanho_vida = 25; espacamento = 8; altura_barra_poder = 10
    fonte_placar = pygame.font.Font(None, 60); fonte_nome = pygame.font.Font(None, 36)

    texto_placar = f"{vitorias_p1}  -  {vitorias_p2}"
    placar_render = fonte_placar.render(texto_placar, True, (255, 255, 255))
    tela.blit(placar_render, placar_render.get_rect(center=(largura_tela / 2, 40)))

    # HUD P1
    nome_p1_render = fonte_nome.render(p1.nome, True, (0, 150, 255))
    tela.blit(nome_p1_render, (margem, altura_tela - margem - tamanho_vida - 50))
    for i in range(p1.vida):
        pygame.draw.rect(tela, (0, 150, 255), (margem + (i * (tamanho_vida + espacamento)), altura_tela - margem - tamanho_vida - 15, tamanho_vida, tamanho_vida))
    for i in range(municao_p1):
        pygame.draw.rect(tela, (255, 255, 0), (margem + (i * (20 + espacamento)), altura_tela - margem - 12, 20, 12))
    desenhar_barra_de_poder(tela, poder_p1, PODER_MAXIMO, margem, altura_tela - margem - tamanho_vida - 30, 200, altura_barra_poder, (0, 128, 255))

    # HUD P2
    nome_p2_render = fonte_nome.render(p2.nome, True, (255, 50, 50))
    nome_p2_rect = nome_p2_render.get_rect(right=largura_tela - margem, y=altura_tela - margem - tamanho_vida - 50)
    tela.blit(nome_p2_render, nome_p2_rect)
    for i in range(p2.vida):
        pygame.draw.rect(tela, (255, 50, 50), (largura_tela - margem - tamanho_vida - (i * (tamanho_vida + espacamento)), altura_tela - margem - tamanho_vida - 15, tamanho_vida, tamanho_vida))
    for i in range(municao_p2):
        pygame.draw.rect(tela, (255, 255, 0), (largura_tela - margem - 20 - (i * (20 + espacamento)), altura_tela - margem - 12, 20, 12))
    desenhar_barra_de_poder(tela, poder_p2, PODER_MAXIMO, largura_tela - margem - 200, altura_tela - margem - tamanho_vida - 30, 200, altura_barra_poder, (255, 128, 0))


def desenhar_botao_sair(tela):
    botao_rect = pygame.Rect(15, 15, 40, 40)
    pygame.draw.rect(tela, (200, 0, 0), botao_rect)
    pygame.draw.line(tela, (255, 255, 255), (20, 20), (50, 50), 4)
    pygame.draw.line(tela, (255, 255, 255), (50, 20), (20, 50), 4)
    return botao_rect


# --- INPUTS DE TECLADO DURANTE O ROUND ---
def processar_keydown_round(evento, jogador1, jogador2, estado, sounds):
    """Trata SPACE/R/C (P1) e RETURN/RSHIFT/RCTRL (P2)."""
    agora = pygame.time.get_ticks()

    # P1
    if evento.key == pygame.K_SPACE and estado['municao_p1'] > 0:
        jogador1.atirar(); sounds.play_shoot(); estado['municao_p1'] -= 1
    elif evento.key == pygame.K_r:
        estado['municao_p1'] = MUNICAO_MAXIMA
    elif evento.key == pygame.K_c and not jogador1.escudo_ativo and estado['poder_p1'] >= PODER_MAXIMO:
        jogador1.escudo_ativo = True; estado['tempo_escudo_p1'] = agora; sounds.play_shield()

    # P2
    if evento.key == pygame.K_RETURN and estado['municao_p2'] > 0:
        jogador2.atirar(); sounds.play_shoot(); estado['municao_p2'] -= 1
    elif evento.key == pygame.K_RSHIFT:
        estado['municao_p2'] = MUNICAO_MAXIMA
    elif evento.key == pygame.K_RCTRL and not jogador2.escudo_ativo and estado['poder_p2'] >= PODER_MAXIMO:
        jogador2.escudo_ativo = True; estado['tempo_escudo_p2'] = agora; sounds.play_shield()


# --- POWER-UPS ---
def atualizar_powerup(estado, jogador1, jogador2, largura_tela, altura_tela):
    """Spawna e processa pickup do power-up (acertado por uma bala)."""
    agora = pygame.time.get_ticks()

    if estado['power_up_ativo'] is None and agora - estado['tempo_ref_powerup'] > INTERVALO_POWERUP_MS:
        tipo = random.choice(['vida', 'escudo'])
        estado['power_up_ativo'] = PowerUp(largura_tela / 2, random.randint(100, altura_tela - 100), tipo)
        estado['tempo_ref_powerup'] = agora
        return

    pu = estado['power_up_ativo']
    if pu is None:
        return
    pu.update()

    def _aplicar(jogador, lado):
        if pu.type == 'vida' and jogador.vida < 3:
            jogador.vida += 1
        elif pu.type == 'escudo':
            estado[lado] = PODER_MAXIMO
        # Remove balas que estavam sobre o power-up
        jogador.bullets = [t for t in jogador.bullets if not pu.rect.colliderect(t.rect)]

    if any(pu.rect.colliderect(t.rect) for t in jogador1.bullets):
        _aplicar(jogador1, 'poder_p1')
        estado['power_up_ativo'] = None
    elif any(pu.rect.colliderect(t.rect) for t in jogador2.bullets):
        _aplicar(jogador2, 'poder_p2')
        estado['power_up_ativo'] = None


# --- ESCUDO + REGEN DE PODER ---
def _atualizar_escudo_jogador(jogador, tempo_escudo_ms, poder_atual, agora):
    """Retorna (poder_atualizado, escudo_ainda_ativo)."""
    if jogador.escudo_ativo:
        decorrido = agora - tempo_escudo_ms
        if decorrido > DURACAO_ESCUDO_MS:
            jogador.escudo_ativo = False
            return 0, False
        # Drena de 100 -> 0 ao longo da duração
        return PODER_MAXIMO - (decorrido / DURACAO_ESCUDO_MS) * PODER_MAXIMO, True
    if poder_atual < PODER_MAXIMO:
        return poder_atual + TAXA_REGEN_PODER, False
    return poder_atual, False


def atualizar_escudos_e_poderes(estado, jogador1, jogador2):
    agora = pygame.time.get_ticks()
    estado['poder_p1'], _ = _atualizar_escudo_jogador(jogador1, estado['tempo_escudo_p1'], estado['poder_p1'], agora)
    estado['poder_p2'], _ = _atualizar_escudo_jogador(jogador2, estado['tempo_escudo_p2'], estado['poder_p2'], agora)


# --- COLISÕES DE BALAS ---
def _resolver_tiros(atacante, alvo, sounds):
    """Move tiros do atacante contra o alvo. Retorna 1 se houve dano efetivo."""
    dano = 0
    for tiro in atacante.bullets[:]:
        if not alvo.escudo_ativo:
            offset = (tiro.rect.x - alvo.rect.x, tiro.rect.y - alvo.rect.y)
            if alvo.mask.overlap(tiro.mask, offset):
                atacante.bullets.remove(tiro)
                alvo.vida -= 1
                sounds.play_hit()
                dano = 1
                break
        else:
            if tiro.rect.colliderect(alvo.rect.inflate(20, 20)):
                atacante.bullets.remove(tiro)
                sounds.play_hit()
    return dano


def processar_colisoes_locais(jogador1, jogador2, tela_rect, sounds):
    """Move balas, descarta as fora da tela, e resolve hits cruzados."""
    for tiro in jogador1.bullets: tiro.mover()
    for tiro in jogador2.bullets: tiro.mover()
    jogador1.bullets = [t for t in jogador1.bullets if tela_rect.colliderect(t.rect)]
    jogador2.bullets = [t for t in jogador2.bullets if tela_rect.colliderect(t.rect)]

    _resolver_tiros(jogador1, jogador2, sounds)
    _resolver_tiros(jogador2, jogador1, sounds)


# --- OVERLAYS ---
def desenhar_overlay_confirma_saida(tela, fonte_media, largura, altura):
    overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    tela.blit(overlay, (0, 0))

    texto_confirma = fonte_media.render("Tem a certeza que quer sair?", True, (255, 255, 255))
    tela.blit(texto_confirma, texto_confirma.get_rect(center=(largura / 2, altura / 2 - 50)))

    texto_sim = fonte_media.render("Sim", True, (0, 255, 0))
    botao_sim_rect = texto_sim.get_rect(center=(largura / 2 - 100, altura / 2 + 50))
    tela.blit(texto_sim, botao_sim_rect)

    texto_nao = fonte_media.render("Não", True, (255, 0, 0))
    botao_nao_rect = texto_nao.get_rect(center=(largura / 2 + 100, altura / 2 + 50))
    tela.blit(texto_nao, botao_nao_rect)
    return botao_sim_rect, botao_nao_rect


def desenhar_overlay_fim_round(tela, fonte_grande, mensagem, largura, altura):
    texto = fonte_grande.render(mensagem, True, (255, 255, 255))
    tela.blit(texto, texto.get_rect(center=(largura / 2, altura / 2)))


def desenhar_overlay_fim_partida(tela, fonte_grande, fonte_media, mensagem, largura, altura):
    texto = fonte_grande.render(mensagem, True, (255, 255, 255))
    tela.blit(texto, texto.get_rect(center=(largura / 2, altura / 2 - 100)))

    texto_novo = fonte_media.render("Jogar Novamente", True, (0, 255, 0))
    botao_novo = texto_novo.get_rect(center=(largura / 2, altura / 2 + 50))
    tela.blit(texto_novo, botao_novo)

    texto_voltar = fonte_media.render("Voltar para o Menu", True, (255, 255, 255))
    botao_voltar = texto_voltar.get_rect(center=(largura / 2, altura / 2 + 120))
    tela.blit(texto_voltar, botao_voltar)
    return botao_novo, botao_voltar


# --- FUNÇÃO PRINCIPAL DO JOGO LOCAL ---
def local_game_main():
    tela = pygame.display.get_surface()
    LARGURA_TELA, ALTURA_TELA = tela.get_size()
    nome_p1, nome_p2 = get_player_names(tela)
    pygame.display.set_caption("Space Shooter - 2 Jogadores Local")
    relogio = pygame.time.Clock()
    fonte_grande = pygame.font.Font(None, 100)
    fonte_media = pygame.font.Font(None, 74)
    cursor = AnimatedCursor()
    gerar_estrelas(LARGURA_TELA, ALTURA_TELA, 200)
    sounds = SoundManager()
    sounds.play_music_in_game()

    jogador1 = Player(100, ALTURA_TELA / 2, 0, nome_p1)
    jogador2 = Player(LARGURA_TELA - 100 - 40, ALTURA_TELA / 2, 1, nome_p2)
    vitorias_p1, vitorias_p2 = 0, 0

    # Estado mutável do round, agrupado para passar fácil por valor
    estado = {
        'municao_p1': MUNICAO_MAXIMA, 'municao_p2': MUNICAO_MAXIMA,
        'poder_p1': PODER_MAXIMO, 'poder_p2': PODER_MAXIMO,
        'tempo_escudo_p1': 0, 'tempo_escudo_p2': 0,
        'power_up_ativo': None,
        'tempo_ref_powerup': pygame.time.get_ticks(),
    }

    fim_de_round = False
    fim_de_partida = False
    confirmando_saida = False
    tempo_fim_round = 0
    mensagem_round = ""
    mensagem_fim_jogo = ""
    round_pontuado = False  # impede que vitorias_p1/p2 sejam incrementadas duas vezes no mesmo round

    def resetar_round():
        nonlocal fim_de_round, mensagem_round, round_pontuado
        jogador1.vida = 3; jogador2.vida = 3
        jogador1.bullets.clear(); jogador2.bullets.clear()
        jogador1.rect.topleft = (100, ALTURA_TELA / 2)
        jogador2.rect.topleft = (LARGURA_TELA - 100 - 40, ALTURA_TELA / 2)
        estado['municao_p1'] = MUNICAO_MAXIMA
        estado['municao_p2'] = MUNICAO_MAXIMA
        estado['poder_p1'] = PODER_MAXIMO
        estado['poder_p2'] = PODER_MAXIMO
        fim_de_round = False
        mensagem_round = ""
        round_pontuado = False

    resetar_round()

    botao_sair_rect = pygame.Rect(15, 15, 40, 40)
    botao_sim_rect = pygame.Rect(0, 0, 0, 0)
    botao_nao_rect = pygame.Rect(0, 0, 0, 0)
    botao_novo_round_rect = pygame.Rect(0, 0, 0, 0)
    botao_voltar_menu_rect = pygame.Rect(0, 0, 0, 0)

    rodando = True
    while rodando:
        relogio.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        cursor.update()
        jogador1.animate(); jogador2.animate()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if confirmando_saida:
                    if botao_sim_rect.collidepoint(mouse_pos): rodando = False
                    if botao_nao_rect.collidepoint(mouse_pos):
                        confirmando_saida = False; pygame.mixer.music.unpause()
                elif fim_de_partida:
                    if botao_novo_round_rect.collidepoint(mouse_pos):
                        vitorias_p1, vitorias_p2 = 0, 0
                        fim_de_partida = False
                        mensagem_fim_jogo = ""
                        resetar_round()
                        sounds.play_music_in_game()
                    if botao_voltar_menu_rect.collidepoint(mouse_pos):
                        rodando = False
                elif botao_sair_rect.collidepoint(mouse_pos):
                    confirmando_saida = True
                    pygame.mixer.music.pause()

            if evento.type == pygame.KEYDOWN and not confirmando_saida and not fim_de_round and not fim_de_partida:
                processar_keydown_round(evento, jogador1, jogador2, estado, sounds)

        if not confirmando_saida and not fim_de_partida:
            atualizar_powerup(estado, jogador1, jogador2, LARGURA_TELA, ALTURA_TELA)
            atualizar_escudos_e_poderes(estado, jogador1, jogador2)

            if not fim_de_round:
                teclas = pygame.key.get_pressed()
                jogador1.mover(teclas, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, LARGURA_TELA, ALTURA_TELA)
                jogador2.mover(teclas, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, LARGURA_TELA, ALTURA_TELA)
                processar_colisoes_locais(jogador1, jogador2, tela.get_rect(), sounds)

                if not round_pontuado:
                    vencedor = decidir_vencedor_round(jogador1.vida, jogador2.vida)
                    if vencedor is not None:
                        if vencedor == 0:
                            vitorias_p1 += 1
                            mensagem_round = f"{nome_p1} Venceu o Round!"
                        elif vencedor == 1:
                            vitorias_p2 += 1
                            mensagem_round = f"{nome_p2} Venceu o Round!"
                        else:  # empate — ninguém pontua, mas o round acaba
                            mensagem_round = "Empate!"
                        fim_de_round = True
                        round_pontuado = True
                        tempo_fim_round = pygame.time.get_ticks()

            if fim_de_round and pygame.time.get_ticks() - tempo_fim_round > DURACAO_FIM_DE_ROUND_MS:
                if vitorias_p1 >= ROUNDS_PARA_VENCER:
                    if not mensagem_fim_jogo:
                        mensagem_fim_jogo = f"{nome_p1} Venceu a Partida!"
                        sounds.play_victory()
                    fim_de_partida = True
                elif vitorias_p2 >= ROUNDS_PARA_VENCER:
                    if not mensagem_fim_jogo:
                        mensagem_fim_jogo = f"{nome_p2} Venceu a Partida!"
                        sounds.play_victory()
                    fim_de_partida = True
                if not fim_de_partida:
                    resetar_round()

        # --- RENDER ---
        desenhar_cenario(tela)
        jogador1.desenhar(tela)
        for bala in jogador1.bullets: bala.desenhar(tela)
        jogador2.desenhar(tela)
        for bala in jogador2.bullets: bala.desenhar(tela)

        if estado['power_up_ativo']:
            estado['power_up_ativo'].draw(tela)

        desenhar_hud_local(tela, jogador1, jogador2, vitorias_p1, vitorias_p2,
                           estado['municao_p1'], estado['municao_p2'],
                           estado['poder_p1'], estado['poder_p2'],
                           LARGURA_TELA, ALTURA_TELA)
        botao_sair_rect = desenhar_botao_sair(tela)

        if confirmando_saida:
            botao_sim_rect, botao_nao_rect = desenhar_overlay_confirma_saida(
                tela, fonte_media, LARGURA_TELA, ALTURA_TELA
            )
        elif fim_de_round and not fim_de_partida:
            desenhar_overlay_fim_round(tela, fonte_grande, mensagem_round, LARGURA_TELA, ALTURA_T