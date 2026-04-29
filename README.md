# 🚀 Space Shooter - Uma Aventura Multiplayer! 🚀

E aí, viajante do GitHub! 👋

Bem-vindo ao meu pequeno grande projeto de um jogo de nave multiplayer feito em Python! 🐍 Se você estava procurando por lasers, explosões e um pouco de caos em rede, você veio ao lugar certo.

## 🌌 A Missão

Este projeto nasceu da minha curiosidade de desvendar os mistérios do universo... do código multiplayer! O objetivo principal aqui é aprender na prática como fazer dois jogadores se conectarem, atirarem um no outro e, o mais importante, se divertirem através da mágica da programação de redes.

Se você encontrar algum buraco de minhoca (bug) ou tiver ideias para novas galáxias (features), saiba que este é o meu playground para aprendizado!

## 🎨 Arte e 🎵 Som

*   **Arte:** Todos os pixels e sprites que você vê por aqui foram desenhados por mim! 🎨✨
*   **Sons:** Os efeitos sonoros e a música são daquele tipo legal que todo mundo pode usar (royalty-free). Então, pode aumentar o volume sem medo! 🎶

## 🛠️ Como Rodar

Pré-requisito: **Python 3.10+** instalado.

```bash
# 1. Clone o projeto
git clone <url-do-repo>
cd Space_shooter

# 2. (opcional, mas recomendado) crie um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Manda bala!
python main.py
```

Quer testar o modo online sozinho rodando servidor + 2 clientes na mesma máquina? Use:

```bash
python test.py
```

## 🎮 Controles

### Modo 2 Jogadores (Local)

| Ação              | Jogador 1 (Azul) | Jogador 2 (Vermelho) |
|-------------------|------------------|----------------------|
| Mover             | `W` `A` `S` `D`  | Setas direcionais    |
| Atirar            | `Espaço`         | `Enter`              |
| Recarregar munição| `R`              | `Right Shift`        |
| Ativar escudo     | `C`              | `Right Ctrl`         |

### Modo Online

Mover com `WASD` e atirar com `Espaço`. Para criar um servidor, vá em **Jogar Online** → **Criar Servidor**, e o IP de rede aparece na tela pra compartilhar com o outro jogador.

### Em qualquer tela

`Esc` volta ao menu / sai do jogo.

## 📦 Download (Em Breve!)

## 📦 Download (Em Breve!)

Para quem não quer mexer com código e só quer sair atirando, relaxa! 😌

Estou planejando adicionar um arquivo `.exe` para download em breve. Assim, você poderá baixar e jogar com apenas alguns cliques. Fique de olho nas "Releases" aqui do GitHub!

Quem já quiser gerar o executável agora, é só rodar:

```bash
python setup.py build
```

(O `cx_Freeze` cuida do resto e gera a pasta `build/`.)

## 📬 Contato

Gostou do projeto? Quer trocar uma ideia, sugerir algo ou até mesmo me contratar? 💼

Mande um e-mail para **pedrohrrribeiro@gmail.com**. Vou adorar conversar com você!
