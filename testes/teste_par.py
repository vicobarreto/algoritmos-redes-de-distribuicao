"""Compara par_mais_proximo (e2.py, divisão e conquista) com a força bruta em
conjuntos de 2 a 600 pontos, em várias distribuições (uniforme, aglomerado,
colunas estreitas, grade esparsa). Só vale quando o par mais próximo é único
(garantia do enunciado), então conjuntos com empate no mínimo são descartados.

Uso: python testes/teste_par.py [quantidade_de_casos]
"""
import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import e2  # noqa: E402


def bruta(coord):
    ids = sorted(coord)
    ds = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (x1, y1), (x2, y2) = coord[a], coord[b]
            ds.append(((x1 - x2) ** 2 + (y1 - y2) ** 2, a, b))
    ds.sort()
    unico = len(ds) < 2 or ds[0][0] < ds[1][0]
    return ds[0], unico


def pontos(r, n, modo):
    s = set()
    while len(s) < n:
        if modo == "uniforme":
            s.add((r.randint(-10 ** 6, 10 ** 6), r.randint(-10 ** 6, 10 ** 6)))
        elif modo == "aglomerado":
            cx, cy = r.choice([(0, 0), (500, 500), (-900, 300)])
            s.add((cx + r.randint(-60, 60), cy + r.randint(-60, 60)))
        elif modo == "colunas":
            s.add((r.randint(0, 6), r.randint(-10 ** 5, 10 ** 5)))
        else:  # grade esparsa
            s.add((r.randint(0, 40) * 25, r.randint(0, 40) * 25))
    return list(s)


def main():
    casos = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    r = random.Random(7)
    feitos = descartados = falhas = 0
    for c in range(casos):
        modo = ["uniforme", "aglomerado", "colunas", "grade"][c % 4]
        n = r.choice([2, 3, 5, 31, 32, 33, 34, 64, 65, 100, 200, 333, 600])
        # os modos densos não comportam n pontos distintos demais
        if modo == "aglomerado":
            n = min(n, 300)
        if modo == "colunas":
            n = min(n, 500)
        if modo == "grade":
            n = min(n, 400)
        pts = pontos(r, n, modo)
        coord = dict(zip(r.sample(range(1, 10 ** 9), len(pts)), pts))
        (d2, a, b), unico = bruta(coord)
        if not unico:
            descartados += 1
            continue
        feitos += 1
        t = e2.math.isqrt(d2)
        esperado = (a, b, t + (t * t < d2))
        obtido = e2.par_mais_proximo(coord)
        if obtido != esperado:
            falhas += 1
            if falhas <= 3:
                print("FALHA", modo, n, obtido, esperado)
    print("casos válidos: %d, descartados por empate: %d, falhas: %d" % (feitos, descartados, falhas))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
