import os
import WConio2
import cursor
import random
import time
import json

#configurações dos elementos de jogo
VAZIO = " "  # Espaço vazio
RIO = "\033[38;5;33m█\033[0m"  # Rio com a cor azul
AVIAO = "\033[48;5;196m█\033[0m"  
OBSTACULO = "\033[48;5;196m■\033[0m"  # Obstáculo em vermelho
COMBUSTIVEL = "\033[48;5;226m▲\033[0m"  # Combustível em amarelo

#dimensões do mapa no jogo
linha = 20
coluna = 25
aviao_linha = linha - 3 #Posição do avião linha
aviao_coluna = coluna // 2  # Posição do avião coluna
matriz = []

#Variáveis do jogo
relogio = 0
combustivel = 100
velocidade = 0.1 #velocidade inicial do jogo
pontuacao = 0 
pausado = False

#arquivo que salva as pontuações
arquivo_pontuacao = "pontuacao.json"

#função para carregar as pontuações do arquivo
def carregar_pontuacoes():
    if os.path.exists(arquivo_pontuacao):
        with open(arquivo_pontuacao, "r") as arquivo:
            return json.load(arquivo)
    return []

#função para salvar uma nova pontuação
def salvar_pontuacao(nome_jogador, pontuacao_final):
    pontuacoes = carregar_pontuacoes()
    pontuacoes.append({"nome": nome_jogador, "pontuacao": pontuacao_final})

    #filtra pontuações válidas
    pontuacoes = [pontuacao for pontuacao in pontuacoes if pontuacao.get("pontuacao") is not None]

    #ordena as pontuações
    pontuacoes = sorted(pontuacoes, key=lambda x: x["pontuacao"], reverse=True)

    # Salva as pontuações ordenadas no arquivo
    with open(arquivo_pontuacao, "w") as arquivo:
        json.dump(pontuacoes, arquivo, indent=4)

#função para exibir as pontuações no menu
def exibir_pontuacoes():
    pontuacoes = carregar_pontuacoes()
    print("\n=== Pontuações Salvas ===")
    if pontuacoes:
        for rank, entrada in enumerate(pontuacoes, start=1):
            print(f"{rank}. {entrada['nome']} - {entrada['pontuacao']}")
    else:
        print("Nenhuma pontuação salva ainda!")

#limpa a matriz preenchendo todos os valores com o símbolo do rio.
def limparTela(matriz): 
    for i in range(linha):
        for j in range(coluna):
            matriz[i][j] = RIO
            
#Limpa a antiga posição do avião antes de redesenhar:
def limpar_posicao():
    for deslocamento_x in [-1, 0, 1]:
        for deslocamento_y in [-1, 0, 1]:
            pos_x = aviao_coluna + deslocamento_x
            pos_y = aviao_linha + deslocamento_y
            if 0 <= pos_x < coluna and 0 <= pos_y <linha:
                 matriz[pos_y][pos_x] = RIO

#limpa a antiga posição do avião antes de redesenhar
def limpar_posicao():
    matriz[aviao_linha][aviao_coluna] = RIO

#Desenha o avião na nova posição 
def desenhar_aviao():
    matriz[aviao_linha][aviao_coluna] = AVIAO


# Move os obstáculos para baixo e remove os que saírem da tela
def mover_obstaculos():
    for i in range(linha - 1, -1, -1):  # Itera de baixo para cima
        for j in range(coluna):
            if matriz[i][j] in [OBSTACULO, COMBUSTIVEL]:
                if i == linha - 1:  # Remove obstáculos na última linha
                    matriz[i][j] = RIO
                else:  # Move obstáculos para baixo
                    if matriz[i + 1][j] == RIO:  # Apenas move se a posição abaixo estiver vazia
                        matriz[i + 1][j] = matriz[i][j]
                        matriz[i][j] = RIO
                        
# Adiciona novos obstáculos e combustíveis na linha superior
def adicionar_obstaculos():
    num_objetos = random.randint(1, 1)  # Define o número de objetos a adicionar
    for _ in range(num_objetos):
        tipo_objeto = random.choice([OBSTACULO, COMBUSTIVEL])
        coluna_random = random.randint(0, coluna - 1)
        if matriz[0][coluna_random] == RIO:
            matriz[0][coluna_random] = tipo_objeto
                
#Detecta colisões
def detectar_colisao():
    global pontuacao, combustivel
    colidiu = False

    for deslocamento_x in [-1, 0, 1]:
        for deslocamento_y in [-1, 0, 1]:
            pos_x = aviao_coluna + deslocamento_x
            pos_y = aviao_linha + deslocamento_y
            if 0 <= pos_x < coluna and 0 <= pos_y < linha:
                if matriz[pos_y][pos_x] == OBSTACULO:
                    print("Game Over! Que pena, você colidiu com um obstáculo!")
                    colidiu = True
                elif matriz[pos_y][pos_x] == COMBUSTIVEL:
                    pontuacao += 10
                    combustivel = min(combustivel + 20, 100)  # Evita que o combustível ultrapasse 100
                    matriz[aviao_linha][aviao_coluna] = RIO  # Remove o combustível após coleta
                    matriz[pos_y][pos_x] = RIO  # Limpa a posição do combustível

    return colidiu

# Exibe informações do jogador (pontuação e combustível restante)
def informacoes_do_jogador():
    return f"Pontuação: {pontuacao} | Combustível: {combustivel:.1f}"

# Imprime a tela do jogo
def delimitacao(matriz):
    for i in range(linha):
        print("\033[32m█\033[0m" * 2, end="")  # Bordas laterais
        for j in range(coluna):
            print(matriz[i][j], end="")
        print("\033[32m█\033[0m" * 2)
    print(informacoes_do_jogador().center(coluna + 4))#Exibe as informações do jogador
   

# Função para reiniciar o estado do jogo
def reiniciar_jogo():
    global pontuacao, combustivel, relogio, aviao_linha, aviao_coluna, matriz

    # Reinicia as variáveis do jogo
    pontuacao = 0
    combustivel = 100
    relogio = 0
    aviao_linha = linha - 3  # Posição inicial do avião na linha
    aviao_coluna = coluna // 2  # Posição inicial do avião na coluna

    # Reinicia a matriz (preenchendo com o rio)
    matriz = [[RIO] * coluna for _ in range(linha)]

# Inicialização da matriz
for i in range(linha):
    matriz.append([RIO] * coluna)

#Função que exibe o menu de pausa
def tela_de_pause():
    global pausado 
    os.system('cls' if os.name == 'nt' else 'clear')  # Limpa a tela
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                        MENU DE PAUSE                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")

    print("         ╔═════════════════╗   ╔═════════════════╗  ")
    print("         ║ 1.Retomar jogo  ║   ║    2. Sair      ║  ")
    print("         ╚═════════════════╝   ╚═════════════════╝  ")
    print("")

    while True:
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            pausado = False
            break
        elif escolha == "2":
                return True  
        else:
            print("Opção inválida. Tente novamente.")
    return False
    
# Parte principal do programa
def jogar():
    global pausado, combustivel, pontuacao, velocidade, relogio, aviao_coluna
    reiniciar_jogo()
    cursor.hide()

    while True:
        # Posiciona o cursor no canto superior esquerdo da tela
        WConio2.gotoxy(0, 0)

        # Verifica se o jogo está pausado
        if pausado:
            if tela_de_pause():  # Exibe o menu de pausa
                break  # Sai para o menu principal
                
        #limpa a posição anterior do avião
        limpar_posicao()
        mover_obstaculos()
        adicionar_obstaculos()

        #atualiza a posição do avião
        desenhar_aviao()

        #exibe a tela
        delimitacao(matriz)

        #detecta colisões
        if detectar_colisao():
            break

        #diminui a quantidade de combustível gradualmente
        combustivel -= 0.5
        if combustivel <= 0:
            print("Game Over! O seu combustível acabou!")
            break

        #controle do avião
        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla in ['a', 'A'] and aviao_coluna > 0:  # Esquerda
                limpar_posicao()
                aviao_coluna -= 1
            elif tecla in ['d', 'D'] and aviao_coluna < coluna - 1:  # Direita
                limpar_posicao()
                aviao_coluna += 1
            elif tecla in ['p', 'P']:  # Pausa
                pausado = True
            time.sleep(0.0005)  #reduz a pausa após o movimento do avião

        #ajusta a dificuldade com o tempo
        relogio += 1
        if relogio % 100 == 0:
            velocidade = max(0.02, velocidade - 0.005)  # Aumenta a velocidade

        #Pausa para desacelerar
        time.sleep(velocidade)

    cursor.show()
    limparTela(matriz) #limpar a tela sem piscar
    return pontuacao  #retorna a pontuação final

#menu
def main_menu():
    while True:
        print("\n=== Menu Principal ===")
        print("1. Jogar")
        print("2. Ver Pontuações")
        print("3. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            pontuacao_final = jogar()
            print(f"Sua pontuação final foi: {pontuacao_final}")
            salvar_opcao = input("Deseja salvar sua pontuação? (s/n): ").strip().lower()
            if salvar_opcao == "s":
                nome_jogador = input("Digite seu nome: ")
                salvar_pontuacao(nome_jogador, pontuacao_final)
                print("Pontuação salva com sucesso!")
        elif escolha == "2":
            exibir_pontuacoes()
        elif escolha == "3":
            print("Saindo do jogo. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

#iniciar o menu
if __name__ == "__main__":
    main_menu()

