import os
import WConio2
import cursor
import random
import time
import json
import shutil
import re


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
nivel_dificuldade = 1

#arquivo que salva as pontuações
arquivo_pontuacao = "pontuacao.json"

def centralizar():
    terminal_size = shutil.get_terminal_size()
    terminal_largura = terminal_size.columns
    terminal_altura = terminal_size.lines

    margem_superior = max(0, (terminal_altura - linha) // 2)
    margem_lateral = max(0, (terminal_largura - (coluna + 4)) // 2)

    return margem_superior, margem_lateral

def centralizar_texto(texto, margem_superior=0):
    largura_tela, altura_tela = shutil.get_terminal_size()

    linhas = texto.split('\n')
    espacos_verticais = (altura_tela - len(linhas)) // 2

    # Agora o cálculo da margem superior pode ser ajustado
    espacos_verticais = max(espacos_verticais - margem_superior, 0)

    # Adiciona linhas em branco antes do texto para centralizar verticalmente
    for _ in range(espacos_verticais):
        print()  # Linha em branco para centralizar verticalmente

    # Centraliza cada linha horizontalmente
    for linha in linhas:
        texto_limpo = re.sub(r'\033\[[0-9;]*m', '', linha)
        espacos_esquerda = (largura_tela - len(texto_limpo)) // 2
        print(' ' * espacos_esquerda + linha)


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

    # Cabeçalho "Pontuações" mais próximo do topo
    pontuacao_display = '''
\033[38;5;208m╔══════════════════════════════════════╗\033[38;5;208m
\033[38;5;208m║                Pontuação             ║\033[38;5;208m
\033[38;5;208m╚══════════════════════════════════════╝\033[38;5;208m'''
    centralizar_texto(pontuacao_display, margem_superior=10)  # Ajuste a margem_superior conforme necessário

    # Largura do terminal
    largura_terminal = shutil.get_terminal_size().columns
    margem_lateral = max(0, (largura_terminal - 40) // 2)

    if pontuacoes:
        for rank, entrada in enumerate(pontuacoes, start=1):
            print(" " * margem_lateral + f"{rank}. {entrada['nome']} - {entrada['pontuacao']}")
    else:
        print(" " * margem_lateral + "Nenhuma pontuação salva ainda!")

# Atualiza a pontuação com base no tempo
def atualizar_pontuacao():
    global pontuacao, inicio_tempo
    tempo_jogado = int(time.time() - inicio_tempo)  # Tempo em segundos
    if tempo_jogado <= 30:
        pontuacao = tempo_jogado * 10  # 10 ponto por segundo até 30 segundos
    elif tempo_jogado <= 60:
        pontuacao = 30 + (tempo_jogado - 30) * 15  # 15 pontos por segundo de 31 a 60 segundos
    else:
        pontuacao = 90 + (tempo_jogado - 60) * 20  # 20 pontos por segundo a partir de 61 segundos

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
def adicionar_obstaculos(nivel_dificuldade):
    num_objetos = random.randint(0, nivel_dificuldade)  # Define o número de objetos a adicionar
    combustivel_na_tela = sum(1 for i in range(linha) for j in range(coluna) if matriz[i][j] == COMBUSTIVEL) #conta quantos combustíveis tem na tela
    max_combustivel = 5  # Define o número máximo de combustíveis que podem aparecer na tela

    for _ in range(num_objetos):
        # Escolhe o tipo de objeto
        if combustivel_na_tela < max_combustivel:
            tipo_objeto = random.choice([OBSTACULO, COMBUSTIVEL])  # Combustível só aparece se estiver abaixo do limite
        else:
            tipo_objeto = OBSTACULO  #Caso contrário apenas obstáculos são gerados

        # Escolhe aleatoriamente uma coluna da matriz onde o objeto vai ser colocado
        coluna_random = random.randint(0, coluna - 1)
        if matriz[0][coluna_random] == RIO:
            matriz[0][coluna_random] = tipo_objeto

        # Atualiza a contagem de combustível na tela
        if tipo_objeto == COMBUSTIVEL:
            combustivel_na_tela += 1

                
#Detecta colisões
def detectar_colisao():
    global pontuacao, combustivel
    colidiu = False
    motivo = None

    for deslocamento_x in [-1, 0, 1]:  # Verifica a área ao redor do avião
        for deslocamento_y in [-1, 0, 1]:
            pos_x = aviao_coluna + deslocamento_x
            pos_y = aviao_linha + deslocamento_y

            # Verifica colisão com a margem
            if not (0 <= pos_x < coluna and 0 <= pos_y < linha):
                motivo = "Que pena, você colidiu com a margem do rio!"
                colidiu = True
                break

            # Verifica colisão com obstáculo
            if matriz[pos_y][pos_x] == OBSTACULO:
                motivo = "Que pena, você colidiu com um obstáculo!"
                colidiu = True
                break

            # Verifica se há combustível
            if matriz[pos_y][pos_x] == COMBUSTIVEL:
                combustivel = min(combustivel + 20, 100)  # Evita que o combustível ultrapasse 100
                matriz[pos_y][pos_x] = RIO  # Limpa a posição do combustível

    return colidiu, motivo


# Função para exibir a tela de "Game Over"
def tela_game_over(motivo):
    os.system('cls' if os.name == 'nt' else 'clear')  # Limpa a tela
    game_over_message = f'''
\033[38;5;3m╔══════════════════════════════════════╗\033[0m
\033[38;5;3m║               GAME OVER              ║\033[0m
\033[38;5;3m╚══════════════════════════════════════╝\033[0m

   >> \033[38;5;15m{motivo.center(28)}\033[0m <<  \033[38;5;9m

    '''
    centralizar_texto(game_over_message, margem_superior=5)  # Centraliza a mensagem de Game Over

    # Exibe a pontuação final centralizada
    centralizar_texto(f"\033[38;5;226mPontuação Final: {pontuacao}\033[0m", margem_superior=15)
    print(' ')
    # Pergunta se deseja salvar
    salvar_opcao = input("                                          Deseja salvar sua pontuação? (s/n): ").strip().lower()
    while salvar_opcao not in ['s', 'n']:
        #print("Opção inválida. Digite 's' para sim ou 'n' para não.")
        salvar_opcao = input("Deseja salvar sua pontuação? (s/n): ").strip().lower()

    if salvar_opcao == "s":
        nome_jogador = input("\n                                          Digite seu nome: ")
        salvar_pontuacao(nome_jogador, pontuacao)
        print("\n                                          \033[38;5;40mPontuação salva com sucesso!\033[38;5;40m")
    else:
        print("\n                                          \033[31mSua pontuação não foi salva.\033[31m")

    # Aguardar o Enter para voltar ao menu
    print("\n\n\n\n                                          \033[37mPressione Enter para voltar ao menu...\033[37m")
    while True:
        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla == '\r':  # Verifica se a tecla pressionada é "Enter"
                main_menu()  # Sai do loop e retorna ao menu
 

# Imprime a tela do jogo
def delimitacao(matriz):
    margem_superior, margem_lateral = centralizar()
    tempo_jogado = time.time() - inicio_tempo - tempo_pausado #calcula o tempo 
    print('\n' * (margem_superior - 1), end='')  # Ajusta a margem superior para subir a pontuação
    print(' ' * margem_lateral, end=' ')
    print(f"\033[38;5;226mPontuação: {pontuacao} | Combustível: {combustivel:.1f}| Tempo: {int(tempo_jogado)}s\033[0m".center(coluna + 8))
    print(' ' * margem_lateral, end=' ')
    print(" ")  # Linha separadora

    for i in range(linha):
        print(' ' * margem_lateral, end=' ')
        print("\033[32m█\033[0m" * 4, end="")  # Bordas laterais
        for j in range(coluna):
            print(matriz[i][j], end="")
        print("\033[32m█\033[0m" * 4)


# Função para reiniciar o estado do jogo
def reiniciar_jogo():
    global pontuacao, combustivel, relogio, aviao_linha, aviao_coluna, matriz, inicio_tempo

    # Reinicia as variáveis do jogo
    pontuacao = 0
    combustivel = 100
    relogio = 0
    aviao_linha = linha - 3  # Posição inicial do avião na linha
    aviao_coluna = coluna // 2  # Posição inicial do avião na coluna

    # Reinicia a matriz (preenchendo com o rio)
    matriz = [[RIO] * coluna for _ in range(linha)]

    #reinicia o o cronometro 
    inicio_tempo = time.time()

# Inicialização da matriz
for i in range(linha):
    matriz.append([RIO] * coluna)

# Função que exibe o menu de pausa
def tela_de_pause():
    global pausado, inicio_tempo, tempo_pausado

    #Marca o inicio do tempo de pause 
    inicio_tempo_pausa = time.time()
    
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela

    pause = '''    
\033[38;5;3m╔═══════════════════════════╗\033[0m
\033[38;5;3m║                           ║\033[0m
                            \033[38;5;3m║\033[0m        \033[38;5;11mJOGO PAUSADO\033[0m     \033[38;5;3m  ║\033[0m
\033[38;5;3m║                           ║\033[0m
\033[38;5;3m║   ╔═══════════════════╗   ║\033[0m
\033[38;5;3m║   ║\033[0m   \033[38;5;11m1.Retomar jogo\033[0m\033[38;5;3m  ║   ║\033[0m
\033[38;5;3m║   ╚═══════════════════╝   ║\033[0m
\033[38;5;3m║   ╔═══════════════════╗   ║\033[0m
\033[38;5;3m║   ║\033[0m       \033[38;5;11m2.Sair\033[0m      \033[38;5;3m║   ║\033[0m
\033[38;5;3m║   ╚═══════════════════╝   ║\033[0m
\033[38;5;3m║                           ║\033[0m
\033[38;5;3m╚═══════════════════════════╝\033[0m'''

    centralizar_texto(pause)

    while True:
        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla in ['1']:
                pausado = False
            
                # Atualiza o tempo acumulado com o período de pausa
                tempo_pausado += time.time() - inicio_tempo_pausa
                inicio_tempo_pausa = None
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
# Função principal de jogo
def jogar():
    global nivel_dificuldade, pausado, combustivel, pontuacao, velocidade, relogio, aviao_coluna, inicio_tempo
    reiniciar_jogo()
    cursor.hide()
    nivel_dificuldade = 1
     inicio_tempo = time.time()
     inicio_tempo = time.time()

    while True:
        if pausado:
            if tela_de_pause():
                break
            pausado = False
            continue

        WConio2.gotoxy(0, 0)  # Posiciona o cursor no canto superior esquerdo

        limpar_posicao()
        mover_obstaculos()
        adicionar_obstaculos(nivel_dificuldade)

        desenhar_aviao()
        
        #atualiza a pontuação com base no tempo
        atualizar_pontuacao()

        delimitacao(matriz)

        colidiu, motivo = detectar_colisao()
        if colidiu:
            animacao_explosao()  # Exibe a animação da explosão
            tela_game_over(motivo)  # Exibe a tela de "Game Over" com o motivo
            break  # Encerra o loop ou reinicia o jogo

        combustivel -= 0.5
        if combustivel <= 0:
            animacao_explosao()
            tela_game_over("O seu combustível acabou!")
            break

        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla in ['a', 'A'] and aviao_coluna > 0:  # Esquerda
                limpar_posicao()
                aviao_coluna -= 1
            elif tecla in ['d', 'D'] and aviao_coluna < coluna - 1:  # Direita
                limpar_posicao()
                aviao_coluna += 1
            elif tecla in ['\u001B']:  # Pausar
                pausado = True

            time.sleep(0.0005)

        relogio += 1
        if relogio % 100 == 0:
            velocidade = max(0.02, velocidade - 0.005)
            nivel_dificuldade = min(nivel_dificuldade + 1, 5)#ajusta o limite máximo de dificuldade
        time.sleep(velocidade)

    cursor.show()
    limparTela(matriz)
    return pontuacao

def exibir_capa():
    capa = ["""
██████╗ ██╗██╗   ██╗███████╗██████╗      
██╔══██╗██║██║   ██║██╔════╝██╔══██╗    
██████╔╝██║██║   ██║█████╗  ██████╔╝    
██╔══██╗██║╚██╗ ██╔╝██╔══╝  ██╔══██╗    
██║  ██║██║ ╚████╔╝ ███████╗██║  ██║    
╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝     

     ██████╗  █████╗ ██╗██████╗
     ██╔══██╗██╔══██╗██║██╔══██╗
     ██████╔╝███████║██║██║  ██║
     ██╔══██╗██╔══██║██║██║  ██║
     ██║  ██║██║  ██║██║██████╔╝
     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝
    """]

    #faz o efeito de digitação da frase
    frase = capa [0]
    for i in list(frase):
        print(i, end='', flush=True)
        time.sleep(0.004)

    print("\nPressione Enter para ir ao menu...")
            
    while True:
        if WConio2.kbhit():
            _, tecla = WConio2.getch()
            if tecla == '\r':  
                 break

#menu
def main_menu():
    
    while True:
        # Exibe o menu apenas uma vez
        os.system('cls')
  
        menu = '''
\033[38;5;3m╔═══════════════════════════╗\033[0m
\033[38;5;3m║                           ║\033[0m
\033[38;5;3m║           \033[38;5;11mMENU\033[0m            \033[38;5;3m║\033[0m
\033[38;5;3m║    ╔═════════════════╗    ║\033[0m
\033[38;5;3m║    ║     \033[38;5;11m1.Jogar\033[0m     \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m
\033[38;5;3m║    ╚═════════════════╝    ║\033[0m
\033[38;5;3m║    ╔═════════════════╗    ║\033[0m
\033[38;5;3m║    ║   \033[38;5;11m2.Pontuação\033[0m   \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m
\033[38;5;3m║    ╚═════════════════╝    ║\033[0m
\033[38;5;3m║    ╔═════════════════╗    ║\033[0m
\033[38;5;3m║    ║  \033[38;5;11m3.Como jogar?\033[0m  \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m
\033[38;5;3m║    ╚═════════════════╝    ║\033[0m
\033[38;5;3m║    ╔═════════════════╗    ║\033[0m
\033[38;5;3m║    ║      \033[38;5;11m4.Sair\033[0m     \033[38;5;3m║\033[0m    \033[38;5;3m║\033[0m
\033[38;5;3m║    ╚═════════════════╝    ║\033[0m
\033[38;5;3m║                           ║\033[0m
\033[38;5;3m╚═══════════════════════════╝\033[0m
        '''

        centralizar_texto(menu)


        tecla = None
        while tecla not in ['1', '2', '3', '4']:  
            if WConio2.kbhit():
                _, tecla = WConio2.getch()

        if tecla == '1':  # Jogar
            pontuacao_final = jogar()
            # pontu = print(f"Sua pontuação final foi: {pontuacao_final}")
            # salvar_opcao = input("Deseja salvar sua pontuação? (s/n): ").strip().lower()
            # centralizar(salvar_opcao)
            # centralizar_texto(pontu)


        elif tecla == '2':  # Highscores
            os.system('cls' if os.name == 'nt' else 'clear')
            exibir_pontuacoes()

            # Aguardar o Enter para voltar ao menu
            centralizar_texto(f"\nPressione Enter para voltar ao menu", margem_superior=15)
            while True:
                if WConio2.kbhit():
                    _, tecla = WConio2.getch()
                    if tecla == '\r':  
                        break

        elif tecla == '3':
            os.system('cls')
            instrucoes = '''            
\033[38;5;3m╔═══════════════════════════════════════════════════════════════╗\033[38;5;3m
\033[38;5;3m║                                                               ║\033[38;5;3m
 \033[38;5;3m║  Voe o máximo que conseguir,                                  ║\033[38;5;3m 
\033[38;5;3m║  evitando obstáculos e                     __/\__             ║\033[38;5;3m
\033[38;5;3m║  coletando gasolina.                      `==/\==`            ║\033[38;5;3m
\033[38;5;3m║                                 ____________/__\____________  ║\033[38;5;3m
\033[38;5;3m║  Você perde se colidir com     /____________________________\ ║\033[38;5;3m
\033[38;5;3m║  um obstáculo ou                 __||__||__/.--.\__||__||_    ║\033[38;5;3m
\033[38;5;3m║  quando o combustível acabar.   /__|___|___( >< )___|___|__\  ║\033[38;5;3m
\033[38;5;3m║                                           _/`--`\_            ║\033[38;5;3m
\033[38;5;3m║  Controles:                              (/------\)           ║\033[38;5;3m
\033[38;5;3m║                                                               ║\033[38;5;3m 
\033[38;5;3m║  [D] Direita           _ .                                    ║\033[38;5;3m
\033[38;5;3m║  [A] Esquerda        (  _ )_                   _              ║\033[38;5;3m
\033[38;5;3m║  [W] Atirar         (_  _(_ ,)                (  )            ║\033[38;5;3m
\033[38;5;3m║  [ESC] Pausar                              ( `  ) . )         ║\033[38;5;3m
\033[38;5;3m║                                           (_, _(  ,_)_)       ║\033[38;5;3m
  \033[38;5;3m║                                                               ║\033[38;5;3m  
\033[38;5;3m╚═══════════════════════════════════════════════════════════════╝\033[38;5;3m
            
Pressione Enter para voltar ao menu...'''
            centralizar_texto(instrucoes)

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
    os.system('cls' if os.name == 'nt' else 'clear')
    cursor.hide()
    exibir_capa()
    main_menu()
