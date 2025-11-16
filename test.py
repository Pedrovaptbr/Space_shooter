import subprocess
import sys
import time

# --- Configurações do Teste ---
HOST = "localhost"
PORTA_TESTE = "5555"

def run_tests():
    """
    Inicia o servidor e dois clientes para um teste local rápido.
    """
    server_process = None
    client1_process = None
    client2_process = None

    try:

        print(f"Iniciando o servidor de teste em {HOST}:{PORTA_TESTE}...")
        server_process = subprocess.Popen(
            [sys.executable, "starter/server.py", PORTA_TESTE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Servidor iniciado (PID: {server_process.pid}). Aguardando inicialização...")


        time.sleep(2)


        print("Iniciando Cliente 1...")
        client1_process = subprocess.Popen(
            [sys.executable, "-m", "starter.client", HOST, PORTA_TESTE, "Tester1"]
        )
        print(f"Cliente 1 iniciado (PID: {client1_process.pid})")


        print("Iniciando Cliente 2...")
        client2_process = subprocess.Popen(
            [sys.executable, "-m", "starter.client", HOST, PORTA_TESTE, "Tester2"]
        )
        print(f"Cliente 2 iniciado (PID: {client2_process.pid})")

        print("\n--- Ambiente de teste iniciado ---")
        print("Feche qualquer uma das janelas do jogo para encerrar o teste.")

        client1_process.wait()

    except FileNotFoundError:
        print("Erro: Não foi possível encontrar os arquivos 'server.py' ou 'client.py'.")
        print("Verifique se este script está na pasta raiz do projeto e se a pasta 'starter' existe.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:

        print("\nEncerrando todos os processos de teste...")
        if server_process:
            server_process.terminate()
        if client1_process:
            client1_process.terminate()
        if client2_process:
            client2_process.terminate()
        print("Processos encerrados.")

if __name__ == "__main__":
    run_tests()