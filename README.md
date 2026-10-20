# Rede de distribuição — Algoritmos e Estruturas de Dados (BCC 2026.2)

Três entregáveis em Python, cada um num único arquivo e com `main` como ponto de ancoragem:

| Arquivo | Operações | Tópicos |
|---|---|---|
| `e1.py` | INSERIR, LUCRO, MELHOR, PROSPERIDADE | busca por chave (hash), pilha + análise amortizada, programação dinâmica (Kadane) |
| `e2.py` | REMOVER, PAR (+ INSERIR, LUCRO) | heap com alteração de chave, divisão e conquista |
| `e3.py` | DIST (+ INSERIR, REMOVER, LUCRO) | grafo esparso dinâmico, Dijkstra reaproveitando o heap |

A documentação exigida pela seção 2.6 do enunciado (cabeçalho, invariantes, pré-condições, efeitos e complexidades) está nos comentários e docstrings de cada arquivo.

Antes de entregar, preencher a linha `Autores:` do cabeçalho de cada arquivo com nomes e matrículas.

## Resumo das decisões

- **Registro por id:** `dict` (tabela hash). Ids vão até 10^9 e há no máximo 5000 vivos; um vetor indexado pelo id é inviável. O total de lucros é um acumulador atualizado por diferença (`novo - antigo`), então L_k sai em O(1).
- **Pilha de prosperidade:** lista usada como pilha, com a soma dos resíduos mantida num acumulador. Cada período empilha no máximo 1 elemento, então os desempilhamentos somam no máximo P: O(1) amortizado por período.
- **MELHOR:** Kadane online, 5 inteiros. Estende o intervalo corrente quando a soma anterior é `>= 0` (menor `i` no empate) e só troca o melhor global quando a soma é estritamente maior (menor `j` no empate).
- **Heap indexado (`FilaPrioridadeMin`):** vetor de ids, vetor de chaves e `dict` id → posição. Alterar a chave de um id qualquer é O(log n). REMOVER extrai a raiz enquanto `lucro < T`: custa O(k log n) para k removidos.
- **PAR:** divisão e conquista em O(n log n), com distâncias ao quadrado em inteiros e `math.isqrt` para o teto da raiz. Nenhuma estrutura guarda distâncias entre pares. O último resultado fica em cache e é invalidado só por INSERIR ou por um REMOVER que fecha algum depósito (LUCRO não altera coordenadas).
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

### 4. Teste de desempenho no pior caso (`testes/gerar_grande.py`)
Gera `testes/grande.txt` (não versionado, é grande) com os limites do enunciado:
- 5000 depósitos, 25000 rotas, ids até 10^9, coordenadas até 10^6;
- 100000 períodos, 1 LUCRO por período;
- 500 PAR, cada um **precedido de um INSERIR** para o cache não ajudar e o PAR ser recalculado com cerca de 5000 pontos;
- 200 DIST, com o grafo quase todo alcançável.

Tempos medidos (Python 3.11, Windows, máquina de desenvolvimento, uma execução cada):

| Programa | Tempo ||
|---|---|
| `e1.py` | ~0,4–0,7 s |
| `e2.py` | ~27 s (a única PAR sem cache custa ~31 ms; 500 PAR ≈ 16 s, o resto são os 100000 LUCRO e INSERIR) |
| `e3.py` | 9 s numa execução e 24 s em outra, sobre o mesmo arquivo (variação da máquina; 200 Dijkstra sobre 25000 rotas) |

Otimizações feitas a partir dessas medições (e retestadas com os testes 2 e 3):
- o heap passou a usar o método do "buraco" (move os pais e escreve o elemento uma vez, em vez de trocar a cada nível): `e3` caiu de ~19 s para ~9 s;
- o PAR usa folhas de até 8 pontos por força bruta e uma faixa central com limites inteiros; o PAR de 5000 pontos caiu de ~42 ms para ~31 ms.

Este é o pior caso que construí (PAR sempre recalculado, DIST sempre sobre o grafo inteiro). Num teste real o cache evita boa parte dos PAR, mas o limite de tempo da ferramenta de correção é desconhecido; se for apertado, o `e2` e o `e3` são os que merecem atenção.

## Como rodar

```
python e1.py < entrada.txt
python e2.py < entrada.txt
python e3.py < entrada.txt
python testes/teste_aleatorio.py 400     # testes 2 e 3
python testes/gerar_grande.py            # teste 4: gera testes/grande.txt
```

## Limitações dos testes (o que não foi coberto)
- O exemplo do PDF foi usado para validar a referência, mas **não** foi alimentado diretamente em cada `eN.py`, porque o enunciado só exercita um subconjunto de operações em cada estágio (o exemplo mistura todas). Cada estágio foi testado com entradas aleatórias do seu próprio subconjunto.
- Não há acesso à ferramenta de correção, então o limite de tempo real é desconhecido.
