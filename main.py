# I = linha
# J = coluna

import os
import WConio2
import cursor

VAZIO = " "
matrizI = 20
matrizJ = 40
aviaoI = 10
aviaoJ = 19
aviao = "$"
relogio = 0
matriz = []

def limparTela(matriz): 
    '''
        função que limpa a tela do jogo apagando todos os valores 
        da matriz de controle
    '''
    for i in range(matrizI):
        for j in range(matrizJ): 
            matriz[i][j] = VAZIO


def delimitacao(matriz):
    '''
        função que desenha a tela do jogo imprimindo uma sequencia de 
        linhas de strings com conteúdo da matriz de controle do jogo
    '''
    # Imprimir separador vertical na esquerda de cada linha
    for i in range(matrizI):
        print("|", end="")  # Separador na vertical antes de cada linha da matriz
        
        # Imprimir o conteúdo da linha da matriz
        for j in range(matrizJ):
            print(matriz[i][j], end="")

        # Depois de imprimir uma linha da matriz, pular para a próxima linha
        print("|")  # Separador na vertical no final de cada linha

    # Imprimir o separador vertical na parte inferior
    print("_" * (matrizJ + 2))  # Separador parte inferior


#Parte principal do programa
if __name__ == '__main__':
    os.system('cls')
    cursor.hide()

    #inicialiando a matriz de controle
    for i in range(matrizI):
        matriz.append([])
        for j in range(matrizJ):
            matriz[i].append(VAZIO)

    while(True):
        #posicionando cursor da tela sempre no mesmo lugar
        WConio2.gotoxy(0,0)
        

        #limpando a matriz antes de desenhar nela
        limparTela(matriz)

        #colocar personagens dentro da matriz
        matriz[aviaoI][aviaoJ] = aviao

        #impressão na tela
        delimitacao(matriz)

        #atualizando relogio do jogo
        #relogio += 1

        #controlando personages
        if WConio2.kbhit():
            value, symbol = WConio2.getch()

            if symbol == 'a':
                aviaoJ -= 1
            elif symbol == 'd':
                aviaoJ += 1
            elif symbol =='w':
                aviaoI -= 1
            elif symbol =="s":
                aviaoI += 1