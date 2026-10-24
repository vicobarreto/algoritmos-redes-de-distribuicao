"""
Algoritmos e Estruturas de Dados - Turma BCC - 2026.2
Rede de distribuição - Entregável 3: rede de rotas

Autores: Vinicius Lima, Laércio Neto e Zaque Mateus

Operações exercitadas neste entregável: DIST, INSERIR e REMOVER (a linha
impressa por REMOVER também é conferida). LUCRO também é tratado, pois é ele
que faz um depósito ficar abaixo da tolerância. PAR, MELHOR e PROSPERIDADE
não são exercitados e foram omitidos. As rotas deixam de ser descartadas.

Resumo das estruturas de dados (e por que foram escolhidas):

  * FilaPrioridadeMin - heap binário de mínimo com tabela de posições
    (a mesma do Entregável 2). Serve para duas coisas: achar quem está
    abaixo da tolerância no REMOVER (chave = lucro) e escolher o próximo
    vértice no Dijkstra do DIST (chave = distância provisória).
  * RegistroDepositos - heap id -> lucro (Entregável 2), que agora também
    reflete a remoção no grafo.
  * Grafo dirigido esparso por listas de adjacência DUPLAS:
    saida[u] = dict {v: custo} e entrada[v] = set {u}. Uma matriz de
    adjacência gastaria O(n^2) de espaço (25 milhões de células com
    n = 5000) e o grafo é esparso. Guardar também as rotas que CHEGAM a
    cada vértice permite apagar um depósito em tempo proporcional ao seu
    grau, sem varrer o grafo.
  * Dijkstra com o heap acima (decrease-key) para o DIST: custos positivos.

Notação: n = depósitos vivos, m = rotas vivas.
"""

import sys



class Leitor:
   

    __slots__ = ("tokens", "pos")

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def palavra(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def inteiro(self):
        return int(self.palavra())



class FilaPrioridadeMin:
    
    def __init__(self):
        self.ids = []
        self.chaves = []
        self.pos = {}

    def __len__(self):
        return len(self.ids)

    def __contains__(self, ident):
        return ident in self.pos

    def minimo(self):
        
        return self.ids[0], self.chaves[0]

    def _subir(self, i):
        
        ids, chaves, pos = self.ids, self.chaves, self.pos
        ident, chave = ids[i], chaves[i]
        while i > 0:
            pai = (i - 1) >> 1
            if chave < chaves[pai]:
                ids[i] = ids[pai]
                chaves[i] = chaves[pai]
                pos[ids[i]] = i
                i = pai
            else:
                break
        ids[i] = ident
        chaves[i] = chave
        pos[ident] = i

    def _descer(self, i):
       
        ids, chaves, pos = self.ids, self.chaves, self.pos
        n = len(ids)
        ident, chave = ids[i], chaves[i]
        while True:
            filho = 2 * i + 1
            if filho >= n:
                break
            if filho + 1 < n and chaves[filho + 1] < chaves[filho]:
                filho += 1
            if chaves[filho] < chave:
                ids[i] = ids[filho]
                chaves[i] = chaves[filho]
                pos[ids[i]] = i
                i = filho
            else:
                break
        ids[i] = ident
        chaves[i] = chave
        pos[ident] = i

    def inserir(self, ident, chave):
       
        i = len(self.ids)
        self.ids.append(ident)
        self.chaves.append(chave)
        self.pos[ident] = i
        if i > 0 and chave < self.chaves[(i - 1) >> 1]:
            self._subir(i)

    def alterar_chave(self, ident, nova):
        
        i = self.pos[ident]
        antiga = self.chaves[i]
        self.chaves[i] = nova
        if nova < antiga:
            self._subir(i)
        elif nova > antiga:
            self._descer(i)

    def extrair_minimo(self):
        
        ids, chaves, pos = self.ids, self.chaves, self.pos
        ident, chave = ids[0], chaves[0]
        ult_id = ids.pop()
        ult_chave = chaves.pop()
        del pos[ident]
        n = len(ids)
        if n == 0:
            return ident, chave
        i = 0
        filho = 1
        while filho < n:
            if filho + 1 < n and chaves[filho + 1] < chaves[filho]:
                filho += 1
            ids[i] = ids[filho]
            chaves[i] = chaves[filho]
            pos[ids[i]] = i
            i = filho
            filho = 2 * i + 1
        while i > 0:
            pai = (i - 1) >> 1
            if ult_chave < chaves[pai]:
                ids[i] = ids[pai]
                chaves[i] = chaves[pai]
                pos[ids[i]] = i
                i = pai
            else:
                break
        ids[i] = ult_id
        chaves[i] = ult_chave
        pos[ult_id] = i
        return ident, chave



class GrafoRotas:
   

    def __init__(self):
        self.saida = {}
        self.entrada = {}

    def adicionar_vertice(self, ident):
        self.saida[ident] = {}
        self.entrada[ident] = set()

    def adicionar_rota(self, u, v, custo):
        
        self.saida[u][v] = custo
        self.entrada[v].add(u)

    def remover_vertice(self, u):
       
        for v in self.saida[u]:
            self.entrada[v].discard(u)
        for w in self.entrada[u]:
            del self.saida[w][u]
        del self.saida[u]
        del self.entrada[u]

    def menores_custos(self, origem):
       
        dist = {origem: 0}
        fila = FilaPrioridadeMin()
        fila.inserir(origem, 0)
        saida = self.saida
        extrair, inserir, alterar = fila.extrair_minimo, fila.inserir, fila.alterar_chave
        while fila.ids:                     
            u, du = extrair()
            for v, c in saida[u].items():
                nd = du + c
                antigo = dist.get(v)
                if antigo is None:           
                    dist[v] = nd
                    inserir(v, nd)
                elif nd < antigo:          
                    dist[v] = nd
                    alterar(v, nd)
        return dist



class RegistroDepositos:
   

    def __init__(self):
        self.fila = FilaPrioridadeMin()
        self.grafo = GrafoRotas()

    def inserir(self, ident, lucro):
       
        self.fila.inserir(ident, lucro)
        self.grafo.adicionar_vertice(ident)

    def atualizar_lucro(self, ident, novo):
        self.fila.alterar_chave(ident, novo)

    def remover_abaixo(self, tolerancia):
       
        fila = self.fila
        removidos = 0
        while len(fila) > 0 and fila.minimo()[1] < tolerancia:
            ident, _ = fila.extrair_minimo()
            self.grafo.remover_vertice(ident)
            removidos += 1
        return removidos



def ler_rotas(leitor, quantidade, grafo):
    
    for _ in range(quantidade):
        u = leitor.inteiro()
        v = leitor.inteiro()
        c = leitor.inteiro()
        grafo.adicionar_rota(u, v, c)


class Rede:
   

    def __init__(self, tolerancia):
        self.registro = RegistroDepositos()
        self.tolerancia = tolerancia

    def inserir(self, leitor):
       
        ident = leitor.inteiro()
        leitor.inteiro()                  
        leitor.inteiro()                
        lucro = leitor.inteiro()
        r = leitor.inteiro()
        self.registro.inserir(ident, lucro)
        ler_rotas(leitor, r, self.registro.grafo)

    def lucro(self, leitor):
        
        ident = leitor.inteiro()
        novo = leitor.inteiro()
        self.registro.atualizar_lucro(ident, novo)

    def remover(self):
       
        return str(self.registro.remover_abaixo(self.tolerancia))

    def dist(self, leitor):
       
        s = leitor.inteiro()
        dist = self.registro.grafo.menores_custos(s)
        vivos = sorted(self.registro.grafo.saida)
        return " ".join(str(dist.get(v, -1)) for v in vivos if v != s)


def executar_lote(leitor, rede, saida):
    
    q = leitor.inteiro()
    for _ in range(q):
        comando = leitor.palavra()
        if comando == "INSERIR":
            rede.inserir(leitor)
        elif comando == "LUCRO":
            rede.lucro(leitor)
        elif comando == "REMOVER":
            saida.append(rede.remover())
        elif comando == "DIST":
            saida.append(rede.dist(leitor))


def main():
    
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    tolerancia = leitor.inteiro()
    rede = Rede(tolerancia)
    for _ in range(n):                    
        ident = leitor.inteiro()
        leitor.inteiro()                  
        leitor.inteiro()                  
        rede.registro.inserir(ident, leitor.inteiro())
    ler_rotas(leitor, m, rede.registro.grafo)   

    saida = []
    p = leitor.inteiro()
    for _ in range(p):
        executar_lote(leitor, rede, saida)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
