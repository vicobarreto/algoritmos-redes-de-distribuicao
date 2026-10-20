"""Monta slides.html (1280x720 por slide) a partir do conteúdo abaixo.
O PDF sai da impressão desse HTML pelo Playwright (ver README)."""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
COR = {"e1": "#38bdf8", "e2": "#fbbf24", "e3": "#34d399", "geral": "#a78bfa"}

CSS = """
@page{size:1280px 720px;margin:0}
*{box-sizing:border-box}
html,body{margin:0;background:#020617}
body{font-family:'Segoe UI',system-ui,sans-serif;color:#e2e8f0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.slide{width:1280px;height:720px;position:relative;overflow:hidden;page-break-after:always;break-after:page;
  background:radial-gradient(1100px 600px at 90% -10%,#1e293b,#0b1224 60%);padding:46px 58px 40px}
.slide:last-child{page-break-after:auto;break-after:auto}
.tag{display:inline-block;font-size:15px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  padding:5px 14px;border-radius:999px;color:#0b1224;background:var(--c)}
h1{font-size:44px;line-height:1.1;margin:18px 0 0;font-weight:800}
h2{font-size:36px;line-height:1.15;margin:14px 0 0;font-weight:800}
.sub{color:#94a3b8;font-size:21px;margin-top:8px}
.corpo{display:flex;gap:34px;margin-top:22px;height:520px}
.esq{flex:0 0 480px;display:flex;flex-direction:column;gap:12px}
.dir{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;min-width:0}
.dir img{max-width:100%;max-height:100%;border-radius:12px;box-shadow:0 12px 40px #0008}
ol,ul{margin:0;padding:0;list-style:none}
li{font-size:20.5px;line-height:1.38;margin:0 0 9px;padding-left:34px;position:relative}
ol{counter-reset:n}
ol li{counter-increment:n}
ol li::before{content:counter(n);position:absolute;left:0;top:2px;width:25px;height:25px;border-radius:50%;
  background:var(--c);color:#0b1224;font-weight:800;font-size:15px;display:flex;align-items:center;justify-content:center}
ul li::before{content:"";position:absolute;left:7px;top:11px;width:9px;height:9px;border-radius:2px;background:var(--c)}
code{font-family:Consolas,monospace;background:#1e293b;border-radius:5px;padding:1px 6px;font-size:.92em;color:#f1f5f9}
.caixa{border:1px solid #334155;background:#0f172a99;border-radius:14px;padding:14px 18px}
.caixa b.c{color:var(--c)}
.caixa p{margin:0;font-size:19px;line-height:1.4}
.fluxo{display:flex;align-items:center;gap:10px;margin:8px 0 0;flex-wrap:nowrap}
.fluxo div{flex:1;border:1px solid var(--c);border-radius:12px;padding:12px 10px;text-align:center;font-size:17.5px;line-height:1.3;background:#0f172a}
.fluxo span{color:var(--c);font-size:26px}
table{border-collapse:collapse;width:100%;font-size:19px}
th{background:var(--c);color:#0b1224;text-align:left;padding:9px 14px}
td{padding:9px 14px;border-bottom:1px solid #334155}
td:first-child{font-weight:700}
.rodape{position:absolute;left:58px;right:58px;bottom:18px;display:flex;justify-content:space-between;color:#64748b;font-size:14px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:30px}
.card{border-radius:16px;padding:22px 24px;border:1px solid #334155;background:#0f172ab0;border-top:5px solid var(--c)}
.card h3{margin:0 0 8px;font-size:26px;color:var(--c)}
.card p{margin:0 0 6px;font-size:19.5px;line-height:1.4}
"""

slides = []
RODAPE = '<div class="rodape"><span>Rede de distribuição · AED BCC 2026.2</span><span>%d</span></div>'


def pagina(chave, tag, titulo, miolo):
    n = len(slides) + 1
    slides.append(
        f'<section class="slide" style="--c:{COR[chave]}"><span class="tag">{tag}</span>'
        f'<h2>{titulo}</h2>{miolo}{RODAPE % n}</section>')


def img(nome):
    return f'<img src="prints/{nome}.png">'


def lista(tipo, itens):
    return f"<{tipo}>" + "".join(f"<li>{i}</li>" for i in itens) + f"</{tipo}>"


def corpo(esq, dir_):
    return f'<div class="corpo"><div class="esq">{esq}</div><div class="dir">{dir_}</div></div>'


def caixa(txt):
    return f'<div class="caixa"><p>{txt}</p></div>'


def tabela(cabecalho, linhas):
    t = "<table><tr>" + "".join(f"<th>{c}</th>" for c in cabecalho) + "</tr>"
    for l in linhas:
        t += "<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>"
    return t + "</table>"


# 1 capa -------------------------------------------------------------
slides.append(f'''<section class="slide" style="--c:{COR["geral"]};display:flex;flex-direction:column;justify-content:center">
<span class="tag" style="align-self:flex-start">Algoritmos e Estruturas de Dados · BCC 2026.2</span>
<h1 style="font-size:70px;margin-top:26px">Rede de distribuição</h1>
<div class="sub" style="font-size:28px;margin-top:14px">Como o algoritmo funciona, quanto custa e como as peças se juntam na saída</div>
<div style="margin-top:46px;font-size:21px;color:#cbd5e1;line-height:1.7">Entregável 1 · histórico de períodos<br>Entregável 2 · fechamento e proximidade<br>Entregável 3 · rede de rotas</div>
<div style="margin-top:44px;font-size:20px;color:#94a3b8">Autores: Vinicius Lima, Laércio Neto e Zaque Mateus</div></section>''')

# 2 visão geral ------------------------------------------------------
slides.append(f'''<section class="slide" style="--c:{COR["geral"]}"><span class="tag">Visão geral</span>
<h2>O problema, em uma frase</h2>
<div class="sub" style="max-width:1100px">Uma rede de depósitos evolui por períodos: a cada lote de operações, depósitos entram, saem ou mudam de lucro, e precisamos responder consultas com eficiência (até 5000 depósitos vivos e 3·10<sup>5</sup> operações).</div>
<div class="cards">
<div class="card" style="--c:{COR["e1"]}"><h3>Entregável 1</h3><p><b>Histórico</b></p><p>Lucro de cada período, melhor intervalo (MELHOR) e pilha de prosperidade (PROSPERIDADE).</p><p style="color:#94a3b8;font-size:17px">Hash · pilha amortizada · programação dinâmica</p></div>
<div class="card" style="--c:{COR["e2"]}"><h3>Entregável 2</h3><p><b>Fechamento e proximidade</b></p><p>Fechar depósitos abaixo da tolerância (REMOVER) e achar o par mais próximo (PAR).</p><p style="color:#94a3b8;font-size:17px">Heap com alteração de chave · divisão e conquista</p></div>
<div class="card" style="--c:{COR["e3"]}"><h3>Entregável 3</h3><p><b>Rede de rotas</b></p><p>Menor custo de um depósito aos demais (DIST) num grafo que cresce e encolhe.</p><p style="color:#94a3b8;font-size:17px">Grafo esparso · Dijkstra com o mesmo heap</p></div>
</div>{RODAPE % 2}</section>''')

# 3 fluxo geral ------------------------------------------------------
slides.append(f'''<section class="slide" style="--c:{COR["geral"]}"><span class="tag">Como tudo se junta</span>
<h2>O programa, de ponta a ponta</h2>
<div class="sub">Os três arquivos seguem o mesmo esqueleto; cada entregável acrescenta uma peça.</div>
<div class="fluxo" style="margin-top:22px"><div>Lê todos os tokens<br>de uma vez</div><span>→</span><div>Setup: n depósitos<br>e m rotas</div><span>→</span><div>Período 1:<br>calcula L₁</div><span>→</span><div>P lotes:<br>q comandos cada</div><span>→</span><div>Fecha o período k<br>(L<sub>k</sub>)</div><span>→</span><div>Imprime só o que<br>os comandos pedem</div></div>
<div class="corpo" style="margin-top:20px;height:420px"><div class="esq" style="flex-basis:500px">
{lista("ul", ["<code>main</code> consome a entrada e chama <code>executar_lote</code> uma vez por período.", "Cada comando (INSERIR, LUCRO, REMOVER, MELHOR…) é um método pequeno que mexe nas estruturas e, se for consulta, devolve <b>uma linha</b>.", "As linhas vão para uma lista e saem juntas no fim, na ordem em que foram executadas.", "Consultas veem o estado do ponto do lote em que estão; L<sub>k</sub> só é fixado <b>depois</b> do lote."])}
</div><div class="dir">{img("e1_lote")}</div></div>{RODAPE % 3}</section>''')

# Entregável 1 -------------------------------------------------------
pagina("e1", "Entregável 1", "Registro por id e lucro do período", corpo(
    lista("ol", ["Ids chegam a 10<sup>9</sup> e há até 5000 vivos: vetor por id é inviável. Usamos um <code>dict</code> (tabela hash).",
                 "Guardamos também <code>total</code>, a soma de todos os lucros.",
                 "INSERIR soma o lucro; LUCRO soma só a <b>diferença</b> (<code>novo − antigo</code>).",
                 "Fim do lote: <code>L<sub>k</sub> = total</code>, sem percorrer depósitos."])
    + caixa("<b class='c'>Complexidade:</b> INSERIR e LUCRO em <b>O(1) esperado</b>; obter L<sub>k</sub> em <b>O(1)</b>. Espaço O(n)."),
    img("e1_registro")))

pagina("e1", "Entregável 1", "Pilha de prosperidade", corpo(
    lista("ol", ["L<sub>k</sub> &gt; 0: empilha <code>(k, L<sub>k</sub>)</code>.",
                 "L<sub>k</sub> = 0: nada muda.",
                 "L<sub>k</sub> &lt; 0: o prejuízo consome o topo; se sobra, desempilha e continua no próximo.",
                 "A soma dos resíduos fica num acumulador, então PROSPERIDADE só lê base, topo e soma."])
    + caixa("<b class='c'>Amortizado O(1):</b> cada período empilha no máximo 1 elemento, e cada elemento sai uma única vez. Em P períodos são ≤ P desempilhamentos no total (pior período isolado: O(h))."),
    img("e1_pilha")))

pagina("e1", "Entregável 1", "MELHOR: Kadane online", corpo(
    lista("ol", ["Recorrência: <code>suf(k) = L<sub>k</sub> + max(0, suf(k−1))</code>: estende o intervalo corrente ou recomeça em k.",
                 "Estende com soma anterior <code>≥ 0</code>: no empate fica o menor <code>i</code>.",
                 "O melhor global só troca com soma <b>estritamente maior</b>: no empate fica o menor <code>j</code>.",
                 "O intervalo nunca é vazio, mesmo com todos os L negativos."])
    + caixa("<b class='c'>Complexidade:</b> registrar um período e responder MELHOR em <b>O(1)</b>, com <b>5 inteiros</b> de estado (espaço O(1)); não guardamos o histórico."),
    img("e1_kadane")))

pagina("e1", "Entregável 1", "Como o Entregável 1 gera a saída",
       '<div style="margin-top:22px">' + tabela(["Comando", "O que faz", "Custo"], [
           ["INSERIR", "cria no <code>dict</code>, soma ao total, descarta as rotas", "O(1) esperado"],
           ["LUCRO", "atualiza o total pela diferença", "O(1) esperado"],
           ["MELHOR", "imprime <code>i j S</code> do estado de Kadane", "O(1)"],
           ["PROSPERIDADE", "imprime <code>h b s i r</code> (ou 0)", "O(1)"],
           ["Fechar período", "L<sub>k</sub> = total → pilha e Kadane", "O(1) amortizado"]]) + '</div>'
       + '<div class="caixa" style="margin-top:22px"><p><b class="c">Juntando tudo:</b> cada período fecha com L<sub>k</sub> = <code>total</code>, que alimenta <b>duas</b> estruturas independentes: a pilha (PROSPERIDADE) e o Kadane (MELHOR). O programa inteiro roda em tempo <b>linear no número de comandos</b> (O(1) por comando); as rotas são só puladas na entrada.</p></div>')

# Entregável 2 -------------------------------------------------------
pagina("e2", "Entregável 2", "Heap indexado: alterar o lucro", corpo(
    lista("ol", ["Heap de mínimo ordenado pelo lucro: o menor lucro fica sempre na raiz.",
                 "Um <code>dict</code> <code>pos</code> (id → posição) acha qualquer depósito sem varrer o heap.",
                 "LUCRO troca a chave: se <b>diminuiu</b>, sobe (<code>_subir</code>); se <b>aumentou</b>, desce.",
                 "Cada elemento movido tem sua posição atualizada em <code>pos</code>."])
    + caixa("<b class='c'>Complexidade:</b> achar o id <b>O(1) esperado</b> + reposicionar <b>O(log n)</b>. Por isso não usamos <code>heapq</code>, que não altera a chave de um elemento qualquer."),
    img("e2_heap")))

pagina("e2", "Entregável 2", "REMOVER sem varrer todos", corpo(
    lista("ol", ["A raiz do heap é o menor lucro.",
                 "Enquanto <code>lucro &lt; T</code> (estrito), extrai a raiz, apaga o depósito e conta.",
                 "Quando a raiz é <code>≥ T</code>, ninguém mais está abaixo: para na hora.",
                 "Imprime a quantidade removida."])
    + caixa("<b class='c'>Complexidade:</b> <b>O(k log n)</b> para k removidos: só toca em quem será fechado, nunca nos n depósitos todos. Depósito abaixo de T <i>continua vivo</i> até o REMOVER."),
    img("e2_remover")))

pagina("e2", "Entregável 2", "PAR: ponto de partida (1/3)", corpo(
    lista("ol", ["Ordena os pontos por x uma vez.",
                 "Compara só os pontos <b>vizinhos</b> nessa ordem (n−1 pares): o melhor deles é um par <b>real</b>, o limite superior inicial.",
                 "Se nada melhor existir, esse par já é a resposta; se existir, a recursão o substitui.",
                 "Chama a divisão e conquista partindo desse limite."])
    + caixa("<b class='c'>Complexidade:</b> ordenar O(n log n) + varrer vizinhos O(n). O limite não muda o pior caso, mas poda as faixas e as comparações da recursão."),
    img("e2_par_ini")))

pagina("e2", "Entregável 2", "PAR: divisão e conquista (2/3)", corpo(
    lista("ol", ["Divide ao meio pela ordem em x.",
                 "Resolve cada metade recursivamente; o par melhor fica numa lista compartilhada (<code>melhor</code>).",
                 "Devolve os pontos ordenados por y (como um merge sort) para o nível de cima.",
                 "Tudo em <b>inteiros</b>: comparamos distâncias <b>ao quadrado</b>. Folhas de até 32 pontos são resolvidas direto."])
    + caixa("<b class='c'>Por quê?</b> Comparar todos os pares é O(n²). Dividindo, o trabalho de cada nível é linear e há log n níveis."),
    img("e2_par_a")))

pagina("e2", "Entregável 2", "PAR: a faixa central (3/3)", corpo(
    lista("ol", ["Um par melhor que δ pode ter um ponto em cada metade; ambos estão a menos de δ da reta divisória: a <b>faixa</b>.",
                 "<code>_confere_pares</code> percorre a faixa ordenada por y e <b>para</b> quando <code>dy² ≥ d²</code>.",
                 "Cada ponto vê no máximo <b>7</b> vizinhos (casa dos pombos num retângulo 2δ×δ).",
                 "Distância final = teto da raiz: <code>isqrt(d²)</code> (+1 se não for exata)."])
    + caixa("<b class='c'>Complexidade:</b> T(n) = 2T(n/2) + O(n) = <b>O(n log n)</b> por consulta. Sem matriz nem heap de distâncias; guardamos só o <b>último resultado</b> (cache)."),
    img("e2_par_b")))

pagina("e2", "Entregável 2", "Como o Entregável 2 gera a saída",
       '<div style="margin-top:22px">' + tabela(["Comando", "O que faz", "Custo"], [
           ["INSERIR", "entra no heap e nas coordenadas; invalida o cache", "O(log n)"],
           ["LUCRO", "reposiciona no heap (não invalida o cache)", "O(log n)"],
           ["REMOVER", "extrai da raiz enquanto lucro &lt; T; imprime a quantidade", "O(k log n)"],
           ["PAR", "divisão e conquista; imprime <code>a b d</code>", "O(n log n) · cache O(1)"]]) + '</div>'
       + '<div class="caixa" style="margin-top:22px"><p><b class="c">Juntando tudo:</b> o heap serve de registro de depósitos <i>e</i> de índice de lucros; o PAR só depende das coordenadas dos vivos. O cache é descartado só quando o conjunto de vivos muda (INSERIR ou REMOVER que fecha ≥ 1), então LUCRO não força recalcular.</p></div>')

# Entregável 3 -------------------------------------------------------
pagina("e3", "Entregável 3", "Grafo com listas de entrada e de saída", corpo(
    lista("ol", ["<code>saida[u]</code> = {v: custo}: rotas que saem de u.",
                 "<code>entrada[v]</code> = {u}: quem tem rota para v.",
                 "INSERIR adiciona a rota nas duas listas.",
                 "Remover u: percorre <code>saida[u]</code> e <code>entrada[u]</code>, apagando u dos vizinhos, e depois apaga u."])
    + caixa("<b class='c'>Por que duas listas?</b> Só com a de saída, achar quem chega em u custaria O(n + m). Com as duas, remover custa <b>O(grau de u)</b>. Matriz de adjacência gastaria O(n²) de espaço; a lista usa <b>O(n + m)</b>."),
    img("e3_grafo")))

pagina("e3", "Entregável 3", "DIST: Dijkstra com o heap do Entregável 2", corpo(
    lista("ol", ["Começa com <code>dist[s] = 0</code> e s no heap.",
                 "Extrai o vértice de menor distância provisória: ela vira definitiva.",
                 "<b>Relaxa</b> suas rotas: se <code>dist[u] + c &lt; dist[v]</code>, atualiza v (decrease-key; insere se for novo).",
                 "Repete até o heap esvaziar; quem não foi alcançado vale −1."])
    + caixa("<b class='c'>Por que funciona:</b> com custos ≥ 1, nenhum caminho por vértice ainda aberto pode ser mais barato que o menor provisório.<br><b class='c'>Complexidade:</b> n extrações + até m decrease-keys, cada um O(log n): <b>O((n + m) log n)</b>."),
    img("e3_dijkstra")))

pagina("e3", "Entregável 3", "Como o Entregável 3 gera a saída", corpo(
    lista("ol", ["O Dijkstra devolve a distância dos alcançáveis.",
                 "Os ids vivos são ordenados (não são contíguos, vão até 10<sup>9</sup>).",
                 "Para cada id ≠ s imprime a distância ou <code>-1</code>.",
                 "Se s é o único vivo, a linha sai vazia."])
    + caixa("<b class='c'>Juntando tudo:</b> REMOVER usa o heap de lucros (E2) <b>e</b> apaga o depósito do grafo; DIST usa outra instância da <b>mesma</b> classe de heap. INSERIR: O(log n + r); REMOVER: O(k log n + graus); DIST: O((n+m) log n + n log n)."),
    img("e3_dist")))

# Fechamento ---------------------------------------------------------
pagina("geral", "Resumo", "Complexidades de tudo",
       '<div style="margin-top:18px">' + tabela(["Operação", "Estrutura / algoritmo", "Custo"], [
           ["Registro por id", "tabela hash (<code>dict</code>)", "O(1) esperado"],
           ["L<sub>k</sub>, PROSPERIDADE, MELHOR", "acumulador, pilha, Kadane", "O(1) (pilha: amortizado)"],
           ["LUCRO / INSERIR", "heap indexado", "O(log n)"],
           ["REMOVER", "heap: extrai enquanto lucro &lt; T", "O(k log n + graus)"],
           ["PAR", "divisão e conquista + cache", "O(n log n)"],
           ["DIST", "Dijkstra com o mesmo heap", "O((n + m) log n)"]]) + '</div>'
       + '<div class="caixa" style="margin-top:18px"><p><b class="c">n</b> = depósitos vivos · <b class="c">m</b> = rotas vivas · <b class="c">P</b> = períodos · <b class="c">h</b> = altura da pilha · <b class="c">k</b> = removidos. Nenhuma operação varre todos os depósitos sem necessidade.</p></div>')

pagina("geral", "Verificação", "Como testamos", corpo(
    lista("ul", ["Referência <b>ingênua</b> (força bruta) das 7 operações, conferida com o exemplo do enunciado.",
                 "<b>400 entradas aleatórias</b> por entregável, comparando saída linha a linha: <b>0 falhas em 1200 execuções</b>.",
                 "Valores pequenos de propósito, para forçar empates, prejuízo que zera a pilha, inalcançáveis e remoção com rotas.",
                 "Pior caso (4000 depósitos, 100 mil períodos, 500 PAR, 200 DIST): e1 ≈ 0,9 s; e2 ≈ 7 s; e3 ≈ 6 s (CPU, Python 3.11)."]),
    caixa("<b class='c'>Limite honesto:</b> o limite de tempo da correção é desconhecido; e2 e e3 são os mais pesados; otimizamos o PAR e o heap, mas manter a fila com decrease-key (pedida no enunciado) custa um pouco de velocidade.")))

open(os.path.join(AQUI, "slides.html"), "w", encoding="utf-8").write(
    '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Rede de distribuição - AED</title>'
    f'<style>{CSS}</style><body>' + "".join(slides) + "</body></html>")
print(len(slides), "slides")
