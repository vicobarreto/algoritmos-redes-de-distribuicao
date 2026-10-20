"""
Algoritmos e Estruturas de Dados - Turma BCC - 2026.2
Rede de distribuição - Entregável 2: fechamento e proximidade

Autores: [preencher nomes e matrículas do grupo]

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

    def pular(self, k):
        """Descarta k tokens (ex.: 3*m para m rotas lidas e descartadas). O(1)."""
        self.pos += k


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

    def chave_de(self, ident):
        """Pré-condição: ident está na fila. Devolve sua chave. O(1) esperado."""
        return self.chaves[self.pos[ident]]

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
        aumentou, só pode precisar descer.
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
# Registro de depósitos
# ---------------------------------------------------------------------------
class RegistroDepositos:
    """
    Registro dos depósitos vivos, com acesso por identificador e remoção.

    Estruturas: FilaPrioridadeMin (id -> lucro, ordenada pelo lucro) e dict
    da biblioteca (tabela hash; busca/inserção/remoção O(1) esperado) para
    as coordenadas.

    Campos:
      fila - heap com um elemento por depósito vivo; a chave é o lucro.
      coord - dict id -> (x, y) dos depósitos vivos.
    Invariantes entre as operações:
      * fila e coord têm exatamente o mesmo conjunto de ids (os vivos);
      * a chave de cada id na fila é o lucro atual do depósito;
      * como o mínimo do heap é o menor lucro, se ele é >= T não existe
        depósito abaixo da tolerância.
    Espaço O(n).
    """

    def __init__(self):
        """Cria o registro vazio. O(1)."""
        self.fila = FilaPrioridadeMin()
        self.coord = {}

    def inserir(self, ident, x, y, lucro):
        """
        Pré-condição: ident nunca foi usado. Cria o depósito vivo.
        O(log n): inserção no heap; o dict é O(1) esperado.
        """
        self.coord[ident] = (x, y)
        self.fila.inserir(ident, lucro)

    def atualizar_lucro(self, ident, novo):
        """
        Pré-condição: ident vivo. Substitui o lucro e reposiciona o
        depósito no heap. O(log n) (alterar_chave).
        """
        self.fila.alterar_chave(ident, novo)

    def remover_abaixo(self, tolerancia):
        """
        Fecha todos os depósitos vivos com lucro estritamente menor que
        `tolerancia` e devolve quantos foram fechados. Efeito: apaga cada um
        do heap e de `coord` (invariante: nenhuma estrutura o menciona).
        O(k log n) para k removidos (o laço faz k extrações de O(log n) e
        mais uma olhada em O(1) para parar): não examina os demais
        depósitos. Justificativa: a raiz é o menor lucro; se ela é >= T,
        todos são >= T.
        """
        fila = self.fila
        removidos = 0
        while len(fila) > 0 and fila.minimo()[1] < tolerancia:
            ident, _ = fila.extrair_minimo()
            del self.coord[ident]
            removidos += 1
        return removidos


# ---------------------------------------------------------------------------
# Par mais próximo (divisão e conquista)
# ---------------------------------------------------------------------------
# Tamanho máximo de um subproblema resolvido por força bruta (todos os pares).
# Só ajusta a constante: comparar <= FOLHA pontos é O(1).
FOLHA = 8


def _par_recursivo(pts, lo, hi):
    """
    Resolve o par mais próximo para pts[lo:hi].
    Recebe `pts`: lista de tuplas (x, y, id) ORDENADA por x, e o intervalo
    meio-aberto [lo, hi) com hi - lo >= 2.
    Devolve (melhor, por_y): `melhor` = (d2, a, b) com d2 a distância ao
    quadrado (inteiro) e a < b os ids; `por_y` = os mesmos pontos de
    pts[lo:hi] ordenados por y (usado pelo nível acima, como no merge sort).
    Só usa aritmética inteira: compara distâncias AO QUADRADO.
    Complexidade: T(n) = 2T(n/2) + O(n) = O(n log n).
      * caso base (n <= FOLHA): compara todos os pares, O(1);
      * divide ao meio pela ordem em x: O(1);
      * junta as duas listas ordenadas por y: O(n) (sorted do Python
        detecta as duas sequências já ordenadas e faz uma só intercalação);
      * faixa central: O(n), pois cada ponto é comparado com no máximo 7
        seguintes (ver abaixo).
    Espaço adicional O(n) (listas por_y e faixa); profundidade O(log n).
    """
    n = hi - lo
    if n <= FOLHA:
        por_y = sorted(pts[lo:hi], key=itemgetter(1))
        d2_min = None
        for i in range(n):
            xi, yi, idi = por_y[i]
            for j in range(i + 1, n):
                xj, yj, idj = por_y[j]
                d2 = (xi - xj) ** 2 + (yi - yj) ** 2
                if d2_min is None or d2 < d2_min:
                    d2_min = d2
                    a, b = (idi, idj) if idi < idj else (idj, idi)
        melhor = (d2_min, a, b)
        return melhor, por_y

    meio = (lo + hi) // 2
    x_meio = pts[meio][0]                       # reta divisória
    esq, y_esq = _par_recursivo(pts, lo, meio)
    dir_, y_dir = _par_recursivo(pts, meio, hi)
    melhor = esq if esq < dir_ else dir_        # delta = min(delta_E, delta_D)
    por_y = sorted(y_esq + y_dir, key=itemgetter(1))

    # Um par "cruzado" (um ponto em cada metade) só melhora o resultado se
    # os dois estão a distância horizontal < delta da reta: é a faixa. Usamos
    # o piso inteiro da raiz mais 1 (sem float); incluir pontos a mais é
    # inofensivo, pois o laço abaixo confere a distância exata de cada par.
    d2_min = melhor[0]
    delta = math.isqrt(d2_min) + 1              # >= delta real: faixa um pouco larga
    esquerda, direita = x_meio - delta, x_meio + delta
    faixa = [p for p in por_y if esquerda < p[0] < direita]
    tam = len(faixa)
    for i in range(tam):
        xi, yi, idi = faixa[i]
        for j in range(i + 1, tam):
            xj, yj, idj = faixa[j]
            dy = yj - yi
            if dy * dy >= d2_min:
                break       # a faixa está ordenada por y: os próximos são piores
            d2 = (xi - xj) ** 2 + dy * dy
            if d2 < d2_min:
                d2_min = d2
                melhor = (d2, min(idi, idj), max(idi, idj))
    # Por que o laço interno é O(1): em cada metade os pontos distam >= delta
    # entre si; um retângulo 2*delta x delta da faixa comporta no máximo 8
    # desses pontos (princípio da casa dos pombos em 8 quadrados de
    # delta/2), logo cada ponto vê no máximo 7 vizinhos antes do break.
    return melhor, por_y


def teto_raiz_inteira(d2):
    """
    Recebe d2 >= 0 inteiro. Devolve o menor inteiro t com t*t >= d2, isto é,
    o teto da raiz quadrada, sem ponto flutuante: math.isqrt(d2) é o piso
    exato; se piso*piso < d2 então a raiz não é exata e somamos 1.
    Tempo O(1) para inteiros de 64 bits (isqrt é aritmética inteira exata).
    """
    t = math.isqrt(d2)
    if t * t < d2:
        t += 1
    return t


def par_mais_proximo(coord):
    """
    Pré-condição: `coord` (dict id -> (x, y)) tem pelo menos 2 depósitos,
    com coordenadas distintas e par mais próximo único.
    Devolve (a, b, d): a < b são os ids do par mais próximo e d é a
    distância euclidiana arredondada para cima.
    Tempo O(n log n): ordenar por x (O(n log n)) + divisão e conquista
    (O(n log n)). Espaço adicional O(n).
    """
    pts = sorted(((x, y, ident) for ident, (x, y) in coord.items()))
    (d2, a, b), _ = _par_recursivo(pts, 0, len(pts))
    return a, b, teto_raiz_inteira(d2)


# ---------------------------------------------------------------------------
# Tratamento dos comandos
# ---------------------------------------------------------------------------
class Rede:
    """
    Estado do programa: registro + tolerância + cache do último PAR.

    Campos:
      registro   - RegistroDepositos.
      tolerancia - T, fixa durante toda a execução.
      cache_par  - None, ou a linha "a b d" calculada para o conjunto
                   atual de depósitos vivos.
    Invariante: cache_par não é None só se o conjunto de vivos e as
    coordenadas não mudaram desde que foi calculado. Mudar o LUCRO não
    invalida (o PAR só depende das coordenadas); INSERIR e um REMOVER que
    fecha pelo menos um depósito invalidam.
    """

    def __init__(self, tolerancia):
        """Cria a rede vazia com tolerância T. O(1)."""
        self.registro = RegistroDepositos()
        self.tolerancia = tolerancia
        self.cache_par = None

    def inserir(self, leitor):
        """
        Comando INSERIR id x y L r + r rotas. Cria o depósito, descarta as
        rotas (3*r tokens) e invalida o cache. Não imprime nada.
        Tempo O(log n): inserção no heap.
        """
        ident = leitor.inteiro()
        x = leitor.inteiro()
        y = leitor.inteiro()
        lucro = leitor.inteiro()
        r = leitor.inteiro()
        self.registro.inserir(ident, x, y, lucro)
        leitor.pular(3 * r)
        self.cache_par = None

    def lucro(self, leitor):
        """
        Comando LUCRO id L (id vivo). Substitui o lucro. Não imprime nada
        e não invalida o cache (as coordenadas não mudam).
        Tempo O(log n) (alterar_chave).
        """
        ident = leitor.inteiro()
        novo = leitor.inteiro()
        self.registro.atualizar_lucro(ident, novo)

    def remover(self):
        """
        Comando REMOVER. Fecha os depósitos com lucro < T e devolve a
        linha com a quantidade. Invalida o cache se fechou algum.
        Tempo O(k log n) para k fechados (ver remover_abaixo).
        """
        k = self.registro.remover_abaixo(self.tolerancia)
        if k > 0:
            self.cache_par = None
        return str(k)

    def par(self):
        """
        Comando PAR (pré-condição: >= 2 vivos). Devolve a linha "a b d".
        Reaproveita o cache se o conjunto de vivos não mudou: O(1);
        senão recalcula: O(n log n).
        """
        if self.cache_par is None:
            a, b, d = par_mais_proximo(self.registro.coord)
            self.cache_par = "%d %d %d" % (a, b, d)
        return self.cache_par


def executar_lote(leitor, rede, saida):
    """
    Lê e executa um lote: q e depois q comandos (cada INSERIR traz as suas
    rotas, que não contam em q). Acrescenta em `saida` uma linha por
    REMOVER/PAR. Tempo: soma dos custos dos comandos (ver Rede).
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
        elif comando == "PAR":
            saida.append(rede.par())


def main():
    """
    Ponto de ancoragem. Lê o setup (n depósitos e m rotas, estas descartadas),
    depois os P lotes, e escreve as respostas. Os lucros por período L_k não
    são necessários neste entregável.
    Tempo: n inserções O(n log n) + custo dos comandos; espaço O(n + entrada).
    """
    leitor = Leitor(sys.stdin.read().split())
    n = leitor.inteiro()
    m = leitor.inteiro()
    tolerancia = leitor.inteiro()
    rede = Rede(tolerancia)
    for _ in range(n):                    # n linhas "id x y L"
        ident = leitor.inteiro()
        x = leitor.inteiro()
        y = leitor.inteiro()
        rede.registro.inserir(ident, x, y, leitor.inteiro())
    leitor.pular(3 * m)                   # m rotas: lidas e descartadas

    saida = []
    p = leitor.inteiro()
    for _ in range(p):
        executar_lote(leitor, rede, saida)

    if saida:
        sys.stdout.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
