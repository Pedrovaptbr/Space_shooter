import subprocess
import sys

def run_git_command(command):
    """Executa um comando Git e verifica se houve erros."""
    try:
        # Usar uma lista de argumentos é mais seguro que shell=True
        result = subprocess.run(command, check=True, text=True, capture_output=True, encoding='utf-8')
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {' '.join(command)}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Erro: O comando 'git' não foi encontrado. Verifique se o Git está instalado e no PATH.")
        sys.exit(1)

def main():
    """Função principal para automatizar o deploy no GitHub."""
    try:
        # 1. Pedir o título do commit (obrigatório)
        commit_title = input("Digite o título do commit: ")
        if not commit_title:
            print("O título do commit não pode ser vazio. Abortando.")
            sys.exit(1)

        # 2. Pedir a descrição longa (opcional)
        print("Digite a descrição longa (pressione Enter duas vezes para finalizar): ")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        commit_description = "\n".join(lines)

    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário. Abortando.")
        sys.exit(0)

    # 3. Adicionar todos os arquivos
    print("\n--- Adicionando todos os arquivos (git add .) ---")
    run_git_command(["git", "add", "."])

    # 4. Construir e executar o comando de commit
    print(f"\n--- Criando commit ---")
    commit_command = ["git", "commit", "-m", commit_title]
    if commit_description:
        commit_command.extend(["-m", commit_description])
    run_git_command(commit_command)

    # 5. Enviar para o GitHub (com a flag -u)
    print("\n--- Enviando para o GitHub (git push) ---")
    run_git_command(["git", "push", "-u", "origin", "HEAD"])

    print("\n✅ Projeto enviado com sucesso para o GitHub!")

if __name__ == "__main__":
    main()
