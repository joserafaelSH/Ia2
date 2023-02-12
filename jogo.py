import random
from enums import Resultado
from enums import Resposta
from enums import EstadoJogo

class Jogo:
    def __init__(self):
        self.cards = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        self.cardValues = dict(zip(self.cards, [x for x in range(len(self.cards))] ))

    #####################################################
    # Probabilidades

    def probWin(self, card:str)->float:
        val = self.cardValues[card]
        pWin = val*4/39
        return pWin

    def probLoss(self, card:str):
        val = self.cardValues[card]
        pLoss = (9-val)*4/39
        return pLoss

    def probTie(self):
        return 3/39

    #####################################################
    # Funções de Jogo

    def distribuirCartas(self):
        numeroDeCartas = len(self.cards) 
        return self.cards[random.randint(0,numeroDeCartas-1)]

    def calcularResultado(self, card1:str, card2:str) -> Resultado:
        cardValue1 = self.cardValues[card1]
        cardValue2 = self.cardValues[card2]
        if cardValue1 == cardValue2: return Resultado.EMPATOU
        return Resultado.GANHOU if cardValue1 > cardValue2 else Resultado.PERDEU 

    def estadoJogo(self, correu:bool, respostaP1:Resposta, respostaP2: Resposta) -> EstadoJogo:
        if correu or respostaP1 == Resposta.CORRER:
            return EstadoJogo.P1_CORREU
        elif respostaP2 == Resposta.CORRER:
            return EstadoJogo.P2_CORREU
        else:
            return EstadoJogo.NORMAL

    def valorJogo(self, trucou:bool, respostaP2: Resposta, respostaP1:Resposta) -> EstadoJogo:
        trucoP1 = trucou or respostaP1 == Resposta.AUMENTAR
        trucoP2 = respostaP2 == Resposta.AUMENTAR

        if trucoP1 and trucoP2:
            return 6
        if (trucou and trucoP1) or trucoP2:
            return 3
        else:
            return 1

    #####################################################
    # Cálculos de Utilidade

    def utilidade(self,resultado:Resultado, valor:int, estado:EstadoJogo) -> int:
        if estado == EstadoJogo.P1_CORREU:
            pontosCorrer = {1:-1, 3:-1, 6:-3}
            return pontosCorrer[valor]

        if estado == EstadoJogo.P2_CORREU:
            pontosCorrer = {1:1, 3:1, 6:3}
            return pontosCorrer[valor]

        utilidade = valor * resultado.value
        
        return utilidade

    def utilidadeP2(self, resultado:Resultado, valor:int, estado:EstadoJogo) -> int:
        if estado == EstadoJogo.P1_CORREU:
            pontosCorrer = {1:1, 3:1, 6:3}
            return pontosCorrer[valor]

        if estado == EstadoJogo.P2_CORREU:
            pontosCorrer = {1:-1, 3:-1, 6:-3}
            return pontosCorrer[valor]

        utilidade = valor * resultado.value
        
        return utilidade

    def utilidadeEsperadaCorrer(self, correr:bool, card:str) -> float:
        if correr:
            return -1
        
        pWin = self.probWin(card)
        pLoss = self.probLoss(card)
        pTie = self.probTie()

        probResults = [pWin, pTie, pLoss]
        probTrucar = [pWin**2, 1-(pWin**2)]
        # As probabilidades de resposta do outro jogador são desconhecidas, e por isso são fixas a priori
        probRespP2 = [0.25, 0.5, 0.25] # Aumentar, Aceitar e Correr
        probRespP1 = [pWin**2, 1 - (pWin**2 + pLoss**2), pLoss**2]

        utility = 0

        for res, pRes in zip(list(Resultado), probResults):
            for trucar, pTrucar in zip([True, False], probTrucar):
                for respP2, pRespP2 in zip(list(Resposta), probRespP2):
                    for respP1, pRespP1 in zip(list(Resposta), probRespP1):
                        probCaso = pRes * pTrucar * pRespP2 * pRespP1
                        uCaso = self.utilidade(res, self.valorJogo(trucar, respP2, respP1), self.estadoJogo(correr, respP1, respP2))
                        utility += uCaso * probCaso

        return utility
    
    def utilidadeEsperadaTrucar(self, trucar:bool, card:str):
        pWin = self.probWin(card)
        pLoss = self.probLoss(card)
        pTie = self.probTie()

        probResults = [pWin, pTie, pLoss]
        # As probabilidades de resposta do outro jogador são desconhecidas, e por isso são fixas a priori
        if trucar:
            probRespP2 = [0.25, 0.5, 0.25] # Aumentar, Aceitar e Correr
        else: # Se o jogador 1 não trucar, é improvável que o jogador 2 corra
            probRespP2 = [0.1, 0.6, 0.3]
        probRespP1 = [pWin**2, 1 - (pWin**2 + pLoss**2), pLoss**2]

        utility = 0

        for res, pRes in zip(list(Resultado), probResults):
            for respP2, pRespP2 in zip(list(Resposta), probRespP2):
                for respP1, pRespP1 in zip(list(Resposta), probRespP1):
                    probCaso = pRes * pRespP2 * pRespP1
                    uCaso = self.utilidade(res, self.valorJogo(trucar, respP2, respP1), self.estadoJogo(False, respP1, respP2))
                    utility += uCaso * probCaso

        return utility

    def utilidadeEsperadaRespostaP2(self,respostaP2: Resposta, p1Trucou: bool, cardP2: str):
        if respostaP2 == Resposta.CORRER:
            return -1

        pWin = self.probWin(cardP2)
        pLoss = self.probLoss(cardP2)
        pTie = self.probTie()

        probResults = [pWin, pTie, pLoss]
        # As probabilidades de resposta do outro jogador são desconhecidas, e por isso são fixas a priori
        if p1Trucou:
            # Nessa versão o jogo vai até 6 pontos no máximo, por isso não há a possibilidade de P1 pedir 9
            probRespP1 = [1/3, 2/3, 0]
        elif respostaP2 == Resposta.ACEITAR:
            # Se P2 deciciu não pedir truco nem correr, o jogo ocorre normalmente e não há outra resposta para P1 
            probRespP1 = [0, 1, 0]
        else:
            probRespP1 = [0.25, 0.5, 0.25]

        utility = 0

        for res, pRes in zip(list(Resultado), probResults):
            for respP1, pRespP1 in zip(list(Resposta), probRespP1):
                probCaso = pRes * pRespP1
                uCaso = self.utilidadeP2(res, self.valorJogo(p1Trucou, respostaP2, respP1), self.estadoJogo(False, respP1, respostaP2))
                utility += uCaso * probCaso

        return utility

    def utilidadeEsperadaRespostaP1(self, respostaP1: Resposta, respostaP2: Resposta, p1Trucou: bool, card: str):
        pWin = self.probWin(card)
        pLoss = self.probLoss(card)
        pTie = self.probTie()

        probResults = [pWin, pTie, pLoss]

        utility = 0

        for res, pRes in zip(list(Resultado), probResults):
            probCaso = pRes
            uCaso = self.utilidade(res, self.valorJogo(p1Trucou, respostaP2, respostaP1), self.estadoJogo(False, respostaP1, respostaP2))
            utility += uCaso * probCaso

        return utility

    # FUNÇÃO DE TESTE
    # Calcula a utilidade de todas as situações de jogo
    def testes(self):
        print('\nUtilidades P1')
        for estado in list(EstadoJogo):
            for resultado in list(Resultado):
                for valor in [1, 3, 6]:
                    print(f'E:{estado.name}, R:{resultado.name}, V:{valor} -> U:{self.utilidade(resultado, valor, estado)}')

        print('\nUtilidades P2')
        for estado in list(EstadoJogo):
            for resultado in list(Resultado):
                for valor in [1, 3, 6]:
                    print(f'E:{estado.name}, R:{resultado.name}, V:{valor} -> U:{self.utilidadeP2(resultado, valor, estado)}')

        print('\nEstados de Jogo')
        for correu in [True, False]:
            for p1 in list(Resposta):
                for p2 in list(Resposta):
                    print(f'Correu:{correu}, P1:{p1.name}, P2:{p2.name} -> {self.estadoJogo(correu, p1, p2).name}')

        print('\nValores de Jogo')
        for trucou in [True, False]:
            for p2 in list(Resposta):
                for p1 in list(Resposta):
                    print(f'Trucou:{trucou}, P2:{p2.name}, P1:{p1.name} -> {self.valorJogo(trucou, p2, p1)}')


    #####################################################
    # Funções de decisão de jogo
    
    def decisaoCorrer(self, card) -> bool:
        print('\nDeseja correr (S/n)? ')
        # calcular utilidade de correr e não correr e mostrar
        for correr in [True, False]:
            UE_Correr = self.utilidadeEsperadaCorrer(correr, card)
            print(f'Utilidade Esperada [Correr = {correr!s:^5}]: {UE_Correr:.2f}')

        userInput = str(input())

        # retornar um bool com base no input do usuario
        while True:
            if userInput.upper() == 'S':
                return True
            elif userInput.upper() == 'N':
                return False
            
            print('Resposta Inválida!\n')
            userInput = str(input('Deseja correr (S/n)? '))

    def decisaoTrucar(self, correu, card) -> bool:
        # Se P1 correu, não existe a decisão de trucar
        if correu == True:
            return False

        print('\nQuer trucar (S/n)? ')
        # calcular utilidade de trucar e não trucar e mostrar
        for trucar in [True, False]:
            UE_Trucar = self.utilidadeEsperadaTrucar(trucar, card)
            print(f'Utilidade Esperada [Trucar = {trucar!s:^5}]: {UE_Trucar:.2f}')
            
        userInput = str(input())
            
        # retornar um bool com base no input do usuario
        while True:
            if userInput.upper() == 'S':
                return True
            elif userInput.upper() == 'N':
                return False
            
            print('Resposta Inválida!\n')
            userInput = str(input('Quer trucar (S/n)? '))

    def decisaoRespostaP2(self, p1Correu, p1Trucou, cardP2) -> Resposta:
        if p1Correu == True:
            return Resposta.ACEITAR

        utilidades = {}
        for resposta in list(Resposta):
            utilidades[resposta] = self.utilidadeEsperadaRespostaP2(resposta, p1Trucou, cardP2)

        melhorDecisao = max(utilidades, key=utilidades.get)
        
        # print(utilidades)
        if melhorDecisao == Resposta.ACEITAR:
            print(f'\nJogador 2 decidiu continuar o jogo')
        elif melhorDecisao == Resposta.AUMENTAR:
            if p1Trucou:
                print(f'\nJogador 2 pediu 6!')
            else:
                print(f'\nJogador 2 trucou!')
        else:
            print(f'\nJogador 2 correu')

        return melhorDecisao

    def decisaoRespostaP1(self, correu, trucou, respostaP2, card) -> Resposta:
        # Se o P2 não trucou, não existe resposta de P1
        if correu == True or respostaP2 != Resposta.AUMENTAR:
            return Resposta.ACEITAR

        # Se P1 trucou e P2 pediu 6, não há a resposta de pedir 9
        print(f'\nO que deseja fazer?')
        print(f'\t0 - Correr')
        print(f'\t1 - Aceitar')
        if trucou == False:
            print(f'\t2 - Pedir 6')
        
        respostasValidas = [Resposta.CORRER, Resposta.ACEITAR]
        if trucou == False:
            respostasValidas.append(Resposta.AUMENTAR)
        for respostaP1 in respostasValidas:
            UE_RespostaP1 = self.utilidadeEsperadaRespostaP1(respostaP1, respostaP2, trucou, card)
            print(f'Utilidade Esperada [Resposta = {respostaP1.name:<8}]: {UE_RespostaP1:.2f}')

        userInput = int(input('Ação: '))

        # retornar uma resposta com base no input do usuario
        while True:
            if userInput == 0:
                return Resposta.CORRER
            elif userInput == 1:
                return Resposta.ACEITAR
            elif userInput == 2 and trucou == False:
                return Resposta.AUMENTAR
            
            print('Resposta Inválida!\n')
            print(f'\nO que deseja fazer?')
            print(f'\t0 - Correr')
            print(f'\t1 - Aceitar')
            if trucou == False:
                print(f'\t2 - Pedir 6')
            userInput = int(input('Ação: '))

    #####################################################
    # Função de simulação de uma rodada
    # Retorna o resultado de pontos da rodada, na perspectiva do Jogador 1
    def simulaRodada(self, cardP1, cardP2) -> int:
        print(f'Sua carta: {cardP1} - Probabilidade prévia de vitória: {self.probWin(cardP1):.2f}')

        correu = self.decisaoCorrer(cardP1)
        trucou = self.decisaoTrucar(correu, cardP1)
        respostaP2 = self.decisaoRespostaP2(correu, trucou, cardP2)
        respostaP1 = self.decisaoRespostaP1(correu, trucou, respostaP2, cardP1)

        resultado = self.calcularResultado(cardP1, cardP2)
        valor = self.valorJogo(trucou, respostaP2, respostaP1)
        estadoJogo = self.estadoJogo(correu, respostaP1, respostaP2)
        return self.utilidade(resultado, valor, estadoJogo)

# jogo = Jogo()
# jogo.testes()