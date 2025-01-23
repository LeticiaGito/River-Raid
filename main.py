import os
import WConio2
import cursor
import random
import time
import json

#configurações dos elementos de jogo
VAZIO = " "  # Espaço vazio
RIO = "\033[38;5;33m█\033[0m"  # Rio com a cor azul
AVIAO = "\033[48;42;47m■\033[0m"  # Avião em branco e cinza
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
    print("\033[38;5;3m╔═════════════════╗\033[0m")
    print("\033[38;5;3m║\033[0m    \033[38;5;11mPontuações\033[0m   \033[38;5;3m║\033[0m")
    print("\033[38;5;3m╚═════════════════╝\033[0m")
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

    for deslocamento_x in [-1, 0, 1]:    # Verifica a área ao redor do avião
        for deslocamento_y in [-1, 0, 1]:
            pos_x = aviao_coluna + deslocamento_x
            pos_y = aviao_linha + deslocamento_y
            
            if not 0 <= pos_x < coluna and 0 <= pos_y < linha:    #Verifica se a posição está fora da matriz (Colisão com a borda do mapa)   
                print("Game over! Que pena, você colidiu com a margem do rio!")
                return True
                    
            if matriz[pos_y][pos_x] == OBSTACULO: # Verifica se há um obstáculo
                print("Game Over! Que pena, você colidiu com um obstáculo!")
                return True
                    
            if matriz[pos_y][pos_x] == COMBUSTIVEL: # Verifica se há combustível
                pontuacao += 10
                combustivel = min(combustivel + 20, 100)  # Evita que o combustível ultrapasse 100
                matriz[aviao_linha][aviao_coluna] = RIO  # Remove o combustível após coleta
                matriz[pos_y][pos_x] = RIO  # Limpa a posição do combustível

    return colidiu

# Exibe informações do jogador (pontuação e combustível restante)
def informacoes_do_jogador():
    pontuacao_str = f"\033[38;5;226mPontuação: {pontuacao}\033[0m"#imprime a informação na cor amarela para o jogador
    combustivel_str = f"\033[38;5;226mCombustível: {combustivel:.1f}\033[0m"
    print("")
    return f"{pontuacao_str} | {combustivel_str}"

# Imprime a tela do jogo
def delimitacao(matriz):
    for i in range(linha):
        print("\033[32m█\033[0m" * 2, end="")  # Bordas laterais
        for j in range(coluna):
            print(matriz[i][j], end="")
        print("\033[32m█\033[0m" * 2)
    print(informacoes_do_jogador().center(coluna + 4))#Exibe as informações do jogador
    print("")
   

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

# Função que exibe o menu de pausa
def tela_de_pause():
    global pausado
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela
    print("\033[38;5;3m╔═══════════════════════════╗\033[0m")
    print("\033[38;5;3m║                           ║\033[0m")
    print("\033[38;5;3m║\033[0m        \033[38;5;11mJOGO PAUSADO\033[0m     \033[38;5;3m  ║\033[0m")
    print("\033[38;5;3m║                           ║\033[0m")
    print("\033[38;5;3m║   ╔═══════════════════╗   ║\033[0m")
    print("\033[38;5;3m║   ║\033[0m   \033[38;5;11m1.Retomar jogo\033[0m\033[38;5;3m  ║   ║\033[0m")
    print("\033[38;5;3m║   ╚═══════════════════╝   ║\033[0m")
    print("\033[38;5;3m║   ╔═══════════════════╗   ║\033[0m")
    print("\033[38;5;3m║   ║\033[0m       \033[38;5;11m2.Sair\033[0m      \033[38;5;3m║   ║\033[0m")
    print("\033[38;5;3m║   ╚═══════════════════╝   ║\033[0m")
    print("\033[38;5;3m║                           ║\033[0m")
    print("\033[38;5;3m╚═══════════════════════════╝\033[0m")
    while True:
        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla in ['1']:
                return False
        
            elif tecla in ['2']:
                return True
        
            else: 
                print('Opção inválida.')

            return False

def animacao_explosao():
    explosao_frames = [
        ["   *   ", "  * *  ", "   *   "],  # Explosão inicial
        ["  * *  ", " *   * ", "  * *  "],  # Expansão da explosão
        [" *   * ", " * * * ", " *   * "],  # Fragmentação
        ["  * *  ", " * * * ", "  * *  "],  # Fragmentação
    ]
   
    # Cor vermelha para a explosão
    cor_explosao = "\033[48;5;196m"  # Vermelho

    for frame in explosao_frames:
        # Preenche a matriz com a animação da explosão
        os.system('cls' if os.name == 'nt' else 'clear')

        for i in range(3):
            for j in range(5):
                if 0 <= aviao_linha + i - 1 < linha and 0 <= aviao_coluna + j - 2 < coluna:
                    if frame[i][j] != " ":
                        matriz[aviao_linha + i - 1][aviao_coluna + j - 2] = cor_explosao + frame[i][j] + "\033[0m"
       
        delimitacao(matriz)
        time.sleep(0.2)  # Espera entre os quadros da animação

# Parte principal do programa
def jogar():
    global pausado, combustivel, pontuacao, velocidade, relogio, aviao_coluna
    reiniciar_jogo()
    cursor.hide()

    while True:

        if pausado:
            if tela_de_pause():
                break
            pausado = False
            continue

        # Posiciona o cursor no canto superior esquerdo da tela
        WConio2.gotoxy(0, 0)
                
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
            animacao_explosao()  # Exibe animação de explosão
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
            elif tecla in ['\u001B']:
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
        # Exibe o menu apenas uma vez
        os.system('cls')
  
        print("\033[38;5;3m╔═══════════════════════════╗\033[0m")
        print("\033[38;5;3m║                           ║\033[0m")
        print("\033[38;5;3m║           \033[38;5;11mMENU\033[0m            \033[38;5;3m║\033[0m")
        print("\033[38;5;3m║    ╔═════════════════╗    ║\033[0m")
        print("\033[38;5;3m║    ║     \033[38;5;11m1.Jogar\033[0m     \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m")
        print("\033[38;5;3m║    ╚═════════════════╝    ║\033[0m")
        print("\033[38;5;3m║    ╔═════════════════╗    ║\033[0m")
        print("\033[38;5;3m║    ║   \033[38;5;11m2.Pontuação\033[0m   \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m")
        print("\033[38;5;3m║    ╚═════════════════╝    ║\033[0m")
        print("\033[38;5;3m║    ╔═════════════════╗    ║\033[0m")
        print("\033[38;5;3m║    ║  \033[38;5;11m3.Como jogar?\033[0m  \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m")
        print("\033[38;5;3m║    ╚═════════════════╝    ║\033[0m")
        print("\033[38;5;3m║    ╔═════════════════╗    ║\033[0m")
        print("\033[38;5;3m║    ║      \033[38;5;11m4.Sair\033[0m     \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m")
        print("\033[38;5;3m║    ╚═════════════════╝    ║\033[0m")
        print("\033[38;5;3m║                           ║\033[0m")
        print("\033[38;5;3m╚═══════════════════════════╝\033[0m")
        
        tecla = None
        while tecla not in ['1', '2', '3', '4']:  
            if WConio2.kbhit():
                _, tecla = WConio2.getch()

        if tecla == '1':  # Jogar
            pontuacao_final = jogar()
            print(f"Sua pontuação final foi: {pontuacao_final}")
            salvar_opcao = input("Deseja salvar sua pontuação? (s/n): ").strip().lower()

            if salvar_opcao == "s":
                nome_jogador = input("Digite seu nome: ")
                salvar_pontuacao(nome_jogador, pontuacao_final)
                print("Pontuação salva com sucesso!")

            # Aguardar o Enter para voltar ao menu
            print("Pressione Enter para voltar ao menu...")
            while True:
                if WConio2.kbhit():
                    _, tecla = WConio2.getch()
                    if tecla == '\r':  
                        break  

        elif tecla == '2':  # Highscores
            os.system('cls' if os.name == 'nt' else 'clear')
            exibir_pontuacoes()

            # Aguardar o Enter para voltar ao menu
            print("Pressione Enter para voltar ao menu...")
            while True:
                if WConio2.kbhit():
                    _, tecla = WConio2.getch()
                    if tecla == '\r':  
                        break

        elif tecla == '3':
            os.system('cls')
            print("\033[38;5;3m╔═══════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[38;5;3m║                                                               ║\033[0m")
            print("\033[38;5;3m║  Voe o máximo que conseguir,                                  ║\033[0m")  
            print("\033[38;5;3m║  evitando obstáculos e                     __/\__             ║\033[0m")
            print("\033[38;5;3m║  coletando gasolina.                      `==/\==`            ║\033[0m")
            print("\033[38;5;3m║                                 ____________/__\____________  ║\033[0m")
            print("\033[38;5;3m║  Você perde se colidir com     /____________________________\ ║\033[0m")
            print("\033[38;5;3m║  um obstáculo ou                 __||__||__/.--.\__||__||_    ║\033[0m")
            print("\033[38;5;3m║  quando o combustível acabar.   /__|___|___( >< )___|___|__\  ║\033[0m")
            print("\033[38;5;3m║                                           _/`--`\_            ║\033[0m")
            print("\033[38;5;3m║  Controles:                              (/------\)           ║\033[0m")
            print("\033[38;5;3m║                                                               ║\033[0m") 
            print("\033[38;5;3m║  [D] Direita           _ .                                    ║\033[0m") 
            print("\033[38;5;3m║  [A] Esquerda        (  _ )_                   _              ║\033[0m")
            print("\033[38;5;3m║  [W] Atirar         (_  _(_ ,)                (  )            ║\033[0m")  
            print("\033[38;5;3m║  [ESC] Pausar                              ( `  ) . )         ║\033[0m")
            print("\033[38;5;3m║                                           (_, _(  ,_)_)       ║\033[0m")
            print("\033[38;5;3m║                                                               ║\033[0m")   
            print("\033[38;5;3m╚═══════════════════════════════════════════════════════════════╝\033[0m")
            print("")
            print("Pressione Enter para voltar ao menu...")
            
            while True:
                if WConio2.kbhit():
                    _, tecla = WConio2.getch()
                    if tecla == '\r':  
                        break

        elif tecla == '4':  # Sair
            print("Saindo do jogo. Até logo!")
            break  # Encerra o loop principal e sai do programa

#iniciar o menu
if __name__ == "__main__":
    main_menu()
