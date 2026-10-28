# Dibujo "a mano": líneas con temblor natural, doble trazo, aguadas de acuarela.
import math, random

INK = '#4f5d45'
PAPER = '#f8f6f1'
STONE = '#e2cfb9'; STONE_D = '#c9b49c'; WOOD = '#b99876'; WOOD_L = '#d3bb9c'
SAGE = '#a8b5a1'; MATCHA = '#8fae6a'; HYD = '#aab6c2'; HYD_L = '#cdd6de'; GLOW = '#f2dfa2'
TERRA = '#d9a98a'

def f(v): return f'{v:.1f}'.rstrip('0').rstrip('.')
def fi(v): return str(int(round(v)))

class Pen:
    ORDER = ('w0', 'f', 'w1', 'd', 'sh', 's')
    def __init__(self, seed=1):
        self.r = random.Random(seed); self.out = []; self.b = {}

    def _add(self, key, d):
        self.b.setdefault(key, []).append(d)

    def flush(self):
        for cat in self.ORDER:
            for key, ds in self.b.items():
                if key[0] != cat: continue
                d = ''.join(ds)
                if cat in ('w0', 'w1'):
                    self.out.append(f'<path d="{d}" fill="{key[1]}" opacity="{key[2]}" filter="url(#wash)"/>')
                elif cat == 'f':
                    self.out.append(f'<path d="{d}" fill="{key[1]}"/>')
                elif cat == 'd':
                    self.out.append(f'<path d="{d}" fill="{key[1]}" opacity="{key[2]}"/>')
                elif cat == 'sh':
                    _, fill, sw, op = key
                    o = f' opacity="{op}"' if op != 1 else ''
                    self.out.append(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"{o}/>')
                else:
                    _, w, op, color = key
                    o = f' opacity="{op}"' if op != 1 else ''
                    self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{o}/>')
        self.b = {}

    def _dense(self, pts, step=6):
        D = [pts[0]]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            L = math.hypot(x2-x1, y2-y1); n = max(1, int(L/step))
            for k in range(1, n+1):
                D.append((x1+(x2-x1)*k/n, y1+(y2-y1)*k/n))
        return D

    def _wobble(self, pts, rough):
        r = self.r; p1, p2, p3 = r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3)
        out = []; s = 0
        for i, (x, y) in enumerate(pts):
            if i: s += math.hypot(x-pts[i-1][0], y-pts[i-1][1])
            a = pts[max(0, i-1)]; b = pts[min(len(pts)-1, i+1)]
            dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
            nx, ny = -dy/L, dx/L
            o = rough*(.55*math.sin(s/31+p1) + .3*math.sin(s/11+p2) + .15*math.sin(s/4.3+p3))
            out.append((x+nx*o, y+ny*o))
        return out

    def _smooth(self, P):
        if len(P) < 3: return f'M{f(P[0][0])} {f(P[0][1])}L{f(P[-1][0])} {f(P[-1][1])}'
        d = f'M{fi(P[0][0])} {fi(P[0][1])}'
        for i in range(1, len(P)-1):
            mx, my = (P[i][0]+P[i+1][0])/2, (P[i][1]+P[i+1][1])/2
            d += f'Q{fi(P[i][0])} {fi(P[i][1])} {fi(mx)} {fi(my)}'
        return d + f'L{fi(P[-1][0])} {fi(P[-1][1])}'

    def stroke(self, pts, w=1, op=1, rough=.7, double=False, over=0, color=INK, step=7):
        if len(pts) < 2: return
        if over:
            (x0, y0), (x1, y1) = pts[0], pts[1]; L = math.hypot(x1-x0, y1-y0) or 1
            a = (x0-(x1-x0)/L*over, y0-(y1-y0)/L*over)
            (x0, y0), (x1, y1) = pts[-1], pts[-2]; L = math.hypot(x1-x0, y1-y0) or 1
            b = (x0-(x1-x0)/L*over, y0-(y1-y0)/L*over)
            pts = [a] + list(pts[1:-1]) + [b] if len(pts) > 2 else [a, b]
        P = self._wobble(self._dense(pts, step), rough)
        self._add(('s', f(w), f(op), color), self._smooth(P))
        if double:
            P2 = self._wobble(self._dense(pts, step), rough*1.5)
            self._add(('s', f(w*.5), f(op*.45), color), self._smooth(P2))

    def line(self, x1, y1, x2, y2, **k): self.stroke([(x1, y1), (x2, y2)], **k)

    def wash(self, pts, color, op=.5, dx=0, dy=0, filt='wash'):
        P = self._wobble(self._dense(list(pts)+[pts[0]], 12), 2.5)
        d = 'M' + 'L'.join(f'{fi(x+dx)} {fi(y+dy)}' for x, y in P) + 'Z'
        self._add(('w0' if (dx or dy) else 'w1', color, f(op)), d)

    def fill(self, pts, color=PAPER):
        if len(pts) < 3: return
        self._add(('f', color), 'M' + 'L'.join(f'{f(x)} {f(y)}' for x, y in pts) + 'Z')

    def dot(self, x, y, r=.8, color=INK, op=1):
        self._add(('d', color, f(op)), circ_d(x, y, r))

    def shape(self, d, fill=PAPER, sw=.5, op=1):
        self._add(('sh', fill, f(sw), f(op)), d)

    def circle(self, x, y, r, fill=PAPER, sw=.5, op=1): self.shape(circ_d(x, y, r), fill, sw, op)

    def leaf(self, x, y, L, ang, w=.38, fill=PAPER, sw=.5, op=1): self.shape(leaf_shape(x, y, L, ang, w), fill, sw, op)

    def raw(self, s): self.flush(); self.out.append(s)

    def svg(self): self.flush(); return ''.join(self.out)

def circ_d(x, y, r):
    return f'M{f(x-r)} {f(y)}a{f(r)} {f(r)} 0 1 0 {f(2*r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2*r)} 0'

    # ---------- formas ----------
def arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx+rx*math.cos(math.radians(a0+(a1-a0)*k/n)), cy+ry*math.sin(math.radians(a0+(a1-a0)*k/n))) for k in range(n+1)]

def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def archway(x0, x1, spring, base):
    cx = (x0+x1)/2; r = (x1-x0)/2
    return [(x0, base)] + arc(cx, spring, r, r, 180, 360) + [(x1, base)]

def catenary(x1, y1, x2, y2, sag, n=20):
    pts = []
    for k in range(n+1):
        t = k/n; x = x1+(x2-x1)*t; y = y1+(y2-y1)*t + sag*4*t*(1-t)
        pts.append((x, y))
    return pts

# ---------- vegetación dibujada ----------
def leaf_shape(x, y, L, ang, w=.38):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    def T(u, v): return (u*ca-v*sa, u*sa+v*ca)
    c1 = T(L*.35, -L*w); c2 = T(L*.75, -L*w*.6); p1 = T(L, 0)
    c3 = T(L*.75-L, L*w*.6); c4 = T(L*.35-L, L*w); p2 = T(-L, 0)
    return (f'M{f(x)} {f(y)}c{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p1[0])} {f(p1[1])}'
            f'c{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(p2[0])} {f(p2[1])}z')

def foliage(pen, cx, cy, rx, ry, n=160, L=(5, 9), wash=SAGE, wash2=MATCHA, seed=1, blossoms=0, bcol=HYD, ink_op=.85):
    """Copa de árbol hecha de muchas hojitas a mano + aguadas suaves."""
    r = random.Random(seed)
    # aguadas en grumos
    for k in range(7):
        a = r.uniform(0, 6.3); t = r.uniform(0, .55)
        x = cx+rx*t*math.cos(a); y = cy+ry*t*math.sin(a)
        pen.wash(arc(x, y, rx*r.uniform(.45, .7), ry*r.uniform(.4, .6), 0, 360, 18)[:-1], wash if k % 3 else wash2, .32)
    leaves = []
    for k in range(n):
        a = r.uniform(0, 6.3); t = math.sqrt(r.uniform(0, 1))
        x = cx+rx*t*math.cos(a); y = cy+ry*t*math.sin(a)
        # más densidad en el borde inferior derecho (sombra)
        if r.random() < .25 and math.sin(a) < 0: continue
        leaves.append((y, x, r.uniform(*L), r.uniform(0, 360)))
    leaves.sort()
    for y, x, l, ang in leaves:
        pen.leaf(x, y, l, ang, sw=.55, op=ink_op)
    for k in range(blossoms):
        a = r.uniform(0, 6.3); t = math.sqrt(r.uniform(0, .9))
        x = cx+rx*t*math.cos(a); y = cy+ry*t*math.sin(a)
        pen.dot(x+.8, y+.8, 2.6, bcol, .55)
        for j in range(5):
            aa = j*72+r.uniform(0, 30)
            pen.leaf(x, y, 3.2, aa, .45, sw=.35)


def crown(pen, cx, cy, rx, ry, seed, wash=SAGE, op=.4, marks=18, ink=.7, blossoms=0, bcol='#e6c9cf'):
    """Copa de árbol estilo toile: contorno festoneado a mano + trazos internos."""
    r = random.Random(seed); n = max(9, int((rx+ry)/10)); base = []
    for i in range(n):
        a0 = math.radians(-90+i*360/n+r.uniform(-6, 6)); k0 = r.uniform(.9, 1.03)
        base.append((cx+rx*k0*math.cos(a0), cy+ry*k0*math.sin(a0)))
    pts = []
    for i in range(n):
        (x0, y0), (x1, y1) = base[i], base[(i+1) % n]
        mx, my = (x0+x1)/2, (y0+y1)/2; dx, dy = mx-cx, my-cy; L = math.hypot(dx, dy) or 1
        seg = math.hypot(x1-x0, y1-y0); bx, by = mx+dx/L*seg*r.uniform(.45, .62), my+dy/L*seg*r.uniform(.45, .62)
        for k in range(6):
            t = k/6; pts.append(((1-t)**2*x0+2*(1-t)*t*bx+t*t*x1, (1-t)**2*y0+2*(1-t)*t*by+t*t*y1))
    pts.append(pts[0])
    pen.wash(pts[:-1], wash, op, 3, 2)
    pen.fill(pts[:-1], PAPER); pen.wash(pts[:-1], wash, op*.8)
    pen.stroke(pts, w=.8, op=ink, rough=.4, step=30)
    for k in range(marks):
        a = r.uniform(-.6, 3.6); t = r.uniform(.25, .85)
        x, y = cx+rx*t*math.cos(a), cy+ry*t*math.sin(a)
        pen.stroke(arc(x, y+3, 5, 4, 200, 340, 5), w=.5, op=ink*.8, rough=.1, step=20)
    for k in range(blossoms):
        a = r.uniform(0, 6.3); t = math.sqrt(r.uniform(0, .8))
        x, y = cx+rx*t*math.cos(a), cy+ry*t*math.sin(a)
        pen.dot(x+.6, y+.6, 2.4, bcol, .6); pen.shape(circ_d(x, y, 1.6), 'none', .35)

def branchy_trunk(pen, x, base, top, spread, seed):
    r = random.Random(seed)
    pen.stroke([(x-5, base), (x-4, base-(base-top)*.4), (x-7, base-(base-top)*.75), (x-14, top)], w=1, double=True)
    pen.stroke([(x+5, base), (x+4, base-(base-top)*.45), (x+9, base-(base-top)*.8), (x+18, top+4)], w=1, double=True)
    for k in range(4):
        y0 = base-(base-top)*r.uniform(.55, .9); sgn = -1 if k % 2 else 1
        pen.stroke([(x+sgn*3, y0), (x+sgn*spread*.4, y0-14), (x+sgn*spread*r.uniform(.6, 1), y0-r.uniform(24, 40))], w=.8)
    for k in range(6):
        y = base-r.uniform(4, (base-top)*.6)
        pen.stroke([(x-3, y), (x+r.uniform(-1, 2), y+3)], w=.5, op=.6)

def palm(pen, x, base, h, lean, seed, fronds=9):
    r = random.Random(seed)
    tx, ty = x+lean, base-h
    spine = [(x+lean*(t**1.6), base-h*t) for t in [k/10 for k in range(11)]]
    L = [(px-4.5+1.2*i/10, py) for i, (px, py) in enumerate(spine)]
    R = [(px+4.5-1.2*i/10, py) for i, (px, py) in enumerate(spine)]
    pen.wash(L+list(reversed(R)), STONE_D, .35, 2, 1)
    pen.fill(L+list(reversed(R)))
    pen.stroke(L, w=.95); pen.stroke(R, w=.95)
    for i in range(1, 30):
        t = i/30; px = x+lean*(t**1.6); py = base-h*t; w = 4.5-1.2*t
        pen.stroke([(px-w, py), (px, py+1.4), (px+w, py)], w=.45, op=.7, rough=.2)
    for k in range(fronds):
        ang = -180+k*(180/(fronds-1))+r.uniform(-8, 8)
        a = math.radians(ang); Ln = r.uniform(48, 66); droop = r.uniform(16, 34)*(1 if abs(ang+90) > 30 else .4)
        ex, ey = tx+Ln*math.cos(a), ty+Ln*math.sin(a)*.55+droop
        mx, my = tx+Ln*.5*math.cos(a), ty+Ln*.5*math.sin(a)*.8-6
        F = [(tx, ty), (mx, my), (ex, ey)]
        pen.stroke(F, w=.8)
        # foliolos
        for j in range(3, 18):
            t = j/18
            px = (1-t)**2*tx+2*(1-t)*t*mx+t*t*ex; py = (1-t)**2*ty+2*(1-t)*t*my+t*t*ey
            ll = 12*(1-t*.55)
            for sg in (-1, 1):
                pen.stroke([(px, py), (px+sg*ll*.35+math.cos(a)*ll*.3, py+ll*.85)], w=.45, op=.8, rough=.3, step=4)
    for k in range(3):
        pen.circle(tx-4+k*4, ty+5+(k % 2)*2, 2.8, WOOD_L)

def grass(pen, x, base, n, seed, h=12, spread=None):
    r = random.Random(seed); spread = spread or n*1.6
    for k in range(n):
        xx = x+r.uniform(-spread, spread); hh = h*r.uniform(.5, 1.1); b = r.uniform(-6, 6)
        pen.stroke([(xx, base), (xx+b*.3, base-hh*.6), (xx+b, base-hh)], w=.5, op=.75, rough=.2, step=4)

def hydrangea_bush(pen, cx, base, w, h, seed, heads=3):
    r = random.Random(seed)
    foliage(pen, cx, base-h*.45, w*.5, h*.5, n=int(w*h/18), L=(5, 8), seed=seed, ink_op=.8)
    for k in range(heads):
        hx = cx+r.uniform(-w*.33, w*.33); hy = base-h*r.uniform(.5, .85); R = r.uniform(11, 14)
        pen.wash(arc(hx, hy, R, R*.9, 0, 360, 16)[:-1], HYD, .5)
        for j in range(int(R*1.4)):
            a = r.uniform(0, 6.3); t = math.sqrt(r.uniform(0, 1))*R*.85
            x, y = hx+t*math.cos(a), hy+t*.9*math.sin(a)
            for q in range(4):
                aa = math.radians(q*90+r.uniform(0, 40))
                pen.leaf(x, y, 3.4, math.degrees(aa), .5, sw=.3, op=.85)

def vine(pen, pts, seed, n_leaves=24, flowers=0):
    r = random.Random(seed)
    pen.stroke(pts, w=.6, op=.85, rough=1.2)
    D = pen._dense(pts, 4)
    for k in range(n_leaves):
        i = r.randrange(len(D)); x, y = D[i]
        pen.leaf(x, y, r.uniform(4, 7), r.uniform(0, 360), .45, sw=.45, op=.9)
        if r.random() < .5: pen.dot(x+1, y+1, 2.2, SAGE, .45)
    for k in range(flowers):
        i = r.randrange(len(D)); x, y = D[i]
        pen.dot(x, y, 2.4, '#e6c9cf', .55)
        pen.shape(circ_d(x, y, 1.6), 'none', .35)

def birds(pen, x, y, n, seed):
    r = random.Random(seed)
    for _ in range(n):
        bx, by, w = x+r.uniform(-30, 30), y+r.uniform(-10, 10), r.uniform(3.5, 5.5)
        pen.stroke([(bx-w, by), (bx-w*.5, by-w*.55), (bx, by), (bx+w*.5, by-w*.55), (bx+w, by)], w=.6, op=.8, rough=.1, step=2)

def cloud(pen, x, y, w, seed):
    r = random.Random(seed); pts = [(x, y)]; cx = x
    while cx < x+w:
        st = r.uniform(12, 22); hh = r.uniform(5, 10)*(1-abs((cx-x)/w-.5))
        pts += arc(cx+st/2, y, st/2, hh, 180, 360, 6)[1:]; cx += st
    pen.stroke(pts, w=.55, op=.5, rough=.3, step=3)

FILTERS = '''<filter id="wash" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="9" result="d"/><feGaussianBlur in="d" stdDeviation="1.1"/></filter>'''


# ======================= IGLESIA REGINA ANGELORUM =======================
def regina_scene():
    pen = Pen(7)
    K = .42; OX, OY = 70, 30
    def P(x, y): return (OX+x*K, OY+y*K)
    def PP(pts): return [P(x, y) for x, y in pts]
    G = 1225; GY = P(0, G)[1]
    r = random.Random(3)

    # cielo
    cloud(pen, 470, 92, 120, 3); cloud(pen, 120, 150, 80, 5); birds(pen, 300, 120, 3, 2)

    # --- aguadas de la fachada ---
    body = [(60, G), (60, 430), (215, 430), (215, 400), (235, 362)] + \
        [(270, 350), (310, 332), (390, 316), (470, 300), (520, 286), (600, 266), (650, 254), (700, 266), (780, 286), (830, 300), (890, 312)] + \
        [(890, 430), (1230, 430), (1230, G)]
    pen.wash(PP(body), STONE, .55, 4, 3)
    pen.fill(PP(body), PAPER)
    pen.wash(PP(body), STONE, .28)
    esp = rect(890, 215, 1185, 430)
    pen.wash(PP(esp), STONE, .55, 4, 3); pen.fill(PP(esp)); pen.wash(PP(esp), STONE, .3)
    cap = [(985, 215), (985, 140)] + arc(1032, 140, 47, 38, 180, 360, 14)[1:-1] + [(1080, 140), (1080, 215)]
    pen.wash(PP(cap), STONE, .5, 3, 2); pen.fill(PP(cap)); pen.wash(PP(cap), STONE, .3)
    # sombras laterales (volumen)
    pen.wash(PP(rect(60, 440, 120, G)), STONE_D, .35)
    pen.wash(PP(rect(1180, 440, 1230, G)), STONE_D, .35)
    pen.wash(PP(rect(1150, 230, 1185, 425)), STONE_D, .35)
    # manchas de piedra envejecida
    for k in range(26):
        x, y = r.uniform(80, 1200), r.uniform(330, 1200)
        pen.wash(PP(arc(x, y, r.uniform(20, 55), r.uniform(10, 28), 0, 360, 10)[:-1]), STONE_D, .18)

    # --- contornos ---
    pen.stroke(PP(body+[body[0]]), w=1.15, double=True, over=1.5)
    pen.stroke(PP([(215, 430), (215, G)]), w=1, double=True)
    pen.stroke(PP([(1120, 430), (1120, G)]), w=1, double=True)
    pen.stroke(PP([(60, 432), (215, 432)]), w=1)
    # cornisa superior buttress
    pen.stroke(PP([(52, 430), (222, 430)]), w=1, over=2)
    pen.stroke(PP([(890, 432), (1238, 432)]), w=1, over=2)

    # espadaña
    pen.stroke(PP(esp+[esp[0]]), w=1.1, double=True)
    pen.stroke(PP([(876, 214), (1198, 214)]), w=1.1, over=3); pen.stroke(PP([(882, 228), (1192, 228)]), w=.7)
    pen.stroke(PP([(896, 362), (1180, 362)]), w=.9, over=2); pen.stroke(PP([(900, 374), (1176, 374)]), w=.6)
    for x0 in (952, 1076):
        op = archway(x0, x0+90, 292, 362)
        pen.wash(PP(op), HYD_L, .55); pen.wash(PP(op), STONE_D, .35, -3, 0)
        pen.stroke(PP(op), w=.95, double=True)
        pen.stroke(PP(arc(x0+45, 292, 58, 58, 185, 355, 16)), w=.6, op=.7)
        bx = x0+45
        bell = [(bx-20, 336), (bx-18, 312), (bx-12, 300), (bx, 297), (bx+12, 300), (bx+18, 312), (bx+20, 336)]
        pen.wash(PP(bell+[(bx, 340)]), '#a89a78', .55)
        pen.stroke(PP(bell), w=.85); pen.stroke(PP([(bx-23, 336), (bx+23, 336)]), w=.85)
        pen.stroke(PP([(bx, 297), (bx, 274)]), w=.6)
        pen.dot(*P(bx, 342), 2.2*K*2)
    pen.stroke(PP(cap+[cap[0]]), w=1.05, double=True)
    small = archway(1012, 1052, 162, 205)
    pen.wash(PP(small), HYD_L, .5); pen.stroke(PP(small), w=.85)
    pen.stroke(PP([(972, 140), (1093, 140)]), w=.8, over=2)
    pen.stroke(PP([(1032, 102), (1032, 78)]), w=.8)
    pen.circle(*P(1032, 74), 2.1, sw=.6)
    # volutas
    pen.stroke(PP([(905, 214), (925, 196), (955, 186), (985, 186)]), w=.8)
    pen.stroke(PP([(1165, 214), (1140, 196), (1110, 186), (1080, 186)]), w=.8)
    pen.stroke(PP(arc(912, 205, 9, 9, 120, 420, 10)), w=.6)
    pen.stroke(PP(arc(1158, 205, 9, 9, -240, 60, 10)), w=.6)

    # cornisa media
    pen.stroke(PP([(158, 700), (1135, 700)]), w=1.1, over=4, double=True)
    pen.stroke(PP([(150, 714), (1142, 714)]), w=.9, over=3)
    pen.stroke(PP([(168, 728), (1126, 728)]), w=.55, op=.7)
    for x in range(176, 1120, 22):
        pen.stroke(PP([(x, 716), (x, 726)]), w=.45, op=.55, rough=.1)
    pen.wash(PP(rect(155, 714, 1140, 735)), STONE_D, .4)

    # pilastras superiores
    for x in (470, 520, 780, 830):
        pen.stroke(PP([(x, 300 if x in (520, 780) else 306), (x, 698)]), w=.8)
    for x0, x1 in ((470, 520), (780, 830)):
        pen.wash(PP(rect(x0+6, 300, x1, 698)), STONE_D, .22)
        pen.stroke(PP([(x0-6, 330), (x1+6, 330)]), w=.6)

    # ventanas con reja
    for x0 in (330, 880):
        win = rect(x0, 546, x0+88, 680)
        pen.wash(PP(win), WOOD, .6); pen.fill([(0, 0)])
        pen.stroke(PP(win+[win[0]]), w=.9, double=True)
        pen.stroke(PP([(x0+44, 548), (x0+44, 620)]), w=.5, op=.7)
        for k in range(1, 7):
            pen.stroke(PP([(x0+k*12.6, 620), (x0+k*12.6, 680)]), w=.5, rough=.1)
        pen.stroke(PP([(x0-4, 620), (x0+92, 620)]), w=.7)
        pen.stroke(PP([(x0-16, 540), (x0+104, 540)]), w=.9, over=2)
        pen.stroke(PP([(x0-10, 688), (x0+98, 688)]), w=.8)
        pen.wash(PP(rect(x0, 546, x0+88, 566)), INK, .18)

    # retablo central
    ret = rect(560, 450, 740, 698)
    pen.wash(PP(ret), STONE, .45, 3, 2)
    pen.stroke(PP(ret+[ret[0]]), w=.95, double=True)
    nic = archway(612, 688, 580, 672)
    pen.wash(PP(nic), HYD_L, .45); pen.wash(PP(nic), STONE_D, .4, -4, 0)
    pen.stroke(PP(nic), w=.85)
    pen.stroke(PP(arc(650, 580, 50, 50, 180, 360, 16)), w=.6, op=.8)
    for k in range(9):
        a = 180+k*22.5
        pen.stroke(PP([(650, 600), (650+32*math.cos(math.radians(a)), 600+32*math.sin(math.radians(a)))]), w=.45, op=.7, rough=.1)
    # columnas estípite
    for xc in (586, 714):
        pen.stroke(PP([(xc-8, 458), (xc-8, 694)]), w=.65); pen.stroke(PP([(xc+8, 458), (xc+8, 694)]), w=.65)
        for y in (500, 540, 590, 640):
            pen.stroke(PP([(xc-12, y), (xc+12, y)]), w=.55)
            pen.stroke(PP(arc(xc, y+14, 10, 12, 200, 340, 6)), w=.45, op=.7)
    pen.stroke(PP([(546, 450), (754, 450)]), w=1, over=3)
    pen.stroke(PP([(552, 438), (748, 438)]), w=.7)
    # frontón curvo partido con figura
    pen.stroke(PP([(568, 436)] + arc(650, 436, 84, 92, 180, 250, 10)[1:]), w=.95, double=True)
    pen.stroke(PP(arc(650, 436, 84, 92, 290, 360, 10)), w=.95, double=True)
    pen.stroke(PP(arc(612, 422, 12, 12, 160, 420, 10)), w=.6); pen.stroke(PP(arc(688, 422, 12, 12, -240, 20, 10)), w=.6)
    fig = [(636, 432), (634, 405), (640, 384), (650, 378), (660, 384), (666, 405), (664, 432)]
    pen.wash(PP(fig), STONE_D, .5); pen.stroke(PP(fig), w=.75)
    pen.circle(*P(650, 368), 10*K, sw=.7)
    pen.stroke(PP([(642, 405), (658, 398)]), w=.5, op=.7)
    # pináculo
    pin = [(640, 300), (644, 272), (650, 262), (656, 272), (660, 300)]
    pen.stroke(PP(pin), w=.8); pen.stroke(PP([(632, 302), (668, 302)]), w=.7)
    pen.circle(*P(650, 256), 1.7, sw=.55)

    # arcos de la planta baja
    for x0, x1 in ((236, 434), (500, 800), (868, 1062)):
        cx = (x0+x1)/2; rr = (x1-x0)/2; sp = 842
        a = archway(x0, x1, sp, G)
        pen.wash(PP(a), STONE_D, .38, -5, 0)
        pen.stroke(PP(a), w=1.05, double=True)
        pen.stroke(PP(arc(cx, sp, rr+22, rr+22, 180, 360, 26)), w=.8)
        # dovelas
        for k in range(1, 12):
            ang = math.radians(180+k*15)
            pen.stroke(PP([(cx+rr*math.cos(ang), sp+rr*math.sin(ang)), (cx+(rr+22)*math.cos(ang), sp+(rr+22)*math.sin(ang))]), w=.5, op=.75, rough=.1)
        # sombra rayada en el intradós
        for k in range(16):
            ang = math.radians(184+k*11.5)
            pen.stroke(PP([(cx+(rr-2)*math.cos(ang), sp+(rr-2)*math.sin(ang)), (cx+(rr-20)*math.cos(ang), sp+(rr-20)*math.sin(ang)+8)]), w=.4, op=.55, rough=.1)
    # pilastras inferiores
    for x0, x1 in ((100, 240), (410, 512), (800, 918), (1090, 1230)):
        pen.stroke(PP([(x0, 856), (x0, 1140)]), w=.95, double=True)
        pen.stroke(PP([(x1, 856), (x1, 1140)]), w=.95, double=True)
        capi = rect(x0-12, 834, x1+12, 856)
        pen.wash(PP(capi), STONE_D, .4); pen.stroke(PP(capi+[capi[0]]), w=.85)
        pen.stroke(PP([(x0-6, 862), (x1+6, 862)]), w=.55, op=.7)
        base = [(x0-10, G), (x0-10, 1150), (x0-4, 1140), (x1+4, 1140), (x1+10, 1150), (x1+10, G)]
        pen.wash(PP(base), STONE_D, .35); pen.stroke(PP(base), w=.85)
        pen.wash(PP(rect(x1-22, 860, x1, 1140)), STONE_D, .22)
    # puerta de madera
    door = rect(530, 846, 774, G)
    pen.wash(PP(door), WOOD, .7, 3, 2); pen.wash(PP(door), WOOD_L, .45)
    pen.stroke(PP(door+[door[0]]), w=1, double=True)
    pen.stroke(PP([(652, 846), (652, G)]), w=.75)
    for x in range(546, 774, 20):
        pen.stroke(PP([(x, 856), (x, G-6)]), w=.4, op=.55, rough=.4)
    for x in range(560, 770, 34):
        for y in (900, 980, 1060, 1140):
            pen.dot(*P(x, y), .7, INK, .7)
    pd = rect(536, 988, 640, G)
    pen.wash(PP(pd), INK, .25); pen.stroke(PP(pd+[pd[0]]), w=.7)
    pen.stroke(PP([(640, 1090), (640, 1110)]), w=1.2)
    # placa
    pl = rect(940, 995, 990, 1058); pen.fill(PP(pl)); pen.stroke(PP(pl+[pl[0]]), w=.6)
    for y in (1010, 1022, 1034, 1046): pen.stroke(PP([(948, y), (982, y)]), w=.35, op=.6, rough=.1)

    # sillares (bloques irregulares)
    zones = [(66, 210, 444, 1135), (240, 465, 362, 530), (430, 466, 540, 692), (836, 884, 330, 692), (1126, 1222, 444, 1135),
             (246, 326, 552, 692), (424, 462, 552, 692), (900, 1110, 382, 426), (910, 1080, 236, 356), (244, 428, 960, 1220), (874, 1056, 960, 1220),
             (970, 1110, 444, 692), (528, 556, 456, 692), (744, 776, 456, 692)]
    for x0, x1, y0, y1 in zones:
        y = y0+r.uniform(10, 24)
        while y < y1-6:
            x = x0+r.uniform(0, 24)
            while x < x1-16:
                w = r.uniform(36, 80)
                if r.random() < .62:
                    pen.stroke(PP([(x+2, y), (min(x1, x+w)-2, y+r.uniform(-1.5, 1.5))]), w=.45, op=.6, rough=.35, step=5)
                if r.random() < .35 and x+w < x1:
                    pen.stroke(PP([(x+w, y), (x+w+r.uniform(-1, 1), y+r.uniform(18, 28))]), w=.4, op=.5, rough=.1)
                x += w+r.uniform(3, 10)
            y += r.uniform(24, 34)
    # pequeños huecos de mechinales (como en la foto)
    for x, y in ((150, 470), (150, 540), (150, 610), (290, 420), (300, 500), (460, 360), (840, 360), (1140, 470), (1140, 540), (1140, 610), (1000, 470), (1000, 540)):
        pen.dot(*P(x, y), 1.1, INK, .55)

    # suelo
    pen.stroke([(0, GY), (800, GY)], w=1, over=0, double=True)
    pen.stroke([(-10, GY+9), (810, GY+9)], w=.6, op=.7)
    for k in range(60):
        x = r.uniform(0, 800); y = r.uniform(GY+14, GY+40)
        pen.stroke(arc(x, y, r.uniform(2, 5), r.uniform(1, 2.2), 0, 360, 8), w=.4, op=.4, rough=.1, step=20)

    # árbol de la izquierda (como en la foto 2)
    pen.flush()
    branchy_trunk(pen, 46, GY+2, 330, 70, 11)
    for k, (cx, cy, rx, ry) in enumerate(((10, 300, 70, 52), (80, 280, 64, 50), (40, 230, 72, 54), (-30, 250, 50, 46), (110, 330, 46, 36), (60, 190, 50, 36), (-10, 345, 50, 34))):
        foliage(pen, cx, cy, rx, ry, n=int(rx*ry/34), L=(6, 10), seed=12+k, blossoms=7, bcol='#e6c9cf')
    # enredadera sobre la esquina
    vine(pen, [P(215, 520), P(205, 640), P(222, 760), P(210, 880), P(224, 1000)], 21, 26, 4)
    vine(pen, [P(1120, 560), P(1128, 700), P(1116, 820), P(1124, 940)], 22, 18, 0)
    # arbustos, hortensias y macetas
    hydrangea_bush(pen, 150, GY+6, 130, 46, 31, 4)
    hydrangea_bush(pen, 610, GY+6, 120, 42, 32, 3)
    grass(pen, 300, GY+2, 12, 1); grass(pen, 470, GY+2, 8, 2); grass(pen, 700, GY+4, 10, 3)
    for x in (282, 472):
        pot = [(x-9, GY-20), (x+9, GY-20), (x+7, GY), (x-7, GY)]
        pen.wash(pot, TERRA, .55); pen.fill(pot, PAPER); pen.wash(pot, TERRA, .45); pen.stroke(pot+[pot[0]], w=.8)
        foliage(pen, x, GY-30, 14, 12, n=40, L=(4, 6), seed=x, ink_op=.8)
    return pen.svg()


# ======================= COUNTRY GARDEN =======================
def chair(pen, x, base, s=1, facing=1):
    h = 34*s; w = 12*s
    pen.stroke([(x, base), (x+1*s, base-14*s)], w=.6); pen.stroke([(x+w, base), (x+w-1*s, base-14*s)], w=.6)
    pen.stroke([(x-1*s, base-14*s), (x+w+1*s, base-14*s)], w=.7)
    bx = x+(w if facing > 0 else 0)
    pen.stroke([(x, base-14*s), (x+1*s, base-h)], w=.6); pen.stroke([(x+w, base-14*s), (x+w-1*s, base-h)], w=.6)
    pen.stroke([(x+1*s, base-h), (x+w-1*s, base-h)], w=.6)
    pen.stroke([(x+1.5*s, base-h+2*s), (x+w-1.5*s, base-17*s)], w=.4, op=.85); pen.stroke([(x+w-1.5*s, base-h+2*s), (x+1.5*s, base-17*s)], w=.4, op=.85)
    pen.wash(rect(x-1, base-h, x+w+1, base), WOOD_L, .35)

def centerpiece(pen, x, y, seed, s=1):
    r = random.Random(seed)
    foliage(pen, x, y-7*s, 15*s, 8*s, n=int(36*s), L=(3, 5), seed=seed, ink_op=.8)
    for k in range(5):
        fx, fy = x+r.uniform(-11, 11)*s, y-r.uniform(4, 12)*s
        pen.dot(fx+.6, fy+.6, 3.2*s, HYD if k % 2 else '#efe4d6', .55)
        pen.circle(fx, fy, 2.6*s, sw=.4)
        pen.shape(circ_d(fx, fy, 1*s), 'none', .3)

def lantern(pen, x, base, h=30):
    body = [(x-6, base), (x-5, base-h*.7), (x, base-h), (x+5, base-h*.7), (x+6, base)]
    pen.wash([(x-9, base), (x, base-h-6), (x+9, base)], GLOW, .45)
    pen.stroke(body, w=.75); pen.stroke([(x-6, base), (x+6, base)], w=.75)
    pen.stroke([(x, base-h), (x, base-h-4)], w=.6)
    pen.shape(f'M{f(x-1.6)} {f(base-11)}h3.2v8h-3.2z', PAPER, .4)
    pen.dot(x, base-13, 1.2, '#e6b85c', .9)

def truss(pen, pts, depth=7, n=None, w=.8):
    (x1, y1), (x2, y2) = pts
    L = math.hypot(x2-x1, y2-y1); ux, uy = (x2-x1)/L, (y2-y1)/L; nx, ny = -uy, ux
    a1 = (x1, y1); a2 = (x2, y2); b1 = (x1+nx*depth, y1+ny*depth); b2 = (x2+nx*depth, y2+ny*depth)
    pen.stroke([a1, a2], w=w); pen.stroke([b1, b2], w=w)
    n = n or int(L/10)
    zz = []
    for k in range(n+1):
        t = k/n; p = (x1+ux*L*t, y1+uy*L*t)
        zz.append(p if k % 2 == 0 else (p[0]+nx*depth, p[1]+ny*depth))
    pen.stroke(zz, w=.4, op=.7, rough=.05, step=20)

def garden_scene():
    pen = Pen(19); r = random.Random(5)
    GY = 470
    cloud(pen, 300, 70, 110, 4); birds(pen, 560, 70, 3, 7)
    # árboles de fondo
    for cx, cy, rx, ry, sd in ((60, 300, 90, 70, 1), (190, 280, 80, 66, 2), (330, 300, 84, 64, 3), (470, 284, 86, 66, 4), (610, 300, 84, 64, 5), (750, 284, 86, 70, 6),
                               (120, 350, 80, 46, 7), (400, 352, 90, 44, 8), (680, 350, 90, 46, 9)):
        crown(pen, cx, cy, rx, ry, sd+50, SAGE, .38, marks=int(rx/5), ink=.55, blossoms=8 if sd % 3 == 0 else 0)
    pen.flush()
    # seto bajo y plantas al fondo
    for k, x in enumerate(range(270, 700, 36)):
        crown(pen, x, 394, 22, 13, 200+k, MATCHA, .4, marks=4, ink=.75)
    # palmeras reales de fondo
    palm(pen, 175, 420, 300, 10, 61, 9)
    palm(pen, 690, 420, 280, -14, 62, 9)
    # edificio del club a la derecha (techo verde)
    roof = [(700, 330), (760, 296), (820, 330)]
    pen.wash(roof+[(820, 334), (700, 334)], MATCHA, .5); pen.stroke(roof+[(700, 330)], w=.8)
    for x in range(708, 818, 7): pen.stroke([(x, 330), (x+(760-x)*.12, 326)], w=.35, op=.5, rough=.05)
    pen.stroke([(708, 334), (708, 400)], w=.7); pen.stroke([(812, 334), (812, 400)], w=.7)
    # muro de piedra a la izquierda
    wall = rect(0, 392, 250, 440)
    pen.wash(wall, '#9fa6a0', .45); pen.stroke(wall[:3], w=.8, over=0)
    for k in range(40):
        x, y = r.uniform(4, 244), r.uniform(396, 436)
        pen.stroke(arc(x, y, r.uniform(5, 10), r.uniform(3, 5), 0, 360, 8), w=.4, op=.55, rough=.2)
    # escalera con baranda a la derecha
    for k in range(6):
        pen.stroke([(690+k*10, 440-k*9), (760, 440-k*9)], w=.55, op=.8)
    pen.stroke([(684, 430), (744, 378)], w=.7); pen.stroke([(684, 412), (744, 360)], w=.6)
    for k in range(6): pen.stroke([(688+k*10, 427-k*8.7), (688+k*10, 409-k*8.7)], w=.4, op=.7)

    # ---------- carpa ----------
    ridge_y = 120; eave_y = 220; L, Rx = 40, 760; C = 400
    roofpoly = [(L-10, eave_y), (C, ridge_y), (Rx+10, eave_y)]
    pen.wash(roofpoly, HYD_L, .45)
    pen.fill(roofpoly, 'rgba(248,246,241,.55)')
    # luces colgantes: hileras de guirnaldas bajo el techo
    for t in (.18, .36, .54, .72, .9):
        y = ridge_y+(eave_y-ridge_y)*t+10; xl = C-(C-L)*t; xr = C+(Rx-C)*t
        n = max(2, int((xr-xl)/85)); seg = (xr-xl)/n
        for k in range(n):
            pts = catenary(xl+seg*k, y, xl+seg*(k+1), y, 9+t*6, 12)
            pen.stroke(pts, w=.4, op=.6, rough=.1, step=10)
            for j in range(1, 12, 2):
                x, yy = pts[j]
                pen.dot(x, yy+3.4, 3.4, GLOW, .5)
                pen.leaf(x, yy+1, 4, 90, .42, sw=.35)
    # cerchas
    truss(pen, [(L-14, eave_y), (C, ridge_y)], 7, 40)
    truss(pen, [(C, ridge_y), (Rx+14, eave_y)], 7, 40)
    truss(pen, [(L-14, eave_y+6), (Rx+14, eave_y+6)], 7, 76)
    for x in (L, 220, 580, Rx):
        pass
    # columnas (forradas de verde, como en la foto)
    for x in (L, 230, 570, Rx):
        col = rect(x-6, eave_y+13, x+6, GY)
        pen.wash(col, MATCHA, .5); pen.fill(col, PAPER); pen.wash(col, SAGE, .55)
        pen.stroke([(x-6, eave_y+13), (x-6, GY)], w=.85); pen.stroke([(x+6, eave_y+13), (x+6, GY)], w=.85)
        for y in range(int(eave_y+18), GY-4, 7):
            pen.leaf(x-4+r.uniform(0, 6), y, 4, r.uniform(0, 360), fill='none', sw=.35, op=.6)
    # palmera dentro de la carpa (tronco atraviesa)
    trunk = [(498, GY), (500, 300), (503, ridge_y+40)]
    for dx in (-6, 6):
        pen.stroke([(x+dx*(1-(GY-y)/700), y) for x, y in trunk], w=.9)
    pen.wash([(492, GY), (497, ridge_y+40), (509, ridge_y+40), (506, GY)], STONE_D, .4)
    for y in range(ridge_y+46, GY, 9):
        pen.stroke([(494, y), (500, y+2), (507, y)], w=.4, op=.65, rough=.1)

    pen.flush()
    # escenario blanco al fondo con arco de celosía (como en la foto)
    stg = rect(300, 340, 470, 416)
    pen.wash(stg, '#e8e4dc', .6, 2, 2); pen.fill(stg); pen.stroke(stg+[stg[0]], w=.9)
    op = rect(316, 356, 454, 416)
    pen.wash(op, SAGE, .55); pen.stroke(op+[op[0]], w=.6, op=.8)
    pen.flush()
    for x in range(326, 450, 22):
        crown(pen, x, 396, 14, 18, 700+x, MATCHA, .35, marks=3, ink=.6)
    pen.flush()
    for x in (360, 385, 410):
        pen.stroke([(x, 356), (x, 370)], w=.4, op=.7); pen.dot(x, 373, 2.6, GLOW, .85)
    ar = [(488, 418), (488, 372)] + arc(510, 372, 22, 26, 180, 360, 12)[1:] + [(532, 418)]
    pen.wash(ar, '#efe9df', .7); pen.stroke(ar, w=.9, double=True)
    for k2 in range(5):
        pen.stroke([(490+k2*9, 418), (490+k2*9+10, 360)], w=.35, op=.5, rough=.1)
        pen.stroke([(530-k2*9, 418), (530-k2*9-10, 360)], w=.35, op=.5, rough=.1)
    pen.flush()
    # árboles en macetas de barro y setos bajos
    for x, s, sd in ((150, 1.1, 301), (262, .85, 302), (590, .9, 303), (690, 1.1, 304)):
        base = 470; h = 26*s
        pot = [(x-15*s, base-h), (x+15*s, base-h), (x+11*s, base), (x-11*s, base)]
        pen.wash(pot, TERRA, .65, 2, 1); pen.fill(pot); pen.wash(pot, TERRA, .5); pen.stroke(pot+[pot[0]], w=.85)
        pen.stroke([(x-16*s, base-h+4), (x+16*s, base-h+4)], w=.5)
        pen.stroke([(x-1, base-h), (x-2, base-h-40*s)], w=.8); pen.stroke([(x+2, base-h), (x+1, base-h-40*s)], w=.8)
        crown(pen, x, base-h-56*s, 30*s, 26*s, sd, MATCHA, .45, marks=8)
        pen.flush()
    for x0, x1 in ((200, 330), (450, 620)):
        for x in range(x0, x1, 26):
            crown(pen, x, 456, 16, 10, 400+x, SAGE, .45, marks=3, ink=.7)
    pen.flush()
    # faroles en el césped
    for x in (70, 290, 380, 610, 730):
        lantern(pen, x, GY+8, 28)
    # césped
    pen.wash([(0, GY), (800, GY), (800, 520), (0, 520)], MATCHA, .32)
    pen.stroke([(0, GY+2), (800, GY+2)], w=.6, op=.6)
    for k in range(260):
        x, y = r.uniform(0, 800), r.uniform(GY+8, 515)
        pen.stroke([(x, y), (x+r.uniform(-1.5, 1.5), y-r.uniform(3, 6))], w=.4, op=.5, rough=0, step=10)
    # primer plano: tinaja de barro, maceta con gramíneas, bola de boj
    jar = [(40, 518)] + [(40+22*math.sin(t*math.pi)*1.0-0, 518-t*58) for t in []]
    jar = [(30, 518), (18, 498), (16, 480), (24, 466), (32, 460), (34, 452), (52, 452), (54, 460), (62, 466), (70, 480), (68, 498), (56, 518)]
    pen.wash(jar, TERRA, .6, 3, 2); pen.fill(jar, PAPER); pen.wash(jar, TERRA, .5)
    pen.stroke(jar+[jar[0]], w=.9, double=True)
    for y in (470, 480, 490, 500): pen.stroke([(22, y), (64, y)], w=.35, op=.55, rough=.3)
    pot = [(92, 520), (88, 490), (126, 490), (122, 520)]
    pen.wash(pot, TERRA, .6); pen.fill(pot, PAPER); pen.wash(pot, TERRA, .45); pen.stroke(pot+[pot[0]], w=.85)
    grass(pen, 107, 490, 26, 9, h=48, spread=14)
    ball = arc(760, 492, 30, 26, 0, 360, 18)[:-1]
    pot2 = [(740, 522), (736, 506), (784, 506), (780, 522)]
    pen.wash(pot2, TERRA, .55); pen.stroke(pot2+[pot2[0]], w=.8)
    foliage(pen, 760, 486, 28, 22, n=110, L=(3, 5), seed=88, ink_op=.85)
    hydrangea_bush(pen, 640, 522, 110, 36, 91, 3)
    hydrangea_bush(pen, 200, 524, 120, 34, 92, 3)
    grass(pen, 330, 520, 14, 93, h=12); grass(pen, 470, 520, 12, 94, h=12)
    return pen.svg()


def svg_scene(content, vb, label, cls, mid):
    x, y, w, h = map(float, vb.split())
    m = (f'<linearGradient id="{mid}h" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".07" stop-color="#fff"/><stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
         f'<linearGradient id="{mid}v" x1="0" x2="0" y1="0" y2="1"><stop offset=".88" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
         f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{mid}h)"/></mask>')
    return f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="{label}"><defs>{FILTERS}{m}</defs><g mask="url(#{mid})">{content}</g></svg>'

REGINA = svg_scene(regina_scene(), '-80 40 860 540', 'Dibujo de la Iglesia y Convento Regina Angelorum', 'scene', 'mkR')
GARDEN = svg_scene(garden_scene(), '0 40 800 488', 'Dibujo de la carpa del Country Garden con luces colgantes', 'scene', 'mkG')

if __name__ == '__main__':
    open('/home/claude/shots/sk.html', 'w').write(f'<html><body style="margin:0;background:{PAPER}"><div style="width:900px;padding:20px">{REGINA}<br>{GARDEN}</div></body></html>')


# ======================= HOTELES (tarjetas en arco, 300x375) =======================
def sky(pen, top=0, bottom=200, col=HYD_L, op=.35):
    pen.wash([(-20, top), (320, top), (320, bottom), (-20, bottom)], col, op)

def hotel_jw():
    pen = Pen(31); r = random.Random(2)
    sky(pen, 0, 260); cloud(pen, 200, 70, 60, 3); birds(pen, 70, 60, 2, 4)
    pen.flush()
    # torre
    T = [(92, 300), (92, 74), (138, 40), (214, 92), (214, 300)]
    pen.wash(T, HYD, .55, 3, 2); pen.fill(T); pen.wash(T, HYD_L, .7)
    pen.wash([(176, 60), (214, 92), (214, 300), (176, 300)], HYD, .35)
    pen.stroke(T+[T[0]], w=1, double=True)
    # corona de lamas inclinada
    for k in range(9):
        y = 74-k*3.6; x0 = 92+k*5.1
        pen.stroke([(x0, y), (x0+76-k*1.2, y+52-k*1.0)], w=.45, op=.75, rough=.1, step=30)
    pen.stroke([(92, 74), (214, 92)], w=.8)
    # pisos y parteluces
    for k in range(18):
        y = 100+k*11
        pen.stroke([(92, y), (214, y)], w=.45, op=.75, rough=.25, step=20)
    for x in range(100, 214, 13):
        pen.stroke([(x, 92+(x-92)*.05), (x, 300)], w=.35, op=.5, rough=.2, step=30)
    pen.flush()
    # caja volada
    box = rect(78, 168, 150, 206)
    pen.wash(box, HYD, .45); pen.fill(box); pen.wash(box, HYD_L, .6)
    pen.stroke(box+[box[0]], w=.9); pen.stroke([(84, 180), (146, 180)], w=.4, op=.6); pen.stroke([(84, 192), (146, 192)], w=.4, op=.6)
    pen.flush()
    # podio (Blue Mall)
    pod = rect(30, 228, 286, 330)
    pen.wash(pod, STONE, .5, 3, 2); pen.fill(pod); pen.wash(pod, '#e7e3dc', .6)
    pen.stroke(pod+[pod[0]], w=1, double=True)
    pen.stroke([(22, 228), (294, 228)], w=1, over=2); pen.stroke([(24, 236), (292, 236)], w=.6)
    glass = rect(36, 240, 280, 262)
    pen.wash(glass, HYD, .5); pen.stroke(glass+[glass[0]], w=.6)
    for x in range(52, 280, 22): pen.stroke([(x, 240), (x, 262)], w=.4, op=.7)
    pen.stroke([(30, 270), (286, 270)], w=.8)
    for x in range(44, 286, 26):
        pen.stroke([(x, 274), (x, 330)], w=.55, op=.8)
        pen.wash([(x+3, 280), (x+22, 280), (x+22, 326), (x+3, 326)], '#d8cfbf', .45)
        pen.dot(x+12, 284, 2.6, GLOW, .55)
    pen.flush()
    # palmeras y suelo
    for x, h, ln in ((26, 150, 6), (280, 136, -6)):
        palm(pen, x, 344, h, ln, x, 7); pen.flush()
    pen.stroke([(-10, 340), (310, 340)], w=.9, double=True)
    pen.wash([(-10, 340), (310, 340), (310, 380), (-10, 380)], '#bfc6c9', .35)
    for x in range(10, 300, 22): pen.stroke([(x, 360), (x+12, 360)], w=.8, op=.5, rough=.1)
    hydrangea_bush(pen, 70, 352, 80, 22, 41, 2); hydrangea_bush(pen, 240, 352, 80, 22, 42, 2)
    return pen.svg()

def hotel_emb():
    pen = Pen(33); r = random.Random(3)
    sky(pen, 0, 220); cloud(pen, 40, 60, 60, 5); birds(pen, 230, 50, 3, 6)
    pen.flush()
    # bloque central alto con letrero
    top = rect(120, 88, 236, 104); pen.wash(top, STONE, .5); pen.fill(top); pen.wash(top, STONE, .45); pen.stroke(top+[top[0]], w=.8)
    pen.flush()
    # alas largas
    wing = rect(-10, 140, 310, 196)
    pen.wash(wing, STONE, .5, 3, 2); pen.fill(wing); pen.wash(wing, '#efe6d6', .6)
    pen.stroke(wing[:2], w=.9); pen.stroke(wing[2:], w=.9)
    for y in (152, 164, 176, 188):
        pen.stroke([(-10, y), (310, y)], w=.5, op=.8, rough=.3, step=20)
        for x in range(-6, 310, 9):
            pen.wash([(x, y-9), (x+6, y-9), (x+6, y-1), (x, y-1)], HYD, .35) if False else None
    for x in range(-4, 310, 10): pen.stroke([(x, 142), (x, 194)], w=.3, op=.45, rough=.2, step=30)
    pen.flush()
    # cuerpo central
    mid = rect(70, 104, 248, 200)
    pen.wash(mid, STONE, .55, 3, 2); pen.fill(mid); pen.wash(mid, '#efe6d6', .6)
    pen.stroke(mid+[mid[0]], w=1, double=True)
    for y in range(114, 196, 11):
        pen.wash([(74, y), (244, y), (244, y+6), (74, y+6)], HYD, .4)
        pen.stroke([(70, y+7), (248, y+7)], w=.45, op=.8, rough=.3, step=20)
    for x in range(78, 248, 12): pen.stroke([(x, 108), (x, 198)], w=.3, op=.5, rough=.2, step=30)
    # banderas
    for x in range(100, 220, 6):
        pen.stroke([(x, 214), (x, 196)], w=.4, op=.7, rough=0)
        pen.wash([(x, 196), (x+5, 197), (x+5, 202), (x, 201)], [HYD, TERRA, MATCHA, GLOW][x % 4], .6)
    pen.flush()
    # árboles y palmas
    crown(pen, 30, 210, 46, 36, 81, SAGE, .45, marks=10)
    crown(pen, 272, 206, 48, 40, 82, SAGE, .45, marks=10)
    pen.flush()
    pen.flush()
    palm(pen, 22, 300, 150, 10, 84, 8)
    palm(pen, 286, 296, 120, -8, 85, 7)
    pen.flush()
    # césped y seto al frente
    pen.wash([(-10, 236), (310, 236), (310, 380), (-10, 380)], MATCHA, .3)
    pen.stroke([(-10, 238), (310, 238)], w=.6, op=.6)
    grass(pen, 70, 300, 14, 95, h=10, spread=50); grass(pen, 230, 310, 14, 96, h=10, spread=50); grass(pen, 150, 345, 12, 97, h=9, spread=60)
    hydrangea_bush(pen, 60, 270, 90, 24, 98, 2); hydrangea_bush(pen, 250, 270, 90, 24, 99, 2)
    return pen.svg()

def hotel_kim():
    pen = Pen(35); r = random.Random(4)
    # edificios laterales con balcones de madera
    for side in (-1, 1):
        x0, x1 = (0, 70) if side < 0 else (230, 300)
        b = rect(x0, 0, x1, 300)
        pen.wash(b, TERRA, .45, 0, 0); pen.wash(b, WOOD_L, .45)
        for y in range(20, 220, 38):
            pen.stroke([(x0, y), (x1, y)], w=.8)
            for x in range(int(x0)+4, int(x1), 5): pen.stroke([(x, y+3), (x, y+20)], w=.35, op=.75, rough=.1, step=30)
            pen.stroke([(x0, y+20), (x1, y+20)], w=.6)
        ax = 6 if side < 0 else 248
        a = archway(ax, ax+46, 248, 310)
        pen.wash(a, '#8f6f58', .5); pen.stroke(a, w=.9, double=True)
        pen.stroke([(x1 if side < 0 else x0, 0), (x1 if side < 0 else x0, 310)], w=.9)
    pen.flush()
    # fondo: edificio con lamas
    back = rect(90, 40, 210, 160)
    pen.wash(back, '#e8e2d6', .6); pen.stroke(back+[back[0]], w=.7, op=.8)
    for y in range(50, 160, 10): pen.stroke([(90, y), (210, y)], w=.35, op=.6, rough=.2, step=20)
    pen.flush()
    # árboles grandes
    for x, sd in ((110, 1), (196, 2)):
        pen.stroke([(x-4, 240), (x-3, 160), (x-8, 90)], w=1, double=True); pen.stroke([(x+4, 240), (x+5, 160), (x+10, 92)], w=1, double=True)
        for k in range(5):
            xx = x+r.uniform(-14, 14); pen.stroke([(xx, 90), (xx+r.uniform(-3, 3), 210)], w=.4, op=.6)
    pen.flush()
    crown(pen, 150, 70, 120, 56, 91, SAGE, .45, marks=24)
    pen.flush()
    crown(pen, 60, 130, 50, 36, 92, MATCHA, .4, marks=8)
    crown(pen, 244, 120, 50, 40, 93, MATCHA, .4, marks=8)
    pen.flush()
    # escalinata en perspectiva
    top_y, bot_y = 168, 300
    for k in range(15):
        t = k/14; y = top_y+(bot_y-top_y)*t; hw = 18+46*t
        pen.stroke([(150-hw, y), (150+hw, y)], w=.65, op=.9, rough=.2, step=15)
    st = [(132, top_y), (168, top_y), (214, bot_y), (86, bot_y)]
    pen.wash(st, STONE, .55); pen.stroke([st[0], st[3]], w=.9); pen.stroke([st[1], st[2]], w=.9)
    pen.stroke([(126, 172), (78, 282)], w=.6, op=.8); pen.stroke([(174, 172), (222, 282)], w=.6, op=.8)
    pen.flush()
    # jardineras escalonadas
    for side in (-1, 1):
        for k, (yt, w_) in enumerate(((200, 40), (240, 52))):
            x_in = 150+side*(30+(yt-top_y)*.35); x_out = x_in+side*w_
            pl = [(x_in, yt), (x_out, yt), (x_out, yt+30), (x_in, yt+30)]
            pen.wash(pl, '#efe6d6', .7); pen.stroke(pl+[pl[0]], w=.8)
            crown(pen, (x_in+x_out)/2, yt-6, w_*.6, 14, 100+k+side*10, MATCHA, .4, marks=5)
            pen.flush()
    pen.flush()
    # piso con sombras de hojas
    floor = [(-10, 300), (310, 300), (310, 380), (-10, 380)]
    pen.wash(floor, STONE, .5)
    for k in range(26):
        x, y = r.uniform(0, 300), r.uniform(306, 370)
        pen.wash(arc(x, y, r.uniform(6, 14), r.uniform(2, 4), 0, 360, 8)[:-1], STONE_D, .4)
    pen.stroke([(-10, 300), (310, 300)], w=.8)
    pen.flush()
    # macetas de barro con plantas
    for x, s in ((44, 1), (100, .8), (206, .8), (258, 1)):
        h = 34*s; w = 14*s
        pot = [(x-w, 330-h), (x+w, 330-h), (x+w*.75, 330), (x-w*.75, 330)]
        pen.wash(pot, TERRA, .7, 2, 1); pen.fill(pot); pen.wash(pot, TERRA, .6); pen.stroke(pot+[pot[0]], w=.85)
        pen.stroke([(x-w-1, 330-h+4), (x+w+1, 330-h+4)], w=.5)
        for k in range(7):
            a = -160+k*24+r.uniform(-8, 8)
            pen.leaf(x, 330-h-2, 18*s*r.uniform(.8, 1.2), a, .32, sw=.5)
            pen.dot(x+math.cos(math.radians(a))*10*s, 330-h-2+math.sin(math.radians(a))*10*s, 4*s, MATCHA, .35)
    return pen.svg()

def hotel_svg(content, mid, vb='0 0 300 375'):
    return '<svg viewBox="' + vb + '" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs>' + FILTERS + '</defs>' + content + '</svg>'

HOTEL_JW = hotel_svg(hotel_jw(), 'h1')
HOTEL_EMB = hotel_svg(hotel_emb(), 'h2', '38 30 220 275')
HOTEL_KIM = hotel_svg(hotel_kim(), 'h3')

if __name__ == '__main__':
    open('/home/claude/shots/hot.html', 'w').write(f'<html><body style="margin:0;background:{PAPER};display:flex;gap:20px;padding:20px">' + ''.join(f'<div style="width:300px;height:375px;border-radius:150px 150px 4px 4px;overflow:hidden;background:#e7ebee">{h}</div>' for h in (HOTEL_EMB, HOTEL_KIM, HOTEL_JW)) + '</body></html>')


def walkway():
    """Senderito de jardín con lajas de piedra, bordeado de flores y faroles."""
    pen = Pen(57); r = random.Random(8)
    C = [(150, 6), (170, 40), (240, 70), (360, 84), (480, 92), (580, 112), (640, 150)]
    D = pen._dense(C, 3)
    def off(i, d):
        a_ = D[max(0, i-1)]; b_ = D[min(len(D)-1, i+1)]
        dx, dy = b_[0]-a_[0], b_[1]-a_[1]; L = math.hypot(dx, dy) or 1
        return (D[i][0]-dy/L*d, D[i][1]+dx/L*d)
    W = lambda i: 9+8*(i/len(D))
    left = [off(i, -W(i)) for i in range(len(D))]; right = [off(i, W(i)) for i in range(len(D))]
    pen.wash(left[::3]+right[::-3], STONE, .45)
    pen.flush()
    # lajas
    i = 4
    while i < len(D)-4:
        x, y = D[i]; s = .7+.6*(i/len(D)); rr = random.Random(i)
        st = [(x+math.cos(t)*7*s*rr.uniform(.8, 1.15), y+math.sin(t)*4.2*s*rr.uniform(.8, 1.15)) for t in [k2*math.pi/4 for k2 in range(8)]]
        pen.wash(st, STONE_D, .55); pen.fill(st, '#f1ebe1'); pen.stroke(st+[st[0]], w=.7, rough=.3, step=3)
        i += int(7+5*s)
    pen.flush()
    # bordes de hierba
    for side in (left, right):
        for j in range(2, len(side)-2, 5):
            x, y = side[j]
            pen.stroke([(x, y+3), (x-1.5, y-3)], w=.45, op=.7, rough=0); pen.stroke([(x+2, y+3), (x+3, y-2)], w=.45, op=.7, rough=0)
    pen.flush()
    # macizos de flores y hortensias
    for x, y, sd in ((120, 40, 1), (250, 46, 2), (330, 110, 3), (450, 64, 4), (520, 128, 5), (660, 112, 6)):
        crown(pen, x, y, 18, 11, 600+sd, SAGE, .4, marks=3, ink=.7)
        pen.flush()
        for q in range(3):
            fx, fy = x+r.uniform(-12, 12), y-r.uniform(2, 8)
            pen.dot(fx+.6, fy+.6, 3.6, HYD if (sd+q) % 2 else '#efe4d6', .55)
            for p5 in range(5): pen.leaf(fx, fy, 3.4, p5*72+r.uniform(0, 20), .5, sw=.35)
        pen.flush()
    # faroles
    for x, y in ((205, 30), (540, 140)):
        pen.stroke([(x, y+6), (x, y-22)], w=.8); pen.stroke([(x, y-22), (x+8, y-24)], w=.6)
        pen.dot(x+8, y-17, 5, GLOW, .5)
        lb = [(x+5, y-20), (x+11, y-20), (x+12, y-13), (x+4, y-13)]
        pen.fill(lb); pen.stroke(lb+[lb[0]], w=.55)
    # mariposa
    pen.stroke([(400, 30), (396, 26), (400, 28), (404, 26), (400, 30)], w=.6, op=.8, rough=0, step=2)
    return '<svg viewBox="90 -14 600 180" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><defs>' + FILTERS + '</defs>' + pen.svg() + '</svg>'

WALK = walkway()
