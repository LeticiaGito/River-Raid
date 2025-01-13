import os
import WConio2
import cursor
import random
import time

#Função para o menu
def menu():
    while True:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                            MENU                            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print("")
        print("╔═════════════════╗   ╔═════════════════╗  ╔═════════════════╗")
        print("║  1. Instruções  ║   ║ 2. Iniciar jogo ║  ║     3. Sair     ║")
        print("╚═════════════════╝   ╚═════════════════╝  ╚═════════════════╝")
        print("")

        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            instrucoes()
        elif opcao == "2":
            iniciar_jogo()
        elif opcao == "3":
            print("Saindo do jogo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def instrucoes():
    while True:
        print("Instruções de como jogar:")
        print("O objetivo do jogo é controlar um avião enquanto desvia e destrói tudo que estiver no seu caminho e, ao destruir, o jogador recebe pontos e combustível para continuar avançando.")
        print("")

        opcao = input("Digite 'm' para voltar ao menu: ")
        if opcao.lower() == 'm':
            break


def iniciar_jogo():
    print("Jogo iniciado!")
    jogar()

    #configurações dos elementos de jogo
def jogar():
    VAZIO = " "  # Espaço vazio
    RIO = "\033[38;5;33m\u2588\033[0m"  # Rio com a cor azul
    AVIAO = "\033[48;5;196m\u2588\033[0m"  # Avião
    OBSTACULO = "\033[48;5;196m\u25A0\033[0m"  # Obstáculo em vermelho
    COMBUSTIVEL = "\033[48;5;226m\u25B2\033[0m"  # Combustível em amarelo

    #dimensões do mapa no jogo
    linha = 20
    coluna = 25
    aviao_linha = 8 #Posição do avião linha
    aviao_coluna = 12  # Posição do avião coluna
    relogio = 0
    matriz = []
    combustivel = 100
    velocidade = 0.1
    pontuacao = 0 


    # Limpa a matriz preenchendo todos os valores com o símbolo do rio.
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

    #Desenha o avião na nova posição 
    def desenhar_aviao():
        matriz[aviao_linha][aviao_coluna] = AVIAO

    # Desenha a tela do jogo com delimitadores laterais em verde e o conteúdo da matriz no meio.
    def delimitacao(matriz):
        for i in range(linha):
            # Delimitadores laterais
            print("\033[32m\u2588\033[0m" * 2, end="")  
            for j in range(coluna):
                print(matriz[i][j], end="")
            print("\033[32m\u2588\033[0m" * 2)
        print(" " * (coluna + 4))  # Espaçamento inferior

    #Adiciona os obstáculos e combustíveis
    def adicionar_obstaculos():
        for _ in range(3):
            tipo_objeto = random.choice([OBSTACULO, COMBUSTIVEL])
            while True:
                coluna_random = random.randint(0, coluna - 1)
                linha_random = random.randint(0, linha - 1)
                if matriz[linha_random][coluna_random] == RIO:
                    matriz[linha_random][coluna_random] = tipo_objeto
                    break
    #Detecta colisões
    def detectar_colisao():
        global pontuacao, combustivel
        colidiu = False

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = aviao_coluna + dx
                y = aviao_linha + dy
                if 0 <= x < coluna and 0 <= y < linha:
                    if matriz[y][x] == OBSTACULO:
                        print("Game Over! Que pena, você colidiu com um obstáculo!")
                        colidiu = True
                    elif matriz[y][x] == COMBUSTIVEL:
                        pontuacao += 10
                        combustivel += 20
                        matriz[y][x] = RIO  # Limpa a posição do combustível

        return colidiu


    # Parte principal do programa
    if __name__ == '__main__':
        os.system('cls' if os.name == 'nt' else 'clear')
        cursor.hide()

        # Inicializando a matriz com valores vazios
        for i in range(linha):
            matriz.append([VAZIO] * coluna)

        while True:
            # Posiciona o cursor no canto superior esquerdo da tela
            WConio2.gotoxy(0, 0)

            #limpa a posição anterior do avião
            limpar_posicao()

            #Diminui a quantidade de combustível gradualmente
            combustivel -= 1
            if combustivel <= 0:
                print("Game Over! O seu combustível acabou!")
                break
            
            # Movimentos automáticos do jogo
            if relogio % 500 == 0 and aviao_linha < linha - 1:
                aviao_linha += 1       

            # Limpa a matriz antes de desenhar
            limparTela(matriz)

            #Adiciona os obstáculos e combustíveis 
            adicionar_obstaculos()
            
            # Garantindo que o avião permaneça dentro da matriz
            aviao_linha = max(1, min(aviao_linha, linha - 2))
            aviao_coluna = max(1, min(aviao_coluna, coluna - 2))

            #Desenha o avião na nova posição
            desenhar_aviao()
            
            #desenha o avião na matriz verificando os limites 
            matriz[aviao_linha][aviao_coluna] = AVIAO
            if aviao_coluna + 1 < coluna:
                matriz[aviao_linha][aviao_coluna + 1] = AVIAO
            if aviao_coluna - 1 >= 0:
                matriz[aviao_linha][aviao_coluna - 1] = AVIAO
            if aviao_linha - 1 >= 0:
                matriz[aviao_linha - 1][aviao_coluna] = AVIAO
            if aviao_linha + 1 < linha:
                matriz[aviao_linha + 1][aviao_coluna] = AVIAO

            # Imprime a tela com a matriz
            delimitacao(matriz)

            #Detecta as colisões
            if detectar_colisao():
                break 

            # Atualiza o relógio do jogo
            relogio += 1

            # Controle do avião
            if WConio2.kbhit():
                value, symbol = WConio2.getch()
                if symbol in ['a', 'A']:  # Esquerda
                    aviao_coluna -= 1
                elif symbol in ['d', 'D']:  # Direita
                    aviao_coluna += 1
                elif symbol in ['w', 'W']:  # Cima
                    aviao_linha -= 1
                elif symbol in ['s', 'S']:  # Baixo
                    aviao_linha += 1

            #Pausa para desacelerar
            time.sleep(0.1)

menu()