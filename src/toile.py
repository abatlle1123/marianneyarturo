# Ilustración botánica a línea fina, estilo grabado / toile, un solo tono de tinta + aguadas suaves.
import math, random

INK = '#56654b'
PAPER = '#f6f3ec'
HYD = '#a9b8c8'     # hortensia
SAGE = '#a8b5a1'    # salvia
MATCHA = '#9db27c'
STONE = '#dcc9b6'

def f(v): return f'{v:.1f}'.rstrip('0').rstrip('.')

def cr(pts, n=10):
    """Catmull-Rom -> lista densa de puntos."""
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(n):
            t = k / n; t2 = t*t; t3 = t2*t
            x = .5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = .5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(pts[-1])
    return out

def poly(pts): return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts)

def line(d, w=1, op=1, c=INK):
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{o}/>'

def shape(d, w=1, fill=PAPER, wash=None, wop=.45, off=(2.2, 1.6)):
    """Forma rellena de papel con contorno; aguada desplazada debajo (efecto grabado coloreado a mano)."""
    s = ''
    if wash:
        s += f'<path d="{d}" fill="{wash}" opacity="{wop}" transform="translate({off[0]} {off[1]})"/>'
    s += f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round"/>'
    return s

def g(inner, x=0, y=0, rot=0, s=1):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(s)})">{inner}</g>'

def tangent(pts, i):
    a = pts[max(0, i-1)]; b = pts[min(len(pts)-1, i+1)]
    return math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))

# ---------------- hojas ----------------
def leaf_d(L, W, asym=0):
    return (f'M0 0 C{f(L*.25)} {f(-W*(1+asym))} {f(L*.7)} {f(-W*.9)} {f(L)} 0 '
            f'C{f(L*.7)} {f(W*.85)} {f(L*.25)} {f(W*(1-asym))} 0 0Z')

def leaf(L, W, wash=SAGE, veins=0, wop=.4, w=.9):
    s = shape(leaf_d(L, W, .08), w, PAPER, wash, wop)
    s += line(f'M{f(L*.04)} 0 Q{f(L*.5)} {f(W*.12)} {f(L*.92)} 0', .7, .85)
    for k in range(veins):
        t = (k+1)/(veins+1); x = L*t*.9
        for sgn in (-1, 1):
            s += line(f'M{f(x)} {f(W*.05*sgn)} q{f(L*.08)} {f(-W*.35*sgn)} {f(L*.16)} {f(-W*.62*sgn)}', .55, .7)
    return s

# ---------------- rama de olivo ----------------
def olive_branch(pts, seed=1, L=30, W=4.6, olives=3):
    r = random.Random(seed)
    P = cr(pts, 14)
    s = line(poly(P), 1.15)
    n = len(P); i = 4; side = 1; leaves = ''
    while i < n - 2:
        a = tangent(P, i); x, y = P[i]
        ang = a + side*r.uniform(28, 46)
        ll = L*r.uniform(.75, 1.1)*(0.6 + .4*min(1, (n-i)/n*1.6))
        leaves += g(leaf(ll, W*r.uniform(.85, 1.1), SAGE), x, y, ang)
        side *= -1; i += r.randint(4, 7)
    # hoja final
    a = tangent(P, n-1); x, y = P[-1]
    leaves += g(leaf(L*.8, W*.9, SAGE), x, y, a)
    oli = ''
    for k in range(olives):
        j = r.randint(n//4, n-6); x, y = P[j]; a = tangent(P, j) + r.choice((-1, 1))*70
        ox = x + math.cos(math.radians(a))*9; oy = y + math.sin(math.radians(a))*9
        oli += line(f'M{f(x)} {f(y)} L{f(ox)} {f(oy)}', .7)
        oli += g(shape('M0 -5.5 C3.6 -5.5 4.2 -1 4.2 0.5 C4.2 4 2.4 5.8 0 5.8 C-2.4 5.8 -4.2 4 -4.2 .5 C-4.2 -1 -3.6 -5.5 0 -5.5Z', .8, PAPER, MATCHA, .55)
                 + line('M-1.6 -2.6 q1 -1 2.2 -.6', .6, .7), ox, oy, a+90)
    return s + leaves + oli

# ---------------- hortensia ----------------
def floret(r, seed):
    rr = random.Random(seed); rot = rr.uniform(0, 90)
    s = ''
    for k in range(4):
        a = rot + k*90 + rr.uniform(-8, 8)
        p = f'M0 0 C{f(r*.55)} {f(-r*.55)} {f(r*1.05)} {f(-r*.38)} {f(r*1.02)} 0 C{f(r*1.05)} {f(r*.38)} {f(r*.55)} {f(r*.55)} 0 0Z'
        s += f'<g transform="rotate({f(a)})"><path d="{p}" fill="{PAPER}" stroke="{INK}" stroke-width=".65" stroke-linejoin="round"/></g>'
    s += f'<circle r="{f(r*.16)}" fill="{INK}"/>'
    return s

def hydrangea_head(R=38, seed=3, wash=HYD):
    r = random.Random(seed)
    s = f'<ellipse cx="3" cy="3" rx="{f(R*1.02)}" ry="{f(R*.92)}" fill="{wash}" opacity=".42"/>'
    pts = []
    N = int(R*R/38)
    for k in range(N):
        rad = R*.92*math.sqrt((k+.5)/N); a = k*2.39996
        pts.append((rad*math.cos(a) + r.uniform(-2, 2), rad*.9*math.sin(a) + r.uniform(-2, 2)))
    pts.sort(key=lambda p: p[1])
    for k, (x, y) in enumerate(pts):
        s += g(floret(r.uniform(5.2, 7), seed*100+k), x, y)
    return s

def big_leaf(L=60, W=20, seed=1):
    r = random.Random(seed)
    # borde ligeramente aserrado
    top = []; bot = []
    for k in range(13):
        t = k/12; w = W*math.sin(math.pi*t)**.85
        j = (1.2 if k % 2 else -.4)
        top.append((L*t, -w - j*(0 < k < 12))); bot.append((L*t, w + j*(0 < k < 12)))
    d = poly(cr(top, 4) + list(reversed(cr(bot, 4)))) + 'Z'
    s = shape(d, .9, PAPER, SAGE, .42)
    s += line(f'M2 0 Q{f(L*.5)} 2 {f(L*.94)} 0', .75)
    for k in range(5):
        x = L*(.14 + k*.15)
        for sg in (-1, 1):
            s += line(f'M{f(x)} {f(sg*.6)} q{f(L*.1)} {f(-sg*W*.35)} {f(L*.2)} {f(-sg*W*.7)}', .55, .7)
    return s

def hydrangea(seed=3, R=38):
    s = line('M0 0 C-4 30 2 62 -6 96', 1.2)
    s += g(big_leaf(56, 18, seed), -3, 52, 150) + g(big_leaf(62, 19, seed+1), -2, 40, 18)
    s += hydrangea_head(R, seed)
    return s

# ---------------- flor silvestre (anémona / cosmos) ----------------
def bloom(r=13, n=7, seed=1, wash=None, center=INK):
    rr = random.Random(seed); s = ''
    if wash: s += f'<circle cx="2" cy="2" r="{f(r*.95)}" fill="{wash}" opacity=".38"/>'
    rot = rr.uniform(0, 360)
    for k in range(n):
        a = rot + k*360/n + rr.uniform(-6, 6); L = r*rr.uniform(.9, 1.06); W = r*.36
        p = (f'M0 0 C{f(L*.25)} {f(-W)} {f(L*.85)} {f(-W*1.05)} {f(L)} {f(-W*.25)} '
             f'L{f(L*.9)} 0 L{f(L)} {f(W*.25)} C{f(L*.85)} {f(W*1.05)} {f(L*.25)} {f(W)} 0 0Z')
        s += f'<g transform="rotate({f(a)})"><path d="{p}" fill="{PAPER}" stroke="{INK}" stroke-width=".75" stroke-linejoin="round"/>'
        s += line(f'M{f(L*.22)} 0 L{f(L*.62)} 0', .45, .55) + '</g>'
    s += f'<circle r="{f(r*.26)}" fill="{PAPER}" stroke="{INK}" stroke-width=".8"/>'
    for k in range(9):
        a = k*2.4; d = r*.15*math.sqrt(k/9)
        s += f'<circle cx="{f(d*math.cos(a))}" cy="{f(d*math.sin(a))}" r=".9" fill="{center}"/>'
    return s

def bud(h=10):
    return (shape(f'M0 0 C{f(h*.45)} {f(-h*.2)} {f(h*.42)} {f(-h*.8)} 0 {f(-h)} C{f(-h*.42)} {f(-h*.8)} {f(-h*.45)} {f(-h*.2)} 0 0Z', .75, PAPER, STONE, .5)
            + line(f'M0 0 L0 {f(-h*.7)}', .5, .6))

def wildflowers(seed=5):
    r = random.Random(seed); s = ''
    specs = [((0, 0), (-8, -50), (-22, -96), (-30, -130), 'f'), ((0, 0), (8, -40), (24, -70), (40, -98), 'f'),
             ((0, 0), (2, -40), (6, -80), (4, -112), 'b'), ((0, 0), (-12, -30), (-36, -52), (-52, -66), 'b')]
    for k, sp in enumerate(specs):
        pts = list(sp[:4]); P = cr(pts, 10)
        s += line(poly(P), .9)
        # hojitas finas
        for j in range(6, len(P)-6, 7):
            a = tangent(P, j) + (40 if j % 2 else -40)
            s += g(leaf(14, 2.2, SAGE, 0, .35, .7), P[j][0], P[j][1], a)
        x, y = P[-1]
        if sp[4] == 'f':
            s += g(bloom(13, 7, seed+k, HYD if k % 2 else STONE), x, y)
        else:
            s += g(bud(11), x, y, tangent(P, len(P)-1)+90)
    return s

def babys(seed=7, spread=46, n=14):
    r = random.Random(seed); s = ''
    for k in range(n):
        a = math.radians(-90 + r.uniform(-55, 55)); L = spread*r.uniform(.55, 1)
        x, y = math.cos(a)*L, math.sin(a)*L
        mx, my = x*.5 + r.uniform(-4, 4), y*.5
        s += line(f'M0 0 Q{f(mx)} {f(my)} {f(x)} {f(y)}', .55, .85)
        s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r.uniform(1.6, 2.4))}" fill="{PAPER}" stroke="{INK}" stroke-width=".6"/>'
    return s

def fern(L=90, seed=2):
    r = random.Random(seed)
    P = cr([(0, 0), (L*.35, -L*.12), (L*.7, -L*.12), (L, L*.04)], 12)
    s = line(poly(P), .9)
    for j in range(3, len(P)-1, 2):
        a = tangent(P, j); sc = 1 - j/len(P)*.75
        for sg in (-1, 1):
            s += g(leaf(9*sc+3, 2.2*sc+.8, SAGE, 0, .3, .6), P[j][0], P[j][1], a + sg*58)
    return s

# ---------------- composiciones ----------------
def spray():
    """Arreglo de esquina (300x300) — se usa rotado/espejado."""
    s = ''
    s += olive_branch([(40, 260), (90, 210), (150, 170), (230, 150), (285, 158)], 4, 30, 4.6, 3)
    s += olive_branch([(40, 260), (60, 190), (78, 120), (70, 50), (52, 12)], 9, 26, 4.2, 2)
    s += g(fern(100, 3), 46, 252, -18)
    s += g(babys(11, 52, 13), 118, 176, 20)
    s += g(babys(12, 40, 10), 62, 150, -40)
    s += g(wildflowers(21), 70, 262, 28, .95)
    s += g(hydrangea(5, 36), 96, 196, -30, .95)
    return s

def sprig_divider():
    """Divisor horizontal fino (260x40)."""
    s = line('M8 22 C60 20 90 24 112 22', .8, .8) + line('M148 22 C170 24 200 20 252 22', .8, .8)
    s += g(leaf(16, 3.2, SAGE, 0, .35, .75), 112, 22, 200) + g(leaf(16, 3.2, SAGE, 0, .35, .75), 148, 22, -20)
    s += g(leaf(12, 2.6, SAGE, 0, .35, .7), 120, 22, -35) + g(leaf(12, 2.6, SAGE, 0, .35, .7), 140, 22, 215)
    s += g(bloom(8, 6, 3, HYD), 130, 21)
    return s

def bouquet():
    s = ''
    s += olive_branch([(100, 200), (88, 150), (60, 100), (28, 70)], 31, 22, 3.6, 2)
    s += olive_branch([(100, 200), (114, 150), (142, 102), (172, 78)], 32, 22, 3.6, 2)
    s += g(fern(70, 8), 100, 196, -100)
    s += g(babys(40, 40, 10), 70, 118, -20) + g(babys(41, 40, 10), 132, 116, 20)
    s += g(hydrangea_head(30, 9), 100, 104)
    s += g(bloom(13, 7, 2, STONE), 66, 128) + g(bloom(12, 6, 5, HYD), 136, 132)
    s += g(bud(10), 84, 72, -15) + g(bud(9), 120, 70, 20)
    # lazo
    s += line('M92 196 C80 210 70 214 62 222 M108 196 C118 210 130 214 138 224', .8)
    s += shape('M100 192 C88 184 76 186 80 196 C84 204 96 198 100 194 C104 198 116 204 120 196 C124 186 112 184 100 192Z', .8, PAPER, STONE, .5)
    return s

def floret_icon():
    return floret(6, 4)


# =============== prendas e íconos ===============
def hanger(cx, top):
    return line(f'M{cx} {top+16} C{cx} {top+8} {cx+9} {top+9} {cx+9} {top+2} C{cx+9} {top-4} {cx+1} {top-6} {cx-3} {top-1}', 1) + \
           line(f'M{cx} {top+16} L{cx-62} {top+42} Q{cx-66} {top+46} {cx-60} {top+46} H{cx+60} Q{cx+66} {top+46} {cx+62} {top+42}Z', 1)

def chacabana():
    # percha: solo gancho y cuello visibles; los brazos quedan dentro de la camisa
    s = line('M100 26 C100 18 109 19 109 12 C109 6 101 4 97 9', 1)
    s += line('M100 26 L60 56 M100 26 L140 56', 1)
    body = ('M72 46 C60 49 44 54 32 64 C24 110 16 160 12 204 L34 208 C38 170 42 130 46 104 L44 222 C80 228 120 228 156 222 '
            'L154 104 C158 130 162 170 166 208 L188 204 C184 160 176 110 168 64 C156 54 140 49 128 46 C120 58 80 58 72 46Z')
    s += f'<path d="{body}" fill="{STONE}" opacity=".22" transform="translate(4 3)"/>'
    s += shape(body, 1.1, PAPER)
    # cuello de camisa: banda trasera + dos puntas dobladas que cierran al centro
    s += shape('M80 46 C86 39 114 39 120 46 C112 50 88 50 80 46Z', .8, '#ebe5da')
    s += shape('M100 62 L80 46 C76 48 72 50 70 52 L84 80 Z', .9, PAPER)
    s += shape('M100 62 L120 46 C124 48 128 50 130 52 L116 80 Z', .9, PAPER)
    s += line('M83 72 L98 62 M117 72 L102 62', .45, .55)
    s += f'<circle cx="100" cy="68" r="1.6" fill="{PAPER}" stroke="{INK}" stroke-width=".6"/>'
    s += line('M100 64 V224 M96 70 V224', .7, .9)
    for y in (100, 124, 148, 172, 196, 214):
        s += f'<circle cx="104" cy="{y}" r="1.6" fill="{PAPER}" stroke="{INK}" stroke-width=".6"/>'
    for x0 in (54, 114):
        s += shape(f'M{x0} 106 h32 v22 q-16 5 -32 0Z', .7, PAPER) + line(f'M{x0} 112 h32', .6, .8)
        s += shape(f'M{x0} 168 h32 v26 q-16 5 -32 0Z', .7, PAPER) + line(f'M{x0} 174 h32', .6, .8)
    for x in (62, 70, 78, 122, 130, 138):
        s += line(f'M{x} 134 V162 M{x} 198 V218', .5, .55)
    # puños y pliegues de las mangas
    s += line('M14 190 L35 194 M186 190 L165 194', .7)
    s += line('M28 92 C26 120 24 150 22 176 M172 92 C174 120 176 150 178 176', .45, .5)
    s += line('M46 104 C44 90 40 76 34 66 M154 104 C156 90 160 76 166 66', .5, .55)
    s += line('M46 212 C80 218 120 218 154 212', .5, .5)
    return s

def dress():
    s = hanger(100, 8)
    s += line('M82 54 L72 30 M118 54 L128 30', .7, .8)
    bod = 'M72 52 C80 58 90 78 100 92 C110 78 120 58 128 52 C132 80 128 112 124 128 H76 C72 112 68 80 72 52Z'
    skirt = 'M76 128 C64 190 40 260 24 330 C60 342 140 342 176 330 C160 260 136 190 124 128Z'
    s += f'<path d="{skirt}" fill="{HYD}" opacity=".32" transform="translate(5 3)"/>'
    s += shape(skirt, 1.1, PAPER)
    s += f'<path d="{bod}" fill="{HYD}" opacity=".32" transform="translate(4 3)"/>' + shape(bod, 1.1, PAPER)
    s += line('M76 128 Q100 134 124 128', .8) + line('M98 130 C92 150 86 168 82 186 M102 130 C110 150 116 166 122 182', .7, .8)
    for x0, x1 in ((84, 50), (92, 78), (100, 104), (108, 130), (116, 156)):
        s += line(f'M{x0} 140 C{(x0+x1)/2 - 4} 220 {x1+2} 280 {x1} 334', .5, .55)
    r = random.Random(9)
    for k in range(22):
        y = r.uniform(150, 320); half = 26 + (y-128)*.36
        x = 100 + r.uniform(-half*.8, half*.8)
        s += g(floret(2.4, k), x, y)
    return s

def rum():
    s = shape('M42 8 h16 v26 C58 44 74 48 74 66 V138 Q74 144 68 144 H32 Q26 144 26 138 V66 C26 48 42 44 42 34Z', 1, PAPER, STONE, .5, (3, 2))
    s += shape('M40 2 h20 v10 h-20Z', .8, PAPER) + shape('M30 80 h40 v34 h-40Z', .8, PAPER)
    s += line('M38 92 h24 M42 100 h16', .6, .8) + line('M34 70 V132', .5, .6)
    s += g(olive_branch([(0, 0), (16, -10), (34, -14)], 3, 13, 2.6, 1), 64, 140, -10)
    return s

def cigar():
    s = g(shape('M0 0 H104 Q114 0 114 7 Q114 14 104 14 H0Z', 1, PAPER, STONE, .55, (2, 2))
          + shape('M64 -1 h16 v16 h-16Z', .8, PAPER, HYD, .4, (1, 1)) + line('M68 7 h8', .6)
          + line('M2 0 v14 M30 1 l8 12 M46 1 l8 12 M90 1 l8 12', .45, .6), 14, 92, -24)
    s += line('M18 92 C10 80 22 72 14 60 C8 50 18 42 12 30', .7, .6) + line('M26 86 C22 78 30 72 26 64', .6, .5)
    return s

def cacao():
    pod = 'M50 14 C74 22 88 56 82 92 C78 116 64 134 50 138 C36 134 22 116 18 92 C12 56 26 22 50 14Z'
    s = shape(pod, 1, PAPER, MATCHA, .45, (3, 2))
    for x0, c in ((50, 0), (36, -10), (64, 10), (26, -18), (74, 18)):
        s += line(f'M50 16 C{x0+c} 50 {x0+c*.6} 100 50 136', .55, .7)
    s += line('M50 14 C52 8 56 4 62 2', .9) + g(leaf(30, 6, SAGE, 3), 62, 4, -20)
    return s

SYMBOLS = '\n'.join([
    f'<symbol id="chacabana" viewBox="10 0 184 310">{chacabana()}</symbol>',
    f'<symbol id="dress" viewBox="20 0 165 346">{dress()}</symbol>',
    f'<symbol id="rum" viewBox="22 -2 92 152">{rum()}</symbol>',
    f'<symbol id="cigar" viewBox="8 26 122 85">{cigar()}</symbol>',
    f'<symbol id="cacao" viewBox="13 -15 86 159">{cacao()}</symbol>',
    f'<symbol id="floret" viewBox="-8 -8 16 16">{floret(6.5, 4)}</symbol>',
    f'<symbol id="spray" viewBox="12 -14 303 319">{spray()}</symbol>',
    f'<symbol id="divider" viewBox="4 7 252 27">{sprig_divider()}</symbol>',
    f'<symbol id="olive" viewBox="2 4 319 68">{olive_branch([(6, 60), (80, 44), (160, 38), (240, 30), (294, 22)], 14, 26, 4.2, 3)}</symbol>',
])
