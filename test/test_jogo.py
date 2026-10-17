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

def linha_objeto(linha: int) -> set:
    """Retorna um conjunto de células na linha especificada."""
    return {(coluna, linha) for coluna in range(9)}

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

def test_parede_cruzada_e_recusada():
    t = Tabuleiro()
    t.colocar_parede(Parede.de_texto("e3h"))
    with pytest.raises(ValueError):
        t.colocar_parede(Parede.de_texto("e3v")) # cruzada com a anterior

def test_sobreposicao_horizontal():
    t = Tabuleiro()
    t.colocar_parede(Parede.de_texto("e3h")) # cobre e e f
    for texto in ("f3h", "d3h", "e3h"):
        with pytest.raises(ValueError):
            t.colocar_parede(Parede.de_texto(texto)) # sobreposição horizontal
    t.colocar_parede(Parede.de_texto("g3h")) # cobre g e h: permitido

def test_parede_que_fecha_o_caminho_e_recusada():
    t = Tabuleiro()
    t.peoes = {1: c("a1")}
    t.objetivos = {1: linha_objeto(8)}
    t.colocar_parede(Parede.de_texto("a1h")) # fecha o norte de a1 e b1
    antes = set(t.paredes)
    with pytest.raises(ValueError):
        t.colocar_parede(Parede.de_texto("b1v")) # fecharia a saída por b1
    assert t.paredes == antes # nada mudou

def test_parede_que_so_alonga_o_caminho_e_aceita():
    t = Tabuleiro()
    t.peoes = {1: c("a1")}
    t.objetivos = {1: linha_objeto(8)}
    t.colocar_parede(Parede.de_texto("a1h")) # a1 ainda sai por c1
    assert t.existe_caminho(c("a1"), linha_objeto(8)) # ainda existe caminho