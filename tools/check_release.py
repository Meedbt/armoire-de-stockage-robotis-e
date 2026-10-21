"""Contrôle des fichiers livrés, sans dépendance CAO. Unités : mm.
Ne valide ni les mouvements, ni la résistance, ni l'imprimabilité physique.
"""
from pathlib import Path
from collections import Counter
import csv
import math
import struct

ROOT = Path(__file__).resolve().parents[1]

def check():
    with (ROOT / 'Documentation/nomenclature_impression.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter=';'))
    names = [r['fichier'] for r in rows]
    if len(names) != len(set(names)):
        raise ValueError('Référence dupliquée dans la nomenclature')
    actual = {p.name for p in (ROOT / 'STL').glob('*.stl')}
    if actual != set(names) or not actual:
        raise ValueError(f'Incohérence STL / CSV : {actual.symmetric_difference(names)}')
    qty = 0
    for row in rows:
        name = row['fichier']
        data = (ROOT / 'STL' / name).read_bytes()
        if len(data) < 84:
            raise ValueError(f'{name}: STL tronqué')
        n, = struct.unpack_from('<I', data, 80)
        if n == 0 or len(data) != 84 + 50*n:
            raise ValueError(f'{name}: format STL binaire incorrect')
        vertices = []
        edges = Counter()
        oriented = Counter()
        volume6 = 0.0
        for i in range(n):
            values = struct.unpack_from('<12fH', data, 84 + i*50)
            if not all(math.isfinite(v) for v in values[:12]):
                raise ValueError(f'{name}: coordonnée non finie')
            a,b,c = (tuple(values[j:j+3]) for j in (3,6,9))
            if len({a,b,c}) != 3:
                raise ValueError(f'{name}: triangle dégénéré')
            vertices.extend((a,b,c))
            for u,v in ((a,b),(b,c),(c,a)):
                edges[tuple(sorted((u,v)))] += 1
                oriented[(u,v)] += 1
            volume6 += a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])
        if any(v != 2 for v in edges.values()):
            raise ValueError(f'{name}: arêtes non fermées ou non-manifold')
        if any(oriented[(v,u)] != count for (u,v),count in oriented.items()):
            raise ValueError(f'{name}: orientation incohérente des triangles')
        if volume6 <= 0:
            raise ValueError(f'{name}: volume signé non positif')
        for axis,key in enumerate(('X_mm','Y_mm','Z_mm')):
            lo = min(v[axis] for v in vertices)
            hi = max(v[axis] for v in vertices)
            size = hi-lo
            if lo < -0.01 or size > 180.01:
                raise ValueError(f'{name}: hors du volume 180 mm ou origine négative')
            if abs(size-float(row[key])) > 0.15:
                raise ValueError(f'{name}: dimension incohérente pour {key}')
        count = int(row['quantite'])
        if count < 1:
            raise ValueError(f'{name}: quantité invalide')
        qty += count
    step = (ROOT / 'CAO/assemblage_Fusion.step').read_bytes()
    if not step.startswith(b'ISO-10303-21;') or b'END-ISO-10303-21;' not in step[-100:]:
        raise ValueError('STEP absent, vide ou incomplet (contrôle syntaxique minimal)')
    print(f'OK : {len(rows)} STL, {qty} exemplaires ; arêtes, orientations, volumes signés, dimensions et nomenclature cohérents.')
    print('STEP : enveloppe syntaxique présente ; aucune validation CAO ou physique exécutée ici.')

if __name__ == '__main__':
    check()
