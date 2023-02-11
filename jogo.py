import random
from enums import Resultado
from enums import Resposta
from enums import EstadoJogo

class Jogo:
    def __init__(self):
        self.cards = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        self.cardValues = dict(zip(self.cards, [x for x in range(len(self.cards))] ))

    
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

    def distribuirCartas(self):
        numeroDeCartas = len(self.cards) 
        return self.cards[random.randint(0,numeroDeCartas-1)]

    def calcularResultado(self, card1:str, card2:str) -> Resultado:
        cardValue1 = self.cardValues[card1]
        cardValue2 = self.cardValues[card2]
        if cardValue1 == cardValue2: return Resultado.EMPATOU
        return Resultado.GANHOU if cardValue1 > cardValue2 else Resultado.PERDEU 

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
    
    def utilidadeEsperadaTrucar(self,trucar:bool, card:str):
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
    
    def decisaoCorrer(self, card) -> bool:
        print('Deseja correr? (S/n)')
        # calcular utilidade de correr e mostrar
        utilCorrer = self.utilidadeEsperadaCorrer(True, card)
        # calcular utilidade de não correr e mostrar
        utilNaoCorrer = self.utilidadeEsperadaCorrer(False, card)
        # pegar input do usuario e retornar em um bool

    def decisaoTrucar(self,card) -> bool:
        print('Quer trucar? (S/n)')
        # calcular utilidade de trucar e mostrar
        self.utilidadeEsperadaTrucar(True, card )
        # calcular utilidade de não trucar e mostrar
        self.utilidadeEsperadaTrucar(False, card)
        # pegar input do usuario e retornar em um bool

    def decisaoResposta(self, trucou, respostaP2, card) -> Resposta:
        print('O que deseja fazer?')
        # mostrar as opções
        # tem que verificar quais ações são válidas
        #   - n pode pedir 9
        #   - se o P2 n trucou nem correu, essa funcao n faz nada -> n precisa nem pedir o que deseja fazer
        # calcular utilidade de aceitar e mostrar
        self.utilidadeEsperadaRespostaP1(True, trucou, card )
        # calcular utilidade de não aceitar e mostrar
        self.utilidadeEsperadaRespostaP1(False, trucou, card )
        # pegar input do usuario e retornar em um bools