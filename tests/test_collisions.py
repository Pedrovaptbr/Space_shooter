"""Testes unitários da lógica de colisão e simulação do servidor.

Testa só funções puras — não precisa subir socket nem pygame.
"""
import unittest

from starter.server import (
    aabb_overlap,
    aplicar_acao,
    avancar_balas,
    processar_colisoes,
    PLAYER_W,
    PLAYER_H,
    BULLET_W,
    BULLET_H,
    LARGURA_TELA,
    ALTURA_TELA,
    PLAYER_SPEED,
    BULLET_SPEED,
)


class TestAabbOverlap(unittest.TestCase):
    def test_retangulos_sobrepostos(self):
        # Mesma origem
        self.assertTrue(aabb_overlap(0, 0, 10, 10, 0, 0, 10, 10))
        # Sobreposição parcial
        self.assertTrue(aabb_overlap(0, 0, 10, 10, 5, 5, 10, 10))

    def test_retangulos_separados(self):
        # Lado a lado sem encostar
        self.assertFalse(aabb_overlap(0, 0, 10, 10, 20, 0, 10, 10))
        # Um em cima do outro mas separados verticalmente
        self.assertFalse(aabb_overlap(0, 0, 10, 10, 0, 20, 10, 10))

    def test_borda_se_tocando_nao_e_sobreposicao(self):
        # AABB em "edge-touch" — convenção half-open: borda colada não conta
        self.assertFalse(aabb_overlap(0, 0, 10, 10, 10, 0, 10, 10))

    def test_bala_no_jogador_caso_real(self):
        # Jogador parado em (100, 360), bala chegando em (110, 395) — deve atingir
        self.assertTrue(
            aabb_overlap(100, 360, PLAYER_W, PLAYER_H, 110, 395, BULLET_W, BULLET_H)
        )
        # Bala bem longe — não deve atingir
        self.assertFalse(
            aabb_overlap(100, 360, PLAYER_W, PLAYER_H, 800, 100, BULLET_W, BULLET_H)
        )


class TestAplicarAcao(unittest.TestCase):
    def _make_player(self, pos=(100, 360)):
        return {'pos': pos, 'vida': 3, 'nome': 'X'}

    def test_move_up_diminui_y(self):
        p = self._make_player((100, 360))
        aplicar_acao(p, 'move_up', 0, [])
        self.assertEqual(p['pos'], (100, 360 - PLAYER_SPEED))

    def test_move_up_clamp_em_zero(self):
        p = self._make_player((100, 0))
        aplicar_acao(p, 'move_up', 0, [])
        self.assertEqual(p['pos'][1], 0)

    def test_move_down_clamp_no_fundo(self):
        p = self._make_player((100, ALTURA_TELA - PLAYER_H))
        aplicar_acao(p, 'move_down', 0, [])
        self.assertEqual(p['pos'][1], ALTURA_TELA - PLAYER_H)

    def test_move_left_clamp_em_zero(self):
        p = self._make_player((0, 360))
        aplicar_acao(p, 'move_left', 0, [])
        self.assertEqual(p['pos'][0], 0)

    def test_move_right_clamp_na_borda(self):
        p = self._make_player((LARGURA_TELA - PLAYER_W, 360))
        aplicar_acao(p, 'move_right', 0, [])
        self.assertEqual(p['pos'][0], LARGURA_TELA - PLAYER_W)

    def test_shoot_player0_cria_bala_indo_pra_direita(self):
        p = self._make_player((100, 360))
        balas = []
        aplicar_acao(p, 'shoot', 0, balas)
        self.assertEqual(len(balas), 1)
        self.assertEqual(balas[0]['owner_id'], 0)
        self.assertEqual(balas[0]['dir'], 1)

    def test_shoot_player1_cria_bala_indo_pra_esquerda(self):
        p = self._make_player((1140, 360))
        balas = []
        aplicar_acao(p, 'shoot', 1, balas)
        self.assertEqual(balas[0]['dir'], -1)


class TestAvancarBalas(unittest.TestCase):
    def test_bala_avanca_pela_velocidade(self):
        balas = [{'pos': (100, 360), 'owner_id': 0, 'dir': 1}]
        novas = avancar_balas(balas)
        self.assertEqual(novas[0]['pos'][0], 100 + BULLET_SPEED)

    def test_bala_que_sai_pela_direita_e_descartada(self):
        balas = [{'pos': (LARGURA_TELA - 1, 360), 'owner_id': 0, 'dir': 1}]
        novas = avancar_balas(balas)
        self.assertEqual(novas, [])

    def test_bala_que_sai_pela_esquerda_e_descartada(self):
        balas = [{'pos': (1, 360), 'owner_id': 1, 'dir': -1}]
        novas = avancar_balas(balas)
        self.assertEqual(novas, [])


class TestProcessarColisoes(unittest.TestCase):
    def _jogadores(self):
        return {
            0: {'pos': (100, 360), 'vida': 3, 'nome': 'A'},
            1: {'pos': (1140, 360), 'vida': 3, 'nome': 'B'},
        }

    def test_bala_acerta_inimigo_remove_e_tira_vida(self):
        jogadores = self._jogadores()
        # Bala do P0 atinge P1
        balas = [{'pos': (1145, 380), 'owner_id': 0, 'dir': 1}]
        sobreviventes = processar_colisoes(balas, jogadores)
        self.assertEqual(sobreviventes, [])
        self.assertEqual(jogadores[1]['vida'], 2)
        self.assertEqual(jogadores[0]['vida'], 3)  # P0 não foi atingido

    def test_bala_propria_nao_atinge_dono(self):
        jogadores = self._jogadores()
        # Bala do P0 sobreposta ao próprio P0 — não deve causar dano
        balas = [{'pos': (105, 365), 'owner_id': 0, 'dir': 1}]
        sobreviventes = processar_colisoes(balas, jogadores)
        self.assertEqual(len(sobreviventes), 1)
        self.assertEqual(jogadores[0]['vida'], 3)

    def test_bala_no_vacuo_sobrevive(self):
        jogadores = self._jogadores()
        balas = [{'pos': (600, 100), 'owner_id': 0, 'dir': 1}]
        sobreviventes = processar_colisoes(balas, jogadores)
        self.assertEqual(len(sobreviventes), 1)
        self.assertEqual(jogadores[0]['vida'], 3)
        self.assertEqual(jogadores[1]['vida'], 3)


if __name__ == '__main__':
    unittest.main()
