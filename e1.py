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


# ---------------------------------------------------------------------------
# Leitura da entrada
# ---------------------------------------------------------------------------
class Leitor:
    """
    Percorre a lista de tokens (palavras separadas por espaço/quebra de linha).

    Campos:
      tokens - lista de str com toda a entrada (lida de uma só vez, o que é
               bem mais rápido em Python do que chamar input() muitas vezes).
      pos    - índice do próximo token ainda não consumido.
    Invariante: 0 <= pos <= len(tokens).
    """

    __slots__ = ("tokens", "pos")

    def __init__(self, tokens):
        """Recebe a lista de tokens. O(1)."""
        self.tokens = tokens
        self.pos = 0

    def palavra(self):
        """
        Pré-condição: ainda há tokens. Devolve o próximo token (str) e avança
        o cursor. Tempo O(1).
        """
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def inteiro(self):
        """Como palavra(), mas converte para int. Tempo O(1)."""
        return int(self.palavra())

    def pular(self, k):
        """
        Descarta k tokens sem convertê-los. É assim que as rotas são
        "lidas e descartadas": cada rota ocupa 3 tokens (u v c), então
        pular(3*m) consome as m rotas do setup. Tempo O(1).
        """
        self.pos += k


# ---------------------------------------------------------------------------
# Registro de depósitos
# ---------------------------------------------------------------------------
class RegistroDepositos:
    """
    Registro dos depósitos vivos com acesso por identificador.

    Estrutura da biblioteca: dict do Python (tabela hash). Operações usadas
    (busca, inserção, atribuição por chave): O(1) esperado, assumindo boa
    dispersão das chaves; pior caso O(n) se houver muitas colisões.
    Espaço O(n).

    Campos:
      lucro  - dict id -> lucro atual do depósito vivo.
      total  - soma dos lucros de todos os depósitos vivos.
    Invariante entre as operações: total == soma de lucro.values().
    (É isso que permite obter L_k sem varrer os depósitos.)
    """

    def __init__(self):
        """Cria o registro vazio. O(1)."""
        self.lucro = {}
        self.total = 0

    def inserir(self, ident, lucro):
        """
        Pré-condição: ident ainda não foi usado (garantia da entrada).
        Cria o depósito e soma seu lucro ao total.
        Tempo O(1) esperado (inserção em dict).
        """
        self.lucro[ident] = lucro
        self.total += lucro

    def atualizar_lucro(self, ident, novo):
        """
        Pré-condição: ident está vivo.
        Substitui o lucro (não soma) e corrige o total pela diferença
        novo - antigo, sem percorrer os outros depósitos.
        Tempo O(1) esperado (uma busca e uma atribuição no dict).
        """
        self.total += novo - self.lucro[ident]
        self.lucro[ident] = novo


# ---------------------------------------------------------------------------
# Pilha de prosperidade
# ---------------------------------------------------------------------------
class PilhaProsperidade:
    """
    Pilha de pares (j, r): j = período em que houve lucro positivo,
    r > 0 = parte desse lucro ainda não absorvida por prejuízos.

    Estrutura: list do Python; append/pop no fim são O(1) amortizado.

    Campos:
      itens - lista de tuplas (j, r); itens[0] é a base (ganho mais antigo)
              e itens[-1] é o topo (ganho mais recente).
      soma  - S, a soma de todos os resíduos r da pilha.
    Invariantes:
      * todo r é estritamente positivo;
      * os j são estritamente crescentes da base para o topo;
      * soma == soma dos r (mantida incrementalmente).
    """

    def __init__(self):
        """Cria a pilha vazia. O(1)."""
        self.itens = []
        self.soma = 0

    def registrar(self, k, lk):
        """
        Pré-condição: chamada exatamente uma vez por período k, logo após
        calcular L_k = lk.
        Efeito (regras da seção 1.4):
          lk > 0  -> empilha (k, lk);
          lk == 0 -> não muda nada;
          lk < 0  -> compensa o prejuízo d = -lk consumindo o topo.
        Complexidade: O(1) amortizado por período (O(h) no pior período).
        Justificativa (método agregado): cada período empilha no máximo um
        elemento; um elemento só é desempilhado uma vez, depois de
        empilhado. Em P períodos há <= P empilhamentos e, portanto, <= P
        desempilhamentos no total: custo total O(P), ou O(1) por período,
        mesmo que um único período desempilhe vários elementos.
        """
        if lk > 0:
            self.itens.append((k, lk))
            self.soma += lk
        elif lk < 0:
            d = -lk                       # prejuízo ainda a compensar
            while d > 0 and self.itens:
                j, r = self.itens[-1]
                if r > d:
                    # o topo absorve todo o prejuízo e sobra resíduo;
                    # mantém o índice j do período em que o ganho ocorreu
                    self.itens[-1] = (j, r - d)
                    self.soma -= d
                    d = 0
                else:
                    # o topo é consumido por inteiro (r <= d): sai da pilha
                    self.itens.pop()
                    self.soma -= r
                    d -= r
            # se a pilha esvaziou e ainda sobra d, a sobra é descartada

    def descricao(self):
        """
        Devolve a linha da operação PROSPERIDADE: "0" se a pilha está vazia;
        senão "h b s i r" (altura, período da base, soma dos resíduos,
        período do topo, resíduo do topo). Não altera a pilha.
        Tempo O(1): só lê a base, o topo, o tamanho e o acumulador `soma`
        (por isso S nunca é recalculada somando a pilha).
        """
        if not self.itens:
            return "0"
        b = self.itens[0][0]
        i, r = self.itens[-1]
        return "%d %d %d %d %d" % (len(self.itens), b, self.soma, i, r)


# ---------------------------------------------------------------------------
# Melhor intervalo (Kadane online)
# ---------------------------------------------------------------------------
class HistoricoMelhorIntervalo:
    """
    Mantém o intervalo [i, j] de maior soma de L_i + ... + L_j entre os
    períodos já registrados (programação dinâmica; algoritmo de Kadane).

    Recorrência: seja suf(k) a maior soma de um intervalo que TERMINA em k.
        suf(k) = L_k + max(0, suf(k-1))
    ou seja, estende-se o melhor intervalo que termina em k-1 se ele não for
    negativo; senão recomeça em k. O estado de k depende só do de k-1, então
    não é preciso guardar o histórico: espaço O(1).

    Campos:
      suf_soma, suf_i - soma e início do melhor intervalo terminando no
                        último período registrado.
      melhor_soma, melhor_i, melhor_j - melhor intervalo global até agora.
      vazio           - True enquanto nenhum período foi registrado.
    Invariantes após registrar o período k:
      * suf_soma = max_{i<=k} (L_i+...+L_k), com o MENOR i que atinge o max;
      * [melhor_i, melhor_j] é o intervalo de maior soma em 1..k, com menor
        i e, persistindo o empate, menor j. Nunca é vazio.
    """

    def __init__(self):
        """Estado inicial (nenhum período). O(1)."""
        self.vazio = True
        self.suf_soma = 0
        self.suf_i = 0
        self.melhor_soma = 0
        self.melhor_i = 0
        self.melhor_j = 0

    def registrar(self, k, lk):
        """
        Pré-condição: chamada uma vez por período, em ordem k = 1, 2, 3...
        Atualiza o estado com L_k = lk. Tempo O(1) (poucas comparações),
        espaço O(1).
        Desempates:
          * estende quando suf_soma >= 0 (e não só > 0): com soma anterior
            zero, estender dá a mesma soma que recomeçar, mas com i menor;
          * troca o melhor global só se a soma é ESTRITAMENTE maior: em
            empate o intervalo antigo já tem i menor ou igual e j menor.
        """
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
        """
        Pré-condição: ao menos um período registrado (sempre vale: o
        período 1 é registrado antes de qualquer operação).
        Devolve a linha "i j S" da operação MELHOR. Tempo O(1).
        """
        return "%d %d %d" % (self.melhor_i, self.melhor_j, self.melhor_soma)


# ---------------------------------------------------------------------------
# Tratamento dos comandos
# ---------------------------------------------------------------------------
def tratar_inserir(leitor, registro):
    """
    Comando INSERIR id x y L r (seguido de r linhas de rota u v c).
    Recebe o leitor posicionado logo após a palavra INSERIR e o registro.
    Cria o depósito (as coordenadas não são usadas neste entregável) e
    descarta as r rotas, consumindo 3*r tokens. Não imprime nada.
    Tempo O(1) esperado (a leitura das rotas é só avançar o cursor).
    """
    ident = leitor.inteiro()
    leitor.pular(2)                       # x e y
    lucro = leitor.inteiro()
    r = leitor.inteiro()
    registro.inserir(ident, lucro)
    leitor.pular(3 * r)


def tratar_lucro(leitor, registro):
    """
    Comando LUCRO id L. Pré-condição: id vivo.
    Substitui o lucro do depósito. Não imprime nada.
    Tempo O(1) esperado (ver RegistroDepositos.atualizar_lucro).
    """
    ident = leitor.inteiro()
    novo = leitor.inteiro()
    registro.atualizar_lucro(ident, novo)


def executar_lote(leitor, registro, pilha, historico, saida):
    """
    Lê e executa um lote: q, seguido de q comandos (cada INSERIR traz as
    suas rotas, que não contam em q). Acrescenta em `saida` uma linha por
    MELHOR/PROSPERIDADE. Ao fim, o lote NÃO fecha o período; quem chama
    faz isso. Como as consultas só enxergam os períodos já registrados,
    MELHOR e PROSPERIDADE usam o estado até k-1.
    Tempo O(q) esperado: cada comando é O(1) esperado.
    """
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
    """
    Registra o período k: L_k = registro.total (já mantido, sem varrer os
    depósitos), e atualiza a pilha e o histórico com ele.
    Tempo O(1) amortizado (a pilha é O(1) amortizada, o histórico O(1)).
    """
    lk = registro.total
    pilha.registrar(k, lk)
    historico.registrar(k, lk)


def main():
    """
    Ponto de ancoragem. Lê toda a entrada, executa o setup e os P lotes e
    escreve as respostas. Tempo total O(T_ops) esperado, onde T_ops é o
    número de comandos (cada um O(1) esperado/amortizado); espaço
    O(n + tamanho da entrada) pelos tokens e pelo registro.
    """
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    leitor.inteiro()                      # T: não é usada neste entregável

    registro = RegistroDepositos()
    for _ in range(n):                    # n linhas "id x y L"
        ident = leitor.inteiro()
        leitor.pular(2)                   # x e y
        registro.inserir(ident, leitor.inteiro())
    leitor.pular(3 * m)                   # m rotas "u v c": lidas e descartadas

    pilha = PilhaProsperidade()
    historico = HistoricoMelhorIntervalo()
    fechar_periodo(1, registro, pilha, historico)   # período 1: após o setup

    saida = []
    p = leitor.inteiro()                  # períodos além do primeiro
    for k in range(2, p + 2):
        executar_lote(leitor, registro, pilha, historico, saida)
        fechar_periodo(k, registro, pilha, historico)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
