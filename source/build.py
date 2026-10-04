import re, shutil, os, html
base = '/tmp/claude-0/-home-claude/40bb297e-0472-5d75-bafd-d440afc86bfb/scratchpad'
out = base + '/site'
shutil.rmtree(out, ignore_errors=True); os.makedirs(out + '/images')
for f in os.listdir(base + '/shots'):
    if f.endswith('.jpg'): shutil.copy(f'{base}/shots/{f}', f'{out}/images/{f}')
shutil.copy(base + '/raman_small.png', out + '/images/raman.png')
body = open(base + '/site_build/body.html', encoding='utf-8').read()

def fig(m):
    name, cap = m.group(1), m.group(2)
    alt = html.escape(re.sub(r'<[^>]+>', '', cap), quote=True)
    return (f'<figure><a href="../images/{name}.jpg"><img src="../images/{name}.jpg" alt="{alt}" loading="lazy"></a>'
            f'<figcaption>{cap}</figcaption></figure>')
body = re.sub(r'<p>\[IMG:([\w-]+)\]</p>\s*<p><em>(.*?)</em></p>', fig, body, flags=re.S)
assert '[IMG:' not in body, 'unreplaced marker'
heads = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
title = 'How I Turned an NCERT Chapter into a Live-Class Teaching Workflow with Gemini Notebook'
sub = 'A step-by-step guide to Interactive Reports, with the exact prompt, the checks I ran and the cards I would actually use'
# ---- hero: original (a+b)^2 area model, vector, so it stays crisp at any size
hero_svg = '''<svg class="hero-art" viewBox="0 0 1600 620" role="img" aria-labelledby="hero-t" preserveAspectRatio="xMidYMid meet">
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

page = f'''<!doctype html>
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
<meta property="og:image" content="https://maths-with-raman.pages.dev/images/09-infographic.jpg">
<link rel="alternate" href="https://rrtiwari.substack.com/p/how-i-turned-an-ncert-chapter-into">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../images/raman.png">
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
<img src="../images/raman.png" alt="">
<div><b>Radha Raman Tiwari</b><span>Maths teacher and Head of Examination, Suditi Global Academy, Mainpuri</span></div>
<span class="links"><a href="https://x.com/RRTiwari19">@RRTiwari19 on X</a><a href="https://rrtiwari.substack.com/p/how-i-turned-an-ncert-chapter-into">Also on Substack</a></span>
</div>
</header>
<div class="hero">{hero_svg}</div>
<div class="layout">
<aside><nav aria-label="Contents"><b>In this guide</b><ol id="toc">{toc}</ol></nav></aside>
<main>
<p class="sub-m">Also published on <a href="https://rrtiwari.substack.com/p/how-i-turned-an-ncert-chapter-into">Substack</a>.</p>
<details class="toc-m"><summary>In this guide</summary><ol>{toc}</ol></details>
{body}
<div class="cta"><b>Tried it on another chapter?</b> I would like to hear what you changed. Find me on X: <a href="https://x.com/RRTiwari19">@RRTiwari19</a>, or read and subscribe on <a href="https://rrtiwari.substack.com/p/how-i-turned-an-ncert-chapter-into">Substack</a>.</div>
</main>
</div>
<footer>&copy; 2026 Radha Raman Tiwari. Screenshots are from Gemini Notebook, taken on 4 October 2026; menu names and options may change. NCERT material is not reproduced here; use the official NCERT PDF.</footer>
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
GUIDE='gemini-notebook-interactive-reports'
os.makedirs(out+'/'+GUIDE)
open(out + '/'+GUIDE+'/index.html', 'w', encoding='utf-8').write(page)
exec(open(base+'/site_build/home.py',encoding='utf-8').read())
open(out + '/_headers', 'w').write('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/images/*\n  Cache-Control: public, max-age=31536000, immutable\n')
print(len(page), 'bytes;', len(heads), 'sections;', len(os.listdir(out+'/images')), 'images')
