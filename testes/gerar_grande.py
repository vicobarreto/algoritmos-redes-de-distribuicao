"""Gera entradas grandes (próximas dos limites do enunciado) para medir tempo.

Uso: python testes/gerar_grande.py [e1|e2|e3|todos]
Cada estágio recebe só as operações que ele exercita (o enunciado seção 2):
  e1: INSERIR, LUCRO, MELHOR, PROSPERIDADE
  e2: INSERIR, LUCRO, REMOVER, PAR     (500 PAR, cada um logo após um INSERIR,
      para o cache não ajudar)
  e3: INSERIR, LUCRO, REMOVER, DIST    (200 DIST, grafo quase todo alcançável)
Escreve testes/grande_<estagio>.txt (ignorado pelo git).
"""
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
N0 = 4000            # depósitos no setup (sobra folga para os INSERIR, máx. 5000 vivos)
P = 100000           # períodos além do primeiro
T = 0


def gerar(estagio, semente=1):
    r = random.Random(semente)
    ids = r.sample(range(1, 10 ** 9), N0 + 5000)
    usados = set()
    coords = {}
    lucro = {}
    while len(usados) < N0:
        usados.add((r.randint(-10 ** 6, 10 ** 6), r.randint(-10 ** 6, 10 ** 6)))
    for i, p in zip(ids, usados):
        coords[i] = p
        lucro[i] = r.randint(0, 100)
    prox = N0
    vivos = list(coords)
    pontos = set(coords.values())

    linhas = ["%d %d %d" % (N0, 5 * N0, T)]
    for i in coords:
        linhas.append("%d %d %d %d" % (i, *coords[i], lucro[i]))
    rotas = set()
    while len(rotas) < 5 * N0:
        a, b = r.sample(vivos, 2)
        rotas.add((a, b))
    for a, b in rotas:
        linhas.append("%d %d %d" % (a, b, r.randint(1, 10 ** 6)))
    linhas.append(str(P))

    n_par = n_dist = 0
    for k in range(P):
        cmds = []
        extra = 0                                     # linhas de rota (não contam em q)
        if vivos:
            i = r.choice(vivos)
            lucro[i] = r.randint(-5, 100)
            cmds.append("LUCRO %d %d" % (i, lucro[i]))
        if estagio == "e1":
            if k % 50 == 0:
                cmds += ["MELHOR", "PROSPERIDADE"]
            if k % 100 == 0 and prox < N0 + 900:     # sem REMOVER no e1: poucos INSERIR
                i = ids[prox]
                prox += 1
                lucro[i] = r.randint(0, 100)
                vivos.append(i)
                cmds.append("INSERIR %d 0 0 %d 1" % (i, lucro[i]))
                cmds.append("%d %d 5" % (i, vivos[0]))
                extra = 1
        else:
            if k % 200 == 0 and len(vivos) < 4900 and prox < len(ids):
                while True:
                    p = (r.randint(2 * 10 ** 6, 3 * 10 ** 6), r.randint(2 * 10 ** 6, 3 * 10 ** 6))
                    if p not in pontos:
                        break
                pontos.add(p)
                i = ids[prox]
                prox += 1
                lucro[i] = 50
                coords[i] = p
                outro = r.choice(vivos)
                vivos.append(i)
                cmds.append("INSERIR %d %d %d 50 1" % (i, *p))
                cmds.append("%d %d 5" % (i, outro))
                extra = 1
                if estagio == "e2" and n_par < 500:
                    cmds.append("PAR")
                    n_par += 1
            if estagio == "e3" and k % 500 == 0 and n_dist < 200:
                cmds.append("DIST %d" % r.choice(vivos))
                n_dist += 1
            if k % 1000 == 999:                        # REMOVER de vez em quando
                cmds.append("REMOVER")
                vivos = [v for v in vivos if lucro[v] >= T]
                for v in [v for v in lucro if lucro[v] < T]:
                    del lucro[v]
        linhas.append(str(len(cmds) - extra))
        linhas += cmds
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "todos"
    for est in (["e1", "e2", "e3"] if alvo == "todos" else [alvo]):
        caminho = os.path.join(AQUI, "grande_%s.txt" % est)
        with open(caminho, "w") as f:
            f.write(gerar(est))
        print(caminho)
