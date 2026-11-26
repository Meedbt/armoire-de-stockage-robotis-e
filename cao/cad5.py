"""Armoire à nacelle V5 — CadQuery. Unités mm. Imprimante visée : Ultimaker 2 Extended+ (223 × 223 × 305).
Repère : X largeur, Y profondeur (face avant du casier Y=0, arrière +), Z hauteur (dessus du socle Z=0).
Repère « chariot » : Z=0 sur l'axe du poussoir. Pose de référence : colonne centrale, rangée basse, poussoir rentré.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cadquery as cq
from cadquery import Vector as V
from cad import B, CX, CY, CZ, U, D, tube_x, tube_z, prism_x, prism_z, frame, mirror_x, gear_points, rack_points, servo_body, servo_horn, servo_cut
import cad4 as c4

BOX = c4.BOX; COLS = c4.COLS
ZC = 70
ROW_AXIS = [ZC + 2 + 10 + 29 * r for r in range(3)]        # 82, 111, 140
Z0 = ROW_AXIS[0]
EXIT = (58, 54.0)                                           # sortie : X, axe
STROKE = c4.STROKE; TIP_REST = c4.TIP_REST
ZR = [(-103, 180), (103, 180), (-103, -30), (103, -30)]
T8 = c4.T8; SZ = c4.SZ; TOP = 160                           # dessus des traverses hautes
# nacelle : pignon m1 14 dents, axe selon Y, centre (x=-10.25, z=-32) dans le repère nacelle
MN = 1.0; ZN = 14; RN = MN * ZN / 2; NX = -10.25; NC = -32.0
FR_N = ((NX, -48.5, NC), (1, 0, 0), (0, 0, -1), (0, 1, 0))  # oreilles du servo en Y=-48.5, corps vers l'arrière

def pinion_m(m, teeth, gh=8.0):
    g = prism_z(gear_points(m, teeth), 0, gh)
    s = U(g, CZ(gh - 0.1, gh + 1.5, 0, 0, 16), CZ(gh + 1.5, gh + 5.5, 0, 0, 36))
    cut = [CZ(-1, gh + 7, 0, 0, 6)]
    for a in range(0, 360, 90):
        cut.append(U(B(11, 16, -1.2, 1.2, gh + 1, gh + 7), CZ(gh + 1, gh + 7, 11, 0, 2.4), CZ(gh + 1, gh + 7, 16, 0, 2.4)).rotate(V(0, 0, 0), V(0, 0, 1), a + 45))
    return D(s, *cut)

# ------------------------------------------------------------------ bâti fixe
def pied():
    s = U(B(0, 18, 0, 6, 0, ZC), B(0, 18, 64, 70, 0, ZC), B(0, 18, 0, 70, ZC - 5, ZC), B(0, 18, 0, 70, 0, 4), B(0, 18, 0, 70, 32, 37))
    h = []
    for y in (15, 55):
        h += [CZ(ZC - 6, ZC + 1, 9, y, 3.4), CZ(-1, 5, 9, y, 4.5), CZ(31, 38, 9, y, 9)]
    return D(s, *h)

def palier(x, y):
    s = U(B(x - 10, x + 10, y - 10, y + 10, 0, 12), B(x - 14, x + 14, y - 14, y + 14, 0, 4))
    return D(s, CZ(2, 13, x, y, 8.2), CX(x, x + 11, y, 8, 2.9), *[CZ(-1, 5, x + dx, y + dy, 4.5) for dx in (-11.5, 11.5) for dy in (-11.5, 11.5)])
def palier_t8():
    x, y = T8
    s = U(CZ(0, 14, x, y, 30), B(x - 22, x + 22, y - 9, y + 9, 0, 4))
    return D(s, CZ(7, 15, x, y, 22.2), CZ(-1, 15, x, y, 10), *[CZ(-1, 5, x + d, y, 4.5) for d in (-18, 18)])

def traverse_haute_ar():
    s = U(B(-115, 115, 168, 205, TOP - 12, TOP))
    s = D(s, *[CZ(TOP - 13, TOP - 1, x, 180, 8.2) for x in (-103, 103)], CZ(TOP - 13, TOP + 1, T8[0], T8[1], 12),
          *[CZ(TOP - 13, TOP + 1, x, y, 4.5) for x in (-40, 20) for y in (175, 200)], *[CZ(TOP - 13, TOP + 1, x, 186, 3.4) for x in (-94, 94)])
    return s
def traverse_haute_av():
    s = B(-115, 115, -42, -18, TOP - 12, TOP)
    return D(s, *[CZ(TOP - 13, TOP - 1, x, -30, 8.2) for x in (-103, 103)], *[CZ(TOP - 13, TOP + 1, x, -24, 3.4) for x in (-94, 94)],
             *[CY(-43, -34, x, TOP - 6, 3.4) for x in (-106, 106)])
def longeron_haut():   # droit, X 88..100
    s = B(88, 100, -24, 192, TOP, TOP + 8)
    return D(s, *[CZ(TOP - 1, TOP + 9, 94, y, 3.4) for y in (-24 + 6, 186)])
def socle_z_haut():
    return c4.socle_z().translate(V(0, 0, TOP))

def montant():   # droit : poteau de façade + bras vers la traverse haute avant
    s = U(B(104, 112, -94, -84, 0, TOP), B(104, 112, -94, -42, TOP - 12, TOP), B(100, 116, -100, -78, 0, 4))
    return D(s, B(103.9, 106, -90.6, -87.4, 4, TOP - 11), *[CZ(-1, 5, 108, y, 4.5) for y in (-96, -80)], *[CY(-50, -40, 106, TOP - 6, 3.4)])
HATCH = (28, 92, 38, 92)
def cadre_trappe():
    x0, x1, z0, z1 = HATCH
    s = D(B(x0 - 6, x1 + 6, -94, -90.6, z0 - 6, z1 + 6), B(x0, x1, -95, -89, z0, z1))
    return s

# ------------------------------------------------------------------ cadre Z (repère chariot)
def eclisse():   # droite, sur la face extérieure des longerons, à la coupe Y=60
    return D(B(100, 104, 36, 84, -26, -10), *[CX(99, 105, y, -18, 3.4) for y in (48, 72)])
def longeron_z():   # droit, X 92..100
    s = U(B(92, 100, -82, -42, -48, -10), B(92, 100, -42, -20, -26, -10), B(92, 100, -20, 0, -48, -10), B(92, 100, 0, 192, -26, -10),
          *[CZ(-24, 0, 103, y, 25) for y in (180, -30)], *[B(100, 103, y - 12, y + 12, -24, -10) for y in (180, -30)],
          *[CX(84, 96, y, -18, 16) for y in (90, 150)], *[CX(84, 96, -12, z, 16) for z in (-22, -40)])
    c = [*[CZ(-50, 1, 103, y, 15.2) for y in (180, -30)], *[CX(91, 106, y, -18, 3.4) for y in (48, 72)], *[CX(84, 94, y, -18, 8.2) for y in (90, 150)], *[CX(84, 94, -12, z, 8.2) for z in (-22, -40)],
         *[CZ(-27, -9, 97, y, 2.9) for y in (90, 150)], *[CY(-20, -4, 97, z, 2.9) for z in (-22, -40)],
         *[CX(91, 101, y, z, 3.4) for y in (-76, -72) for z in (-44,)], *[CX(91, 101, y, -20, 3.4) for y in (74, 189, 196)],
         *[CX(91, 101, 75, z, 3.4) for z in (-4,)]]
    return D(s, *c)

def rack_x_ar(x0, x1):
    pts = [(s, 80 + h) for s, h in rack_points(x0, x1, 1.5)]
    return prism_z(pts, 8, 16)
def poutre_x_ar():   # crémaillère X du chariot arrière + peigne, entre les longerons
    s = U(B(-92, 92, 72, 80, 6, 17), rack_x_ar(-87, 87), B(-92, 92, 78, 80, 16.5, 28),
          B(-92, -84, 72, 77, -26, 17), B(84, 92, 72, 77, -26, 17))
    return D(s, *[B(x - 2, x + 2, 77, 81, 19, 29) for x in COLS], *[CX(-93, 93, 74.5, z, 3.4) for z in (-20, -4)])

def traverse_z_ar():   # écrou T8
    s = U(B(-92, 92, 188, 198, -26, -14), CZ(-26, -14, T8[0], T8[1], 28))
    h = [CZ(-30, -10, T8[0], T8[1], 10.5), *[CX(-93, 93, y, -20, 3.4) for y in (189 + 2, 196 - 2)]]
    h += [CZ(-30, -10, T8[0] + 8 * math.cos(math.radians(a)), T8[1] + 8 * math.sin(math.radians(a)), 3.4) for a in (45, 135, 225, 315)]
    return D(s, *h)

def rack_x_av(x0, x1):   # crémaillère m1 dents vers le haut, bande Y -78..-70
    pts = [(s, -40.25 + h) for s, h in rack_points(x0, x1, MN)]
    return cq.Workplane("XZ", origin=(0, -70, 0)).polyline(pts).close().extrude(8).val()
def traverse_z_av():   # crémaillère de la nacelle + peigne
    s = U(B(-92, 92, -82, -68, -47, -40.25), rack_x_av(-82, 70), B(-92, 92, -82, -80.5, -40.3, -30))
    return D(s, *[B(x + 24.5, x + 28.5, -83, -80, -39, -29) for x in COLS], *[CX(-93, 93, y, -44, 3.4) for y in (-76, -72)])

# ------------------------------------------------------------------ nacelle (repère chariot, centrée en X=0)
def nacelle():
    y0, y1 = -68, -1.5
    s = U(B(-31, 31, y0, y1, -12.5, -10.5), B(-31, -29.5, y0, y1, -12.5, -2.5), B(29.5, 31, y0, y1, -12.5, -2.5),
          B(-31, 31, y0, y0 + 1.5, -12.5, -4.5),
          B(-31, 31, -48.5, -42.5, -46, -12.5), B(-31, 31, -26, -2, -14, -12.5),
          *[CX(-12, 12, -12, z, 19) for z in (-22, -40)], B(-14, 14, -21, -3, -40, -12.5),
          B(-31, -25, -48.5, -26, -46, -12.5), B(25, 31, -48.5, -26, -46, -12.5),
          B(22, 31, -86.5, -76, -36, -28), B(28, 31, -76, -48.5, -36, -28))
    s = D(s, prism_x([(y1 - 3, -10.4), (y1 + 0.1, -10.4), (y1 + 0.1, -11.6)], -29.4, 29.4))
    c = [*[CX(-13, 13, -12, z, 15.2) for z in (-22, -40)], *[CX(-40, 40, -12, z, 10) for z in (-22, -40)],
         frame(servo_cut(-1, 7), *FR_N), B(21, 32, -83, -79.5, -37, -29.5), B(-8, 8, -40, -28, -11, -10)]
    return D(s, *c)

# ------------------------------------------------------------------ inventaire
def build():
    P = {}
    def add(k, shape, qty, rot, title): P[k] = dict(shape=shape, qty=qty, rot=rot, title=title)
    zz = V(0, 0, Z0)
    add('01_casier', c4.casier(), 1, ((1, 0, 0), 90), 'Casier 3 × 3 monobloc')
    add('02_pied_casier', pied(), 2, ((0, 1, 0), -90), 'Pied du casier')
    add('03_nacelle', nacelle(), 1, None, 'Nacelle (reçoit la boîte)')
    L = longeron_z(); cutF = B(0, 200, -100, 60, -100, 100); cutR = B(0, 200, 60, 300, -100, 100)
    add('04_longeron_Z_avant_droit', L.intersect(cutF), 1, ((0, 1, 0), 90), 'Longeron Z avant droit')
    add('04_longeron_Z_avant_gauche', mirror_x(L.intersect(cutF)), 1, ((0, 1, 0), -90), 'Longeron Z avant gauche')
    add('04_longeron_Z_arriere_droit', L.intersect(cutR), 1, ((0, 1, 0), 90), 'Longeron Z arrière droit')
    add('04_longeron_Z_arriere_gauche', mirror_x(L.intersect(cutR)), 1, ((0, 1, 0), -90), 'Longeron Z arrière gauche')
    add('04_eclisse_longeron', eclisse(), 2, ((0, 1, 0), 90), 'Éclisse de jonction des longerons')
    add('05_poutre_X_arriere', poutre_x_ar(), 1, ((1, 0, 0), -90), 'Poutre X arrière (crémaillère du chariot)')
    add('06_traverse_Z_avant', traverse_z_av(), 1, None, 'Traverse avant du cadre Z (crémaillère nacelle)')
    add('07_traverse_Z_arriere', traverse_z_ar(), 1, None, 'Traverse arrière du cadre Z (écrou T8)')
    add('08_chariot_arriere', c4.chariot(), 1, None, 'Chariot arrière (poussoir)')
    add('09_poussoir', c4.poussoir(), 1, ((0, 1, 0), 90), 'Poussoir à crémaillère')
    add('10_pignon_24', c4.pinion(24, 8), 2, None, 'Pignon 24 dents (X arrière, servo Z)')
    add('11_pignon_16', c4.pinion(16, 6.5), 1, None, 'Pignon 16 dents (poussoir)')
    add('12_pignon_m1_14', pinion_m(MN, ZN, 8), 1, None, 'Pignon m1 14 dents (nacelle)')
    add('13_engrenage_T8', c4.engrenage_t8(), 1, None, 'Engrenage T8 + disque codeur')
    add('14_palier', palier(0, 0), 4, None, 'Palier bas de tige Z')
    add('15_palier_T8', palier_t8().translate(V(-T8[0], -T8[1], 0)), 1, None, 'Palier bas de la vis T8')
    add('16_traverse_haute_arriere', traverse_haute_ar(), 1, None, 'Traverse haute arrière')
    add('17_traverse_haute_avant', traverse_haute_av(), 1, None, 'Traverse haute avant')
    add('19_socle_servo_Z', c4.socle_z(), 1, None, 'Socle du servo Z (sur la traverse haute)')
    add('20_montant_droit', montant(), 1, ((0, 1, 0), 90), 'Montant de façade droit')
    add('20_montant_gauche', mirror_x(montant()), 1, ((0, 1, 0), -90), 'Montant de façade gauche')
    add('21_cadre_trappe', cadre_trappe(), 1, ((1, 0, 0), 90), 'Cadre de la trappe')
    add('22_coupon_essai', c4.coupon(), 1, None, "Coupon d'essai")

    I = []
    I.append(('Casier 3 × 3', 'fixe', P['01_casier']['shape'].translate(V(0, 0, ZC)), 'casier'))
    I.append(('Pied du casier droit', 'fixe', P['02_pied_casier']['shape'].translate(V(70, 0, 0)), 'structure'))
    I.append(('Pied du casier gauche', 'fixe', P['02_pied_casier']['shape'].translate(V(-88, 0, 0)), 'structure'))
    for x, y in ZR:
        I.append(('Palier bas de tige Z', 'fixe', palier(x, y), 'structure'))
    I.append(('Palier bas de la vis T8', 'fixe', palier_t8(), 'structure'))
    I.append(('Traverse haute arrière', 'fixe', P['16_traverse_haute_arriere']['shape'], 'structure'))
    I.append(('Traverse haute avant', 'fixe', P['17_traverse_haute_avant']['shape'], 'structure'))
    I.append(('Socle du servo Z', 'fixe', socle_z_haut(), 'structure'))
    I.append(('Montant de façade droit', 'fixe', P['20_montant_droit']['shape'], 'goulotte'))
    I.append(('Montant de façade gauche', 'fixe', P['20_montant_gauche']['shape'], 'goulotte'))
    I.append(('Cadre de la trappe', 'fixe', P['21_cadre_trappe']['shape'], 'bac'))
    I.append(('Pignon du servo Z', 'fixe', frame(P['10_pignon_24']['shape'], (SZ[0], SZ[1], 59.5 + TOP), (1, 0, 0), (0, -1, 0), (0, 0, -1)), 'pignonZs'))
    I.append(('Engrenage T8 + codeur', 'fixe', P['13_engrenage_T8']['shape'].translate(V(T8[0], T8[1], 42 + TOP)), 'pignonZ'))
    for k, n in (('04_longeron_Z_avant_droit', 'Longeron Z avant droit'), ('04_longeron_Z_avant_gauche', 'Longeron Z avant gauche'),
                 ('04_longeron_Z_arriere_droit', 'Longeron Z arrière droit'), ('04_longeron_Z_arriere_gauche', 'Longeron Z arrière gauche')):
        I.append((n, 'Z', P[k]['shape'].translate(zz), 'axeZ'))
    I.append(('Éclisse droite', 'Z', P['04_eclisse_longeron']['shape'].translate(zz), 'axeZ'))
    I.append(('Éclisse gauche', 'Z', mirror_x(P['04_eclisse_longeron']['shape']).translate(zz), 'axeZ'))
    I.append(('Poutre X arrière', 'Z', P['05_poutre_X_arriere']['shape'].translate(zz), 'axeZ'))
    I.append(('Traverse avant du cadre Z', 'Z', P['06_traverse_Z_avant']['shape'].translate(zz), 'axeZ'))
    I.append(('Traverse arrière du cadre Z', 'Z', P['07_traverse_Z_arriere']['shape'].translate(zz), 'axeZ'))
    I.append(('Chariot arrière', 'X', P['08_chariot_arriere']['shape'].translate(zz), 'axeX'))
    I.append(('Poussoir', 'Y', P['09_poussoir']['shape'].translate(zz), 'axeY'))
    I.append(('Pignon X arrière', 'X', P['10_pignon_24']['shape'].translate(V(c4.PX[0], c4.PX[1], 8)).translate(zz), 'pignonX'))
    I.append(('Pignon du poussoir', 'X', P['11_pignon_16']['shape'].translate(V(c4.PY[0], c4.PY[1], -5)).translate(zz), 'pignonY'))
    I.append(('Nacelle', 'N', P['03_nacelle']['shape'].translate(zz), 'nacelle'))
    I.append(('Pignon de la nacelle', 'N', frame(P['12_pignon_m1_14']['shape'], (NX, -78, NC), (1, 0, 0), (0, 0, -1), (0, 1, 0)).translate(zz), 'pignonN'))

    A = []
    A.append(('Socle contreplaqué 236 × 315 × 10', 'fixe', B(-118, 118, -100, 215, -10, 0), 'bois'))
    for x, y in ZR:
        A.append(('Tige lisse Z Ø8 × 157', 'fixe', CZ(2, TOP - 1, x, y, 8), 'tige'))
    A.append(('Vis trapézoïdale T8 pas 8 × 205', 'fixe', CZ(7, 59.5 + TOP - 8, T8[0], T8[1], 8), 'vis'))
    x0, x1, z0, z1 = HATCH
    A.append(('Plexiglas 3 mm 210 × 145 (trappe découpée)', 'fixe', D(B(-105, 105, -90.5, -87.5, 6, TOP - 12), B(x0, x1, -91, -87, z0, z1)), 'plexi'))
    A.append(('Servo Parallax : axe Z', 'fixe', frame(servo_body(), *c4.FR_Z).translate(V(0, 0, TOP)), 'servo'))
    A.append(('Palonnier (servo Z)', 'fixe', frame(servo_horn(), *c4.FR_Z).translate(V(0, 0, TOP)), 'servo'))
    for y in (90, 150):
        A.append(('Tige lisse X arrière Ø8 × 186', 'Z', CX(-93, 93, y, Z0 - 18, 8), 'tige'))
    for z in (-22, -40):
        A.append(('Tige lisse X avant Ø8 × 186', 'Z', CX(-93, 93, -12, Z0 + z, 8), 'tige'))
    for x, y in ZR:
        A.append(('Roulement linéaire LM8UU (Z)', 'Z', tube_z(Z0 - 24, Z0, x, y, 15, 8), 'roulement'))
    A.append(('Écrou laiton T8', 'Z', U(CZ(Z0 - 29.5, Z0 - 26, T8[0], T8[1], 22), CZ(Z0 - 26, Z0 - 11, T8[0], T8[1], 10.2)).cut(CZ(Z0 - 35, Z0, T8[0], T8[1], 8)), 'vis'))
    for y in (90, 150):
        A.append(('Roulement linéaire LM8UU (chariot)', 'X', tube_x(-12, 12, y, Z0 - 18, 15, 8), 'roulement'))
    for z in (-22, -40):
        A.append(('Roulement linéaire LM8UU (nacelle)', 'N', tube_x(-12, 12, -12, Z0 + z, 15, 8), 'roulement'))
    zz = V(0, 0, Z0)
    A.append(('Servo Parallax : poussoir', 'X', frame(servo_body(), *c4.FR_Y).translate(zz), 'servo'))
    A.append(('Palonnier (poussoir)', 'X', frame(servo_horn(), *c4.FR_Y).translate(zz), 'servo'))
    A.append(('Servo Parallax : X arrière', 'X', frame(servo_body(), *c4.FR_X).translate(zz), 'servo'))
    A.append(('Palonnier (X arrière)', 'X', frame(servo_horn(), *c4.FR_X).translate(zz), 'servo'))
    A.append(('Servo Parallax : X nacelle', 'N', frame(servo_body(), *FR_N).translate(zz), 'servo'))
    A.append(('Palonnier (X nacelle)', 'N', frame(servo_horn(), *FR_N).translate(zz), 'servo'))
    return P, I, A
