from __future__ import annotations

from .erros import JogadaInvalida
from .tabuleiro import TAMANHO, Celula, Parede, Tabuleiro, parse_celula

INICIOS = {1: "e1", 2: "e9", 3: "a5", 4: "i5"}

# Objetivo de cada jogador: uma linha ou coluna inteira do lado oposto.
OBJETIVOS = {
    1: ("linha", 8),
    2: ("linha", 0),
    3: ("coluna", 8),
    4: ("coluna", 0),
}

ORDEM_TURNOS = {2: [1, 2], 4: [1, 3, 2, 4]} # sentido horário no jogo
PAREDES_POR_JOGADOR = {2: 10, 4: 5}

def casas_objetivo(jogador: int) -> set[Celula]:
    """Retorna o conjunto de casas que constituem o objetivo do jogador."""
    eixo, valor = OBJETIVOS[jogador]
    if eixo == "linha":
        return {(coluna, valor) for coluna in range(TAMANHO)}
    return {(valor, linha) for linha in range(TAMANHO)}


class Partida:
    def __init__(self, num_jogadores: int) -> None:
        if num_jogadores not in ORDEM_TURNOS:
            raise ValueError(f"Número de jogadores inválido: {num_jogadores}.")
        self.num_jogadores = num_jogadores
        self.ordem = ORDEM_TURNOS[num_jogadores]
        self.tabuleiro = Tabuleiro()
        self.paredes_restantes: dict[int, int] = {}
        for jogador in self.ordem:
            self.tabuleiro.peoes[jogador] = parse_celula(INICIOS[jogador])
            self.tabuleiro.objetivos[jogador] = casas_objetivo(jogador)
            self.paredes_restantes[jogador] = PAREDES_POR_JOGADOR[num_jogadores]
        self._indice_vez = 0
        self.vencedor: int | None = None

    @property
    def jogador_da_vez(self) -> int:
        return self.ordem[self._indice_vez]

    @property
    def finalizada(self) -> bool:
        return self.vencedor is not None

    def _validar_vez(self, jogador: int) -> None:
        if self.finalizada:
            raise JogadaInvalida("A partida já terminou.")
        if jogador != self.jogador_da_vez:
            raise JogadaInvalida(f"Não é a vez do jogador {jogador}.")

    def _passar_vez(self) -> None:
        self._indice_vez = (self._indice_vez + 1) % len(self.ordem)

    def mover_peao(self, jogador: int, destino: Celula) -> None:
        self._validar_vez(jogador)
        self.tabuleiro.mover(jogador, destino)
        if destino in self.tabuleiro.objetivos[jogador]:
            self.vencedor = jogador
        else:
            self._passar_vez()

    def colocar_parede(self, jogador: int, parede: Parede) -> None:
        self._validar_vez(jogador)
        if self.paredes_restantes[jogador] == 0:
            raise JogadaInvalida("Você não tem mais paredes.")
        self.tabuleiro.colocar_parede(parede)
        self.paredes_restantes[jogador] -= 1
        self._passar_vez()