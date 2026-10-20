# Roteiro para a entrevista (50% da nota)

Cada pessoa deve saber explicar **o próprio entregável e apontar no código** onde está cada ideia. Sugestão de divisão: e1 = Você, e2 = Laércio, e3 = Zaque. Mas o e2 contém o e1 e o e3 contém o e2: todos devem conseguir explicar as estruturas compartilhadas (hash, heap).

Regra de ouro: não decorar a resposta, e sim saber **por que** vale. Para cada pergunta há a resposta curta, o ponto do código e a armadilha em que o professor costuma cutucar.

---

## Parte 1 — e1.py (histórico, pilha, Kadane)

**1. Por que `dict` e não um vetor indexado pelo id?**
Ids vão até 10^9, e há no máximo 5000 vivos. Um vetor de 10^9 posições é inviável em memória. O `dict` é uma tabela hash: busca, inserção e atualização em O(1) **esperado** e espaço O(n). Pior caso O(n) com muitas colisões.
*Alternativa:* árvore balanceada, O(log n) no pior caso, mas mais lenta na prática e sem necessidade, pois não precisamos de ordem. *Código:* `RegistroDepositos`.

**2. Como L_k sai sem somar todos os depósitos?**
`total` é um acumulador. No INSERIR soma-se L. No LUCRO soma-se `novo - antigo`. O período k lê `registro.total` em O(1). *Código:* `inserir`, `atualizar_lucro`, `fechar_periodo`.
*Armadilha:* o LUCRO **substitui**, não soma; por isso o antigo precisa ser subtraído.

**3. Por que a pilha é O(1) amortizado se o `while` pode desempilhar vários?**
Cada período empilha no máximo 1 elemento. Um elemento só sai se já entrou, e uma vez só. Em P períodos há no máximo P empilhamentos e, portanto, no máximo P desempilhamentos no total: custo total O(P). Método agregado. O pior período isolado é O(h), mas a média é O(1). *Código:* `PilhaProsperidade.registrar`.

**4. Como PROSPERIDADE é O(1) sem somar a pilha?**
`soma` é mantida junto: soma `lk` ao empilhar e desconta `d` ou `r` a cada abatimento. *Armadilha:* a soma precisa ser corrigida nos dois ramos do `while` (substituição e desempilhamento).

**5. Recorrência do Kadane e por que `>= 0`.**
`suf(k) = L_k + max(0, suf(k-1))`: estende o melhor intervalo que termina em k-1 ou recomeça em k. Com `suf = 0`, estender dá a mesma soma que recomeçar, mas com `i` menor, e o desempate pede o menor `i`. O melhor global só troca com soma **estritamente maior**: em empate o antigo já tem `i` menor ou igual e `j` menor. *Código:* `HistoricoMelhorIntervalo.registrar`.
*Teste feito:* a referência ingênua testa todos os intervalos e bateu em 400 casos aleatórios, com valores pequenos para forçar empates.

**6. Por que espaço O(1) e não um vetor de DP?**
O estado de k depende só do estado de k-1 e do melhor global. Guardamos 5 inteiros. MELHOR responde em O(1).

**7. Por que o intervalo nunca é vazio?**
O primeiro período é registrado direto como melhor (`vazio`), e depois o melhor só é substituído por outro intervalo não vazio. Com todos os L negativos, o resultado é o maior (menos negativo) elemento isolado.

**8. Por que MELHOR no lote k enxerga só até k-1?**
O período k ainda não foi calculado (L_k só existe ao fim do lote). Por isso `executar_lote` roda os comandos e **só depois** chama `fechar_periodo`.

**9. O que fazemos com as rotas?**
Lemos e descartamos: `pular(3*m)` no setup e `pular(3*r)` no INSERIR. Se não consumirmos esses tokens, o cursor dessincroniza e todos os testes falham.

---

## Parte 2 — e2.py (heap, REMOVER, PAR)

**1. Por que não usar `heapq`?**
O `heapq` não altera a chave de um elemento arbitrário. O LUCRO exige isso. Nosso heap tem o `dict` `pos` (id → índice) e acha o elemento em O(1) esperado, e `_subir`/`_descer` restauram em O(log n). *Código:* `FilaPrioridadeMin.alterar_chave`.

**2. Se o lucro diminui, sobe ou desce? E se aumenta?**
Diminuiu: pode violar a relação com o **pai**, então `_subir`. Aumentou: pode violar com os **filhos**, então `_descer`.

**3. Qual o invariante do heap e por que o REMOVER não varre tudo?**
`chaves[pai(i)] <= chaves[i]`, logo a raiz é o menor lucro. O REMOVER extrai a raiz **enquanto** `lucro < T`. Quando a raiz é `>= T`, todos são `>= T` e para. Custo O(k log n) para k removidos. *Código:* `remover_abaixo`.
*Armadilha:* é `<` estrito. Um depósito com lucro exatamente T **não** é removido.

**4. Por que `pos` precisa ser atualizado a cada troca?**
Senão `pos[id]` aponta para o lugar errado e a alteração de chave mexe em outro depósito. Na nossa implementação a posição é atualizada quando cada elemento é escrito (método do "buraco"). O `extrair_minimo` usa a variante "de baixo para cima": desce o buraco da raiz até uma folha (1 comparação por nível) e sobe o último elemento depois; continua O(log n). Durante um `_subir`/`_descer` o invariante fica momentaneamente incompleto e volta a valer ao fim.

**5. Divisão e conquista do PAR, passo a passo.**
Ordena por x, divide ao meio, resolve cada metade (δ_E, δ_D), δ = min. O melhor par pode ter um ponto em cada metade; então olhamos a **faixa** de largura 2δ em torno da reta divisória, ordenada por y. *Código:* `_par_recursivo`.

**6. Por que o laço interno da faixa é O(1)?**
Em cada metade os pontos distam ≥ δ entre si. Num retângulo 2δ × δ cabem no máximo 8 pontos (8 quadrados de lado δ/2, cada um com no máximo 1 ponto). Logo cada ponto vê no máximo 7 seguintes antes de `dy >= δ`. Recorrência T(n) = 2T(n/2) + O(n) = O(n log n) (Teorema Mestre).

**7. Como se calcula o teto da raiz sem ponto flutuante?**
`t = isqrt(d2)`. Se `t*t < d2`, soma 1. `isqrt` é exato em inteiros. *Código:* `teto_raiz_inteira`. Comparamos sempre distâncias **ao quadrado**.

**8. O que invalida o cache do PAR?**
INSERIR e um REMOVER que fecha pelo menos 1 depósito (o conjunto de pontos mudou). LUCRO **não** invalida, porque o PAR só depende das coordenadas. A restrição proíbe estruturas de distâncias entre pares, e o cache guarda só **uma linha de resultado**, o que o enunciado permite expressamente.

**9. Para que serve o limite superior inicial do PAR?**
Antes de dividir, tomamos o melhor par de vizinhos na ordem de x (O(n)). Como é um par real, δ já começa pequeno: as faixas centrais ficam estreitas e `_confere_pares` para logo. Sem ele o algoritmo está correto do mesmo jeito, só mais lento. *Teste feito:* `testes/teste_par.py` compara com a força bruta em 487 conjuntos (2 a 600 pontos); desligar a faixa de propósito faz o teste falhar (72 falhas).

**10. Pontos fracos para você mesmo conhecer (seja honesto na entrevista).**
- A intercalação por y usa `sorted(y_esq + y_dir)`. O Timsort detecta as duas sequências já ordenadas e faz uma só intercalação linear, mas a garantia O(n) vem dessa propriedade do Timsort, não de um `merge` escrito por nós.
- A faixa usa `isqrt(d2) + 1` em vez de δ exato. Ela fica ligeiramente mais larga, o que é inofensivo (o laço confere a distância exata) e evita ponto flutuante.
- Folhas de até 32 pontos são resolvidas direto (ordena por y e confere pares com parada antecipada): é só uma constante (O(1) por folha).
- O limite superior inicial (melhor par de vizinhos em x) é uma otimização de poda, não parte do algoritmo clássico. Saiba explicar que ele é um par **real** (então nunca dá resposta errada) e que só encolhe: por isso a análise dos 7 vizinhos continua valendo com δ = o melhor atual.

---

## Parte 3 — e3.py (grafo e Dijkstra)

**1. Por que lista de adjacência e não matriz?**
Matriz: O(n²) de espaço, 25 milhões de células com n = 5000, e O(n) para listar os vizinhos de um vértice. Lista: O(n + m), e percorre só as rotas que existem, O(grau). O grafo é esparso (m ≤ 5n no setup, r ≤ 20 por inserção).

**2. Por que guardar as rotas de entrada também?**
`saida[u]` não diz quem aponta para u. Só com ela, apagar as rotas que chegam em u exigiria varrer o grafo todo, O(n + m). Com `entrada[u]` basta visitar os vizinhos: O(grau_saída + grau_entrada). *Código:* `GrafoRotas.remover_vertice`.
*Invariante:* `v in saida[u]` ⇔ `u in entrada[v]`.

**3. O que acontece com uma rota 2-ciclo (u→w e w→u) ao remover u?**
O primeiro laço tira u de `entrada[w]`; o segundo apaga `saida[w][u]`. Ambos os lados ficam coerentes, e por isso os dois laços são necessários.

**4. Como o Dijkstra funciona e por que precisa de custos positivos?**
Relaxar (u,v,c): se `dist[u] + c < dist[v]`, atualiza `dist[v]` (decrease-key). A escolha gulosa fecha o vértice de menor distância provisória. Com c ≥ 1, qualquer caminho que passe por outro vértice aberto não pode ser mais barato. Com custo negativo isso falha: um caminho mais longo poderia "descontar" depois. *Código:* `menores_custos`.

**5. Complexidade do Dijkstra.**
Cada vértice entra e sai do heap uma vez: n · O(log n). Cada rota é relaxada uma vez, com no máximo um decrease-key: m · O(log n). Total O((n + m) log n). A ordenação dos ids na impressão soma O(n log n).

**6. Como o heap do Entregável 2 foi reaproveitado?**
É a mesma classe `FilaPrioridadeMin`: no REMOVER a chave é o lucro, e no Dijkstra, a distância provisória. A operação `alterar_chave` é o decrease-key.

**7. O que imprimir no DIST?**
Em ordem crescente de id (os ids não são contíguos, então ordenamos `sorted(grafo.saida)`), o custo mínimo de s a cada outro vivo. `-1` se inalcançável. Linha vazia se s for o único vivo.

**8. O REMOVER alcança o grafo?**
Sim: `remover_abaixo` extrai do heap e chama `grafo.remover_vertice`. Os invariantes: todas as estruturas deixam de mencionar o depósito removido.

---

## Perguntas gerais (qualquer um pode receber)

- **"Qual a diferença entre pior caso e amortizado?"** Pior caso limita uma operação isolada; amortizado limita o custo **médio** numa sequência (a pilha é O(h) no pior período, mas O(1) amortizado).
- **"O que muda se a entrada tiver o dobro de depósitos?"** Hash e heap escalam bem (O(1) e O(log n)); o PAR dobra um pouco acima de linear; o Dijkstra cresce com (n+m) log n.
- **"Como vocês testaram?"** Veja o `README.md`: referência ingênua conferida com o exemplo do PDF, 400 testes aleatórios por entregável (0 falhas) e um teste de desempenho no pior caso.
- **"O que não está coberto?"** O exemplo do PDF não foi rodado direto em cada `eN.py` (mistura operações de estágios diferentes), e o limite de tempo real da correção é desconhecido.
- **"Onde está o invariante X?"** Cada classe tem os invariantes no docstring, logo abaixo do `class`.

## Como treinar
1. Cada um explica em voz alta o próprio arquivo, na ordem: estruturas → invariantes → uma função por vez.
2. Um sorteia uma função e pergunta "o que acontece aqui se o lucro diminuir?" ou "por que isto é O(log n)?".
3. Rode `python testes/teste_aleatorio.py 50`, quebre de propósito uma linha (por exemplo troque `>=` por `>` no Kadane ou tire o `discard` do grafo) e veja qual teste falha. Isso mostra, na prática, por que cada linha existe.
