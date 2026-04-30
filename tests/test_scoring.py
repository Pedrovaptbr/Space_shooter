# tests/test_scoring.py
"""Testa decidir_vencedor_round — função pura que decide o vencedor de um round.

Garantia principal: ela retorna apenas UMA decisão por estado. Combinada com a flag
`round_pontuado` no loop principal, isso impede o bug de "+2 pontos" que pode
ocorrer se a checagem rodasse em frames consecutivos antes do reset.
"""
import unittest

from starter.scoring import decidir_vencedor_round


class TestDecidirVencedorRound(unittest.TestCase):
    def test_ambos_vivos_retorna_None(self):
        self.assertIsNone(decidir_vencedor_round(3, 3))
        self.assertIsNone(decidir_vencedor_round(1, 1))

    def test_p1_morto_p2_vivo_retorna_1(self):
        # P2 venceu (id 1)
        self.assertEqual(decidir_vencedor_round(0, 2), 1)
        self.assertEqual(decidir_vencedor_round(-1, 1), 1)

    def test_p2_morto_p1_vivo_retorna_0(self):
        # P1 venceu (id 0)
        self.assertEqual(decidir_vencedor_round(2, 0), 0)
        self.assertEqual(decidir_vencedor_round(1, -1), 0)

    def test_ambos_mortos_retorna_empate(self):
        self.assertEqual(decidir_vencedor_round(0, 0), 'empate')
        self.assertEqual(decidir_vencedor_round(-1, -2), 'empate')

    def test_funcao_e_pura_nao_tem_efeito_colateral(self):
        # Chamadas repetidas com o mesmo input retornam o mesmo output
        for _ in range(5):
            self.assertEqual(decidir_vencedor_round(0, 1), 1)
            self.assertEqual(decidir_vencedor_round(1, 0), 0)


class TestImpossibilidadeDeDoublePoint(unittest.TestCase):
    """Simula o fluxo do loop principal e garante que a pontuação só ocorre uma vez."""

    def test_loop_simulado_so_pontua_uma_vez(self):
        vitorias_p1, vitorias_p2 = 0, 0
        round_pontuado = False
        fim_de_round = False

        # Simula 100 frames com P1 morto e P2 vivo (após a morte)
        for _ in range(100):
            if not fim_de_round and not round_pontuado:
                vencedor = decidir_vencedor_round(0, 2)
                if vencedor is not None:
                    if vencedor == 0:
                        vitorias_p1 += 1
                    elif vencedor == 1:
                        vitorias_p2 += 1
                    fim_de_round = True
                    round_pontuado = True
            # Simula que fim_de_round permanece True (esperando os 3s do overlay)

        self.assertEqual(vitorias_p1, 0)
        self.assertEqual(vitorias_p2, 1, "P2 deveria ter ganhado exatamente 1 ponto, não mais")

    def test_empate_nao_da_ponto_pra_ninguem(self):
        vitorias_p1, vitorias_p2 = 0, 0
        round_pontuado = False
        fim_de_round = False

        for _ in range(50):
            if not fim_de_round and not round_pontuado:
                vencedor = decidir_vencedor_round(0, 0)
                if vencedor is not None:
                    if vencedor == 0:
                        vitorias_p1 += 1
                    elif vencedor == 1:
                        vitorias_p2 += 1
                    # 'empate' não cai em nenhum ramo de pontuação
                    fim_de_round = True
                    round_pontuado = True

        self.assertEqual(vitorias_p1, 0)
        self.assertEqual(vitorias_p2, 0)


if __name__ == "__main__":
    unittest.main()
