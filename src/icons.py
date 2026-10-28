# Íconos dibujados a mano (100x100) para los recuadros del inicio y "Bueno saber".
import math, random
from sketch import Pen, arc, rect, PAPER, INK, STONE, STONE_D, WOOD, WOOD_L, SAGE, MATCHA, HYD, HYD_L, GLOW, TERRA, FILTERS, leaf_shape

def _done(pen, name):
    return f'<symbol id="{name}" viewBox="0 0 100 100">{pen.svg()}</symbol>'

def church():
    p = Pen(101)
    body = [(22, 86), (22, 46), (30, 40), (42, 36), (50, 30), (58, 36), (68, 40), (68, 86)]
    p.wash(body, STONE, .6, 2, 2); p.fill(body); p.wash(body, STONE, .35)
    p.stroke(body + [body[0]], w=1.3, double=True)
    tower = rect(68, 30, 84, 86)
    p.wash(tower, STONE, .55, 2, 2); p.fill(tower); p.wash(tower, STONE, .3)
    p.stroke(tower + [tower[0]], w=1.2, double=True)
    p.stroke([(64, 30), (88, 30)], w=1.1)
    for x in (71, 78):
        a = [(x, 46)] + arc(x + 2.5, 40, 2.5, 3, 180, 360, 6) + [(x + 5, 46)]
        p.wash(a, HYD, .55); p.stroke(a, w=.9)
    cap = [(72, 30)] + arc(76, 26, 4, 4, 180, 360, 8) + [(80, 30)]
    p.stroke(cap, w=1); p.stroke([(76, 22), (76, 16)], w=.9)
    door = [(38, 86)] + arc(45, 68, 7, 7, 180, 360, 10) + [(52, 86)]
    p.wash(door, WOOD, .7); p.stroke(door, w=1.1)
    p.stroke([(45, 61), (45, 86)], w=.6)
    for x in (27, 58):
        p.stroke(rect(x, 54, x + 6, 62) + [(x, 54)], w=.8)
    p.stroke([(50, 30), (50, 22)], w=.9); p.stroke([(46, 25), (54, 25)], w=.9)
    p.stroke([(10, 86), (92, 86)], w=1.1, over=1)
    for x in (14, 90):
        for k in range(5):
            p.leaf(x + random.Random(x + k).uniform(-5, 5), 84 - k * 3, 6, -90 + random.Random(k).uniform(-60, 60), .4, sw=.6)
    return _done(p, 'ic-church')

def hanger():
    p = Pen(102)
    p.stroke([(50, 22), (50, 16), (55, 13), (55, 9), (51, 6), (47, 9)], w=1.2, rough=.2, step=3)
    p.stroke([(50, 22), (20, 40), (80, 40), (50, 22)], w=1.2)
    shirt = [(36, 38), (22, 46), (16, 76), (24, 78), (28, 58), (28, 90), (72, 90), (72, 58), (76, 78), (84, 76), (78, 46), (64, 38), (58, 44), (42, 44)]
    p.wash(shirt, STONE, .4, 2, 2); p.fill(shirt); p.stroke(shirt + [shirt[0]], w=1.2, double=True)
    p.stroke([(42, 44), (36, 38), (46, 50), (50, 46), (54, 50), (64, 38), (58, 44)], w=.9)
    p.stroke([(50, 48), (50, 90)], w=.8)
    for x in (32, 56):
        p.stroke(rect(x, 56, x + 12, 64) + [(x, 56)], w=.7)
        p.stroke(rect(x, 72, x + 12, 80) + [(x, 72)], w=.7)
    for y in (56, 66, 76, 86): p.dot(52, y, .9)
    return _done(p, 'ic-hanger')

def travel():
    p = Pen(103)
    # maleta
    case = rect(24, 50, 66, 88)
    p.wash(case, TERRA, .55, 2, 2); p.fill(case); p.wash(case, TERRA, .35)
    p.stroke(case + [case[0]], w=1.2, double=True)
    p.stroke([(37, 50), (37, 44), (53, 44), (53, 50)], w=1.1)
    p.stroke([(24, 62), (66, 62)], w=.7); p.stroke([(34, 50), (34, 88)], w=.6, op=.7); p.stroke([(56, 50), (56, 88)], w=.6, op=.7)
    p.circle(30, 90, 2.2, sw=.7); p.circle(60, 90, 2.2, sw=.7)
    # palma
    p.stroke([(76, 90), (75, 70), (72, 50), (70, 34)], w=1.2)
    for a, L in ((-160, 20), (-125, 18), (-70, 18), (-30, 20), (10, 16)):
        r = math.radians(a); ex, ey = 70 + L * math.cos(r), 34 + L * math.sin(r) * .6 + 8
        p.stroke([(70, 34), (70 + L * .5 * math.cos(r), 34 + L * .5 * math.sin(r) * .8 - 2), (ex, ey)], w=.9)
        for k in range(3, 9):
            t = k / 9; x = 70 + (ex - 70) * t; y = 34 + (ey - 34) * t - 3 * math.sin(t * 3.1)
            p.stroke([(x, y), (x + 1, y + 4)], w=.5, op=.8, rough=.1)
    p.wash(arc(70, 40, 16, 9, 0, 360, 12)[:-1], MATCHA, .35)
    # avión
    p.stroke([(14, 24), (40, 18)], w=.9, op=.8); p.stroke([(24, 26), (30, 16)], w=.8, op=.8)
    p.stroke([(42, 20), (50, 22), (58, 22)], w=.6, op=.5, rough=.1)
    return _done(p, 'ic-travel')

def gift():
    p = Pen(104)
    box = rect(22, 46, 78, 88); lid = rect(18, 36, 82, 48)
    p.wash(box, HYD, .45, 2, 2); p.fill(box); p.wash(box, HYD_L, .5); p.stroke(box + [box[0]], w=1.2, double=True)
    p.wash(lid, HYD, .5, 2, 2); p.fill(lid); p.wash(lid, HYD_L, .45); p.stroke(lid + [lid[0]], w=1.2, double=True)
    p.stroke([(50, 36), (50, 88)], w=1); p.stroke([(46, 36), (46, 88)], w=.6, op=.7)
    p.stroke(arc(40, 28, 10, 7, 20, 340, 12), w=1); p.stroke(arc(58, 28, 10, 7, -160, 160, 12), w=1)
    p.stroke([(48, 34), (40, 44)], w=.8); p.stroke([(50, 34), (60, 44)], w=.8)
    for k in range(4):
        p.leaf(78 + k * 2, 40 - k * 5, 7, -60 + k * 12, .38, sw=.6)
    return _done(p, 'ic-gift')

def envelope():
    p = Pen(105)
    env = rect(14, 30, 86, 80)
    p.wash(env, STONE, .45, 2, 2); p.fill(env); p.wash(env, '#efe7de', .5)
    p.stroke(env + [env[0]], w=1.2, double=True)
    p.stroke([(14, 30), (50, 58), (86, 30)], w=1.1)
    p.stroke([(14, 80), (42, 54)], w=.7, op=.7); p.stroke([(86, 80), (58, 54)], w=.7, op=.7)
    seal = arc(50, 58, 8, 8, 0, 360, 14)[:-1]
    p.wash(seal, SAGE, .8); p.stroke(seal + [seal[0]], w=.9)
    for k in range(5):
        p.leaf(50, 58, 5, k * 72 + 10, .5, sw=.45)
    p.stroke([(64, 20), (70, 14)], w=.6, op=.6); p.stroke([(74, 22), (80, 18)], w=.6, op=.6)
    return _done(p, 'ic-envelope')

def sun():
    p = Pen(106)
    c = arc(50, 50, 16, 16, 0, 360, 18)[:-1]
    p.wash(c, GLOW, .8); p.stroke(c + [c[0]], w=1.2, double=True)
    for k in range(12):
        a = math.radians(k * 30); r1, r2 = 23, 31 if k % 2 == 0 else 28
        p.stroke([(50 + r1 * math.cos(a), 50 + r1 * math.sin(a)), (50 + r2 * math.cos(a), 50 + r2 * math.sin(a))], w=1, rough=.1)
    return _done(p, 'ic-sun')

def bag():
    p = Pen(107)
    b = rect(22, 38, 78, 82)
    p.wash(b, STONE, .55, 2, 2); p.fill(b); p.wash(b, STONE, .3); p.stroke(b + [b[0]], w=1.2, double=True)
    p.stroke([(38, 38), (38, 28), (62, 28), (62, 38)], w=1.1)
    p.stroke([(22, 54), (78, 54)], w=.8); p.stroke(rect(46, 51, 54, 58) + [(46, 51)], w=.8)
    # sombrero y gafas
    p.stroke(arc(30, 30, 10, 3, 0, 360, 10), w=.7, op=.8)
    return _done(p, 'ic-bag')

def coin():
    p = Pen(108)
    c = arc(42, 54, 20, 20, 0, 360, 20)[:-1]
    p.wash(c, GLOW, .55, 2, 2); p.fill(c); p.wash(c, GLOW, .35); p.stroke(c + [c[0]], w=1.2, double=True)
    p.stroke(arc(42, 54, 14, 14, 0, 360, 16), w=.6, op=.7)
    p.stroke([(38, 46), (38, 62)], w=1); p.stroke([(38, 46), (44, 46), (48, 50), (48, 58), (44, 62), (38, 62)], w=1)
    # enchufe
    pl = rect(66, 26, 84, 42)
    p.fill(pl); p.stroke(pl + [pl[0]], w=1); p.stroke([(71, 26), (71, 18)], w=1.1); p.stroke([(79, 26), (79, 18)], w=1.1)
    p.stroke([(75, 42), (75, 50), (70, 60), (66, 66)], w=.8)
    return _done(p, 'ic-coin')

SYMBOLS = ''.join([church(), hanger(), travel(), gift(), envelope(), sun(), bag(), coin()])
