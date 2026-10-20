"""Gera uma página HTML por trecho de código (destacado com pygments).
Os prints PNG são tirados dessas páginas com o Playwright (ver README)."""
import ast, os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))

# nome do trecho -> (arquivo, [alvos "Funcao" ou "Classe.metodo"], titulo no print)
TRECHOS = {
    "e1_lote":     ("e1.py", ["executar_lote", "fechar_periodo"], "e1.py"),
    "e1_registro": ("e1.py", ["RegistroDepositos.inserir", "RegistroDepositos.atualizar_lucro"], "e1.py"),
    "e1_pilha":    ("e1.py", ["PilhaProsperidade.registrar"], "e1.py"),
    "e1_kadane":   ("e1.py", ["HistoricoMelhorIntervalo.registrar"], "e1.py"),
    "e2_heap":     ("e2.py", ["FilaPrioridadeMin._subir", "FilaPrioridadeMin.alterar_chave"], "e2.py"),
    "e2_remover":  ("e2.py", ["RegistroDepositos.remover_abaixo"], "e2.py"),
    "e2_par_a":    ("e2.py", [("_par_recursivo", "meio = (lo + hi) // 2", "por_y = sorted(y_esq + y_dir")], "e2.py  (_par_recursivo, divisão)"),
    "e2_par_b":    ("e2.py", [("_par_recursivo", "d2_min = melhor[0]", "return melhor, por_y")], "e2.py  (_par_recursivo, faixa central)"),
    "e3_grafo":    ("e3.py", ["GrafoRotas.adicionar_rota", "GrafoRotas.remover_vertice"], "e3.py"),
    "e3_dijkstra": ("e3.py", ["GrafoRotas.menores_custos"], "e3.py"),
    "e3_dist":     ("e3.py", ["Rede.dist"], "e3.py"),
}

def achar(arvore, alvo):
    partes = alvo.split(".")
    corpo = arvore.body
    no = None
    for p in partes:
        no = next(n for n in corpo if getattr(n, "name", None) == p)
        corpo = getattr(no, "body", [])
    return no

def recorte(texto, ini, fim):
    linhas = texto.split(chr(10))
    a = next(i for i, l in enumerate(linhas) if ini in l)
    b = next(i for i, l in enumerate(linhas) if fim in l and i >= a)
    return chr(10).join(linhas[a:b + 1])

def trecho(fonte, no):
    linhas = fonte.split("\n")
    ini, fim = no.lineno - 1, no.end_lineno
    doc = no.body[0]
    tira = set()
    if isinstance(doc, ast.Expr) and isinstance(getattr(doc, "value", None), ast.Constant) and isinstance(doc.value.value, str):
        tira = set(range(doc.lineno - 1, doc.end_lineno))
    sel = [l for i, l in enumerate(linhas[ini:fim], ini) if i not in tira]
    # tira a indentação comum (métodos viram "def" na margem)
    recuo = min(len(l) - len(l.lstrip()) for l in sel if l.strip())
    return "\n".join(l[recuo:] for l in sel)

CSS = """
body{margin:0;background:#0f172a;font-family:Consolas,'Cascadia Mono',monospace}
#code{display:inline-block;background:#0f172a;border:1px solid #334155;border-radius:14px;padding:22px 28px 24px;min-width:760px}
.barra{color:#94a3b8;font-size:15px;margin:0 0 14px;display:flex;gap:8px;align-items:center}
.barra i{width:12px;height:12px;border-radius:50%;display:inline-block}
pre{margin:0;font-size:19px;line-height:1.5;color:#e2e8f0}
""" + HtmlFormatter(style="monokai").get_style_defs(".hl")

for nome, (arq, alvos, titulo) in TRECHOS.items():
    fonte = open(os.path.join(RAIZ, arq), encoding="utf-8").read()
    arv = ast.parse(fonte)
    partes = []
    for a in alvos:
        if isinstance(a, tuple):     # (alvo, trecho inicial, trecho final)
            partes.append(recorte(trecho(fonte, achar(arv, a[0])), a[1], a[2]))
        else:
            partes.append(trecho(fonte, achar(arv, a)))
    codigo = "\n\n".join(partes)
    corpo = highlight(codigo, PythonLexer(), HtmlFormatter(nowrap=True, classprefix=""))
    html = f"""<!doctype html><meta charset="utf-8"><style>{CSS}
.hl .k,.hl .kn{{}}</style><body><div id="code"><div class="barra"><i style="background:#ef4444"></i><i style="background:#eab308"></i><i style="background:#22c55e"></i>&nbsp;{titulo}</div><div class="hl"><pre>{corpo}</pre></div></div>"""
    open(os.path.join(AQUI, f"trecho_{nome}.html"), "w", encoding="utf-8").write(html)
    print(nome, len(codigo.split("\n")), "linhas")
