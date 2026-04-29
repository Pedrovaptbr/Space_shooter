"""Testes do protocolo JSON cliente↔servidor.

Garantem que:
  - Pacotes serializam pra UTF-8 e des-serializam de volta sem perder informação relevante.
  - Estruturas que viraram lista (tuplas) seguem indexáveis igual.
  - Chaves de jogador (int no servidor) podem ser reconvertidas no cliente.
"""
import json
import unittest


def _round_trip(obj):
    return json.loads(json.dumps(obj).encode('utf-8').decode('utf-8'))


class TestHandshake(unittest.TestCase):
    def test_join_request(self):
        join = {'action': 'join', 'name': 'Pedro'}
        recv = _round_trip(join)
        self.assertEqual(recv['action'], 'join')
        self.assertEqual(recv['name'], 'Pedro')

    def test_id_assignment_response(self):
        resp = {'type': 'id_assignment', 'id': 1}
        recv = _round_trip(resp)
        self.assertEqual(recv['type'], 'id_assignment')
        self.assertEqual(recv['id'], 1)


class TestActionList(unittest.TestCase):
    def test_lista_vazia(self):
        self.assertEqual(_round_trip([]), [])

    def test_lista_com_acoes(self):
        actions = ['move_up', 'move_right', 'shoot']
        self.assertEqual(_round_trip(actions), actions)


class TestGameState(unittest.TestCase):
    def _state(self):
        return {
            'jogadores': {
                0: {'pos': (100, 360), 'vida': 3, 'vitorias': 0, 'escudo': False, 'conectado': True, 'nome': 'A'},
                1: {'pos': (1140, 360), 'vida': 2, 'vitorias': 1, 'escudo': False, 'conectado': True, 'nome': 'B'},
            },
            'balas': [
                {'pos': (200, 360), 'owner_id': 0, 'dir': 1},
                {'pos': (1000, 360), 'owner_id': 1, 'dir': -1},
            ],
        }

    def test_chaves_de_jogador_reconvertem_pra_int(self):
        packet = {'type': 'game_state', 'data': self._state(), 'timestamp': 0.0}
        recv = _round_trip(packet)
        # JSON converteu chaves int em str
        self.assertIn('0', recv['data']['jogadores'])
        # Reconversão (mesma lógica usada no client.py)
        recv['data']['jogadores'] = {int(k): v for k, v in recv['data']['jogadores'].items()}
        self.assertIn(0, recv['data']['jogadores'])
        self.assertEqual(recv['data']['jogadores'][0]['nome'], 'A')

    def test_pos_continua_indexavel_apos_round_trip(self):
        recv = _round_trip(self._state())
        recv['jogadores'] = {int(k): v for k, v in recv['jogadores'].items()}
        # tuplas viraram listas, mas pos[0]/pos[1] precisa funcionar igual
        self.assertEqual(recv['jogadores'][0]['pos'][0], 100)
        self.assertEqual(recv['jogadores'][0]['pos'][1], 360)
        self.assertEqual(recv['balas'][0]['pos'][0], 200)
        self.assertEqual(recv['balas'][1]['owner_id'], 1)

    def test_pacote_cabe_no_buffer_size(self):
        # BUFFER_SIZE do cliente/servidor é 4096. Estado típico deve caber com folga.
        wire = json.dumps({'type': 'game_state', 'data': self._state(), 'timestamp': 1.0}).encode('utf-8')
        self.assertLess(len(wire), 4096)


class TestPacoteMalformado(unittest.TestCase):
    def test_bytes_aleatorios_disparam_erro_de_json(self):
        with self.assertRaises(json.JSONDecodeError):
            json.loads(b'\xff\xfe\x00not-json'.decode('utf-8', errors='replace'))

    def test_string_vazia_dispara_erro(self):
        with self.assertRaises(json.JSONDecodeError):
            json.loads('')


if __name__ == '__main__':
    unittest.main()
