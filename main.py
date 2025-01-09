import os
import WConio2
import cursor

VAZIO = " "  # Espaço vazio
RIO = "\033[38;5;33m\u2588\033[0m"  # Rio com a cor azul
linha = 20
coluna = 25
aviao_linha = 8 #Posição do avião linha
aviao_coluna = 12  # Posição do avião coluna
aviao = "\033[48;5;196m\u2588\033[0m"  # Avião
relogio = 0
matriz = []

# Limpa a matriz preenchendo todos os valores com o símbolo do rio.
def limparTela(matriz): 
    for i in range(linha):
        for j in range(coluna):
            matriz[i][j] = RIO

# Desenha a tela do jogo com delimitadores laterais em verde e o conteúdo da matriz no meio.
def delimitacao(matriz):
    for i in range(linha):
        # Delimitadores laterais
        print("\033[32m\u2588\033[0m" * 2, end="")  
        for j in range(coluna):
            print(matriz[i][j], end="")
        print("\033[32m\u2588\033[0m" * 2)
    print(" " * (coluna + 4))  # Espaçamento inferior

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
        
        # Movimentos automáticos do jogo
        if relogio % 500 == 0 and aviao_linha < linha - 1:
            aviao_linha += 1       

        # Limpa a matriz antes de desenhar
        limparTela(matriz)

        # Garantindo que o avião permaneça dentro da matriz
        aviao_linha = max(1, min(aviao_linha, linha - 2))
        aviao_coluna = max(1, min(aviao_coluna, coluna - 2))

        # Desenha o avião na matriz (verificando os limites)
        matriz[aviao_linha][aviao_coluna] = aviao
        if aviao_coluna + 1 < coluna:
            matriz[aviao_linha][aviao_coluna + 1] = aviao
        if aviao_coluna - 1 >= 0:
            matriz[aviao_linha][aviao_coluna - 1] = aviao
        if aviao_linha - 1 >= 0:
            matriz[aviao_linha - 1][aviao_coluna] = aviao
        if aviao_linha + 1 < linha:
            matriz[aviao_linha + 1][aviao_coluna] = aviao

        # Imprime a tela com a matriz
        delimitacao(matriz)

        # Atualiza o relógio do jogo
        relogio += 1

        # Controle do avião
        if WConio2.kbhit():
            value, symbol = WConio2.getch()
            if symbol == 'a':  # Esquerda
                aviao_coluna -= 1
            elif symbol == 'd':  # Direita
                aviao_coluna += 1
            elif symbol == 'w':  # Cima
                aviao_linha -= 1
            elif symbol == 's':  # Baixo
                aviao_linha += 1