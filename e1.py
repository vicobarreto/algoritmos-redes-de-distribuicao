"""
Algoritmos e Estruturas de Dados - Turma BCC - 2026.2
Rede de distribuição - Entregável 1: histórico de períodos

Autores: Vinicius Lima, Laércio Neto e Zaque Mateus

Operações exercitadas neste entregável: INSERIR, LUCRO, MELHOR e PROSPERIDADE.
As rotas (setup e INSERIR) são lidas e descartadas.

Resumo das estruturas de dados (e por que foram escolhidas):

  * RegistroDepositos  - dict (tabela hash) id -> lucro, mais um acumulador
    com a soma dos lucros. Os ids chegam a 10^9, mas há no máximo 5000
    depósitos vivos: um vetor indexado pelo id seria inviável; a tabela hash
    dá busca/inserção/atualização em O(1) esperado e ocupa O(n). O acumulador
    evita somar todos os depósitos a cada período.
  * PilhaProsperidade  - lista do Python usada como pilha (append/pop no fim
    são O(1) amortizado), mais um acumulador com a soma dos resíduos.
  * HistoricoMelhorIntervalo - 5 inteiros (algoritmo de Kadane "online"):
    programação dinâmica com espaço O(1); não guarda o histórico dos L_k.

Notação de complexidade: n = depósitos vivos, P = períodos registrados,
h = altura da pilha de prosperidade.
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

    def pular(self, k):
       
        self.pos += k



class RegistroDepositos:
   

    def __init__(self):
        self.lucro = {}
        self.total = 0

    def inserir(self, ident, lucro):
       
        self.lucro[ident] = lucro
        self.total += lucro

    def atualizar_lucro(self, ident, novo):
       
        self.total += novo - self.lucro[ident]
        self.lucro[ident] = novo



class PilhaProsperidade:
   
    def __init__(self):
        """Cria a pilha vazia. O(1)."""
        self.itens = []
        self.soma = 0

    def registrar(self, k, lk):
        
        if lk > 0:
            self.itens.append((k, lk))
            self.soma += lk
        elif lk < 0:
            d = -lk
            while d > 0 and self.itens:
                j, r = self.itens[-1]
                if r > d:
                    
                    self.itens[-1] = (j, r - d)
                    self.soma -= d
                    d = 0
                else:
                    self.itens.pop()
                    self.soma -= r
                    d -= r

    def descricao(self):
        
        if not self.itens:
            return "0"
        b = self.itens[0][0]
        i, r = self.itens[-1]
        return "%d %d %d %d %d" % (len(self.itens), b, self.soma, i, r)



class HistoricoMelhorIntervalo:
   

    def __init__(self):
        self.vazio = True
        self.suf_soma = 0
        self.suf_i = 0
        self.melhor_soma = 0
        self.melhor_i = 0
        self.melhor_j = 0

    def registrar(self, k, lk):
        
        if self.vazio or self.suf_soma < 0:
            self.suf_soma = lk
            self.suf_i = k
        else:
            self.suf_soma += lk
        if self.vazio or self.suf_soma > self.melhor_soma:
            self.melhor_soma = self.suf_soma
            self.melhor_i = self.suf_i
            self.melhor_j = k
        self.vazio = False

    def descricao(self):
        
        return "%d %d %d" % (self.melhor_i, self.melhor_j, self.melhor_soma)



def tratar_inserir(leitor, registro):
   
    ident = leitor.inteiro()
    leitor.pular(2)                       
    lucro = leitor.inteiro()
    r = leitor.inteiro()
    registro.inserir(ident, lucro)
    leitor.pular(3 * r)


def tratar_lucro(leitor, registro):
   
    ident = leitor.inteiro()
    novo = leitor.inteiro()
    registro.atualizar_lucro(ident, novo)


def executar_lote(leitor, registro, pilha, historico, saida):
   
    q = leitor.inteiro()
    for _ in range(q):
        comando = leitor.palavra()
        if comando == "INSERIR":
            tratar_inserir(leitor, registro)
        elif comando == "LUCRO":
            tratar_lucro(leitor, registro)
        elif comando == "MELHOR":
            saida.append(historico.descricao())
        elif comando == "PROSPERIDADE":
            saida.append(pilha.descricao())


def fechar_periodo(k, registro, pilha, historico):
   
    lk = registro.total
    pilha.registrar(k, lk)
    historico.registrar(k, lk)


def main():
  
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    leitor.inteiro()                      

    registro = RegistroDepositos()
    for _ in range(n):                    
        ident = leitor.inteiro()
        leitor.pular(2)               
        registro.inserir(ident, leitor.inteiro())
    leitor.pular(3 * m)                 

    pilha = PilhaProsperidade()
    historico = HistoricoMelhorIntervalo()
    fechar_periodo(1, registro, pilha, historico)   

    saida = []
    p = leitor.inteiro()                 
    for k in range(2, p + 2):
        executar_lote(leitor, registro, pilha, historico, saida)
        fechar_periodo(k, registro, pilha, historico)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
