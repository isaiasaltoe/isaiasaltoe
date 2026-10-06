# Gera fastfetch.svg — edite as configs abaixo e rode: python3 gerar.py
# Idade, repos e linhas de código são calculados sozinhos (o GitHub Actions roda isso todo dia).
import json, os, re, subprocess, tempfile, urllib.request
from datetime import date
from html import escape

GITHUB_USER = "isaiasaltoe"
BIRTHDAY = date(2004, 2, 6)  # <- coloque sua data de nascimento (ano, mês, dia)

USER = "isaias@altoe"

# ---------- dados automáticos ----------
def idade():
    hoje = date.today()
    anos = hoje.year - BIRTHDAY.year
    meses = hoje.month - BIRTHDAY.month
    dias = hoje.day - BIRTHDAY.day
    if dias < 0:
        meses -= 1
        mes_ant = (hoje.month - 2) % 12 + 1
        ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
        dias += (date(ano_ant + (mes_ant == 12), mes_ant % 12 + 1, 1) - date(ano_ant, mes_ant, 1)).days
    if meses < 0:
        anos -= 1
        meses += 12
    p = lambda n, w: f"{n} {w}" + ("s" if n != 1 else "")
    return f"{p(anos, 'year')}, {p(meses, 'month')}, {p(dias, 'day')}"

# Com FASTFETCH_TOKEN (token pessoal) entram também os repos privados.
TOKEN = os.environ.get("FASTFETCH_TOKEN") or os.environ.get("GH_TOKEN")
PRIVADO = bool(os.environ.get("FASTFETCH_TOKEN"))

def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def repos():
    base = "/user/repos?affiliation=owner&visibility=all" if PRIVADO else f"/users/{GITHUB_USER}/repos?type=owner"
    todos, page = [], 1
    while True:
        lote = api(f"{base}&per_page=100&page={page}")
        if not lote:
            return todos
        todos += lote
        page += 1

def url_clone(r):
    if PRIVADO:
        return r["clone_url"].replace("https://", f"https://x-access-token:{TOKEN}@")
    return r["clone_url"]

IGNORAR = ("package-lock.json", "yarn.lock", "Gemfile.lock", "pnpm-lock.yaml", ".min.js", ".svg", ".map")

def linhas_de_codigo(lista):
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for r in lista:
            if r["fork"] or r["size"] == 0:
                continue
            dest = os.path.join(tmp, r["name"])
            if subprocess.run(["git", "clone", "-q", "--depth", "1", url_clone(r), dest], stderr=subprocess.DEVNULL).returncode:
                continue
            arquivos = subprocess.run(["git", "-C", dest, "ls-files"], capture_output=True, text=True).stdout.split("\n")
            for f in filter(None, arquivos):
                if f.endswith(IGNORAR) or "/vendor/" in f or f.startswith("vendor/"):
                    continue
                try:
                    dados = open(os.path.join(dest, f), "rb").read()
                except OSError:
                    continue
                if b"\0" not in dados[:8000]:  # pula binários (imagens, etc)
                    total += dados.count(b"\n")
    return total

lista = repos()
proprios = [r for r in lista if not r["fork"]]
estrelas = sum(r["stargazers_count"] for r in proprios)
privados = sum(r["private"] for r in proprios)

INFO = [
    ("OS", "MacOS, Linux"),
    ("Age", idade()),
    ("Current role", "Software Developer at V360"),
    ("College", "Universidade Federal do Espírito Santo (UFES)"),
    ("Degree", "Computer Science ({green:85%})"),
    ("Technologies", "Ruby, Ruby on Rails, SQL, React, Bootstrap, Figma"),
    ("Infrastructure", "PostgreSQL, Docker, Sidekiq, Redis"),
    ("Repos", f"{len(proprios)}" + (f" ({privados} private)" if privados else "") + f" | Stars: {estrelas}"),
    ("Lines of Code", f"{linhas_de_codigo(lista):,}".replace(",", ".")),
    ("Locale", "pt_BR.UTF-8"),
    ("Email", "isaiasaltoe7@gmail.com"),
    ("Linkedin", "isaiasaltoe"),
    ("Portfolio", "https://altoe.dev"),
    ("Resume", "https://altoe.dev/#contact")
    
]

# --- logo do Ruby (edite logo.txt para trocar a arte) ---
LOGO = [l.rstrip() for l in open("logo.txt").read().rstrip("\n").split("\n")]
W = max(map(len, LOGO))
# --- temas: escuro (GitHub dark) e claro (GitHub light) ---
# SHADE = tom de vermelho por "densidade" do caractere da arte
TEMAS = {
    "fastfetch.svg": dict(
        BG="#21242d", HEADER="#8cb369", KEY="#d6b46c", VAL="#e6e6e6",
        SHADE={"%": "#f0544a", "#": "#cc342d", "*": "#a8231d", "+": "#8c1d18",
               "=": "#741813", "-": "#5e1410", ":": "#4a100c", ".": "#3a0c09"},
        CORES={"green": "#8cb369", "red": "#d47766", "yellow": "#d6b46c"},
        PALETA=[["#30363d", "#e01b24", "#26c940", "#f5c211", "#1c71ff", "#c01cff", "#00c8d6", "#d0d0d0"],
                ["#5e5c64", "#ff4d4d", "#4cff6a", "#ffe33d", "#4d9bff", "#e55cff", "#3df2ff", "#ffffff"]],
    ),
    "fastfetch-light.svg": dict(
        BG="#f6f8fa", HEADER="#3f7d20", KEY="#9a6700", VAL="#24292f",
        SHADE={"%": "#b3261e", "#": "#cc342d", "*": "#d9534a", "+": "#e06d65",
               "=": "#e8877f", "-": "#efa29b", ":": "#f4bdb8", ".": "#f8d6d3"},
        CORES={"green": "#2f8a1e", "red": "#cf222e", "yellow": "#9a6700"},
        PALETA=[["#24292f", "#cf222e", "#2da44e", "#d4a72c", "#0969da", "#8250df", "#1b7c83", "#8c959f"],
                ["#57606a", "#ff6b6b", "#4ac26b", "#eac54f", "#54aeff", "#c297ff", "#3fb8c1", "#d0d7de"]],
    ),
}
FS, LH, CW = 14, 20, 9.2
# infos um pouco maiores para ocupar a mesma altura da arte
FS2 = 15
CW2 = CW * FS2 / FS

# valores podem ter trechos coloridos: "texto {green:85%} texto"
def texto_puro(v):
    return re.sub(r"\{(\w+):([^}]*)\}", r"\2", v or "")

def valor_svg(v, cores):
    partes, pos = [], 0
    for m in re.finditer(r"\{(\w+):([^}]*)\}", v):
        partes.append(escape(v[pos:m.start()]))
        partes.append(f'<tspan fill="{cores.get(m[1], m[1])}">{escape(m[2])}</tspan>')
        pos = m.end()
    partes.append(escape(v[pos:]))
    return "".join(partes)

lines = [(USER, None), ("-" * len(USER), None)] + INFO
right_x = 20 + (W + 6) * CW
h = 30 + len(LOGO) * LH
# espaçamento das infos calculado para a paleta terminar junto com a arte
LH2 = (len(LOGO) * LH - 14 - 36 + 14) / (len(lines) + 1)
w = right_x + (max(len(k) + len(texto_puro(v)) + 2 for k, v in lines) + 2) * CW2

for arquivo, t in TEMAS.items():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}">',
           f'<rect width="100%" height="100%" rx="10" fill="{t["BG"]}"/>',
           f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}" xml:space="preserve">']
    for i, line in enumerate(LOGO):
        spans = "".join(f'<tspan fill="{t["SHADE"].get(ch, t["SHADE"]["#"])}">{escape(ch)}</tspan>' if ch != " " else "&#160;" for ch in line)
        out.append(f'<text x="20" y="{30 + i * LH}">{spans}</text>')
    out.append(f'<g font-size="{FS2}">')
    for i, (k, v) in enumerate(lines):
        y = round(30 + i * LH2, 1)
        if v is None:
            if "@" in k:
                a, b = k.split("@")
                out.append(f'<text x="{right_x:.0f}" y="{y}" font-weight="bold"><tspan fill="{t["HEADER"]}">{escape(a)}</tspan><tspan fill="{t["VAL"]}">@</tspan><tspan fill="{t["HEADER"]}">{escape(b)}</tspan></text>')
            else:
                out.append(f'<text x="{right_x:.0f}" y="{y}" fill="{t["VAL"]}">{escape(k)}</text>')
        else:
            out.append(f'<text x="{right_x:.0f}" y="{y}"><tspan fill="{t["KEY"]}" font-weight="bold">{escape(k)}</tspan><tspan fill="{t["VAL"]}">: {valor_svg(v, t["CORES"])}</tspan></text>')
    out.append("</g>")
    # paleta igual ao fastfetch: linha normal + linha brilhante
    y = round(30 + (len(lines) + 1) * LH2 - 14, 1)
    for i, row in enumerate(t["PALETA"]):
        for j, c in enumerate(row):
            out.append(f'<rect x="{right_x + j * 3 * CW2:.0f}" y="{y + i * 18}" width="{3 * CW2 + 0.5:.1f}" height="18" fill="{c}"/>')
    out.append("</g></svg>")
    open(arquivo, "w").write("\n".join(out))
    print(f"{arquivo} gerado")
