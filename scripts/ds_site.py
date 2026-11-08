#!/usr/bin/env python3
"""Inventaria um site baixado e confere o design system gerado. Imprime JSON. Só lê.

Uso:
  ds_site.py inventario <pasta-do-site> [--pagina index.html]
  ds_site.py conferir <pasta-do-site> <pasta-de-saida>

Biblioteca padrão do Python 3.8 em diante.
"""
import argparse
import colorsys
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

EXT_TEXTO = {".html", ".htm", ".css", ".js", ".mjs"}
IGNORAR = {".git", "node_modules", "__pycache__"}
RASTREADORES = {
    "Google Analytics/Tag Manager": r"googletagmanager\.com|google-analytics\.com|\bgtag\(",
    "Meta Pixel": r"connect\.facebook\.net|\bfbq\(",
    "Hotjar": r"hotjar\.com|\bhj\(",
    "Microsoft Clarity": r"clarity\.ms",
    "TikTok Pixel": r"analytics\.tiktok\.com|\bttq\.",
    "LinkedIn Insight": r"snap\.licdn\.com",
}
BIBLIOTECAS = {"GSAP": r"gsap", "ScrollTrigger": r"ScrollTrigger", "Three.js": r"three(\.min)?\.js|THREE\.", "Lottie": r"lottie", "AOS": r"\baos\b", "Swiper": r"swiper", "Lenis": r"lenis"}
TAG_VISIVEL_IGNORAR = {"script", "style", "noscript", "template", "svg"}
SECOES_OBRIGATORIAS = ("overview", "tipografia", "cores", "superficies", "icones", "motion", "componentes", "layout")
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})(?:[\s,/]+([\d.]+%?))?\s*\)", re.I)
HSL = re.compile(r"hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:[\s,/]+([\d.]+%?))?\s*\)", re.I)
COMENTARIO_CSS = re.compile(r"/\*.*?\*/", re.S)


def imprimir(dados):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(dados, ensure_ascii=False, indent=2))


def ler(p):
    return Path(p).read_text(encoding="utf-8-sig", errors="replace")


def arquivos(pasta):
    return [p for p in sorted(Path(pasta).rglob("*")) if p.is_file() and not (set(p.relative_to(pasta).parts) & IGNORAR) and p.name != ".DS_Store"]


class Leitor(HTMLParser):
    """Separa texto visível, CSS inline, moldura, links de recursos, ids e comentários."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.textos, self.css, self.moldura, self.js, self.recursos, self.ids, self.scripts_externos = [], [], [], [], [], [], set(), []
        self.modulo = False
        self.comentarios = 0
        self.em_moldura = False

    def handle_starttag(self, tag, attrs):
        a = dict((k, v or "") for k, v in attrs)
        if tag not in ("meta", "link", "img", "br", "hr", "input", "source"):
            self.pilha.append(tag)
        if a.get("id"):
            self.ids.add(a["id"])
        if a.get("style", "").strip():
            self.css.append("x{%s}" % a["style"])
        if tag == "style":
            self.em_moldura = "data-ds-moldura" in a
        if tag == "script" and a.get("type", "").lower() == "module":
            self.modulo = True
        if tag == "script" and a.get("src"):
            self.scripts_externos.append(a["src"])
        for chave in ("src", "href", "poster"):
            if a.get(chave) and tag in ("script", "link", "img", "video", "source", "audio", "iframe"):
                self.recursos.append((tag, a[chave], a.get("rel", "")))
        for chave in ("alt", "title", "placeholder", "aria-label"):
            if a.get(chave, "").strip():
                self.textos.append(a[chave].strip())
        if tag == "input" and a.get("type", "text") in ("button", "submit") and a.get("value", "").strip():
            self.textos.append(a["value"].strip())

    def handle_endtag(self, tag):
        if tag in self.pilha:
            while self.pilha and self.pilha.pop() != tag:
                pass
        if tag == "style":
            self.em_moldura = False

    def handle_data(self, data):
        atual = self.pilha[-1] if self.pilha else ""
        if atual == "style":
            (self.moldura if self.em_moldura else self.css).append(data)
        elif atual == "script":
            self.js.append(data)
        elif not any(t in TAG_VISIVEL_IGNORAR for t in self.pilha) and data.strip():
            self.textos.append(re.sub(r"\s+", " ", data).strip())

    def handle_comment(self, data):
        self.comentarios += 1


def ler_html(caminho):
    leitor = Leitor()
    leitor.feed(ler(caminho))
    return leitor


def normalizar_cor(cor):
    """Devolve a cor em hexadecimal minúsculo, ou None."""
    cor = cor.strip()
    m = HEX.fullmatch(cor)
    if m:
        h = cor[1:].lower()
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        return "#" + h
    m = RGB.fullmatch(cor)
    if m:
        return "#%02x%02x%02x" % tuple(min(int(m.group(i)), 255) for i in (1, 2, 3)) + sufixo_alfa(m.group(4))
    m = HSL.fullmatch(cor)
    if m:
        r, g, b = colorsys.hls_to_rgb(float(m.group(1)) % 360 / 360, float(m.group(3)) / 100, float(m.group(2)) / 100)
        return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255)) + sufixo_alfa(m.group(4))
    return None


def sufixo_alfa(a):
    if a is None:
        return ""
    v = float(a[:-1]) / 100 if a.endswith("%") else float(a)
    return "" if v >= 1 else "%02x" % round(v * 255)


def cores_de(texto):
    """Lê cores só nos valores de propriedades, para não confundir seletor #id ou url(#id) com cor."""
    achadas = []
    for m in re.finditer(r":\s*([^;{}]+)(?=[;}])", texto):
        valor = re.sub(r"url\([^)]*\)", " ", m.group(1))
        achadas += [c.group(0) for rx in (HEX, RGB, HSL) for c in rx.finditer(valor)]
    return Counter(n for n in map(normalizar_cor, achadas) if n)


def gradientes_de(texto):
    """Extrai gradientes respeitando parênteses internos, como rgba(...)."""
    saida = Counter()
    for m in re.finditer(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", texto):
        nivel, i = 1, m.end()
        while i < len(texto) and nivel:
            nivel += {"(": 1, ")": -1}.get(texto[i], 0)
            i += 1
        saida[re.sub(r"\s+", " ", texto[m.start():i])] += 1
    return saida


def valores(texto, propriedade):
    return Counter(re.sub(r"\s+", " ", m.group(1)).strip() for m in re.finditer(r"(?<![\w-])" + propriedade + r"\s*:\s*([^;}{]+)[;}]", texto, re.I))


def fontes_de(texto):
    nomes = Counter()
    for valor, n in valores(texto, "font-family").items():
        for parte in valor.split(","):
            nome = parte.replace("!important", "").strip().strip("'\"")
            if nome and not nome.lower().startswith("var("):
                nomes[nome] += n
    return nomes


SISTEMA = {"arial", "helvetica", "helvetica neue", "georgia", "times", "times new roman", "courier", "courier new", "verdana", "tahoma", "trebuchet ms", "segoe ui", "roboto", "san francisco", "menlo", "consolas", "monaco"}
GENERICAS = {"sans-serif", "serif", "monospace", "system-ui", "cursive", "inherit", "initial", "-apple-system", "ui-sans-serif", "ui-monospace", "ui-serif", "blinkmacsystemfont"}


def arquivos_css_ligados(pasta, leitor, base):
    raiz = Path(pasta)
    for tag, url, rel in leitor.recursos:
        local = caminho_local(url)
        if local and tag == "link":
            alvo = (raiz / local.lstrip("/")) if local.startswith("/") else (base / local)
            if alvo.is_file() and alvo.suffix.lower() == ".css":
                yield alvo


def urls_do_css(pasta, leitor, base):
    """Confere url() do CSS. Devolve (caminhos absolutos, arquivos que faltam)."""
    raiz = Path(pasta)
    absolutos, faltando = set(), set()
    fontes = [(base, t) for t in leitor.css] + [(f.parent, ler(f)) for f in arquivos_css_ligados(pasta, leitor, base)]
    for pasta_css, texto in fontes:
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", COMENTARIO_CSS.sub("", texto)):
            local = caminho_local(m.group(1).strip())
            if not local:
                continue
            if local.startswith("/"):
                absolutos.add(local)
                alvo = raiz / local.lstrip("/")
            else:
                alvo = pasta_css / local
            if not alvo.is_file():
                faltando.add(m.group(1).strip())
    return sorted(absolutos), sorted(faltando)


def fontes_sem_arquivo(fontes, css, leitor):
    """Fontes citadas no CSS que nada carrega: a tela mostra a fonte seguinte da lista."""
    declaradas = {m.strip().strip("'\"").lower() for b in re.findall(r"@font-face\s*\{([^}]*)\}", css, re.I) for m in re.findall(r"font-family\s*:\s*([^;}]+)", b, re.I)}
    carregadas_por_link = any(re.search(r"fonts\.(googleapis|bunny)|typekit|fontshare", u, re.I) for _, u, _ in leitor.recursos)
    if carregadas_por_link:
        return []
    return sorted(f for f in fontes if f.lower() not in declaradas and f.lower() not in GENERICAS and f.lower() not in SISTEMA)


def caminho_local(url):
    u = urlparse(url)
    if u.scheme or url.startswith(("//", "#", "data:", "mailto:", "tel:", "javascript:")):
        return None
    return unquote(u.path) or None


def eh_externo(url):
    u = urlparse(url)
    return u.scheme in ("http", "https") or url.startswith("//")


def juntar_fontes(pasta, leitor, base=None):
    """Junta CSS e JS de uma página (inline e arquivos locais ligados)."""
    css, js = list(leitor.css), list(leitor.js)
    raiz = Path(pasta)
    for tag, url, rel in leitor.recursos:
        local = caminho_local(url)
        if not local:
            continue
        alvo = (raiz / local.lstrip("/")) if local.startswith("/") else ((base or raiz) / local)
        if alvo.is_file():
            if alvo.suffix.lower() == ".css":
                css.append(ler(alvo))
            elif alvo.suffix.lower() in (".js", ".mjs"):
                js.append(ler(alvo))
    return COMENTARIO_CSS.sub("", "\n".join(css)), "\n".join(js)


def modo_de_abertura(html_bruto, leitor, js):
    motivos = []
    if leitor.modulo:
        motivos.append("<script type=module>")
    if re.search(r"\bimport\s*\(", js):
        motivos.append("import() dinâmico")
    if re.search(r"\bfetch\s*\(|XMLHttpRequest", js):
        motivos.append("fetch/XHR")
    if re.search(r"serviceWorker\.register", js):
        motivos.append("service worker")
    if re.search(r"""(?:src|href)=["']/(?!/)""", html_bruto) or any((caminho_local(u) or "").startswith("/") for _, u, _ in leitor.recursos):
        motivos.append("caminhos absolutos")
    return ("precisa_servidor" if motivos else "autocontido"), motivos


def checar_rastreadores(texto):
    return [nome for nome, rx in RASTREADORES.items() if re.search(rx, texto)]


def arquivos_quebrados(pasta, pagina, leitor):
    faltando = []
    base = pagina.parent
    for tag, url, rel in leitor.recursos:
        if tag == "link" and rel not in ("stylesheet", "icon", "preload", "modulepreload"):
            continue
        local = caminho_local(url)
        if not local or local.endswith(".html"):
            continue
        alvo = (Path(pasta) / local.lstrip("/")) if local.startswith("/") else (base / local)
        if not alvo.is_file():
            faltando.append(url)
    return sorted(set(faltando))


def topo(contador, n=30):
    return [{"valor": v, "usos": q} for v, q in contador.most_common(n)]


def inventario(args):
    pasta = Path(args.pasta)
    if not pasta.is_dir():
        return {"erro": "Não encontrei a pasta do site."}, 2
    lista = arquivos(pasta)
    paginas = [p for p in lista if p.suffix.lower() in (".html", ".htm")]
    if not paginas:
        return {"erro": "A pasta não tem nenhuma página HTML."}, 2
    alvo = pasta / args.pagina if args.pagina else next((p for p in paginas if p.name.lower() == "index.html"), paginas[0])
    if not alvo.is_file():
        return {"erro": "Não encontrei a página %s." % args.pagina, "paginas": [str(p.relative_to(pasta)) for p in paginas]}, 2
    bruto = ler(alvo)
    leitor = Leitor()
    leitor.feed(bruto)
    css, js = juntar_fontes(pasta, leitor, alvo.parent)
    modo, motivos = modo_de_abertura(bruto, leitor, js)
    absolutos, urls_faltando = urls_do_css(pasta, leitor, alvo.parent)
    if absolutos:
        modo = "precisa_servidor"
        motivos.append("url() absoluta no CSS")
    tudo = bruto + "\n" + css + "\n" + js
    externos = sorted({urlparse(u if not u.startswith("//") else "https:" + u).netloc for _, u, _ in leitor.recursos if eh_externo(u)})
    tipos = Counter(p.suffix.lower() or "(sem extensão)" for p in lista)
    fontes = fontes_de(css)
    return {
        "pagina": str(alvo.relative_to(pasta)),
        "paginas_html": [str(p.relative_to(pasta)) for p in paginas],
        "modo": modo,
        "motivos_do_modo": motivos,
        "tamanho_total_mb": round(sum(p.stat().st_size for p in lista) / 1048576, 2),
        "arquivos_por_tipo": dict(tipos.most_common()),
        "arquivos_quebrados": sorted(set(arquivos_quebrados(pasta, alvo, leitor)) | set(urls_faltando)),
        "cores": topo(cores_de(css), 40),
        "variaveis_css": dict(sorted({m.group(1): re.sub(r"\s+", " ", m.group(2)).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}]+)", css)}.items())),
        "gradientes": [g for g, _ in gradientes_de(css).most_common(15)],
        "fontes": topo(fontes),
        "fontes_sem_arquivo": fontes_sem_arquivo(fontes, css, leitor),
        "tamanhos_de_fonte": topo(valores(css, "font-size")),
        "pesos": topo(valores(css, "font-weight"), 12),
        "entrelinhas": topo(valores(css, "line-height"), 12),
        "espacamento_de_letras": topo(valores(css, "letter-spacing"), 10),
        "preenchimentos": topo(valores(css, "padding"), 15),
        "vaos": topo(valores(css, "gap"), 10),
        "larguras_maximas": topo(valores(css, "max-width"), 10),
        "grades": topo(valores(css, "grid-template-columns"), 10),
        "raios": topo(valores(css, "border-radius"), 15),
        "sombras": topo(valores(css, "box-shadow"), 15),
        "filtros_de_fundo": topo(valores(css, "backdrop-filter"), 8),
        "medidas_de_tela": sorted({re.sub(r"\s+", " ", m).strip() for m in re.findall(r"@media\s*([^{]+)\{", css)}),
        "animacoes_keyframes": sorted(set(re.findall(r"@keyframes\s+([\w-]+)", css))),
        "animacoes": topo(valores(css, "animation"), 15),
        "transicoes": topo(valores(css, "transition"), 15),
        "bibliotecas": [n for n, rx in BIBLIOTECAS.items() if re.search(rx, tudo, re.I)],
        "rastreadores": checar_rastreadores(tudo),
        "dominios_externos": externos,
        "textos_visiveis": len(leitor.textos),
        "comentarios_html": leitor.comentarios,
    }, 0


def conferir(args):
    pasta, saida = Path(args.pasta), Path(args.saida)
    ds = saida / "design-system.html"
    if not pasta.is_dir():
        return {"erro": "Não encontrei a pasta do site."}, 2
    if not ds.is_file():
        return {"erro": "Não encontrei design-system.html na pasta de saída."}, 2
    def janelas(t, n=4):
        p = re.findall(r"\w+", t.lower())
        return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}

    orig_textos, orig_css = set(), []
    fontes_orig = Counter()
    for pagina in (p for p in arquivos(pasta) if p.suffix.lower() in (".html", ".htm")):
        lei = ler_html(pagina)
        orig_textos.update(lei.textos)
        css, _ = juntar_fontes(pasta, lei, pagina.parent)
        orig_css.append(css)
    for p in arquivos(pasta):
        if p.suffix.lower() == ".css":
            orig_css.append(COMENTARIO_CSS.sub("", ler(p)))
    css_orig = "\n".join(orig_css)
    fontes_orig.update(fontes_de(css_orig))

    bruto = ler(ds)
    lei = Leitor()
    lei.feed(bruto)
    css_ds, js_ds = juntar_fontes(saida, lei, ds.parent)
    textos_ds = set(lei.textos)
    orig_janelas = set().union(*(janelas(t) for t in orig_textos)) if orig_textos else set()
    restante = sorted(t for t in textos_ds if (t in orig_textos and (len(t) >= 12 or len(t.split()) >= 3 or re.search(r"\d", t))) or janelas(t) & orig_janelas)
    nomes = {w for t in orig_textos for w in re.findall(r"(?<=\s)[A-ZÀ-Ý][a-zà-ÿ]{3,}", t)}
    marcas = sorted(n for n in nomes if any(re.search(r"\b%s\b" % n, t) for t in textos_ds))
    cores_o = set(cores_de(css_orig))
    # compara ignorando o alfa, porque o catálogo mostra a mesma cor com outra opacidade
    bases = {c[:7] for c in cores_o}
    cores_extra = sorted(c for c in cores_de(css_ds) if c[:7] not in bases)
    cores_moldura = sorted(c for c in cores_de("\n".join(lei.moldura)) if c[:7] not in bases)
    fontes_moldura = sorted(f for f in fontes_de("\n".join(lei.moldura)) if f.lower() not in {g.lower() for g in fontes_orig} and f.lower() not in GENERICAS)
    _, urls_faltando = urls_do_css(saida, lei, ds.parent)
    fontes_extra = sorted(f for f in fontes_de(css_ds) if f.lower() not in {g.lower() for g in fontes_orig} and f.lower() not in GENERICAS)
    tudo = bruto + "\n" + css_ds + "\n" + js_ds
    secoes = [s for s in SECOES_OBRIGATORIAS if s not in lei.ids]
    externos = sorted({u for _, u, _ in lei.recursos if eh_externo(u)})
    resultado = {
        "copy_restante": restante[:80],
        "possiveis_nomes_de_marca": marcas[:40],
        "cores_fora_do_original": cores_extra,
        "fontes_fora_do_original": fontes_extra,
        "rastreadores": checar_rastreadores(tudo),
        "links_externos": externos,
        "arquivos_quebrados": sorted(set(arquivos_quebrados(saida, ds, lei)) | set(urls_faltando)),
        "secoes_ausentes": secoes,
        "comentarios_html": lei.comentarios,
        "so_na_moldura": {"cores": cores_moldura, "fontes": fontes_moldura},
    }
    resultado["ok"] = not any(resultado[k] for k in ("copy_restante", "cores_fora_do_original", "fontes_fora_do_original", "rastreadores", "links_externos", "arquivos_quebrados", "secoes_ausentes", "comentarios_html"))
    return resultado, 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    i = sub.add_parser("inventario")
    i.add_argument("pasta")
    i.add_argument("--pagina")
    c = sub.add_parser("conferir")
    c.add_argument("pasta")
    c.add_argument("saida")
    a = p.parse_args()
    dados, codigo = inventario(a) if a.comando == "inventario" else conferir(a)
    imprimir(dados)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
