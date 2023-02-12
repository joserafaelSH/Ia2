from jogo import Jogo
from enums import Resultado
from enums import Resposta
from enums import EstadoJogo

def main():
    jogo = Jogo() 
    pontosP1 = 0
    pontosP2 = 0
    userInput = ''

    while userInput.upper() != 'X':
        cardP1 = jogo.distribuirCartas()
        cardP2 = jogo.distribuirCartas()

        pontos = jogo.simulaRodada(cardP1, cardP2)

        resultado = jogo.calcularResultado(cardP1, cardP2)
        print(f'\n - Resultado do Jogo -\n')
        print(f'Player 1: {cardP1} - Probabilidade prévia de vitória: {jogo.probWin(cardP1):.2f}')
        print(f'Player 2: {cardP2} - Probabilidade prévia de vitória: {jogo.probWin(cardP2):.2f}')
        print(f'Resultado: {pontos} PONTO(S)')

        if pontos > 0:
            pontosP1 += pontos
        else:
            pontosP2 -= pontos

        print(f'------------------------------------------------------------------')
        print(f' - Score -\n')
        print(f'Jogador 1: {pontosP1} Pontos')
        print(f'Jogador 2: {pontosP2} Pontos\n')
        userInput = input('Sair (X) ou Continuar (Enter)? ')
        print(f'\n==================================================================\n')


if __name__ == "__main__":
    main()