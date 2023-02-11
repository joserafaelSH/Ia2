from enum import Enum

class Resultado(Enum):
  GANHOU = 1
  EMPATOU = 0
  PERDEU = -1

class Resposta(Enum):
  # Aumentar pode ser interpretado como pedir truco ou pedir 6
  AUMENTAR = 1
  ACEITAR = 0
  CORRER = -1

class EstadoJogo(Enum):
  P2_CORREU = 1
  NORMAL = 0
  P1_CORREU = -1
