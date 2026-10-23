import pytest

from jogo.erros import JogadaInvalida
from jogo.partida import Partida, casas_objetivo
from jogo.tabuleiro import Parede, parse_celula as c

def test_configuracao_2_jogadores():
    p = Partida(2)
    assert p.tabuleiro.peoes == {1: c("e1"), 2: c("e9")}
    assert p.paredes_restantes == {1: 10, 2: 10}
    assert p.jogador_da_vez == 1


def test_configuracao_4_jogadores():
    p = Partida(4)
    assert p.tabuleiro.peoes == {1: c("e1"), 2: c("e9"), 3: c("a5"), 4: c("i5")}
    assert p.paredes_restantes == {1: 5, 2: 5, 3: 5, 4: 5}


# Tirar dúvida depois
def test_objetivos_do_jogo_de_4():
    assert c("a9") in casas_objetivo(1) and c("a1") not in casas_objetivo(1)
    assert c("i1") in casas_objetivo(3) and c("a1") not in casas_objetivo(3)
    assert c("a9") in casas_objetivo(4) and c("b9") not in casas_objetivo(4)


def test_objetivos_completos():
    assert casas_objetivo(1) == {c(f"{col}9") for col in "abcdefghi"}
    assert casas_objetivo(2) == {c(f"{col}1") for col in "abcdefghi"}
    assert casas_objetivo(3) == {c(f"i{lin}") for lin in "123456789"}
    assert casas_objetivo(4) == {c(f"a{lin}") for lin in "123456789"}


def test_ordem_dos_turnos_no_jogo_de_4():
    p = Partida(4)
    vezes = []
    for jogador, destino in [(1, "e2"), (3, "b5"), (2, "e8"), (4, "h5")]:
        vezes.append(p.jogador_da_vez)
        p.mover_peao(jogador, c(destino))
    assert vezes == [1, 3, 2, 4]
    assert p.jogador_da_vez == 1


def test_jogar_fora_da_vez():
    p = Partida(2)
    with pytest.raises(JogadaInvalida):
        p.mover_peao(2, c("e8"))


def test_jogada_invalida_nao_passa_a_vez():
    p = Partida(2)
    with pytest.raises(JogadaInvalida):
        p.mover_peao(1, c("e5")) # longe demais
    assert p.jogador_da_vez == 1


def test_parede_consome_estoque_e_passa_a_vez():
    p = Partida(2)
    p.colocar_parede(1, Parede.de_texto("e3h"))
    assert p.paredes_restantes[1] == 9
    assert p.jogador_da_vez == 2


def test_sem_paredes_restantes():
    p = Partida(2)
    p.paredes_restantes[1] = 0
    with pytest.raises(JogadaInvalida):
        p.colocar_parede(1, Parede.de_texto("e3h"))


def test_vitoria_encerra_a_partida():
    p = Partida(2)
    p.tabuleiro.peoes[1] = c("e8")
    p.tabuleiro.peoes[2] = c("a5")
    p.mover_peao(1, c("e9"))
    assert p.vencedor == 1 and p.finalizada
    with pytest.raises(JogadaInvalida):
        p.mover_peao(2, c("a6"))

