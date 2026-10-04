"""Builds the whole site. Run from anywhere:  python3 source/build.py
Reads  source/guides/<slug>/{guide.json, body.html, shots/*.jpg}  and  source/assets/.
Writes index.html, assets/, and one folder per guide at the repo root (what Cloudflare Pages serves)."""
import re, shutil, os, html, json, glob
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
SITE = 'https://maths-with-raman.pages.dev/'
SUBSTACK = 'https://rrtiwari.substack.com'

AREA_MODEL_HERO = '''<svg class="hero-art" viewBox="0 0 1600 620" role="img" aria-labelledby="hero-t" preserveAspectRatio="xMidYMid meet">
<title id="hero-t">Area model of (a + b) squared: a square split into a squared, two rectangles of area ab, and b squared</title>
<defs><pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".06"/></pattern></defs>
<rect width="1600" height="620" fill="#101a2e"/><rect width="1600" height="620" fill="url(#g)"/>
<g font-family="Georgia,'Times New Roman',serif" fill="#fff">
<text x="130" y="250" font-size="92" font-style="italic">(a + b)<tspan dy="-34" font-size="54">2</tspan></text>
<text x="130" y="350" font-size="64" font-style="italic" fill="#9fb3d1">= a<tspan dy="-22" font-size="38">2</tspan><tspan dy="22"> + 2ab + b</tspan><tspan dy="-22" font-size="38">2</tspan></text>
<text x="130" y="440" font-family="system-ui,sans-serif" font-size="26" fill="#9fb3d1">Class IX, NCERT, Chapter 4</text>
</g>
<g transform="translate(930 90)" font-family="Georgia,serif" font-style="italic" text-anchor="middle">
<rect x="0" y="0" width="270" height="270" fill="#4cc9e0"/>
<rect x="270" y="0" width="190" height="270" fill="#d6409f"/>
<rect x="0" y="270" width="270" height="190" fill="#d6409f"/>
<rect x="270" y="270" width="190" height="190" fill="#f5c542"/>
<g fill="#101a2e" font-size="64"><text x="135" y="160">a<tspan dy="-22" font-size="36">2</tspan></text><text x="365" y="160" fill="#fff">ab</text><text x="135" y="390" fill="#fff">ab</text><text x="365" y="390">b<tspan dy="-22" font-size="36">2</tspan></text></g>
<g fill="#9fb3d1" font-size="34"><text x="135" y="-18">a</text><text x="365" y="-18">b</text><text x="-34" y="148">a</text><text x="-34" y="378">b</text></g>
<path d="M0 -50H460M-50 0V460" stroke="#9fb3d1" stroke-opacity=".5" fill="none"/>
</g></svg>'''

def _art():
    W,H=560,440
    layers=[(70,[150,290]),(205,[80,185,255,360]),(340,[80,185,255,360]),(460,[220])]
    cols=['#4cc9e0','#d6409f']
    o=[]
    o.append('<defs><pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#fff" fill-opacity=".10"/></pattern>'
             '<linearGradient id="hot" x1="0" x2="1"><stop offset="0" stop-color="#4cc9e0"/><stop offset=".55" stop-color="#d6409f"/><stop offset="1" stop-color="#f5c542"/></linearGradient></defs>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
    # faint symbols
    syms=[('Σ',24,52,54),('π',470,60,50),('∫',30,410,56),('</>',420,410,34),('x²',250,34,32),('{ }',478,396,30),('0110',130,425,22)]
    for t,x,y,sz in syms:
        o.append(f'<text x="{x}" y="{y}" font-family="Georgia,serif" font-style="italic" font-size="{sz}" fill="#fff" fill-opacity=".16">{t}</text>')
    # edges
    for li in range(len(layers)-1):
        x1,ys1=layers[li]; x2,ys2=layers[li+1]
        for i,y1 in enumerate(ys1):
            for j,y2 in enumerate(ys2):
                hot=(li+i+j)%5==0
                o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{"url(#hot)" if hot else "#9fb3d1"}" stroke-opacity="{.9 if hot else .22}" stroke-width="{2.4 if hot else 1}"/>')
    # nodes
    for li,(x,ys) in enumerate(layers[:-1]):
        for i,y in enumerate(ys):
            c=cols[i%2] if li==0 else ('#9fb3d1' if (i+li)%3 else '#f5c542')
            r=22 if li==0 else 13
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#101a2e" stroke="{c}" stroke-width="3"/>')
            if li==0:
                o.append(f'<text x="{x}" y="{y+9}" text-anchor="middle" font-family="Georgia,serif" font-style="italic" font-size="26" fill="{c}">{"ab"[i]}</text>')
            else:
                o.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{c}"/>')
    # output: mini area model tile
    ox,oy=460,220
    o.append(f'<g transform="translate({ox-60} {oy-60}) scale(1.33)" font-family="Georgia,serif" font-style="italic" text-anchor="middle" font-size="22">'
             '<rect width="52" height="52" fill="#4cc9e0"/><rect x="52" width="38" height="52" fill="#d6409f"/><rect y="52" width="52" height="38" fill="#d6409f"/><rect x="52" y="52" width="38" height="38" fill="#f5c542"/>'
             '<text x="26" y="34" fill="#101a2e">a²</text><text x="71" y="34" fill="#fff">ab</text><text x="26" y="78" fill="#fff">ab</text><text x="71" y="78" fill="#101a2e">b²</text></g>')
    o.append(f'<text x="{ox}" y="{oy+92}" text-anchor="middle" font-family="Georgia,serif" font-style="italic" font-size="26" fill="#fff">(a + b)²</text>')
    # circuit trace
    o.append('<g fill="none" stroke="#4cc9e0" stroke-opacity=".5" stroke-width="2"><path d="M20 398H110V380H200"/><path d="M250 420H330V400H400"/></g>'
             '<g fill="#4cc9e0" fill-opacity=".7"><circle cx="200" cy="380" r="4"/><circle cx="400" cy="400" r="4"/></g>')
    return ('<svg class="sq" viewBox="0 0 %d %d" role="img" aria-label="A neural network whose inputs a and b produce the area model of (a + b) squared">'%(W,H))+''.join(o)+'</svg>'

NET_ART = _art()

def render_guide(g, body, toc, hero):
    title, sub, substack = g['title'], g['subtitle'], g['substack']
    og = SITE + g['slug'] + '/img/' + g['thumb']
    footer = g.get('footer', '')
    cta_head = g.get('cta_head', 'Tried it yourself?')
    cta_text = g.get('cta_text', 'I would like to hear what you changed.')
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{sub}">
<meta name="author" content="Radha Raman Tiwari">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{sub}">
<meta property="og:image" content="{og}">
<link rel="alternate" href="{substack}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../assets/raman.png">
<style>
:root{{--bg:#fff;--fg:#1a2233;--muted:#5b6578;--accent:#b3267a;--line:#e3e6ec;--card:#f5f7fa;--code:#f1f3f7;--ink:#101a2e;--serif:Charter,"Bitstream Charter","Sitka Text",Cambria,Georgia,serif;--ui:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1424;--fg:#e6eaf2;--muted:#9aa6bd;--accent:#ff7cc3;--line:#26324a;--card:#141d33;--code:#18223a}}}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:19px/1.75 var(--serif);-webkit-text-size-adjust:100%}}
a{{color:var(--accent);text-underline-offset:3px}}
a:focus-visible,summary:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:3px}}
.crumb{{font:15px/1 var(--ui);margin:0 0 22px}}
.crumb a{{text-decoration:none}}
.top{{max-width:1120px;margin:0 auto;padding:40px 24px 28px}}
h1{{font:700 clamp(30px,4.2vw,46px)/1.12 var(--serif);letter-spacing:-.015em;margin:0 0 16px;max-width:24ch}}
.sub{{font:400 clamp(18px,2vw,21px)/1.5 var(--serif);color:var(--muted);margin:0 0 22px;max-width:34em}}
.author{{display:flex;align-items:center;gap:14px;font:15px/1.4 var(--ui)}}
.author img{{width:52px;height:52px;border-radius:50%;object-fit:cover;background:var(--code)}}
.author b{{display:block;font-size:16px}}
.author span{{color:var(--muted)}}
.author .links{{margin-left:auto;display:flex;gap:20px;white-space:nowrap}}
.hero{{margin:0;background:var(--ink);overflow:hidden}}
.hero-art{{display:block;width:100%;height:auto;max-height:480px;margin:0 auto}}
@media (max-width:700px){{.hero-art{{width:190%;max-width:none;max-height:none;margin-left:-88%}}}}
.layout{{max-width:1120px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:230px minmax(0,700px);gap:64px;justify-content:center}}
aside{{position:relative}}
aside nav{{position:sticky;top:32px;padding:40px 0;font:15px/1.4 var(--ui);max-height:100vh;overflow-y:auto}}
aside b{{display:block;margin-bottom:12px;color:var(--muted);font-weight:600}}
aside ol{{list-style:none;margin:0;padding:0;border-left:2px solid var(--line)}}
aside li{{margin:0}}
aside a{{display:block;padding:7px 0 7px 16px;margin-left:-2px;border-left:2px solid transparent;color:var(--muted);text-decoration:none}}
aside a:hover{{color:var(--fg)}}
aside a.on{{color:var(--fg);font-weight:600;border-left-color:var(--accent)}}
.sub-m{{display:none;font:15px/1.5 var(--ui);margin:0 0 12px}}
.toc-m{{display:none;margin:0 0 8px;border:1px solid var(--line);border-radius:8px;font:15px/1.5 var(--ui)}}
.toc-m summary{{padding:12px 16px;cursor:pointer;font-weight:600}}
.toc-m ol{{margin:0;padding:0 16px 14px 36px}}
main{{padding:40px 0 0;min-width:0}}
h2{{font:700 clamp(25px,3vw,31px)/1.25 var(--serif);letter-spacing:-.01em;margin:56px 0 14px;scroll-margin-top:24px}}
main>h2:first-child,main>p.lead+h2{{margin-top:48px}}
h3{{font:700 21px/1.3 var(--serif);margin:32px 0 8px}}
p.lead{{font-size:22px;line-height:1.6;margin-top:0}}
figure{{margin:28px 0;text-align:center}}
figure img{{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}}
figcaption{{font:15px/1.5 var(--ui);color:var(--muted);margin-top:10px}}
pre{{background:var(--code);border:1px solid var(--line);border-radius:6px;padding:16px 18px;overflow-x:auto;font:14px/1.6 ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-word}}
.table-wrap{{overflow-x:auto;margin:22px 0}}
table{{border-collapse:collapse;width:100%;font:15px/1.5 var(--ui)}}
th,td{{border-bottom:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}}
th{{background:var(--code);border-bottom:2px solid var(--line)}}
li{{margin:6px 0}}
.cta{{margin:56px 0 24px;padding:22px 24px;border-left:4px solid var(--accent);background:var(--card);font:17px/1.6 var(--ui)}}
footer{{max-width:1120px;margin:40px auto 0;padding:24px;border-top:1px solid var(--line);color:var(--muted);font:14px/1.6 var(--ui)}}
@media (max-width:960px){{
.layout{{display:block;max-width:728px}}
aside{{display:none}}
.toc-m{{display:block}}
.sub-m{{display:block}}
.top{{padding-top:36px}}
.author .links{{display:none}}
body{{font-size:18px}}
}}
@media print{{aside,.toc-m,.hero{{display:none}}body{{background:#fff;color:#000}}}}
</style>
</head>
<body>
<header class="top">
<p class="crumb"><a href="../">&larr; Maths with Raman</a></p>
<h1>{title}</h1>
<p class="sub">{sub}</p>
<div class="author">
<img src="../assets/raman.png" alt="">
<div><b>Radha Raman Tiwari</b><span>Maths teacher and Head of Examination, Suditi Global Academy, Mainpuri</span></div>
<span class="links"><a href="https://x.com/RRTiwari19">@RRTiwari19 on X</a><a href="{substack}">Also on Substack</a></span>
</div>
</header>
<div class="hero">{hero}</div>
<div class="layout">
<aside><nav aria-label="Contents"><b>In this guide</b><ol id="toc">{toc}</ol></nav></aside>
<main>
<p class="sub-m">Also published on <a href="{substack}">Substack</a>.</p>
<details class="toc-m"><summary>In this guide</summary><ol>{toc}</ol></details>
{body}
<div class="cta"><b>{cta_head}</b> {cta_text} Find me on X: <a href="https://x.com/RRTiwari19">@RRTiwari19</a>, or read and subscribe on <a href="{substack}">Substack</a>.</div>
</main>
</div>
<footer>&copy; 2026 Radha Raman Tiwari. {footer}</footer>
<script>
(function(){{
var links=[].slice.call(document.querySelectorAll('#toc a'));
var map={{}};links.forEach(function(a){{map[a.getAttribute('href').slice(1)]=a}});
var heads=links.map(function(a){{return document.getElementById(a.getAttribute('href').slice(1))}}).filter(Boolean);
function spy(){{var y=window.scrollY+120,cur=heads[0];heads.forEach(function(h){{if(h.offsetTop<=y)cur=h}});
links.forEach(function(a){{a.classList.toggle('on',a===map[cur.id])}})}}
document.addEventListener('scroll',spy,{{passive:true}});spy();
document.querySelectorAll('.toc-m a').forEach(function(a){{a.addEventListener('click',function(){{a.closest('details').open=false}})}});
}})();
</script>
</body>
</html>
'''

def render_home(cards, og):
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maths with Raman</title>
<meta name="description" content="Practical how-to guides for teachers, written by Radha Raman Tiwari, a maths teacher in Mainpuri.">
<meta property="og:type" content="website">
<meta property="og:title" content="Maths with Raman">
<meta property="og:description" content="Practical how-to guides for teachers, written by Radha Raman Tiwari, a maths teacher in Mainpuri.">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/raman.png">
<style>
:root{{--bg:#fff;--fg:#1a2233;--muted:#5b6578;--accent:#b3267a;--line:#e3e6ec;--card:#f5f7fa;--ink:#101a2e;--serif:Charter,"Bitstream Charter","Sitka Text",Cambria,Georgia,serif;--ui:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1424;--fg:#e6eaf2;--muted:#9aa6bd;--accent:#ff7cc3;--line:#26324a;--card:#141d33}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:19px/1.75 var(--serif);-webkit-text-size-adjust:100%}}
a{{color:var(--accent);text-underline-offset:3px}}
a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:3px}}
.hero{{background:var(--ink);color:#fff}}
.bar,.hero-in,.about,.guides,footer{{max-width:1040px;margin:0 auto;padding-left:24px;padding-right:24px}}
.bar{{display:flex;justify-content:space-between;align-items:center;padding-top:22px;font:15px/1 var(--ui)}}
.bar b{{font:700 17px/1 var(--serif)}}
.bar nav{{display:flex;gap:22px}}
.bar a{{color:#c9d4ea}}
.hero-in{{display:grid;grid-template-columns:minmax(0,1fr) 500px;gap:40px;align-items:center;padding-top:48px;padding-bottom:64px}}
h1{{font:700 clamp(36px,5.6vw,64px)/1.05 var(--serif);letter-spacing:-.02em;margin:0 0 18px}}
.hero p{{font-size:clamp(19px,2.2vw,23px);line-height:1.5;color:#b9c6e0;margin:0;max-width:30em}}
.sq{{width:100%;height:auto;display:block}}
.about{{display:grid;grid-template-columns:240px minmax(0,1fr);gap:48px;padding-top:64px;padding-bottom:24px;align-items:center}}
.about img{{width:240px;height:240px;border-radius:50%;object-fit:cover;display:block}}
h2{{font:700 clamp(26px,3vw,32px)/1.2 var(--serif);margin:0 0 14px}}
.about p{{margin:0 0 14px}}
.facts{{font:15px/1.5 var(--ui);color:var(--muted);margin:18px 0 0;padding:0;list-style:none}}
.facts li{{margin:4px 0}}
.guides{{padding-top:40px;padding-bottom:56px}}
.card{{display:grid;grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:28px;align-items:center;margin-top:20px;padding:20px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:inherit;text-decoration:none}}
.card:hover{{border-color:var(--accent)}}
.card img{{width:100%;height:auto;display:block;border-radius:6px;border:1px solid var(--line);background:#fff}}
.card h3{{font:700 clamp(22px,2.4vw,28px)/1.25 var(--serif);margin:0 0 10px}}
.card p{{margin:0 0 12px;font-size:17px;line-height:1.6;color:var(--muted)}}
.card .go{{font:600 15px var(--ui);color:var(--accent)}}
.soon{{margin:18px 0 0;font:15px/1.5 var(--ui);color:var(--muted)}}
footer{{border-top:1px solid var(--line);padding-top:24px;padding-bottom:40px;color:var(--muted);font:14px/1.6 var(--ui)}}
@media (max-width:820px){{
.hero-in{{grid-template-columns:1fr;gap:32px;padding-bottom:44px}}
.sq{{max-width:100%}}
.about{{grid-template-columns:1fr;gap:24px;padding-top:44px;align-items:start}}
.about img{{width:128px;height:128px}}
.card{{grid-template-columns:1fr;gap:16px}}
body{{font-size:18px}}
}}
</style>
</head>
<body>
<header class="hero">
<div class="bar"><b>Maths with Raman</b><nav><a href="https://x.com/RRTiwari19">X</a><a href="{SUBSTACK}">Substack</a></nav></div>
<div class="hero-in">
<div><h1>Maths with Raman</h1><p>Practical guides for teachers, from a maths classroom and the examination office of a CBSE school. Teaching ideas, exam workflows and AI tools, tested in real school work and written up step by step.</p></div>
{square}
</div>
</header>
<main>
<section class="about" aria-labelledby="about-h">
<img src="assets/raman-photo.jpg" alt="Radha Raman Tiwari">
<div>
<h2 id="about-h">About me</h2>
<p>I am Radha Raman Tiwari. I am a maths teacher with 15+ years of experience, and I am the Head of Examination at Suditi Global Academy in Mainpuri, Uttar Pradesh.</p>
<p>My work sits between the classroom and the examination office: designing lessons, running school and board examinations from question paper to result, and finding tools that save a teacher's time without lowering the standard. These guides are the notes I keep for myself and my colleagues.</p>
<ul class="facts"><li>Maths teacher, 15+ years of experience</li><li>Head of Examination, Suditi Global Academy (CBSE)</li><li>Writing on <a href="{SUBSTACK}">Substack</a> and posting on <a href="https://x.com/RRTiwari19">X</a></li></ul>
</div>
</section>
<section class="guides" aria-labelledby="guides-h">
<h2 id="guides-h">Guides</h2>
{cards}
<p class="soon">New guides will be added here.</p>
</section>
</main>
<footer>&copy; 2026 Radha Raman Tiwari.</footer>
</body>
</html>
'''

def fig_factory():
    def fig(m):
        name, cap = m.group(1), m.group(2)
        alt = html.escape(re.sub(r'<[^>]+>', '', cap), quote=True)
        return (f'<figure><a href="img/{name}.jpg"><img src="img/{name}.jpg" alt="{alt}" loading="lazy"></a>'
                f'<figcaption>{cap}</figcaption></figure>')
    return fig

# ---- clean previously generated output (never touches source/ or .git)
guides = []
for gj in sorted(glob.glob(SRC + '/guides/*/guide.json')):
    g = json.load(open(gj, encoding='utf-8')); g['slug'] = os.path.basename(os.path.dirname(gj)); g['dir'] = os.path.dirname(gj)
    guides.append(g)
guides.sort(key=lambda g: g.get('date', ''), reverse=True)
for p in ['index.html', 'assets', 'images', '_headers'] + [g['slug'] for g in guides]:
    t = os.path.join(OUT, p)
    shutil.rmtree(t, ignore_errors=True) if os.path.isdir(t) else (os.path.exists(t) and os.remove(t))
shutil.copytree(SRC + '/assets', OUT + '/assets')

cards = ''
for g in guides:
    d = OUT + '/' + g['slug']; os.makedirs(d + '/img')
    for f in os.listdir(g['dir'] + '/shots'):
        if f.endswith(('.jpg', '.png')): shutil.copy(f"{g['dir']}/shots/{f}", f'{d}/img/{f}')
    body = open(g['dir'] + '/body.html', encoding='utf-8').read()
    body = re.sub(r'<p>\[IMG:([\w-]+)\]</p>\s*<p><em>(.*?)</em></p>', fig_factory(), body, flags=re.S)
    assert '[IMG:' not in body, g['slug'] + ': unreplaced image marker'
    heads = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
    toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    hero = AREA_MODEL_HERO.replace('Class IX, NCERT, Chapter 4', g.get('hero_caption', 'Class IX, NCERT, Chapter 4')) if g.get('hero', 'area-model') == 'area-model' else f'<img class="hero-art" src="img/{g["hero"]}" alt="">'
    open(d + '/index.html', 'w', encoding='utf-8').write(render_guide(g, body, toc, hero))
    cards += (f'<a class="card" href="{g["slug"]}/"><img src="{g["slug"]}/img/{g["thumb"]}" alt="{html.escape(g.get("thumb_alt", ""), quote=True)}" loading="lazy">'
              f'<div><h3>{g["title"]}</h3><p>{g["subtitle"]}</p><span class="go">Read the guide &rarr;</span></div></a>\n')
    print(g['slug'], len(heads), 'sections')

og = SITE + guides[0]['slug'] + '/img/' + guides[0]['thumb'] if guides else ''
square = NET_ART
open(OUT + '/index.html', 'w', encoding='utf-8').write(render_home(cards, og))
open(OUT + '/_headers', 'w').write('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/*/img/*\n  Cache-Control: public, max-age=31536000, immutable\n')
print('built', len(guides), 'guide(s)')
