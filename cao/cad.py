"""Armoire robotisée V2 — modèle paramétrique CadQuery.
Unités : mm. Repère : X largeur (droite +), Y profondeur (avant du casier en Y=0, arrière +), Z hauteur (dessus du socle bois Z=0).
Pose de référence : chariot sur la colonne centrale (X=0), rangée basse, poussoir rentré.
"""
import math
import cadquery as cq
from cadquery import Vector as V

# ---------------------------------------------------------------- paramètres
BOX = (60, 80, 35)            # boîte factice l × p × h
PITCH_X, PITCH_Z = 72, 48     # pas des cases
MOD_W, MOD_D, MOD_H = 72, 96, 146.4
WALL = 2.4
Z_CASIER = 110                # dessous du casier
COLS = [-72, 0, 72]
ROW_AXIS = [Z_CASIER + WALL + BOX[2] / 2 + PITCH_Z * r for r in range(3)]   # 129.9, 177.9, 225.9
Z0 = ROW_AXIS[0]
STROKE = 105                  # course du poussoir
TIP_REST = 98                 # face avant de l'embout, poussoir rentré
MOD = 1.5; TEETH = 24         # pignon module 1,5, 24 dents (Ø primitif 36)
RP = MOD * TEETH / 2
BACKLASH = 0.15
YP_Y = 135                    # axe du pignon Y (repère chariot)
PIN_Y_Z = 2 + 1.25 * MOD + RP # 21.875
RACK_X_ROOT = 205             # face d'appui des dents de la crémaillère X
PIN_X_Y = RACK_X_ROOT - 1.25 * MOD - RP   # 185.125
ZR_X, ZR_Y = 150, 150         # tiges Z en (±150, 150)
T8 = (-150, 110)

# ---------------------------------------------------------------- primitives
def B(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def CX(x0, x1, y, z, d): return cq.Solid.makeCylinder(d / 2, x1 - x0, V(x0, y, z), V(1, 0, 0))
def CY(y0, y1, x, z, d): return cq.Solid.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))
def CZ(z0, z1, x, y, d): return cq.Solid.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))
def U(*s):
    r = s[0]
    for t in s[1:]:
        r = r.fuse(t)
    return r.clean()
def D(a, *s): return a.cut(U(*s)).clean()
def tube_x(x0, x1, y, z, do, di): return D(CX(x0, x1, y, z, do), CX(x0 - 1, x1 + 1, y, z, di))
def tube_z(z0, z1, x, y, do, di): return D(CZ(z0, z1, x, y, do), CZ(z0 - 1, z1 + 1, x, y, di))
def prism_x(pts, x0, x1):      # polygone (y,z) extrudé selon X
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0).val()
def prism_z(pts, z0, z1):      # polygone (x,y) extrudé selon Z
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(z1 - z0).val()
def prism_y(pts, y0, y1):      # polygone (x,z) extrudé selon Y
    return cq.Workplane("XZ", origin=(0, y1, 0)).polyline(pts).close().extrude(y1 - y0).val()
def frame(shape, o, u, v, w):  # repère local (u,v,w) -> global
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    t = gp_Trsf()
    t.SetValues(u[0], v[0], w[0], o[0], u[1], v[1], w[1], o[1], u[2], v[2], w[2], o[2])
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, t, True).Shape())
def mirror_x(s): return s.mirror("YZ")

# ---------------------------------------------------------------- engrenages
def gear_points(m=MOD, z=TEETH, pa=20, bl=BACKLASH, steps=7):
    r = m * z / 2; rb = r * math.cos(math.radians(pa)); ra = r + m; rf = r - 1.25 * m
    inv = lambda a: math.tan(a) - a
    half = math.pi / (2 * z) - bl / (2 * r) + inv(math.radians(pa))
    def th(rr):
        rr = max(rr, rb)
        return half - inv(math.acos(rb / rr))
    radii = [rf] + [max(rf, rb) + (ra - max(rf, rb)) * i / steps for i in range(steps + 1)]
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z
        flank = [(rr, c - th(rr)) for rr in radii]
        tip = [(ra, c - th(ra) + (2 * th(ra)) * i / 3) for i in range(1, 3)]
        back = [(rr, c + th(rr)) for rr in reversed(radii)]
        for rr, a in flank + tip + back:
            pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts

def rack_points(s0, s1, m=MOD, bl=BACKLASH, base=1.0):
    """Profil (s,h) : racine h=0, dents vers h+. Dents centrées sur s = k·p (phase globale)."""
    p = math.pi * m; t = math.tan(math.radians(20))
    w_pitch = p / 2 - bl; wr = w_pitch + 2 * 1.25 * m * t; wt = w_pitch - 2 * m * t; ht = 2.25 * m
    pts = [(s0, -base), (s0, 0)]
    k = math.ceil((s0 + wr / 2) / p)
    while k * p + wr / 2 <= s1:
        c = k * p
        pts += [(c - wr / 2, 0), (c - wt / 2, ht), (c + wt / 2, ht), (c + wr / 2, 0)]
        k += 1
    pts += [(s1, 0), (s1, -base)]
    return pts

def pinion():
    g = prism_z(gear_points(), 0, 8)
    fl = CZ(8, 12, 0, 0, 36)
    s = U(g, fl)
    cut = [CZ(-1, 13, 0, 0, 10)]
    for a in range(0, 360, 90):
        sl = U(B(11, 16, -1.2, 1.2, 7, 13), CZ(7, 13, 11, 0, 2.4), CZ(7, 13, 16, 0, 2.4))
        cut.append(sl.rotate(V(0, 0, 0), V(0, 0, 1), a + 45))
    return D(s, *cut)

# ---------------------------------------------------------------- servo Parallax (enveloppe nominale)
# repère servo : u = longueur du corps, v = largeur, w = 0 au plan des oreilles, w>0 côté corps, palonnier à w=-16
def servo_body():
    body = U(B(-10, 30.5, -10, 10, -10, 26), B(-17.5, 38, -9, 9, -2.5, 0), CZ(-14, -10, 0, 0, 6))
    return body
def servo_horn(): return CZ(-16, -14, 0, 0, 25)
def servo_cut(w0=-1, w1=7):
    c = [B(-10.6, 31.1, -10.6, 10.6, w0, w1)]
    for u in (-14.5, 35.5):
        for v in (-5, 5):
            c += [B(u - 1.5, u + 1.5, v - 1.8, v + 1.8, w0, w1), CZ(w0, w1, u - 1.5, v, 3.6), CZ(w0, w1, u + 1.5, v, 3.6)]
    return U(*c)
FR_Y = ((-6 + 16 + 12, YP_Y, PIN_Y_Z), (0, 1, 0), (0, 0, 1), (1, 0, 0))     # oreilles en X=22
FR_X = ((0, PIN_X_Y, -73), (0, -1, 0), (-1, 0, 0), (0, 0, -1))
FR_Z = ((T8[0], T8[1], 316), (0, 1, 0), (-1, 0, 0), (0, 0, 1))

# ---------------------------------------------------------------- 01 module colonne du casier (repère local, X centré, Z=0 en bas)
def module():
    s = B(-36, 36, 0, MOD_D, 0, MOD_H)
    inner = []
    for r in range(3):
        z0 = PITCH_Z * r + WALL
        inner.append(B(-36 + WALL, 36 - WALL, -1, MOD_D + 1, z0, PITCH_Z * (r + 1)))
    s = D(s, *inner)
    ix = 36 - WALL
    lips = [prism_z([(-ix, 82), (-ix, MOD_D), (-ix + 14, MOD_D)], 0, MOD_H),
            prism_z([(ix, 82), (ix, MOD_D), (ix - 14, MOD_D)], 0, MOD_H)]
    bumps = [prism_x([(0, z), (2, z + 1.2), (4, z)], -ix, ix) for z in (PITCH_Z * r + WALL for r in range(3))]
    s = U(s, *lips, *bumps)
    holes = []
    for y in (20, 76):
        for r in range(3):
            holes.append(CX(-37, 37, y, PITCH_Z * r + 25, 3.4))
    for x in (-21, 21):
        for y in (20, 76):
            holes.append(CZ(-1, WALL + 1, x, y, 3.4))
    for x in (-28, 28):
        for y in (62, 88):
            holes.append(CZ(MOD_H - WALL - 1, MOD_H + 1, x, y, 3.4))
    return D(s, *holes)

# ---------------------------------------------------------------- 02 pied du casier (local X 0..30)
def pied():
    s = U(B(0, 30, 0, 8, 0, Z_CASIER), B(0, 30, 88, 96, 0, Z_CASIER), B(0, 30, 0, 96, Z_CASIER - 5, Z_CASIER),
          B(0, 30, 0, 96, 0, 5), B(0, 30, 0, 96, 50, 56))
    h = []
    for y in (20, 76):
        h += [CZ(Z_CASIER - 6, Z_CASIER + 1, 15, y, 3.4), CZ(-1, 6, 15, y, 4.5), CZ(49, 57, 15, y, 9)]
    return D(s, *h)

# ---------------------------------------------------------------- 03 rampe (demi, X 0..108)
def rampe():
    plate = prism_x([(0, 100), (-90, 10), (-90, 4.34), (0, 94.34)], 0, 108)
    rib = [(0, 0), (0, 100), (-55, 45), (-55, 0)]
    s = U(plate, prism_x(rib, 0, 4), prism_x(rib, 104, 108), B(0, 108, -55, 0, 0, 4))
    h = [CZ(-1, 5, x, -27, 4.5) for x in (20, 88)]
    h += [CX(-1, 5, y, z, 3.4) for y, z in ((-10, 20), (-10, 70), (-40, 20))]
    return D(s, *h)

# ---------------------------------------------------------------- 04 bac de réception (demi droit X 0..107)
def bac():
    s = D(B(0, 107, -178, -60, 0, 30), B(WALL, 107 - WALL, -178 + WALL, -60 - WALL, WALL, 31))
    s = D(s, CY(-179, -175, 53, 31, 34))
    s = D(s, prism_x([(1, 101.4), (-91.4, 9), (-91.4, 2.9), (1, 95.3)], -1, 108))
    s = D(s, B(-1, WALL + 0.6, -178 + WALL, -60 - WALL, WALL, 31))
    return D(s, *[CZ(-1, WALL + 1, x, y, 4.5) for x, y in ((18, -165), (90, -165), (54, -100))])

# ---------------------------------------------------------------- 05 joue de goulotte (droite, X 108..111)
def joue():
    s = B(108, 111, -92, 30, 20, 198)
    return D(s, B(107.9, 109.5, -89.2, -85.8, 65, 199), *[CX(107, 112, 20, z, 3.4) for z in (135, 183)],
             *[CX(107, 112, y, 60, 3.4) for y in (-70, -20)])

# ---------------------------------------------------------------- 06 paliers bas
def palier_bas_d():
    s = U(B(135, 165, 135, 165, 0, 22), B(128, 172, 128, 172, 0, 5))
    return D(s, CZ(4, 23, ZR_X, ZR_Y, 8.2), CX(ZR_X, 166, ZR_Y, 13, 2.9),
             *[CZ(-1, 6, x, y, 4.5) for x in (132, 168) for y in (132, 168)])
def palier_bas_g():
    s = U(mirror_x(palier_bas_d()), B(-165, -135, 95, 136, 0, 22), B(-172, -128, 88, 136, 0, 5), B(-137, -121, 138, 162, 0, 60))
    return D(s, CZ(15, 23, T8[0], T8[1], 22.2), CZ(-1, 23, T8[0], T8[1], 10),
             *[CZ(-1, 6, x, 92, 4.5) for x in (-168, -132)], *[CY(137, 163, -129, z, 2.2) for z in (48, 57.5)])

# ---------------------------------------------------------------- 07 supports hauts
def support_haut_d():
    s = U(B(135, 165, 135, 165, 254, 276), B(135, 165, 50, 165, 262, 276), B(92, 165, 50, 100, 256.4, 262.4))
    return D(s, CZ(253, 272, ZR_X, ZR_Y, 8.2), CX(ZR_X, 166, ZR_Y, 266, 2.9),
             *[CZ(255, 277, 100, y, 3.4) for y in (62, 88)])
def support_haut_g():
    s = U(mirror_x(support_haut_d()), B(-165, -135, 96, 136, 254, 276),
          B(-166, -162, 132, 150, 275, 308), B(-138, -134, 132, 150, 275, 308), B(-170, -130, 88, 152, 307.5, 313.5))
    s = D(s, CZ(269, 277, T8[0], T8[1], 22.2), CZ(250, 277, T8[0], T8[1], 9))
    return D(s, frame(servo_cut(-9, -2), *FR_Z))

# ---------------------------------------------------------------- 08 peigne de repérage Z
def peigne_z():
    s = B(108, 111, 55, 113, 100, 240)
    slots = [B(107, 112, 100, 114, Z0 - 21 + PITCH_Z * r - 2, Z0 - 21 + PITCH_Z * r + 2) for r in range(3)]
    return D(s, *slots, *[CX(107, 112, 76, z, 3.4) for z in (135, 183, 231)])

# ---------------------------------------------------------------- 09/10 traverses Z (repère chariot : Z=0 sur l'axe du poussoir)
def rack_x(x0, x1):
    pts = [(s, RACK_X_ROOT - h) for s, h in rack_points(x0, x1)]
    return prism_z(pts, -53, -45)
def traverse_base():
    s = U(CZ(-56, -6, ZR_X, ZR_Y, 25), B(112, 162, 112, 188, -42, -18),
          CX(112, 140, 120, -30, 16), CX(112, 140, 180, -30, 16), B(112, 150, 180, 216, -58, -30),
          B(0, 150, 205, 216, -58, -42), rack_x(0.5, 148), B(0, 140, 207, 209, -72, -57))
    return D(s, CZ(-60, 0, ZR_X, ZR_Y, 15.2), CX(111, 138, 120, -30, 8.2), CX(111, 138, 180, -30, 8.2),
             CZ(-31, -17, 128, 120, 2.9), CZ(-31, -17, 128, 180, 2.9),
             B(PITCH_X - 2, PITCH_X + 2, 206, 210, -73, -62), B(-1, 2, 206, 210, -73, -62))
def traverse_d():
    s = U(traverse_base(), B(-16, 10, 216, 226, -58, -42), B(0, 10, 213, 217, -58, -42), B(100, 122, 100, 120, -24, -18))
    return D(s, B(107.5, 111.5, 95, 115, -30, -10), *[CY(215, 227, -8, z, 3.4) for z in (-55, -45)],
             *[CZ(-25, -17, x, 117.5, 2.2) for x in (103, 119)])
def traverse_g():
    s = U(mirror_x(traverse_base()), B(-164, -136, 96, 124, -42, -30), B(-114, -104, 126, 146, -40, -20))
    h = [CZ(-80, 10, T8[0], T8[1], 10.5), CX(-142, -110, 120, -30, 8.2), *[CY(207, 217, -8, z, 4.2) for z in (-55, -45)],
         *[CY(125, 147, -108, z, 2.2) for z in (-35, -25)]]
    h += [CZ(-43, -29, T8[0] + 8 * math.cos(math.radians(a)), T8[1] + 8 * math.sin(math.radians(a)), 3.4) for a in (45, 135, 225, 315)]
    return D(s, *h)

# ---------------------------------------------------------------- 11 chariot X (repère chariot)
def chariot_x():
    s = U(B(-14, 14, 103, 170, -22, 12), CX(-15, 15, 120, -30, 23), CX(-15, 15, 180, -30, 23),
          B(-14, 14, 150, 190, -34, -18), B(-25, 25, 150, 200, -34, -30),
          B(-25, -21, 150, 200, -79, -30), B(21, 25, 150, 200, -79, -30), B(-25, 25, 147, 203, -79, -73),
          B(22, 28, 115, 175, 6, 36), B(10, 28, 115, 175, -2, 6), B(5, 25, 198, 222, -85, -78),
          B(-20, -13, 140, 168, -20, -8))
    cuts = [B(-6.4, 6.4, 100, 175, -8.4, 6), B(-2.4, 2.4, 100, 175, -16.6, -7), B(-7, 7, 113, 157, 2, 13), B(7, 15, 113, 171, 6, 13),
            CX(-16, 16, 120, -30, 15.2), CX(-16, 16, 180, -30, 15.2), CX(-40, 40, 120, -30, 10), CX(-40, 40, 180, -30, 10),
            frame(servo_cut(), *FR_Y), frame(servo_cut(), *FR_X), CZ(-61, -43, 0, PIN_X_Y, 42),
            *[CZ(-86, -77, x, 212, 3.2) for x in (10, 20)], *[CX(-21, -12, y, -14, 2.2) for y in (146, 162)]]
    return D(s, *cuts)

# ---------------------------------------------------------------- 12 poussoir (repère chariot, rentré)
def poussoir():
    t = TIP_REST
    s = U(B(-15, 15, t, t + 4, -10, 10), B(-6, 6, t + 4, t + 155, -8, 2), B(-2, 2, t + 143, t + 155, -16, -8))
    pts = [(s_, 2 + h) for s_, h in rack_points(t + 30, t + 150)]
    teeth = cq.Workplane("YZ", origin=(-6, 0, 0)).polyline(pts).close().extrude(8).val()
    return U(s, teeth)

# ---------------------------------------------------------------- 13 accouplement servo – T8
def accouplement():
    s = U(CZ(0, 18, 0, 0, 20), CZ(18, 22, 0, 0, 38))
    c = [CZ(-1, 23, 0, 0, 8.2)]
    for a in range(0, 360, 90):
        c.append(U(B(11, 16, -1.2, 1.2, 17, 23), CZ(17, 23, 11, 0, 2.4), CZ(17, 23, 16, 0, 2.4)).rotate(V(0, 0, 0), V(0, 0, 1), a + 45))
    c += [CX(0, 11, 0, 7, 2.9), CY(0, 11, 0, 7, 2.9)]
    return D(s, *c)

# ---------------------------------------------------------------- 14 coupon d'essai
def coupon():
    s = U(B(0, 150, 0, 60, 0, 6), CZ(0, 15, 88, 16, 23), CZ(0, 9, 88, 44, 28), B(118, 148, 20, 28, 0, 12))
    pts = [(s_, 12 + h) for s_, h in rack_points(119, 147)]
    teeth = cq.Workplane("XZ", origin=(0, 28, 0)).polyline(pts).close().extrude(8).val()
    s = U(s, teeth)
    sv = frame(servo_cut(-1, 8), (22, 30, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    c = [sv, CZ(-1, 16, 88, 16, 15.2), CZ(2, 10, 88, 44, 22.2), CZ(-1, 10, 88, 44, 10), CZ(-1, 7, 108, 14, 8.2),
         CZ(-1, 7, 108, 44, 10.5)]
    c += [CZ(-1, 7, 108 + 8 * math.cos(math.radians(a)), 44 + 8 * math.sin(math.radians(a)), 3.4) for a in (45, 135, 225, 315)]
    return D(s, *c)

# ---------------------------------------------------------------- inventaire
def place_pinion_y(p): return frame(p, (-6, YP_Y, PIN_Y_Z), (0, 1, 0), (0, 0, 1), (1, 0, 0))
def place_pinion_x(p): return frame(p, (0, PIN_X_Y, -45), (0, -1, 0), (-1, 0, 0), (0, 0, -1))

def build():
    """Renvoie parts (pièces à imprimer) et inst (instances positionnées : nom, groupe, forme, catégorie)."""
    P = {}
    P['01_module_casier'] = dict(shape=module(), qty=3, rot=((1, 0, 0), 90), title='Module colonne (3 cases)')
    P['02_pied_casier'] = dict(shape=pied(), qty=2, rot=((0, 1, 0), -90), title='Pied du casier')
    P['03_rampe'] = dict(shape=rampe(), qty=2, rot=None, title='Rampe 45° (demi)')
    P['04_bac_droit'] = dict(shape=bac(), qty=1, rot=None, title='Bac de réception droit')
    P['04_bac_gauche'] = dict(shape=mirror_x(bac()), qty=1, rot=None, title='Bac de réception gauche')
    P['05_joue_droite'] = dict(shape=joue(), qty=1, rot=((0, 1, 0), 90), title='Joue de goulotte droite')
    P['05_joue_gauche'] = dict(shape=mirror_x(joue()), qty=1, rot=((0, 1, 0), -90), title='Joue de goulotte gauche')
    P['06_palier_bas_droit'] = dict(shape=palier_bas_d(), qty=1, rot=None, title='Palier bas droit')
    P['06_palier_bas_gauche'] = dict(shape=palier_bas_g(), qty=1, rot=None, title='Palier bas gauche (T8 + fin de course Z)')
    P['07_support_haut_droit'] = dict(shape=support_haut_d(), qty=1, rot=((1, 0, 0), 180), title='Support haut droit')
    P['07_support_haut_gauche'] = dict(shape=support_haut_g(), qty=1, rot=None, title='Support haut gauche (servo Z)')
    P['08_peigne_Z'] = dict(shape=peigne_z(), qty=1, rot=((0, 1, 0), 90), title='Peigne de repérage Z')
    P['09_traverse_droite'] = dict(shape=traverse_d(), qty=1, rot=None, title='Traverse Z droite (crémaillère X)')
    P['10_traverse_gauche'] = dict(shape=traverse_g(), qty=1, rot=None, title='Traverse Z gauche (écrou T8)')
    P['11_chariot_X'] = dict(shape=chariot_x(), qty=1, rot=((0, 1, 0), 90), title='Chariot X + guide du poussoir')
    P['12_poussoir'] = dict(shape=poussoir(), qty=1, rot=((0, 1, 0), 90), title='Poussoir à crémaillère')
    P['13_pignon_servo'] = dict(shape=pinion(), qty=2, rot=None, title='Pignon m1,5 z24 sur palonnier')
    P['14_accouplement_T8'] = dict(shape=accouplement(), qty=1, rot=((1, 0, 0), 180), title='Accouplement servo – vis T8')
    P['15_coupon_essai'] = dict(shape=coupon(), qty=1, rot=None, title="Coupon d'essai (à imprimer en premier)")

    I = []  # (nom, groupe, forme, catégorie)
    for i, x in enumerate(COLS):
        I.append((f'Module colonne C{i+1}', 'fixe', P['01_module_casier']['shape'].translate(V(x, 0, Z_CASIER)), 'casier'))
    I.append(('Pied du casier droit', 'fixe', P['02_pied_casier']['shape'].translate(V(78, 0, 0)), 'structure'))
    I.append(('Pied du casier gauche', 'fixe', P['02_pied_casier']['shape'].translate(V(-108, 0, 0)), 'structure'))
    I.append(('Rampe 45° droite', 'fixe', P['03_rampe']['shape'], 'goulotte'))
    I.append(('Rampe 45° gauche', 'fixe', P['03_rampe']['shape'].translate(V(-108, 0, 0)), 'goulotte'))
    I.append(('Bac de réception droit', 'fixe', P['04_bac_droit']['shape'], 'bac'))
    I.append(('Bac de réception gauche', 'fixe', P['04_bac_gauche']['shape'], 'bac'))
    I.append(('Joue de goulotte droite', 'fixe', P['05_joue_droite']['shape'], 'goulotte'))
    I.append(('Joue de goulotte gauche', 'fixe', P['05_joue_gauche']['shape'], 'goulotte'))
    for k in ('06_palier_bas_droit', '06_palier_bas_gauche', '07_support_haut_droit', '07_support_haut_gauche', '08_peigne_Z'):
        I.append((P[k]['title'], 'fixe', P[k]['shape'], 'structure'))
    zz = V(0, 0, Z0)
    I.append(('Traverse Z droite', 'Z', P['09_traverse_droite']['shape'].translate(zz), 'axeZ'))
    I.append(('Traverse Z gauche', 'Z', P['10_traverse_gauche']['shape'].translate(zz), 'axeZ'))
    I.append(('Chariot X', 'X', P['11_chariot_X']['shape'].translate(zz), 'axeX'))
    I.append(('Poussoir', 'Y', P['12_poussoir']['shape'].translate(zz), 'axeY'))
    I.append(('Pignon Y', 'X', place_pinion_y(P['13_pignon_servo']['shape']).translate(zz), 'pignonY'))
    I.append(('Pignon X', 'X', place_pinion_x(P['13_pignon_servo']['shape']).translate(zz), 'pignonX'))
    I.append(('Accouplement servo – T8', 'fixe', P['14_accouplement_T8']['shape'].translate(V(T8[0], T8[1], 278)), 'pignonZ'))

    # achats
    A = []
    A.append(('Socle contreplaqué 360 × 470 × 10', 'fixe', B(-180, 180, -190, 280, -10, 0), 'bois'))
    for x in (-ZR_X, ZR_X):
        A.append(('Tige lisse Z Ø8 × 268', 'fixe', CZ(4, 272, x, ZR_Y, 8), 'tige'))
    A.append(('Vis trapézoïdale T8 pas 8 × 277', 'fixe', CZ(15, 292, T8[0], T8[1], 8), 'vis'))
    A.append(('Plexiglas 3 mm 218 × 125', 'fixe', B(-109.3, 109.3, -88.9, -85.9, 70, 195), 'plexi'))
    A.append(('Servo Parallax : axe Z', 'fixe', frame(servo_body(), *FR_Z), 'servo'))
    A.append(('Palonnier (servo Z)', 'fixe', frame(servo_horn(), *FR_Z), 'servo'))
    for y in (120, 180):
        A.append(('Tige lisse X Ø8 × 274', 'Z', CX(-137, 137, y, Z0 - 30, 8), 'tige'))
    for x in (-ZR_X, ZR_X):
        for z0 in (-55, -31):
            A.append(('Roulement linéaire LM8UU', 'Z', tube_z(Z0 + z0, Z0 + z0 + 24, x, ZR_Y, 15, 8), 'roulement'))
    A.append(('Écrou laiton T8', 'Z', U(CZ(Z0 - 45.5, Z0 - 42, T8[0], T8[1], 22), CZ(Z0 - 42, Z0 - 27, T8[0], T8[1], 10.2)).cut(CZ(Z0 - 50, Z0, T8[0], T8[1], 8)), 'vis'))
    for y in (120, 180):
        A.append(('Roulement linéaire LM8UU', 'X', tube_x(-12, 12, y, Z0 - 30, 15, 8), 'roulement'))
    A.append(('Servo Parallax : axe Y (poussoir)', 'X', frame(servo_body(), *FR_Y).translate(zz), 'servo'))
    A.append(('Palonnier (servo Y)', 'X', frame(servo_horn(), *FR_Y).translate(zz), 'servo'))
    A.append(('Servo Parallax : axe X', 'X', frame(servo_body(), *FR_X).translate(zz), 'servo'))
    A.append(('Palonnier (servo X)', 'X', frame(servo_horn(), *FR_X).translate(zz), 'servo'))
    return P, I, A
