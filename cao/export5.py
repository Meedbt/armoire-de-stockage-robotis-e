"""Construit, vérifie et exporte : STL d'impression orientés, STL d'assemblage, STEP, nomenclature, rapport."""
import json, csv, sys, time, math, itertools
from pathlib import Path
import cadquery as cq
from cadquery import Vector as V
import cad5 as cad

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'out')
(OUT / 'STL_impression').mkdir(parents=True, exist_ok=True)
(OUT / 'assemblage').mkdir(parents=True, exist_ok=True)
t0 = time.time()
P, I, A = cad.build()
print('build', round(time.time() - t0, 1), 's', flush=True)

report = {'pieces': [], 'collisions': [], 'positions': 0}
rows = []
for name, p in P.items():
    s = p['shape']
    assert s.isValid(), name
    n = len(s.Solids())
    assert n == 1, (name, n)
    if p['rot']:
        s = s.rotate(V(0, 0, 0), V(*p['rot'][0]), p['rot'][1])
    bb = s.BoundingBox()
    s = s.translate(V(-bb.xmin, -bb.ymin, -bb.zmin)); bb = s.BoundingBox()
    fits = bb.zlen <= 300 and ((bb.xlen <= 220 and bb.ylen <= 220) or (max(bb.xlen, bb.ylen) <= 300 and bb.xlen + bb.ylen <= 305))
    diag = fits and not (bb.xlen <= 220 and bb.ylen <= 220)
    vol = s.Volume() / 1000
    cq.exporters.export(s, str(OUT / 'STL_impression' / f'{name}.stl'), tolerance=0.05, angularTolerance=0.12)
    rows.append(dict(fichier=f'{name}.stl', piece=p['title'], quantite=p['qty'], X_mm=round(bb.xlen, 1), Y_mm=round(bb.ylen, 1),
                     Z_mm=round(bb.zlen, 1), volume_cm3=round(vol, 1)))
    rows[-1]['pose'] = 'diagonale' if diag else 'normale'
    report['pieces'].append(dict(nom=name, valide=True, imprimable=fits, diagonale=diag, dims=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]))
    print(name, rows[-1]['X_mm'], rows[-1]['Y_mm'], rows[-1]['Z_mm'], ('OK diag' if diag else 'OK') if fits else 'TROP GRAND', flush=True)

with open(OUT / 'nomenclature_impression.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter=';'); w.writeheader(); w.writerows(rows)

# ---------- collisions dans 9 cases × poussoir rentré / sorti
inst = [(n, g, s, c) for n, g, s, c in I + A]
skip = lambda a, b: ({a[3], b[3]} in ({'pignonX', 'axeZ'}, {'pignonY', 'axeY'}) or 'tige' in (a[3], b[3]) and 'roulement' in (a[3], b[3])
                     or {a[3], b[3]} == {'pignonX', 'servo'} or {a[3], b[3]} == {'pignonY', 'servo'} or {a[3], b[3]} == {'pignonZ', 'servo'}
                     or {a[3], b[3]} == {'vis', 'pignonZ'} or {a[3], b[3]} == {'pignonZs', 'pignonZ'} or {a[3], b[3]} == {'pignonZs', 'servo'} or {a[3], b[3]} == {'pignonN', 'axeZ'} or {a[3], b[3]} == {'pignonN', 'servo'} or {a[3], b[3]} == {'bois', 'structure'} or {a[3], b[3]} == {'bois', 'goulotte'} or {a[3], b[3]} == {'bois', 'bac'})
def moved(g, col, row, push):
    if col == 'S':
        dx, dz = cad.EXIT[0], cad.EXIT[1] - cad.Z0
    else:
        dz = cad.ROW_AXIS[row] - cad.Z0; dx = cad.COLS[col]
    return {'fixe': V(0, 0, 0), 'Z': V(0, 0, dz), 'X': V(dx, 0, dz), 'N': V(dx, 0, dz), 'Y': V(dx, -push, dz)}[g]
poses = [(c, r, p) for c in range(3) for r in range(3) for p in (0, cad.STROKE)] + [('S', 0, 0)]
for col, row, push in poses:
    objs = [(n, g, s.translate(moved(g, col, row, push)), c) for n, g, s, c in inst]
    bbs = [o[2].BoundingBox() for o in objs]
    for i, j in itertools.combinations(range(len(objs)), 2):
        a, b = objs[i], objs[j]
        if a[1] == b[1] and a[1] == 'fixe' and (push or col or row):
            continue
        if skip(a, b):
            continue
        A_, B_ = bbs[i], bbs[j]
        if min(A_.xmax, B_.xmax) - max(A_.xmin, B_.xmin) < 0.01 or min(A_.ymax, B_.ymax) - max(A_.ymin, B_.ymin) < 0.01 or min(A_.zmax, B_.zmax) - max(A_.zmin, B_.zmin) < 0.01:
            continue
        v = a[2].intersect(b[2]).Volume()
        if v > 0.5:
            report['collisions'].append(dict(pose=[col if col == 'S' else col + 1, row + 1, push], a=a[0], b=b[0], volume_mm3=round(v, 1)))
    report['positions'] += 1
    print('pose', col, row + 1, push, 'collisions', len(report['collisions']), flush=True)
(OUT / 'rapport_verification.json').write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding='utf-8')

# ---------- assemblage : un STL par instance + manifeste
man = []
for k, (n, g, s, c) in enumerate(inst):
    fn = f'a{k:02d}.stl'
    cq.exporters.export(s, str(OUT / 'assemblage' / fn), tolerance=0.08, angularTolerance=0.2)
    man.append(dict(file=fn, name=n, group=g, cat=c))
meta = dict(cols=cad.COLS, rows=cad.ROW_AXIS, z0=cad.Z0, stroke=cad.STROKE, box=cad.BOX, zc=cad.ZC, tip=cad.TIP_REST, exit=list(cad.EXIT),
            pinY=[cad.c4.PY[0], cad.c4.PY[1]], pinX=[cad.c4.PX[0], cad.c4.PX[1]], t8=[cad.T8[0], cad.T8[1]], sz=[cad.SZ[0], cad.SZ[1]], pinN=[cad.NX, cad.NC], rn=cad.RN, top=cad.TOP)
(OUT / 'assemblage' / 'manifest.json').write_text(json.dumps(dict(parts=man, meta=meta), ensure_ascii=False), encoding='utf-8')

# ---------- STEP
asm = cq.Assembly(name='Armoire_V5')
for k, (n, g, s, c) in enumerate(inst):
    asm.add(s, name=f'{k:02d}_{n}'.replace(' ', '_'))
asm.save(str(OUT / 'armoire_V5_assemblage.step'))
print('done', round(time.time() - t0, 1), 's; collisions:', len(report['collisions']))
