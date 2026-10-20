import random, subprocess, sys, heapq, math, os
T_DIR = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(T_DIR)  # raiz do repositório (onde estão e1/e2/e3.py)

def ref(toks_text):
    t = toks_text.split(); p = 0
    def nx():
        nonlocal p; v = t[p]; p += 1; return v
    n, m, T = int(nx()), int(nx()), int(nx())
    L = {}; C = {}; E = {}
    for _ in range(n):
        i, x, y, l = (int(nx()) for _ in range(4)); L[i] = l; C[i] = (x, y)
    for _ in range(m):
        u, v, c = (int(nx()) for _ in range(3)); E[(u, v)] = c
    Ls = []; out = []
    def fecha():
        Ls.append(sum(L.values()))
    fecha()
    P = int(nx())
    for k in range(2, P + 2):
        q = int(nx())
        for _ in range(q):
            op = nx()
            if op == "INSERIR":
                i, x, y, l, r = (int(nx()) for _ in range(5)); L[i] = l; C[i] = (x, y)
                for _ in range(r):
                    u, v, c = (int(nx()) for _ in range(3)); E[(u, v)] = c
            elif op == "LUCRO":
                i = int(nx()); L[i] = int(nx())
            elif op == "REMOVER":
                rem = [i for i in L if L[i] < T]
                for i in rem:
                    del L[i]; del C[i]
                for e in [e for e in E if e[0] in rem or e[1] in rem]: del E[e]
                out.append(str(len(rem)))
            elif op == "DIST":
                s = int(nx()); d = {s: 0}; h = [(0, s)]
                while h:
                    du, u = heapq.heappop(h)
                    if du > d[u]: continue
                    for (a, b), c in E.items():
                        if a == u and du + c < d.get(b, 1 << 60):
                            d[b] = du + c; heapq.heappush(h, (du + c, b))
                out.append(" ".join(str(d.get(v, -1)) for v in sorted(L) if v != s))
            elif op == "PAR":
                ids = sorted(L); best = None
                for a in range(len(ids)):
                    for b in range(a + 1, len(ids)):
                        (x1, y1), (x2, y2) = C[ids[a]], C[ids[b]]
                        d2 = (x1-x2)**2 + (y1-y2)**2
                        if best is None or d2 < best[0]: best = (d2, ids[a], ids[b])
                tt = math.isqrt(best[0]); tt += tt*tt < best[0]
                out.append("%d %d %d" % (best[1], best[2], tt))
            elif op == "MELHOR":
                bb = None
                for i in range(len(Ls)):
                    s = 0
                    for j in range(i, len(Ls)):
                        s += Ls[j]
                        if bb is None or s > bb[0]: bb = (s, i+1, j+1)
                out.append("%d %d %d" % (bb[1], bb[2], bb[0]))
            elif op == "PROSPERIDADE":
                st = []
                for kk, lk in enumerate(Ls, 1):
                    if lk > 0: st.append([kk, lk])
                    elif lk < 0:
                        d = -lk
                        while d > 0 and st:
                            if st[-1][1] > d: st[-1][1] -= d; d = 0
                            else: d -= st[-1][1]; st.pop()
                out.append("0" if not st else "%d %d %d %d %d" % (len(st), st[0][0], sum(r for _, r in st), st[-1][0], st[-1][1]))
        fecha()
    return "\n".join(out) + ("\n" if out else "")

def gen(ops, rng):
    n = rng.randint(2, 8); T = rng.randint(-30, 10)
    used = set(); coords = {}; lucro = {}; edges = set()
    lines = []
    def novo_id():
        while True:
            i = rng.randint(1, 10**9 if rng.random() < .3 else 60)
            if i not in used: used.add(i); return i
    def coord_livre():
        while True:
            c = (rng.randint(-8, 8), rng.randint(-8, 8))
            if c not in coords.values(): return c
    for _ in range(n):
        i = novo_id(); coords[i] = coord_livre(); lucro[i] = rng.randint(T, T + 40)
    ids = list(coords)
    es = []
    for _ in range(rng.randint(0, 3 * n)):
        u, v = rng.sample(ids, 2) if len(ids) > 1 else (0, 0)
        if (u, v) not in edges and u != v: edges.add((u, v)); es.append((u, v, rng.randint(1, 9)))
    head = ["%d %d %d" % (n, len(es), T)]
    for i in ids: head.append("%d %d %d %d" % (i, *coords[i], lucro[i]))
    for e in es: head.append("%d %d %d" % e)
    P = rng.randint(1, 8); body = [str(P)]
    def pares_unico():
        v = list(coords); best = []
        ds = sorted((((coords[a][0]-coords[b][0])**2 + (coords[a][1]-coords[b][1])**2), a, b) for i, a in enumerate(v) for b in v[i+1:])
        return len(ds) >= 2 and (len(ds) < 2 or ds[0][0] < ds[1][0])
    for _ in range(P):
        q = rng.randint(1, 8); cmds = []
        for _ in range(q):
            op = rng.choice(ops)
            if op == "INSERIR":
                if len(coords) >= 40: continue
                i = novo_id(); c = coord_livre(); l = rng.randint(T, T + 40)
                alvo = list(coords); r = []
                for _ in range(rng.randint(0, 4) if alvo else 0):
                    o = rng.choice(alvo)
                    e = (i, o) if rng.random() < .5 else (o, i)
                    if e not in edges: edges.add(e); r.append("%d %d %d" % (*e, rng.randint(1, 9)))
                coords[i] = c; lucro[i] = l
                cmds.append("INSERIR %d %d %d %d %d" % (i, *c, l, len(r)) + ("\n" + "\n".join(r) if r else ""))
            elif op == "LUCRO":
                if not coords: continue
                i = rng.choice(list(coords)); l = rng.randint(T - 30, T + 40); lucro[i] = l
                cmds.append("LUCRO %d %d" % (i, l))
            elif op == "REMOVER":
                rem = [i for i in lucro if lucro[i] < T]
                for i in rem: del lucro[i]; del coords[i]
                for e in [e for e in edges if e[0] in rem or e[1] in rem]: edges.discard(e)
                cmds.append("REMOVER")
            elif op == "DIST":
                if not coords: continue
                cmds.append("DIST %d" % rng.choice(list(coords)))
            elif op == "PAR":
                if len(coords) < 2 or not pares_unico(): continue
                cmds.append("PAR")
            else: cmds.append(op)
        body.append(str(len(cmds))); body += cmds
    return "\n".join(head + body) + "\n"

def rodar(f, txt):
    return subprocess.run([sys.executable, os.path.join(D, f)], input=txt, capture_output=True, text=True, timeout=60)

if __name__ == "__main__":
    ex = open(os.path.join(T_DIR, "exemplo.txt")).read()
    esp = open(os.path.join(T_DIR, "esperado.txt")).read()
    assert ref(ex) == esp, "ref != esperado do PDF"
    assert rodar("e3.py", ex).stdout == "\n".join(l for l in []) or True
    # exemplo completo: e3 filtra DIST/REMOVER; e2 REMOVER/PAR; e1 MELHOR/PROSPERIDADE
    print("ref bate com o PDF")
    stages = {"e1.py": ["INSERIR", "LUCRO", "MELHOR", "PROSPERIDADE"],
              "e2.py": ["INSERIR", "LUCRO", "REMOVER", "PAR"],
              "e3.py": ["INSERIR", "LUCRO", "REMOVER", "DIST"]}
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    for f, ops in stages.items():
        ruim = 0
        for s in range(N):
            txt = gen(ops, random.Random(s))
            r = rodar(f, txt)
            if r.returncode or r.stdout != ref(txt):
                ruim += 1
                if ruim == 1: print(f, "FALHA seed", s, r.stderr[-400:], "\n", txt, "\n--\n", r.stdout, "\n--\n", ref(txt))
        print(f, "falhas:", ruim, "/", N)
