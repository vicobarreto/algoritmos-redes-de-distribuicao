import random, sys
r = random.Random(1); n = 5000; T = 0
pts = set()
while len(pts) < n: pts.add((r.randint(-10**6, 10**6), r.randint(-10**6, 10**6)))
pts = list(pts); ids = r.sample(range(1, 10**9), n+200000)
L = ["%d %d %d" % (n, 5*n, T)]
for i in range(n): L.append("%d %d %d %d" % (ids[i], *pts[i], r.randint(0, 100)))
es = set()
while len(es) < 5*n:
    a, b = r.sample(ids[:n], 2); es.add((a, b))
for a, b in es: L.append("%d %d %d" % (a, b, r.randint(1, 10**6)))
P = 100000; L.append(str(P))
nid = n; ops_tot = 0; dist = par = 0
live = list(ids[:n])
for k in range(P):
    cmds = []
    # 1 LUCRO por periodo, de vez em quando PAR/DIST precedido de INSERIR (invalida cache)
    cmds.append("LUCRO %d %d" % (r.choice(live), r.randint(-5, 100)))
    if k % 200 == 0 and par < 500:
        # INSERIR com coordenadas novas, depois PAR
        x, y = r.randint(2*10**6, 3*10**6), r.randint(2*10**6, 3*10**6) + k
        i = ids[nid]; nid += 1
        cmds.append("INSERIR %d %d %d %d 1" % (i, x, y, 50)); cmds.append("%d %d 5" % (i, live[0]))
        live.append(i)
        cmds.append("PAR"); par += 1
    if k % 500 == 0 and dist < 200:
        cmds.append("DIST %d" % r.choice(live)); dist += 1
    L.append(str(len(cmds) - (1 if any(c.startswith("INSERIR") for c in cmds) else 0) ))
    L += cmds
open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "grande.txt"), "w").write("\n".join(L) + "\n")
