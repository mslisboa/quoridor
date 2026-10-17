from __future__ import annotations
from collections import deque

from dataclasses import dataclass

TAMANHO = 9
COLUNAS = "abcdefghi"

Celula = tuple[int, int]  # (linha, coluna)

DIRECOES = {
    "N": (0, 1),
    "S": (0, -1),
    "L": (1, 0),
    "O": (-1, 0),
}

def parse_celula(texto: str) -> Celula:
    """Converte uma string de coordenadas em uma tupla (linha, coluna)."""
    texto = texto.strip().lower()

    if len(texto) != 2 or texto[0] not in COLUNAS or texto[1] not in "123456789":
        raise ValueError(f"Coordenadas inválidas: {texto!r}. User algo como 'e5'.")
    return COLUNAS.index(texto[0]), int(texto[1]) - 1

def formatar_celula(celula: Celula) -> str:
    """"Formata uma tupla (linha, coluna) em uma string de coordenadas."""
    coluna, linha = celula
    return f"{COLUNAS[coluna]}{linha + 1}"

@dataclass(frozen=True)
class Parede:
    """Parede ancorada na casa (coluna, linha)
    
    'h': borda superior da âncora, estendendo-se para a direita
    'v': borda direita da âncora, estendendo-se para cima
    """

    coluna: int
    linha: int
    orientacao: str # 'h' ou 'v'

    def __post_init__(self) -> None:
        if self.orientacao not in ("h", "v"):
            raise ValueError(f"Orientação inválida: {self.orientacao!r}. Use 'h' ou 'v'.")
        if not (0 <= self.coluna < TAMANHO - 1 and 0 <= self.linha < TAMANHO - 1):
            raise ValueError(f"Coordenadas inválidas: ({self.coluna}, {self.linha}). Deve estar dentro do tabuleiro.")

    @classmethod
    def de_texto(cls, texto: str) -> Parede:
        """Converte uma string de coordenadas e orientação em uma instância de Parede."""
        textto = texto.strip().lower()
        if len(textto) != 3:
            raise ValueError(f"Coordenadas inválidas: {texto!r}. Use algo como 'e5h' ou 'e5v'.")
        coluna, linha = parse_celula(textto[:2])
        return cls(coluna, linha, textto[2])

    def __str__(self) -> str:
        return f"{formatar_celula((self.coluna, self.linha))}{self.orientacao}"


class Tabuleiro:
    def __init__(self) -> None:
        self.paredes: set[Parede] = set()
        self.peoes: dict[int, Celula] = {} # id do jogador -> posição do peão
        self.objetivos: dict[int, set[Celula]] = {} # id do jogador -> conjunto de células de objetivo

    # ---------------- Consultas ----------------

    @staticmethod
    def dentro(celula: Celula) -> bool:
        """Verifica se a célula está dentro dos limites do tabuleiro."""
        coluna, linha = celula
        return 0 <= coluna < TAMANHO and 0 <= linha < TAMANHO


    def _tem_parede(self, coluna: int, linha: int, orientacao: str) -> bool:
        if not (0 <= coluna < TAMANHO - 1 and 0 <= linha < TAMANHO - 1):
            return False
        return Parede(coluna, linha, orientacao) in self.paredes


    def aresta_bloqueada(self, a: Celula, b: Celula) -> bool:
        """Verifica se a aresta entre duas células adjacentes está bloqueada por uma parede."""
        if not self.dentro(b):
            return True

        (ac, al), (bc, bl) = a, b

        if ac == bc:
            # Passo vertical: só paredes horizontais podem bloquear
            base = min(al, bl)
            return self._tem_parede(ac, base, "h") or self._tem_parede(ac - 1, base, "h")
        # Passo horizontal: só paredes verticais podem bloquear
        esquerda = min(ac, bc)
        return self._tem_parede(esquerda, al, "v") or self._tem_parede(esquerda, al - 1, "v")


    def destinos_validos(self, jogador: int) -> set[Celula]:
        """Retorna o conjunto de células que o jogador pode alcançar a partir da posição atual do peão."""
        origem = self.peoes[jogador]
        ocupados = set(self.peoes.values())
        destinos: set[Celula] = set()

        for dc, dl in DIRECOES.values():
            vizinha = (origem[0] + dc, origem[1] + dl)
            
            if self.aresta_bloqueada(origem, vizinha):
                continue

            if vizinha not in ocupados:
                destinos.add(vizinha)
                continue

            # Vizinha ocupada por outro peão: tenta pular
            atras = (vizinha[0] + dc, vizinha[1] + dl)
            if not self.aresta_bloqueada(vizinha, atras) and atras not in ocupados:
                destinos.add(atras) # pulo reto
            else:
                # Pulo lateral
                for pc, pl in ((dl, dc), (-dl, -dc)):
                    lateral = (vizinha[0] + pc, vizinha[1] + pl)
                    if not self.aresta_bloqueada(vizinha, lateral) and lateral not in ocupados:
                        destinos.add(lateral)

        return destinos

    def existe_caminho(self, origem: Celula, objetivo: set[Celula]) -> bool:
        """BFS: Verifica se existe um caminho da célula de origem até qualquer célula do conjunto de objetivos."""
        visitados = {origem}
        fila = deque([origem])

        while fila:
            atual = fila.popleft()
            if atual in objetivo:
                return True
            for dc, dl in DIRECOES.values():
                vizinha = (atual[0] + dc, atual[1] + dl)
                if vizinha in visitados or self.aresta_bloqueada(atual, vizinha):
                    continue
                visitados.add(vizinha)
                fila.append(vizinha)
        return False

    def _conflito(self, p: Parede) -> bool:
        """Verifica se a parede p conflita com paredes existentes"""
        if p in self.paredes:
            return True
        if p.orientacao == "h":
            cruza = self._tem_parede(p.coluna, p.linha, "v")
            sobrepoe = (self._tem_parede(p.coluna - 1, p.linha, "h") or
                        self._tem_parede(p.coluna + 1, p.linha, "h"))
        else:
            cruza = self._tem_parede(p.coluna, p.linha, "h")
            sobrepoe = (self._tem_parede(p.coluna, p.linha - 1, "v") or
                        self._tem_parede(p.coluna, p.linha + 1, "v"))
        return cruza or sobrepoe

    def colocar_parede(self, p: Parede) -> None:
        """Coloca a parede ou lança ValueError (e deixa o tabuleiro intacto)"""
        if self._conflito(p):
            raise ValueError(f"A parede {p} sobrepõe ou cruxa outra parede.")
        
        self.paredes.add(p)

        if not all(self.existe_caminho(origem, self.objetivos[jogador]) for jogador, origem in self.peoes.items()):
            self.paredes.remove(p)
            raise ValueError(f"A parede {p} bloqueia o caminho de algum jogador.")

    # ----------- ação ------------

    def mover(self, jogador: int, destino: Celula) -> None:
        """Move o peão do jogador para a célula de destino."""
        if destino not in self.destinos_validados(jogador):
            raise ValueError(f"Movimento inválido para {formatar_celula(destino)}.")
        self.peoes[jogador] = destino