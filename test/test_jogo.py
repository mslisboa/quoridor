import pytest

from jogo.tabuleiro import Parede, Tabuleiro, parse_celula as c

def tabuleiro_com(**peoes: str) -> Tabuleiro:
    """Cria um tabuleiro com os peões nas posições especificadas."""
    t = Tabuleiro()
    t.peoes = {int(nome[1:]): c(casa) for nome, casa in peoes.items()}
    return t

def casas(*nomes: str) -> set:
    """Converte uma lista de nomes de casas em um conjunto de tuplas (coluna, linha)."""
    return {c(nome) for nome in nomes}

def test_notacao():
    assert c("e5") == (4, 4)
    with pytest.raises(ValueError):
        c("z9")

def test_passos_livres_e_borda():
    t = tabuleiro_com(j1="e1")
    assert t.destinos_validos(1) == casas("e2", "d1", "f1")

def test_pulo_reto():
    t = tabuleiro_com(j1="e4", j2="e5")
    assert t.destinos_validos(1) == casas("d4", "f4", "e3", "e6")

def test_parede_entre_os_peoes():
    t = tabuleiro_com(j1="e4", j2="e5")
    t.paredes.add(Parede.de_texto("e4h"))
    assert t.destinos_validos(1) == casas("d4", "f4", "e3")

def test_pulo_diagonal_com_parede_atras():
    t = tabuleiro_com(j1="e4", j2="e5")
    t.paredes.add(Parede.de_texto("e5h")) # borda superior de e5
    assert t.destinos_validos(1) == casas("d4", "f4", "e3", "d5", "f5")

def test_parede_vertical_bloqueia_passo_lateral():
    t = tabuleiro_com(j1="e4")
    t.paredes.add(Parede.de_texto("e3v")) # borda direita de e3
    assert c("f4") not in t.destinos_validos(1)