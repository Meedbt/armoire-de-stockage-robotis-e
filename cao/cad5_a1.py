"""Variante V5 pour Bambu Lab A1 mini (plateau 180 × 180) : traverses hautes coupées en deux et réunies par une éclisse dessous."""
from cadquery import Vector as V
import cad5 as c
from cad import B, CZ, D, U, mirror_x

TOP = c.TOP
SPL = {'ar': (176, 200), 'av': (-42, -18)}        # Y de chaque éclisse
HX = (-18, -8, 8, 18)                              # trous des vis M3 (X)

def eclisse_haute(which):
    y0, y1 = SPL[which]; yc = (y0 + y1) / 2
    return D(B(-25, 25, y0, y1, TOP - 16, TOP - 12), *[CZ(TOP - 17, TOP - 11, x, yc, 3.4) for x in HX])

def moitie(full, which, side):
    y0, y1 = SPL[which]; yc = (y0 + y1) / 2
    s = full.cut(CZ(TOP - 13, TOP + 1, 0, 0, 1)).intersect(B(0 if side > 0 else -200, 200 if side > 0 else 0, -300, 300, 0, 400))
    return D(s, *[CZ(TOP - 13, TOP + 1, x, yc, 3.4) for x in HX if x * side > 0])

def build():
    P, I, A = c.build()
    full_ar, full_av = P['16_traverse_haute_arriere']['shape'], P['17_traverse_haute_avant']['shape']
    for k in ('16_traverse_haute_arriere', '17_traverse_haute_avant'):
        del P[k]
    parts = {
        '16_traverse_haute_arriere_droite': (moitie(full_ar, 'ar', 1), 'Traverse haute arrière, moitié droite'),
        '16_traverse_haute_arriere_gauche': (moitie(full_ar, 'ar', -1), 'Traverse haute arrière, moitié gauche'),
        '17_traverse_haute_avant_droite': (moitie(full_av, 'av', 1), 'Traverse haute avant, moitié droite'),
        '17_traverse_haute_avant_gauche': (moitie(full_av, 'av', -1), 'Traverse haute avant, moitié gauche'),
        '18_eclisse_haute_arriere': (eclisse_haute('ar'), 'Éclisse sous la traverse haute arrière'),
        '18_eclisse_haute_avant': (eclisse_haute('av'), 'Éclisse sous la traverse haute avant'),
    }
    for k, (s, t) in parts.items():
        P[k] = dict(shape=s, qty=1, rot=None, title=t)
    I = [x for x in I if x[0] not in ('Traverse haute arrière', 'Traverse haute avant')]
    for k, (s, t) in parts.items():
        I.append((t, 'fixe', s, 'structure'))
    return P, I, A
