# starter/scoring.py
"""Lógica pura de pontuação — sem dependência de pygame, fácil de testar."""


def decidir_vencedor_round(vida_p1, vida_p2):
    """Retorna 0 se P1 venceu, 1 se P2 venceu, 'empate' se ambos caíram, ou None se o round ainda está em andamento.

    Função pura, sem efeitos colaterais.
    """
    p1_morto = vida_p1 <= 0
    p2_morto = vida_p2 <= 0
    if p1_morto and p2_morto:
        return 'empate'
    if p1_morto:
        return 1  # P2 venceu
    if p2_morto:
        return 0  # P1 venceu
    return None
