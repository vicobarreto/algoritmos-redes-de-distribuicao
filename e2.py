"""
Algoritmos e Estruturas de Dados - Turma BCC - 2026.2
Rede de distribuição - Entregável 2: fechamento e proximidade

Autores: Vinicius Lima, Laércio Neto e Zaque Mateus

Operações exercitadas neste entregável: REMOVER, PAR, INSERIR e LUCRO.
As rotas (setup e INSERIR) são lidas e descartadas.

Resumo das estruturas de dados (e por que foram escolhidas):

  * FilaPrioridadeMin - heap binário de mínimo, implementado por nós, com
    tabela de posições (dict id -> índice no vetor). O heap da biblioteca
    (heapq) não permite mudar a chave de um elemento arbitrário; o LUCRO
    exige isso. Com a tabela de posições achamos o elemento em O(1)
    esperado e o reposicionamos em O(log n). O mínimo (menor lucro) fica
    sempre na raiz, então REMOVER só visita quem será removido.
  * RegistroDepositos - evolução do registro do Entregável 1: o dict id ->
    lucro foi substituído pelo heap (que já é indexado por id, e guarda o
    lucro como chave), mais um dict id -> (x, y) com as coordenadas.
  * Divisão e conquista (par mais próximo) - O(n log n) por consulta, sem
    nenhuma matriz/heap de distâncias entre pares. O último resultado é
    guardado em cache e só é descartado se o conjunto de vivos mudar.

Notação: n = depósitos vivos.
"""

import math
import sys
from operator import itemgetter



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

    def pular(self, k):
        self.pos += k



class FilaPrioridadeMin:
    

    def __init__(self):
        self.ids = []
        self.chaves = []
        self.pos = {}

    def __len__(self):
        return len(self.ids)

    def __contains__(self, ident):
        return ident in self.pos

    def chave_de(self, ident):
        return self.chaves[self.pos[ident]]

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



class RegistroDepositos:
   

    def __init__(self):
        self.fila = FilaPrioridadeMin()
        self.coord = {}

    def inserir(self, ident, x, y, lucro):
        
        self.coord[ident] = (x, y)
        self.fila.inserir(ident, lucro)

    def atualizar_lucro(self, ident, novo):
        
        self.fila.alterar_chave(ident, novo)

    def remover_abaixo(self, tolerancia):
       
        fila = self.fila
        removidos = 0
        while len(fila) > 0 and fila.minimo()[1] < tolerancia:
            ident, _ = fila.extrair_minimo()
            del self.coord[ident]
            removidos += 1
        return removidos



FOLHA = 32


def _confere_pares(por_y, melhor):
   
    tam = len(por_y)
    for i in range(tam):
        xi, yi, idi = por_y[i]
        for j in range(i + 1, tam):
            xj, yj, idj = por_y[j]
            dy = yj - yi
            if dy * dy >= melhor[0]:
                break      
            d2 = (xi - xj) ** 2 + dy * dy
            if d2 < melhor[0]:
                melhor[0] = d2
                melhor[1] = idi if idi < idj else idj
                melhor[2] = idj if idi < idj else idi


def _par_recursivo(pts, lo, hi, melhor):
   
    n = hi - lo
    if n <= FOLHA:
        por_y = sorted(pts[lo:hi], key=itemgetter(1))
        _confere_pares(por_y, melhor)
        return por_y

    meio = (lo + hi) // 2
    x_meio = pts[meio][0]                      
    y_esq = _par_recursivo(pts, lo, meio, melhor)
    y_dir = _par_recursivo(pts, meio, hi, melhor)
    por_y = sorted(y_esq + y_dir, key=itemgetter(1))

   
    delta = math.isqrt(melhor[0]) + 1
    esquerda, direita = x_meio - delta, x_meio + delta
    faixa = [p for p in por_y if esquerda < p[0] < direita]
    _confere_pares(faixa, melhor)
   
    return por_y


def teto_raiz_inteira(d2):
    
    t = math.isqrt(d2)
    if t * t < d2:
        t += 1
    return t


def par_mais_proximo(coord):
   
    pts = [(x, y, ident) for ident, (x, y) in coord.items()]
    pts.sort()
    melhor = None
    ant = pts[0]
    for k in range(1, len(pts)):
        q = pts[k]
        dx = ant[0] - q[0]
        dy = ant[1] - q[1]
        d2 = dx * dx + dy * dy
        if melhor is None or d2 < melhor[0]:
            melhor = [d2, min(ant[2], q[2]), max(ant[2], q[2])]
        ant = q
    _par_recursivo(pts, 0, len(pts), melhor)
    return melhor[1], melhor[2], teto_raiz_inteira(melhor[0])



class Rede:
  

    def __init__(self, tolerancia):
        self.registro = RegistroDepositos()
        self.tolerancia = tolerancia
        self.cache_par = None

    def inserir(self, leitor):
        
        ident = leitor.inteiro()
        x = leitor.inteiro()
        y = leitor.inteiro()
        lucro = leitor.inteiro()
        r = leitor.inteiro()
        self.registro.inserir(ident, x, y, lucro)
        leitor.pular(3 * r)
        self.cache_par = None

    def lucro(self, leitor):
      
        ident = leitor.inteiro()
        novo = leitor.inteiro()
        self.registro.atualizar_lucro(ident, novo)

    def remover(self):
        
        k = self.registro.remover_abaixo(self.tolerancia)
        if k > 0:
            self.cache_par = None
        return str(k)

    def par(self):
        
        if self.cache_par is None:
            a, b, d = par_mais_proximo(self.registro.coord)
            self.cache_par = "%d %d %d" % (a, b, d)
        return self.cache_par


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
        elif comando == "PAR":
            saida.append(rede.par())


def main():
    
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    tolerancia = leitor.inteiro()
    rede = Rede(tolerancia)
    for _ in range(n):                    
        ident = leitor.inteiro()
        x = leitor.inteiro()
        y = leitor.inteiro()
        rede.registro.inserir(ident, x, y, leitor.inteiro())
    leitor.pular(3 * m)                   

    saida = []
    p = leitor.inteiro()
    for _ in range(p):
        executar_lote(leitor, rede, saida)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
