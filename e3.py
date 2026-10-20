"""
Algoritmos e Estruturas de Dados - Turma BCC - 2026.2
Rede de distribuição - Entregável 3: rede de rotas

Autores: [preencher nomes e matrículas do grupo]

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


# ---------------------------------------------------------------------------
# Leitura da entrada
# ---------------------------------------------------------------------------
class Leitor:
    """
    Percorre a lista de tokens (palavras separadas por espaço/quebra de linha).

    Campos:
      tokens - lista de str com toda a entrada (lida de uma só vez).
      pos    - índice do próximo token ainda não consumido.
    Invariante: 0 <= pos <= len(tokens).
    """

    __slots__ = ("tokens", "pos")

    def __init__(self, tokens):
        """Recebe a lista de tokens. O(1)."""
        self.tokens = tokens
        self.pos = 0

    def palavra(self):
        """Devolve o próximo token (str) e avança o cursor. O(1)."""
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def inteiro(self):
        """Como palavra(), mas converte para int. O(1)."""
        return int(self.palavra())


# ---------------------------------------------------------------------------
# Fila de prioridade com alteração de chave
# ---------------------------------------------------------------------------
class FilaPrioridadeMin:
    """
    Heap binário de mínimo indexado: guarda pares (id, chave) e ordena pela
    chave. Permite inserir, ler o mínimo, extrair o mínimo e ALTERAR a chave
    de qualquer id presente.

    Campos:
      ids    - vetor do heap: ids[i] é o id que está na posição i.
      chaves - vetor paralelo: chaves[i] é a chave de ids[i].
      pos    - dict id -> índice i tal que ids[i] == id.
    O filho de i está em 2i+1 e 2i+2; o pai de i está em (i-1)//2.
    Invariantes entre as operações:
      (1) ordem do heap: chaves[pai(i)] <= chaves[i] para todo i > 0
          (logo o mínimo está sempre em chaves[0]);
      (2) pos é o inverso de ids: pos[ids[i]] == i e len(pos) == len(ids)
          (durante um _subir/_descer ele fica momentaneamente incompleto;
          vale de novo quando a operação termina);
      (3) nenhum id aparece duas vezes.
    Espaço O(n). O dict `pos` torna "achar um id" O(1) esperado (hash).
    """

    def __init__(self):
        """Cria a fila vazia. O(1)."""
        self.ids = []
        self.chaves = []
        self.pos = {}

    def __len__(self):
        """Número de elementos. O(1)."""
        return len(self.ids)

    def __contains__(self, ident):
        """True se ident está na fila. O(1) esperado (busca no dict)."""
        return ident in self.pos

    def minimo(self):
        """
        Pré-condição: fila não vazia. Devolve (id, chave) do menor elemento
        sem removê-lo. O(1): é a raiz, pelo invariante (1).
        """
        return self.ids[0], self.chaves[0]

    def _subir(self, i):
        """
        Pré-condição: a ordem do heap só pode estar violada entre i e seu pai.
        Leva o elemento da posição i para cima até o lugar certo. Em vez de
        trocar o elemento com o pai a cada passo, ele fica "na mão" e os pais
        maiores descem um nível (um "buraco" sobe); o elemento é escrito uma
        única vez no fim. Cada pai que desce tem `pos` atualizado, então o
        invariante (2) volta a valer ao terminar.
        O(log n): a altura do heap é floor(log2 n) e cada passo sobe um nível.
        """
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
        """
        Pré-condição: a ordem do heap só pode estar violada entre i e seus
        filhos. Leva o elemento da posição i para baixo até o lugar certo,
        subindo o menor filho a cada passo (mesma ideia do "buraco" de
        _subir). O(log n): cada passo desce um nível.
        """
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
        """
        Pré-condição: ident não está na fila. Coloca o novo elemento no fim
        do vetor (próxima folha) e o faz subir até a posição correta.
        O(log n) no pior caso (um _subir). Espaço adicional O(1).
        """
        i = len(self.ids)
        self.ids.append(ident)
        self.chaves.append(chave)
        self.pos[ident] = i
        self._subir(i)

    def alterar_chave(self, ident, nova):
        """
        Pré-condição: ident está na fila. Troca a chave (para maior ou para
        menor) e restaura o heap: se diminuiu, só pode precisar subir; se
        aumentou, só pode precisar descer (no Dijkstra isto é o decrease-key).
        O(log n) no pior caso: acha a posição em O(1) esperado por `pos` e
        faz um único _subir ou _descer.
        """
        i = self.pos[ident]
        antiga = self.chaves[i]
        self.chaves[i] = nova
        if nova < antiga:
            self._subir(i)
        elif nova > antiga:
            self._descer(i)

    def extrair_minimo(self):
        """
        Pré-condição: fila não vazia. Remove e devolve (id, chave) do menor
        elemento: tira o último elemento do vetor, coloca-o na raiz e o faz
        descer até o lugar certo.
        O(log n) no pior caso (um _descer).
        """
        ident, chave = self.ids[0], self.chaves[0]
        ult_id = self.ids.pop()
        ult_chave = self.chaves.pop()
        del self.pos[ident]
        if self.ids:
            self.ids[0] = ult_id
            self.chaves[0] = ult_chave
            self.pos[ult_id] = 0
            self._descer(0)
        return ident, chave


# ---------------------------------------------------------------------------
# Grafo de rotas
# ---------------------------------------------------------------------------
class GrafoRotas:
    """
    Grafo dirigido, esparso e dinâmico das rotas entre depósitos vivos.

    Estruturas: dict e set da biblioteca (tabelas hash; busca, inserção e
    remoção O(1) esperado). Espaço O(n + m).

    Campos:
      saida   - dict u -> dict {v: custo}: rotas que SAEM de u.
      entrada - dict v -> set {u}: depósitos u com rota u -> v (rotas que
                CHEGAM a v; o custo fica só em `saida`).
    Invariantes entre as operações:
      * as chaves de `saida` e de `entrada` são exatamente os depósitos
        vivos (cada vivo tem as duas entradas, mesmo vazias);
      * v in saida[u]  <=>  u in entrada[v]  (a rota está nas duas);
      * não há rota de u para u, nem rotas para depósitos removidos.
    """

    def __init__(self):
        """Cria o grafo vazio. O(1)."""
        self.saida = {}
        self.entrada = {}

    def adicionar_vertice(self, ident):
        """Pré-condição: ident novo. Cria o vértice sem rotas. O(1) esperado."""
        self.saida[ident] = {}
        self.entrada[ident] = set()

    def adicionar_rota(self, u, v, custo):
        """
        Pré-condição: u e v vivos, u != v, rota (u, v) ainda inexistente
        (garantias da entrada). Registra a rota nas duas listas.
        O(1) esperado.
        """
        self.saida[u][v] = custo
        self.entrada[v].add(u)

    def remover_vertice(self, u):
        """
        Pré-condição: u vivo. Apaga u e todas as rotas que saem dele ou
        chegam a ele, mantendo os invariantes:
          * para cada v em saida[u]: tira u de entrada[v];
          * para cada w em entrada[u]: tira u de saida[w];
          * apaga as entradas de u nos dois dicionários.
        O(grau_saida(u) + grau_entrada(u)) esperado: só visita as rotas
        incidentes a u. Só com a lista de saída, achar quem chega em u
        custaria O(n + m) (varrer o grafo todo).
        """
        for v in self.saida[u]:
            self.entrada[v].discard(u)
        for w in self.entrada[u]:
            del self.saida[w][u]
        del self.saida[u]
        del self.entrada[u]

    def menores_custos(self, origem):
        """
        Dijkstra a partir de `origem` (vivo). Devolve um dict id -> menor
        custo de transporte para cada depósito ALCANÇÁVEL (inclui a origem,
        com 0); os não alcançáveis simplesmente não aparecem.

        Algoritmo: mantém a distância provisória `dist` de cada vértice já
        descoberto e uma FilaPrioridadeMin com os ainda não fechados,
        ordenada por `dist`. Repete: extrai o de menor distância (ela agora
        é definitiva) e RELAXA suas rotas de saída: para a rota (u, v, c),
        se dist[u] + c < dist[v], atualiza dist[v] (decrease-key no heap,
        ou inserção se v acabou de ser descoberto).
        Correção: com custos c >= 1 (positivos), qualquer caminho passando
        por um vértice ainda aberto não pode ser mais barato que o menor
        provisório, então fechá-lo é seguro (escolha gulosa). Por isso os
        vértices fechados nunca são melhorados depois.
        Complexidade O((n + m) log n): cada vértice é inserido e extraído
        uma vez (n * O(log n)) e cada rota é relaxada uma vez, com no
        máximo um decrease-key de O(log n) (m * O(log n)).
        Espaço adicional O(n) (dist e o heap).
        """
        dist = {origem: 0}
        fila = FilaPrioridadeMin()
        fila.inserir(origem, 0)
        saida = self.saida
        while len(fila) > 0:
            u, du = fila.extrair_minimo()
            for v, c in saida[u].items():
                nd = du + c
                if v not in dist:
                    dist[v] = nd
                    fila.inserir(v, nd)
                elif nd < dist[v]:
                    dist[v] = nd
                    fila.alterar_chave(v, nd)
        return dist


# ---------------------------------------------------------------------------
# Registro de depósitos
# ---------------------------------------------------------------------------
class RegistroDepositos:
    """
    Registro dos depósitos vivos (Entregável 1, com a remoção do 2) que agora
    também mantém o grafo de rotas coerente.

    Campos:
      fila  - FilaPrioridadeMin com um elemento por depósito vivo; a chave
              é o lucro. Seu mínimo é o menor lucro.
      grafo - GrafoRotas.
    Invariantes entre as operações:
      * os ids em `fila` são exatamente os vértices de `grafo` (os vivos);
      * a chave de cada id na fila é o lucro atual do depósito;
      * remover um depósito o apaga da fila E do grafo (todas as estruturas
        que o mencionam).
    Espaço O(n + m).
    """

    def __init__(self):
        """Cria o registro vazio. O(1)."""
        self.fila = FilaPrioridadeMin()
        self.grafo = GrafoRotas()

    def inserir(self, ident, lucro):
        """
        Pré-condição: ident nunca foi usado. Cria o depósito vivo, sem
        rotas. O(log n) (inserção no heap; o grafo é O(1) esperado).
        """
        self.fila.inserir(ident, lucro)
        self.grafo.adicionar_vertice(ident)

    def atualizar_lucro(self, ident, novo):
        """Pré-condição: ident vivo. Substitui o lucro. O(log n)."""
        self.fila.alterar_chave(ident, novo)

    def remover_abaixo(self, tolerancia):
        """
        Fecha os depósitos vivos com lucro estritamente menor que
        `tolerancia`, removendo-os da fila e do grafo (com suas rotas de
        entrada e de saída). Devolve quantos foram fechados.
        O(k log n + soma dos graus dos k removidos) esperado: a raiz é o
        menor lucro, então o laço para na primeira raiz >= T sem examinar
        os demais depósitos.
        """
        fila = self.fila
        removidos = 0
        while len(fila) > 0 and fila.minimo()[1] < tolerancia:
            ident, _ = fila.extrair_minimo()
            self.grafo.remover_vertice(ident)
            removidos += 1
        return removidos


# ---------------------------------------------------------------------------
# Tratamento dos comandos
# ---------------------------------------------------------------------------
def ler_rotas(leitor, quantidade, grafo):
    """
    Lê `quantidade` linhas "u v c" e as insere no grafo.
    Pré-condição: os dois extremos de cada rota estão vivos (no INSERIR, o
    novo depósito já foi criado antes). Tempo O(quantidade) esperado.
    """
    for _ in range(quantidade):
        u = leitor.inteiro()
        v = leitor.inteiro()
        c = leitor.inteiro()
        grafo.adicionar_rota(u, v, c)


class Rede:
    """
    Estado do programa: registro + tolerância T (fixa na execução).
    """

    def __init__(self, tolerancia):
        """Cria a rede vazia com tolerância T. O(1)."""
        self.registro = RegistroDepositos()
        self.tolerancia = tolerancia

    def inserir(self, leitor):
        """
        Comando INSERIR id x y L r + r rotas. Cria o depósito (as
        coordenadas não são usadas aqui) e lê as r rotas para o grafo.
        Não imprime nada. Tempo O(log n + r) esperado, com r <= 20.
        """
        ident = leitor.inteiro()
        leitor.inteiro()                  # x
        leitor.inteiro()                  # y
        lucro = leitor.inteiro()
        r = leitor.inteiro()
        self.registro.inserir(ident, lucro)
        ler_rotas(leitor, r, self.registro.grafo)

    def lucro(self, leitor):
        """
        Comando LUCRO id L (id vivo). Substitui o lucro. Não imprime nada.
        Tempo O(log n).
        """
        ident = leitor.inteiro()
        novo = leitor.inteiro()
        self.registro.atualizar_lucro(ident, novo)

    def remover(self):
        """
        Comando REMOVER. Fecha os depósitos com lucro < T (e suas rotas) e
        devolve a linha com a quantidade. Tempo: ver remover_abaixo.
        """
        return str(self.registro.remover_abaixo(self.tolerancia))

    def dist(self, leitor):
        """
        Comando DIST s (s vivo). Devolve a linha com o menor custo de s a
        cada outro depósito vivo, em ordem crescente de id, separados por
        espaço; -1 para os inalcançáveis; linha vazia se s é o único vivo.
        Tempo O((n + m) log n) do Dijkstra + O(n log n) para ordenar os ids
        (os ids chegam a 10^9 e não são contíguos, então é preciso ordenar).
        Espaço adicional O(n).
        """
        s = leitor.inteiro()
        dist = self.registro.grafo.menores_custos(s)
        vivos = sorted(self.registro.grafo.saida)
        return " ".join(str(dist.get(v, -1)) for v in vivos if v != s)


def executar_lote(leitor, rede, saida):
    """
    Lê e executa um lote: q e depois q comandos (cada INSERIR traz as suas
    rotas, que não contam em q). Acrescenta em `saida` uma linha por
    DIST/REMOVER. Tempo: soma dos custos dos comandos (ver Rede).
    """
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
    """
    Ponto de ancoragem. Lê o setup (n depósitos e m rotas), depois os P
    lotes, e escreve as respostas.
    Tempo: n inserções O(n log n) + m rotas O(m) + custo dos comandos;
    espaço O(n + m + entrada).
    """
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    tolerancia = leitor.inteiro()
    rede = Rede(tolerancia)
    for _ in range(n):                    # n linhas "id x y L"
        ident = leitor.inteiro()
        leitor.inteiro()                  # x
        leitor.inteiro()                  # y
        rede.registro.inserir(ident, leitor.inteiro())
    ler_rotas(leitor, m, rede.registro.grafo)   # m rotas "u v c"

    saida = []
    p = leitor.inteiro()
    for _ in range(p):
        executar_lote(leitor, rede, saida)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
