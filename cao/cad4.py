"""Armoire robotisée V3 compacte — CadQuery. Unités mm.
Repère : X largeur (centre 0), Y profondeur (face avant du casier Y=0, arrière +), Z hauteur (dessus du socle Z=0).
Boîtes posées à plat : 50 (X) × 60 (Y) × 20 (Z). Pose de référence : chariot colonne centrale, rangée basse, poussoir rentré.
"""
import math, sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import cadquery as cq
from cadquery import Vector as V
from cad import B, CX, CY, CZ, U, D, tube_x, tube_z, prism_x, prism_y, prism_z, frame, mirror_x, gear_points, rack_points, servo_body, servo_horn, servo_cut

BOX = (50, 60, 20)
CW = 56; WALL = 2.0; PITCH_X = 58; PITCH_Z = 29
CAS_W, CAS_D, CAS_H = 176, 70, 89
ZC = 62                                   # dessous du casier
COLS = [-58, 0, 58]
ROW_AXIS = [ZC + WALL + BOX[2] / 2 + PITCH_Z * r for r in range(3)]   # 74, 103, 132
Z0 = ROW_AXIS[0]
STROKE = 77; TIP_REST = 74
M = 1.5
BAR_TOP = 1.5
PY = (6 + 1.25 * M + 12, 100)            # pignon Y 16 dents (r 12) : (x, y)
PX = (-21, 80 + 1.25 * M + 18)           # pignon X 24 dents (r 18) : (x, y)
ZR = (82, 180); T8 = (-30, 193); SZ = (0, 193)

# ------------------------------------------------------------------ engrenages
def pinion(teeth, gh=8.0):
    g = prism_z(gear_points(M, teeth), 0, gh)
    s = U(g, CZ(gh - 0.1, gh + 1.5, 0, 0, 20), CZ(gh + 1.5, gh + 5.5, 0, 0, 36))
    cut = [CZ(-1, gh + 7, 0, 0, 10)]
    for a in range(0, 360, 90):
        cut.append(U(B(11, 16, -1.2, 1.2, gh + 1, gh + 7), CZ(gh + 1, gh + 7, 11, 0, 2.4), CZ(gh + 1, gh + 7, 16, 0, 2.4)).rotate(V(0, 0, 0), V(0, 0, 1), a + 45))
    return D(s, *cut)

def engrenage_t8():
    s = U(CZ(0, 2, 0, 0, 44), CZ(1.9, 9.6, 0, 0, 18), prism_z(gear_points(M, 16), 9.5, 17.5))
    c = [CZ(-1, 19, 0, 0, 8.2), CX(0, 10, 0, 5.5, 2.9)]
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        c.append(CZ(-1, 3, 19 * math.cos(a), 19 * math.sin(a), 4.5))
    return D(s, *c)

# ------------------------------------------------------------------ servos (repère servo : voir V2)
FR_Y = ((PY[0], PY[1], 23), (0, 1, 0), (-1, 0, 0), (0, 0, 1))
FR_X = ((PX[0], PX[1], 37.5), (0, 1, 0), (-1, 0, 0), (0, 0, 1))
FR_Z = ((SZ[0], SZ[1], 30), (0, -1, 0), (-1, 0, 0), (0, 0, -1))

# ------------------------------------------------------------------ 01 casier monobloc (local : X centré, Y 0..70, Z 0..89)
def casier():
    s = B(-88, 88, 0, CAS_D, 0, CAS_H)
    cols = [(-86, -30), (-28, 28), (30, 86)]
    rows = [(2, 29), (31, 58), (60, 87)]
    s = D(s, *[B(a, b, -1, CAS_D + 1, z0, z1) for a, b in cols for z0, z1 in rows])
    add = []
    for a, b in cols:
        add += [prism_z([(a, 60), (a, CAS_D), (a + 10, CAS_D)], 0, CAS_H), prism_z([(b, 60), (b, CAS_D), (b - 10, CAS_D)], 0, CAS_H)]
        for z0, _ in rows:
            add.append(prism_x([(0, z0), (2, z0 + 1), (4, z0)], a, b))
    s = U(s, *add)
    h = [CZ(-1, 3, x, y, 3.4) for x in (-79, 79) for y in (15, 55)]
    h += [CX(-89, 89, 5, z, 3.4) for z in (15, 44, 73)]
    return D(s, *h)

def pied():   # local X 0..18
    s = U(B(0, 18, 0, 6, 0, ZC), B(0, 18, 64, 70, 0, ZC), B(0, 18, 0, 70, ZC - 5, ZC), B(0, 18, 0, 70, 0, 4), B(0, 18, 0, 70, 28, 33))
    h = []
    for y in (15, 55):
        h += [CZ(ZC - 6, ZC + 1, 9, y, 3.4), CZ(-1, 5, 9, y, 4.5), CZ(27, 34, 9, y, 9)]
    return D(s, *h)

# ------------------------------------------------------------------ ascenseur et façade
TRAY_Y = (-67, -1.5)
def plateau():   # repère chariot ; dessus du fond à -10.5 (0,5 mm sous le plancher des cases)
    y0, y1 = TRAY_Y
    s = U(B(-86, 86, y0, y1, -12.5, -10.5), B(-86, -84.5, y0, y1, -12.5, -2.5), B(84.5, 86, y0, y1, -12.5, -2.5),
          B(-86, 86, y0, y0 + 1.5, -12.5, -4.5), B(-89, -84.5, -60, -8, -14, -10.5), B(84.5, 89, -60, -8, -14, -10.5))
    s = D(s, prism_x([(y1 - 3, -10.4), (y1 + 0.1, -10.4), (y1 + 0.1, -11.6)], -84.4, 84.4))
    return D(s, *[CX(x0, x0 + 7, y, -12.25, 3.4) for y in (-50, -18) for x0 in (-91, 84)])

def bras_avant():   # droit
    s = U(B(89, 96, -70, 72, -14, -7), B(96, 99, 60, 100, -26, -7))
    h = [CX(85, 97, y, -12.25, 3.4) for y in (-50, -18)] + [CX(95, 100, y, z, 3.4) for y in (86, 94) for z in (-20, -12)]
    return D(s, *h)

def joue():   # droite, X 100..103
    s = U(B(100, 103, -76, 12, 4, 150), B(88, 103, 0, 12, 130, 150), B(92, 103, -60, -20, 0, 4))
    return D(s, B(99.9, 101.5, -74.6, -71.4, 94, 151), CX(87, 104, 5, ZC + 73, 3.4), *[CZ(-1, 5, 97, y, 4.5) for y in (-50, -30)])

# ------------------------------------------------------------------ axe Z : paliers, pont haut, socle Z
def palier_d():
    y = ZR[1]
    s = U(B(72, 92, y - 10, y + 10, 0, 22), B(70, 96, y - 14, y + 14, 0, 5))
    return D(s, CZ(4, 23, ZR[0], y, 8.2), CX(ZR[0], 93, y, 13, 2.9), *[CZ(-1, 6, x, yy, 4.5) for x in (74, 93) for yy in (y - 11, y + 11)])
def palier_g():
    y = ZR[1]
    s = U(mirror_x(palier_d()), B(-74, -64, y - 10, y + 10, 0, 38))
    return D(s, *[CY(y - 11, y + 11, -69, z, 2.2) for z in (26, 35)])

def pont_base():
    y = ZR[1]
    s = U(B(72, 92, y - 10, y + 10, 155, 167), B(0, 92, y - 5, y + 20, 159, 167))
    return D(s, CZ(154, 165, ZR[0], y, 8.2), CX(ZR[0], 93, y, 161, 2.9))
def pont_d():
    y = ZR[1]
    s = U(pont_base(), B(-20, 0.5, y - 5, y + 20, 167, 171))
    return D(s, *[CZ(150, 172, -10, yy, 3.4) for yy in (y, y + 14)])
def pont_g():
    y = ZR[1]
    s = U(mirror_x(pont_base()), CZ(155, 167, T8[0], T8[1], 32))
    s = D(s, CZ(154, 162, T8[0], T8[1], 22.2), CZ(150, 172, T8[0], T8[1], 9))
    return D(s, *[CZ(154, 168, -10, yy, 2.8) for yy in (y, y + 14)])

def socle_z():
    s = U(B(-48, 20, 148, 214, 0, 4), CZ(0, 38, T8[0], T8[1], 26), B(-16, 16, 152, 212, 24, 30), B(-16, -12, 152, 212, 3, 24), B(12, 16, 152, 212, 3, 24),
          B(-62, -42, 187, 199, 3, 36))
    s = D(s, CZ(30.9, 39, T8[0], T8[1], 22.2), CZ(-1, 39, T8[0], T8[1], 10), frame(servo_cut(-1, 7), *FR_Z),
          *[CZ(-1, 5, x, y, 4.5) for x in (-40, 8) for y in (152, 210)], CY(186, 200, -52, 30, 2.2))
    return s

# ------------------------------------------------------------------ traverses (repère chariot : Z=0 sur l'axe du poussoir)
BACK = (188, 198)
def rack_x(x0, x1):
    pts = [(s, 80 + h) for s, h in rack_points(x0, x1, M)]
    return prism_z(pts, 8, 16)
def trav_base():
    s = U(CZ(-30, 20, ZR[0], ZR[1], 25), B(88, 96, 72, BACK[1], -28, -7), B(88, 96, 72, 80, -7, 17),
          CX(84, 96, 90, -18, 16), CX(84, 96, 150, -18, 16), B(0, 96, 72, 80, 6, 17), rack_x(0.5, 87), B(0, 96, 78, 80, 16.5, 28),
          B(0, 88, BACK[0], BACK[1], -10, 2))
    c = [CZ(-31, 21, ZR[0], ZR[1], 15.2), CX(84, 94, 90, -18, 8.2), CX(84, 94, 150, -18, 8.2), CZ(-29, -6, 92, 90, 2.9), CZ(-29, -6, 92, 150, 2.9),
         B(PITCH_X - 2, PITCH_X + 2, 77, 81, 19, 29), B(-1, 2, 77, 81, 19, 29), *[CX(95, 97, y, z, 3.4) for y in (86, 94) for z in (-20, -12)]]
    return D(s, *c)
def trav_d():
    s = U(trav_base(), B(-3, 0.5, 72, 80, 6, 17), rack_x(-3, 0.6), B(-16, 10, 72, 78, 17, 21))
    return D(s, *[CZ(15, 22, -8, y, 3.4) for y in (74, 76.5)], *[CZ(-6, 3, 8, y, 2.8) for y in (190, 196)])
def trav_g():
    s = U(mirror_x(trav_base()), CZ(-10, 2, T8[0], T8[1], 28), B(-12, 16, BACK[0], BACK[1], 2, 6))
    s = D(s, B(-3.2, 1, 70, 84, 5, 18))
    h = [CZ(-15, 5, T8[0], T8[1], 10.5), *[CZ(10, 18, -8, y, 2.8) for y in (74, 76.5)], *[CZ(1, 7, 8, y, 3.4) for y in (190, 196)]]
    h += [CZ(-15, 5, T8[0] + 8 * math.cos(math.radians(a)), T8[1] + 8 * math.sin(math.radians(a)), 3.4) for a in (45, 135, 225, 315)]
    return D(s, *h)

# ------------------------------------------------------------------ chariot X + poussoir (repère chariot)
def chariot():
    s = U(B(-29, 29, 78, 160, -9, -5.4), CX(-15, 15, 90, -18, 23), CX(-15, 15, 150, -18, 23),
          B(-12, -6.4, 78, 160, -5.4, 2), B(9.8, 14, 120, 160, -5.4, 2), B(-12, 14, 140, 160, 2, 4),
          B(10, 14, 138, 144, -9, 14.5),
          B(-1, 29.5, 84, 146, 14.5, 20.5), B(-1, 3, 84, 88, 4, 35), B(-12, 6, 84, 88, 2, 4),
          B(-29, -23, 138, 144, -9, 29), B(-12, -6, 138, 144, -9, 29), B(-36, -1, 84, 146, 29, 35),
          B(-7, 6, 74, 92, 24, 32), B(-18, -12, 128, 158, -9, 2))
    s = U(s, B(24, 29, 138, 144, -9, 14.5))
    c = [B(-6.4, 6.4, 70, 165, -5.4, 1.9), B(6, 9.8, 70, 165, -5.4, 1.9), CZ(-6, 8, PY[0], PY[1], 30),
         CX(-16, 16, 90, -18, 15.2), CX(-16, 16, 150, -18, 15.2), CX(-40, 40, 90, -18, 10), CX(-40, 40, 150, -18, 10),
         frame(servo_cut(-9, -2), *FR_Y), frame(servo_cut(-9, -2), *FR_X), B(-8, 7, 77, 81, 23, 30.5),
         *[CX(-19, -11, y, -4, 2.2) for y in (133, 153)]]
    return D(s, *c)

def poussoir():
    t = TIP_REST
    s = U(B(-12, 12, t, t + 4, -5, 5), B(-6, 6, t + 4, t + 112, -5, BAR_TOP))
    pts = [(6 + h, s_) for s_, h in rack_points(t + 16, t + 109, M)]
    return U(s, prism_z(pts, -5, BAR_TOP))

def coupon():
    s = U(B(0, 150, 0, 60, 0, 6), CZ(0, 15, 88, 16, 23), CZ(0, 9, 88, 44, 28), B(118, 148, 20, 28, 0, 12))
    pts = [(s_, 12 + h) for s_, h in rack_points(119, 147, M)]
    s = U(s, cq.Workplane("XZ", origin=(0, 28, 0)).polyline(pts).close().extrude(8).val())
    c = [frame(servo_cut(-1, 8), (22, 30, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)), CZ(-1, 16, 88, 16, 15.2), CZ(2, 10, 88, 44, 22.2),
         CZ(-1, 10, 88, 44, 10), CZ(-1, 7, 108, 14, 8.2), CZ(-1, 7, 108, 44, 10.5)]
    c += [CZ(-1, 7, 108 + 8 * math.cos(math.radians(a)), 44 + 8 * math.sin(math.radians(a)), 3.4) for a in (45, 135, 225, 315)]
    return D(s, *c)

# ------------------------------------------------------------------ inventaire
def build():
    P = {}
    def add(k, shape, qty, rot, title): P[k] = dict(shape=shape, qty=qty, rot=rot, title=title)
    add('01_casier', casier(), 1, ((1, 0, 0), 90), 'Casier 3 × 3 monobloc')
    add('02_pied_casier', pied(), 2, ((0, 1, 0), -90), 'Pied du casier')
    add('03_plateau_ascenseur', plateau(), 1, None, "Plateau de l'ascenseur")
    add('04_bras_avant_droit', bras_avant(), 1, ((0, 1, 0), 90), 'Bras avant droit')
    add('04_bras_avant_gauche', mirror_x(bras_avant()), 1, ((0, 1, 0), -90), 'Bras avant gauche')
    add('15_joue_droite', joue(), 1, ((0, 1, 0), 90), 'Joue droite (plexi)')
    add('15_joue_gauche', mirror_x(joue()), 1, ((0, 1, 0), -90), 'Joue gauche (plexi)')
    add('05_palier_droit', palier_d(), 1, None, 'Palier bas droit')
    add('05_palier_gauche', palier_g(), 1, None, 'Palier bas gauche (fin de course Z)')
    add('06_pont_droit', pont_d(), 1, ((1, 0, 0), 180), 'Pont haut droit (roulement T8)')
    add('06_pont_gauche', pont_g(), 1, ((1, 0, 0), 180), 'Pont haut gauche')
    add('07_socle_Z', socle_z(), 1, None, 'Socle du servo Z')
    add('08_traverse_droite', trav_d(), 1, None, 'Traverse droite (crémaillère X, écrou T8)')
    add('08_traverse_gauche', trav_g(), 1, None, 'Traverse gauche (crémaillère X)')
    add('09_chariot_X', chariot(), 1, None, 'Chariot X')
    add('10_poussoir', poussoir(), 1, ((0, 1, 0), 90), 'Poussoir à crémaillère')
    add('11_pignon_24', pinion(24, 8), 2, None, 'Pignon 24 dents (X et servo Z)')
    add('12_pignon_16', pinion(16, 6.5), 1, None, 'Pignon 16 dents (poussoir)')
    add('13_engrenage_T8', engrenage_t8(), 1, None, 'Engrenage T8 16 dents + disque codeur')
    add('14_coupon_essai', coupon(), 1, None, "Coupon d'essai")

    zz = V(0, 0, Z0)
    I = []
    I.append(('Casier 3 × 3', 'fixe', P['01_casier']['shape'].translate(V(0, 0, ZC)), 'casier'))
    I.append(('Pied du casier droit', 'fixe', P['02_pied_casier']['shape'].translate(V(70, 0, 0)), 'structure'))
    I.append(('Pied du casier gauche', 'fixe', P['02_pied_casier']['shape'].translate(V(-88, 0, 0)), 'structure'))
    I.append(('Joue droite', 'fixe', P['15_joue_droite']['shape'], 'goulotte'))
    I.append(('Joue gauche', 'fixe', P['15_joue_gauche']['shape'], 'goulotte'))
    for k in ('05_palier_droit', '05_palier_gauche', '06_pont_droit', '06_pont_gauche', '07_socle_Z'):
        I.append((P[k]['title'], 'fixe', P[k]['shape'], 'structure'))
    I.append(('Traverse droite', 'Z', P['08_traverse_droite']['shape'].translate(zz), 'axeZ'))
    I.append(('Traverse gauche', 'Z', P['08_traverse_gauche']['shape'].translate(zz), 'axeZ'))
    I.append(("Plateau de l'ascenseur", 'Z', P['03_plateau_ascenseur']['shape'].translate(zz), 'bac'))
    I.append(('Bras avant droit', 'Z', P['04_bras_avant_droit']['shape'].translate(zz), 'axeZ'))
    I.append(('Bras avant gauche', 'Z', P['04_bras_avant_gauche']['shape'].translate(zz), 'axeZ'))
    I.append(('Chariot X', 'X', P['09_chariot_X']['shape'].translate(zz), 'axeX'))
    I.append(('Poussoir', 'Y', P['10_poussoir']['shape'].translate(zz), 'axeY'))
    I.append(('Pignon X', 'X', P['11_pignon_24']['shape'].translate(V(PX[0], PX[1], 8)).translate(zz), 'pignonX'))
    I.append(('Pignon du poussoir', 'X', P['12_pignon_16']['shape'].translate(V(PY[0], PY[1], -5)).translate(zz), 'pignonY'))
    I.append(('Pignon du servo Z', 'fixe', frame(P['11_pignon_24']['shape'], (SZ[0], SZ[1], 59.5), (1, 0, 0), (0, -1, 0), (0, 0, -1)), 'pignonZs'))
    I.append(('Engrenage T8 + codeur', 'fixe', P['13_engrenage_T8']['shape'].translate(V(T8[0], T8[1], 42)), 'pignonZ'))

    A = []
    A.append(('Socle contreplaqué 210 × 296 × 10', 'fixe', B(-105, 105, -80, 216, -10, 0), 'bois'))
    for x in (-ZR[0], ZR[0]):
        A.append(('Tige lisse Z Ø8 × 161', 'fixe', CZ(4, 165, x, ZR[1], 8), 'tige'))
    A.append(('Vis trapézoïdale T8 pas 8 × 132', 'fixe', CZ(30, 162, T8[0], T8[1], 8), 'vis'))
    A.append(('Plexiglas 3 mm 202 × 54', 'fixe', B(-101.3, 101.3, -74.5, -71.5, 95, 149), 'plexi'))
    A.append(('Servo Parallax : axe Z', 'fixe', frame(servo_body(), *FR_Z), 'servo'))
    A.append(('Palonnier (servo Z)', 'fixe', frame(servo_horn(), *FR_Z), 'servo'))
    for y in (90, 150):
        A.append(('Tige lisse X Ø8 × 187', 'Z', CX(-93.5, 93.5, y, Z0 - 18, 8), 'tige'))
    for x in (-ZR[0], ZR[0]):
        for z0 in (-29, -5):
            A.append(('Roulement linéaire LM8UU', 'Z', tube_z(Z0 + z0, Z0 + z0 + 24, x, ZR[1], 15, 8), 'roulement'))
    A.append(('Écrou laiton T8', 'Z', U(CZ(Z0 - 13.5, Z0 - 10, T8[0], T8[1], 22), CZ(Z0 - 10, Z0 + 5, T8[0], T8[1], 10.2)).cut(CZ(Z0 - 20, Z0 + 10, T8[0], T8[1], 8)), 'vis'))
    for y in (90, 150):
        A.append(('Roulement linéaire LM8UU', 'X', tube_x(-12, 12, y, Z0 - 18, 15, 8), 'roulement'))
    A.append(('Servo Parallax : poussoir', 'X', frame(servo_body(), *FR_Y).translate(zz), 'servo'))
    A.append(('Palonnier (poussoir)', 'X', frame(servo_horn(), *FR_Y).translate(zz), 'servo'))
    A.append(('Servo Parallax : axe X', 'X', frame(servo_body(), *FR_X).translate(zz), 'servo'))
    A.append(('Palonnier (servo X)', 'X', frame(servo_horn(), *FR_X).translate(zz), 'servo'))
    return P, I, A
