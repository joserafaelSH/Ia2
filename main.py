from jogo import Jogo
from enums import Resultado
from enums import Resposta
from enums import EstadoJogo

def main():
    jogo = Jogo() 
    while 1:
        cardP1 = jogo.distribuirCartas()
        cardP2 = jogo.distribuirCartas()

        print('\n====================================================================\n')

        print(f'Player1: {cardP1}')


        decisao = int(input('1 - Aceitar, 2 - Trucar, 3 - Correr): '))
        print(f'utilidade esperada de trucar: {jogo.utilidadeEsperadaTrucar(True, cardP1):.2f}')
        print(f'utilidade esperada de correr: {jogo.utilidadeEsperadaCorrer(True, cardP1):.2f}')
    
        print('\nPonto de vista Jogador1:')
        for trucar in [True, False]:
            for respP2 in list(Resposta):
                for respP1 in list(Resposta):
                    UE_RespP1 = jogo.utilidadeEsperadaRespostaP1(respP1, respP2, trucar, cardP1)
                    print(f'utilidadeEsperada: {UE_RespP1:.2f} / Truco: {trucar}, RespP2: {respP2}, RespP1: {respP1}')
            
        resultado = jogo.calcularResultado(cardP1, cardP2)
        print(f'Player2: {cardP2}')
        print(f'resultado: {resultado.name}')

        print('\nPonto de vista Jogador2:')
        for trucar in [True, False]:
            for respP2 in list(Resposta):
                UE_RespP2 = jogo.utilidadeEsperadaRespostaP2(respP2, trucar, cardP2)
                print(f'utilidadeEsperada: {UE_RespP2:.2f} / Truco: {trucar}, RespP2: {respP2}')

        x = input()

if __name__ == "__main__":
    main()