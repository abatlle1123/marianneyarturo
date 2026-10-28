"""Genera el sitio listo para publicar en /home/claude/dist:
   index.html (HTML+CSS+JS en un archivo, con los íconos pequeños en línea)
   assets/hero.jpg + hero.webp, assets/ill/*.svg (ilustraciones grandes, carga diferida),
   favicon.svg"""
import sys, os, re, shutil
sys.path.insert(0, '/home/claude/src')
import toile, sketch, icons
from PIL import Image

SRC = '/home/claude/src'; OUT = '/home/claude/site/public'
R = lambda p: open(os.path.join(SRC, p), encoding='utf-8').read()
os.makedirs(OUT + '/assets/ill', exist_ok=True)

def svg_file(s, name):
    s = s.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    s = re.sub(r' class="[^"]*"', lambda m: m.group(0) if 'walk' in m.group(0) else '', s, count=1)
    open(f'{OUT}/assets/ill/{name}.svg', 'w', encoding='utf-8').write(s)
    return len(s)

sizes = {n: svg_file(s, n) for n, s in (('iglesia', sketch.REGINA), ('country-garden', sketch.GARDEN), ('camino', sketch.WALK),
        ('hotel-embajador', sketch.HOTEL_EMB), ('hotel-kimpton', sketch.HOTEL_KIM), ('hotel-jw-marriott', sketch.HOTEL_JW))}

# foto principal: jpg + webp
im = Image.open('/home/claude/assets/hero.jpg').convert('RGB')
im.save(f'{OUT}/assets/hero.jpg', quality=82, optimize=True, progressive=True)
im.save(f'{OUT}/assets/hero.webp', quality=80, method=6)

fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#f3f1ed"/><text x="32" y="42" text-anchor="middle" font-family="Georgia,serif" font-style="italic" font-size="28" fill="#3f4b36">M&amp;A</text></svg>'
open(f'{OUT}/favicon.svg', 'w').write(fav)

import hashlib
shutil.copy(SRC + '/og.jpg', OUT + '/assets/og.jpg')
def ver(p):
    return hashlib.md5(open(f'{OUT}/{p}', 'rb').read()).hexdigest()[:8]
css = R('styles8.css')
js = R('app8.js').replace('/* ===== RSVP_PLACEHOLDER ===== */', R('rsvp_v9.js'))
body = R('body8.html').replace(
    '<img class="pic" src="assets/hero.jpg"',
    '<picture><source srcset="assets/hero.webp" type="image/webp"><img class="pic" src="assets/hero.jpg"').replace(
    'fetchpriority="high" decoding="async">', 'fetchpriority="high" decoding="async"></picture>', 1)
body = re.sub(r'(src|srcset)="(assets/[^"?]+)"', lambda m: f'{m.group(1)}="{m.group(2)}?v={ver(m.group(2))}"', body)
sprite = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{sketch.FILTERS}</defs>{toile.SYMBOLS}{icons.SYMBOLS}</svg>'

html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<base href="/">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marianne y Arturo · 5 de marzo, 2027</title>
<meta name="description" content="Marianne y Arturo se casan el 5 de marzo de 2027 en Santo Domingo. Itinerario, vestimenta, guía para viajeros, lista de boda y RSVP.">
<meta property="og:title" content="Marianne y Arturo · 5 de marzo, 2027">
<meta property="og:description" content="Nos casamos en Santo Domingo. Itinerario, vestimenta, viaje y RSVP.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://marianneyarturo.com/">
<meta property="og:site_name" content="Marianne y Arturo">
<meta property="og:image" content="https://marianneyarturo.com/assets/og.jpg?v={ver('assets/og.jpg')}">
<meta property="og:image:secure_url" content="https://marianneyarturo.com/assets/og.jpg?v={ver('assets/og.jpg')}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="Marianne y Arturo · 5 de marzo, 2027 · Santo Domingo">
<meta name="twitter:image" content="https://marianneyarturo.com/assets/og.jpg?v={ver('assets/og.jpg')}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_DO">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://marianneyarturo.com/">
<meta name="theme-color" content="#f3f1ed">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" as="image" href="/assets/hero.webp?v={ver('assets/hero.webp')}" type="image/webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&family=Pinyon+Script&display=swap" rel="stylesheet">
<style>
{css}</style>
</head>
<body>
{sprite}
{body}
<script>
{js}</script>
</body>
</html>
'''
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(html)
os.makedirs(OUT + '/panel', exist_ok=True)
shutil.copy('/home/claude/src/panel.html', OUT + '/panel/index.html')
shutil.copy('/home/claude/src/boda.ics', OUT + '/boda.ics')

# vista previa: un solo archivo con todo incluido (abre directo, navega con #/seccion)
import base64
def uri(p):
    mt = {'svg': 'image/svg+xml', 'webp': 'image/webp', 'jpg': 'image/jpeg'}[p.rsplit('.', 1)[1]]
    return f'data:{mt};base64,' + base64.b64encode(open(f'{OUT}/{p}', 'rb').read()).decode()
pv = html.replace('<base href="/">\n', '').replace("endpoint:'/api/rsvp',", "endpoint:'',").replace('demo:false,', 'demo:true, ')
pv = re.sub(r'<link rel="preload"[^>]*>\n', '', pv).replace('', '')
pv = re.sub(r'<source srcset="[^"]*" type="image/webp">', '', pv)
for p in set(re.findall(r'(?:src|href)="((?:assets/[^"]+)|favicon\.svg)"', pv)):
    pv = pv.replace(f'"{p}"', '"' + uri(p.split('?')[0]) + '"')
open('/home/claude/boda-marianne-arturo.html', 'w', encoding='utf-8').write(pv)
print('index.html', len(html), '| ilustraciones', sizes,
      '| hero jpg/webp', os.path.getsize(f'{OUT}/assets/hero.jpg'), os.path.getsize(f'{OUT}/assets/hero.webp'))
