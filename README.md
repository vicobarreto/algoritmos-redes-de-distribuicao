# Rede de distribuição — Algoritmos e Estruturas de Dados (BCC 2026.2)

Três entregáveis em Python, cada um num único arquivo e com `main` como ponto de ancoragem:

| Arquivo | Operações | Tópicos |
|---|---|---|
| `e1.py` | INSERIR, LUCRO, MELHOR, PROSPERIDADE | busca por chave (hash), pilha + análise amortizada, programação dinâmica (Kadane) |
| `e2.py` | REMOVER, PAR (+ INSERIR, LUCRO) | heap com alteração de chave, divisão e conquista |
| `e3.py` | DIST (+ INSERIR, REMOVER, LUCRO) | grafo esparso dinâmico, Dijkstra reaproveitando o heap |

A documentação exigida pela seção 2.6 do enunciado (cabeçalho, invariantes, pré-condições, efeitos e complexidades) está nos comentários e docstrings de cada arquivo.

Autores: Vinicius Lima, Laércio Neto e Zaque Mateus.

## Resumo das decisões

- **Registro por id:** `dict` (tabela hash). Ids vão até 10^9 e há no máximo 5000 vivos; um vetor indexado pelo id é inviável. O total de lucros é um acumulador atualizado por diferença (`novo - antigo`), então L_k sai em O(1).
- **Pilha de prosperidade:** lista usada como pilha, com a soma dos resíduos mantida num acumulador. Cada período empilha no máximo 1 elemento, então os desempilhamentos somam no máximo P: O(1) amortizado por período.
- **MELHOR:** Kadane online, 5 inteiros. Estende o intervalo corrente quando a soma anterior é `>= 0` (menor `i` no empate) e só troca o melhor global quando a soma é estritamente maior (menor `j` no empate).
- **Heap indexado (`FilaPrioridadeMin`):** vetor de ids, vetor de chaves e `dict` id → posição. Alterar a chave de um id qualquer é O(log n). REMOVER extrai a raiz enquanto `lucro < T`: custa O(k log n) para k removidos.
- **PAR:** divisão e conquista em O(n log n), com distâncias ao quadrado em inteiros e `math.isqrt` para o teto da raiz. Parte de um limite superior (o melhor par de vizinhos em x) para podar as faixas. Nenhuma estrutura guarda distâncias entre pares. O último resultado fica em cache e é invalidado só por INSERIR ou por um REMOVER que fecha algum depósito (LUCRO não altera coordenadas).
- **Grafo:** `saida[u] = {v: custo}` e `entrada[v] = {u}`. Remover um depósito percorre só as rotas incidentes a ele.
- **DIST:** Dijkstra com o mesmo heap (decrease-key), O((n + m) log n), e ordenação dos ids vivos na impressão.

## Testes realizados

Tudo está em `testes/` e pode ser reexecutado.

### 1. Leitura do enunciado e do exemplo da seção 1.7
O texto do PDF perdeu espaços e símbolos na extração (por exemplo, a saída aparecia como `233`). A entrada está em `testes/exemplo.txt` e a saída completa esperada, reconstruída linha a linha, está em `testes/esperado.txt`. Conferi cada linha na mão contra a explicação do próprio enunciado:
- `L1..L5 = 22, -8, 15, -29, 11`;
- evolução da pilha `[(1,22)] → [(1,14)] → [(1,14),(3,15)] → [] → [(5,11)]`;
- primeiro PAR = `2 3 3` (distância `√5 ≈ 2,24`, arredondada para 3); segundo PAR = `3 5 1`.

### 2. Solução de referência ingênua (`testes/teste_aleatorio.py`, função `ref`)
Implementa as 7 operações do jeito mais simples possível, sem se preocupar com eficiência:
- soma todos os lucros a cada período;
- refaz a pilha de prosperidade do zero a cada consulta;
- testa todos os intervalos no MELHOR;
- testa todos os pares no PAR;
- usa Dijkstra varrendo a lista de rotas no DIST.

**Teste:** a referência rodada sobre `exemplo.txt` produz exatamente `esperado.txt`. Resultado: passou. Isso valida a própria referência antes de usá-la como juiz.

### 3. Teste diferencial aleatório, por estágio
Para cada entregável, o gerador cria entradas aleatórias válidas (seguindo as garantias da seção 1.5):
- ids únicos e nunca reutilizados, inclusive ids grandes (até 10^9);
- coordenadas distintas entre os vivos;
- lucro de setup e de INSERIR `>= T`;
- rotas só entre depósitos vivos, sem laços e sem duplicatas;
- PAR só quando há pelo menos 2 vivos **e** o par mais próximo é único.

Cada estágio usa só as operações que ele exercita:
- `e1`: INSERIR, LUCRO, MELHOR, PROSPERIDADE;
- `e2`: INSERIR, LUCRO, REMOVER, PAR;
- `e3`: INSERIR, LUCRO, REMOVER, DIST.

O programa e a referência rodam sobre a mesma entrada e as saídas precisam ser idênticas. Os valores são pequenos de propósito (lucros em torno de `T`, custos de 1 a 9, coordenadas em `[-8, 8]`) para forçar casos de borda: empates no MELHOR, soma zero no Kadane, prejuízo que consome a pilha exatamente, depósito que cai abaixo de `T` e continua vivo até o REMOVER, vértices inalcançáveis no DIST, e depósito removido que tinha rotas de entrada e de saída.

`python testes/teste_aleatorio.py 400` roda 400 sementes por estágio. **Resultado: 0 falhas em 400 para e1, e2 e e3** (1200 execuções).

### 4. Teste específico do PAR (`testes/teste_par.py`)
Os testes aleatórios do item 3 usam no máximo 40 depósitos vivos, então quase não entram na recursão do PAR (que só divide acima de `FOLHA = 32` pontos). Este teste compara `par_mais_proximo` com a força bruta em conjuntos de 2 a 600 pontos, com quatro distribuições (uniforme, aglomerado, colunas estreitas e grade esparsa) e tamanhos nas fronteiras (31, 32, 33, 34, 64, 65…). Conjuntos com empate no par mais próximo são descartados (o enunciado garante unicidade).

`python testes/teste_par.py 600`: **487 casos válidos, 113 descartados por empate, 0 falhas.**

**Sabotagem para provar que o teste pode falhar:** com a faixa central desligada (`_confere_pares(faixa, melhor)` trocado por `pass`) o teste passa a dar 72 falhas; com a faixa estreitada (`delta // 4`), 9 falhas. Código restaurado depois, 0 falhas.

### 5. Teste de desempenho (`testes/gerar_grande.py`)
Gera uma entrada **válida para cada estágio** (só com as operações dele) perto dos limites do enunciado:
- 4000 depósitos no setup e 20000 rotas, ids até 10^9, coordenadas até 10^6, 100000 períodos, 1 LUCRO por período, INSERIR e REMOVER de vez em quando;
- `e1`: MELHOR e PROSPERIDADE a cada 50 períodos;
- `e2`: 500 PAR, cada um logo **após um INSERIR**, para o cache não ajudar e o PAR ser recalculado com ~4000 pontos;
- `e3`: 200 DIST, com o grafo quase todo alcançável.

`python testes/gerar_grande.py` escreve `testes/grande_e1.txt`, `grande_e2.txt` e `grande_e3.txt` (ignorados pelo git).

> **Correção de uma medição anterior.** Uma versão inicial deste teste usava um único arquivo com DIST e PAR misturados para os três programas. O `e1` e o `e2` não conhecem DIST e perdiam o sincronismo da leitura, então os tempos que anotei para eles não valiam. Os números abaixo vêm das entradas separadas por estágio, e a saída de cada versão foi comparada com a da versão anterior (idêntica).

Tempo de CPU em Python 3.11, Windows, máquina de desenvolvimento (a máquina tem ruído; melhor de 3 execuções):

| Programa | Antes das otimizações | Depois |
|---|---|---|
| `e1.py` | ~0,9 s | ~0,9 s (já era O(1) por comando) |
| `e2.py` | 12,4 s | **7,4 s** |
| `e3.py` | 7,0 s | **5,8 s** |

O que foi feito (com os testes 3 e 4 verdes depois de cada mudança):
- **PAR, limite superior inicial:** antes da recursão, o melhor par de vizinhos na ordem de x (O(n)) vira o par inicial. Ele é real, então vale como resposta se nada for melhor, e permite podar: faixas centrais ficam bem mais estreitas e as folhas param de comparar assim que `dy² >= d²`. A complexidade continua O(n log n).
- **PAR, folhas de 32 pontos** em vez de 8 (menos níveis de recursão, menos intercalações), e conferência de pares extraída para `_confere_pares`.
- **Heap, `extrair_minimo` "de baixo para cima":** desce o buraco da raiz até uma folha com uma comparação por nível e depois sobe o último elemento (menos comparações por extração).
- **Heap, `inserir`** só chama `_subir` quando a chave é menor que a do pai.
- **Dijkstra:** uma única consulta ao dicionário por rota relaxada.

O que **não** foi feito, de propósito: trocar o heap por `heapq` com "remoção preguiçosa" seria ~2x mais rápido no `e3`, mas o enunciado pede a fila com alteração de chave (decrease-key) reaproveitada, e é o que a disciplina cobra. O limite de tempo da ferramenta de correção continua desconhecido.

## Como rodar

```
python e1.py < entrada.txt
python e2.py < entrada.txt
python e3.py < entrada.txt
python testes/teste_aleatorio.py 400     # testes 2 e 3
python testes/teste_par.py 600           # teste 4 (PAR com muitos pontos)
python testes/gerar_grande.py            # teste 5: gera testes/grande_e1|e2|e3.txt
```

## Limitações dos testes (o que não foi coberto)
- O exemplo do PDF foi usado para validar a referência, mas **não** foi alimentado diretamente em cada `eN.py`, porque o enunciado só exercita um subconjunto de operações em cada estágio (o exemplo mistura todas). Cada estágio foi testado com entradas aleatórias do seu próprio subconjunto.
- Não há acesso à ferramenta de correção, então o limite de tempo real é desconhecido.

## Apresentação (PDF)

`apresentacao/rede-distribuicao-aed.pdf`: 17 slides com o passo a passo geral dos algoritmos, as complexidades e como as peças se juntam para produzir a saída de cada entregável.

Como foi gerado (reproduzível):
1. `python apresentacao/gerar_trechos.py` extrai do código real (`e1.py`, `e2.py`, `e3.py`, sem docstrings) 11 trechos e os destaca com pygments em `trecho_*.html`.
2. O Playwright abre cada `trecho_*.html` e tira o print em `apresentacao/prints/*.png` (zoom 2x).
3. `python apresentacao/gerar_slides.py` monta `slides.html` (1280x720 por slide) com os prints.
4. O Playwright abre `slides.html` e imprime o PDF (`page.pdf`, fundo ligado, tamanho 1280x720).

Se o código mudar, rodar os passos 1 a 4 de novo para atualizar os prints.
