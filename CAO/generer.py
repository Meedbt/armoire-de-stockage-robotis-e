"""V0.3 Parallax 900-00008. Modèle nominal à ajuster sur le servo réel.
Exécuter ce fichier, pas base_v02.py. Millimètres ; axes et courses V0.2 conservés.
"""
import base_v02 as g
from base_v02 import box,cyl,join,cut,holes,hexhole
import cadquery as cq
import csv,json
from cadquery.occ_impl.exporters.assembly import exportAssembly
ROOT=g.ROOT; DOC=g.DOC; STL=g.STL
parts=g.parts; instances=g.instances; hardware=g.hardware
# Interface nominale : corps 40.5 x 20, axe à 10 du petit côté.
# Les lumières couvrent des variations d'entraxe ; à mesurer avant impression générale.
BODY_L=40.5; BODY_W=20.0; SHAFT_OFFSET=10.0
CLEARANCE=0.6
MOUNT_U=(-14.5,35.5); MOUNT_V=(-5.0,5.0)
SLOT_TRAVEL=3.0; SLOT_D=3.6

def slot(u,v,q,L=8):
 d=SLOT_D; h=SLOT_TRAVEL/2
 return join(box(u-h,v-d/2,q,2*h,d,L),cyl(u-h,v,q,d,L),cyl(u+h,v,q,d,L))

def opening(s):
 s=cut(s,box(-SHAFT_OFFSET-CLEARANCE,-BODY_W/2-CLEARANCE,31,BODY_L+2*CLEARANCE,BODY_W+2*CLEARANCE,8))
 for u in MOUNT_U:
  for v in MOUNT_V: s=cut(s,slot(u,v,31))
 return s

def tf(s,axis):
 if axis=='Z': return s.translate((-10,205,446))
 if axis=='X': return s.rotate((0,0,0),(0,1,0),-90).rotate((0,0,0),(1,0,0),-90).translate((-32,230,255.5))
 return s.rotate((0,0,0),(1,0,0),-90).translate((45,414,225.5))

def replace(old,new,s,placements,note,rot=None):
 global instances
 count=parts[old]['qty']; del parts[old]
 instances=[t for t in instances if t[0]!=old]
 assert s.isValid() and len(s.Solids())==1,new
 parts[new]={'shape':s,'note':note,'rot':rot,'qty':count}
 for shape,group in placements: instances.append((new,shape,group))

# Z : entretoises allongées de 8 mm pour dégager le contre-écrou M8.
p=opening(box(-45,-40,32,90,80,6))
p=holes(p,[(u,v,31) for u in [-25,25] for v in [-25,25]],4.5,8)
p=tf(p,'Z')
replace('14_support_moteur_Z','14_support_servo_Z',p,[(p,'fixe')],'Parallax : oreille côté Z=484. Lumières M3 réglables ; vérifier le coupon 46 avant montage.')
s=cut(cyl(0,0,0,12,44),cyl(0,0,-1,4.5,46))
replace('15_entretoise_36','15_entretoise_44',s,[(s.translate((x,y,434)),'fixe') for x in [-35,15] for y in [180,230]],'Remplace la 15 V0.2. Quatre vis M4x65, longueur à vérifier selon rondelles.')

# X : conserver les bras de liaison au chariot ; nouvelle fenêtre de servo décentrée.
p=tf(opening(box(-26,-23,32,72,61,6)),'X')
p=join(p,box(-64,216,217.5,19,8,8),box(-64,248,217.5,19,8,8))
p=holes(p,[(-71,y,221.5) for y in [220,252]],4.5,44,'x')
replace('19_support_moteur_X','19_support_servo_X',p,[(p,'Z')],'Deux M4x40 vers le chariot. Servo sortant vers X négatif ; lumières M3.',((0,0,0),(0,1,0),90))

# Y : allonger les entretoises de 2 mm pour dégager le contre-écrou.
p=opening(box(-45,-25,32,90,82,6))
p=holes(p,[(u,v,31) for u in [-27,27] for v in [-18,50]],4.5,8)
p=tf(p,'Y')
replace('26_support_moteur_Y','26_support_servo_Y',p,[(p,'XZ')],'Servo tourné vers le chariot ; oreilles à Y=452.',((0,0,0),(1,0,0),90))
s=cut(cyl(0,0,0,12,40),cyl(0,0,-1,4.5,42))
replace('27_entretoise_38','27_entretoise_40',s,[(s.rotate((0,0,0),(1,0,0),-90).translate((45+x,406,200.5+z)),'XZ') for x in [-27,27] for z in [-25,43]],'Quatre M4x60 avec rondelles et écrous ; vérifier le dépassement utile.')

# Adaptateur : écrou M8 captif accessible côté vis, contre-écrou extérieur.
# Réutiliser un palonnier 25T compatible avec le servo réel ; aucun spline imprimé.
s=join(cyl(0,0,0,20,18),cyl(0,0,18,38,4))
s=cut(s,cyl(0,0,-1,8.6,20),hexhole(0,0,-0.1,13.4,7.1),cyl(0,0,18,10,5))
for angle in [0,90,180,270]:
 h=join(box(13,-1.2,17,3,2.4,6),cyl(13,0,17,2.4,6),cyl(16,0,17,2.4,6)).rotate((0,0,0),(0,0,1),angle)
 s=cut(s,h)
assert s.isValid() and len(s.Solids())==1
parts['45_adaptateur_palonnier_M8']={'shape':s,'qty':3,'rot':((0,0,0),(1,0,0),180),'note':'Palonnier réel requis : quatre trous au rayon 13 à 16 mm (ou au moins deux opposés), M2. Écrou M8 dans le logement puis contre-écrou extérieur. Bride sur plateau ; supports éventuels sous épaulement intérieur.'}
for axis,group in [('Z','fixe'),('X','Z'),('Y','XZ')]: instances.append(('45_adaptateur_palonnier_M8',tf(s,axis),group))
# Coupon reproduisant EXACTEMENT la fenêtre et les lumières des trois supports.
s=opening(box(-23,-17,32,67,34,6)).translate((23,17,-32))
assert s.isValid() and len(s.Solids())==1
parts['46_coupon_fixation_servo']={'shape':s,'qty':1,'rot':None,'note':'À imprimer en premier. Tester corps, quatre oreilles, passage câble et décalage axe. Dimensions nominales ajustables dans generer.py.'}
parts['39_support_capteur_reglable']['qty']=9
parts['39_support_capteur_reglable']['note']='Réserve de 9 supports : 3 positions X, 3 Z, 2 Y et passage boîte. Implantation et actionneurs à concevoir selon capteurs réels ; pas inclus dans assemblage.'

# Retirer uniquement les références NEMA17 et anciens accouplements.
hardware=[(n,s) for n,s in hardware if not n.startswith(('moteur_','accouplement_','vis_Z_','vis_Y_'))]
hardware += [('vis_Z_M8',cyl(-10,205,135,8,323)),('vis_Y_M8',cyl(45,180,225.5,8,246,'y'))]
# Enveloppes nominales du servo ; trous et oreilles simplifiés, dimensions non certifiées.
body=join(box(-SHAFT_OFFSET,-BODY_W/2,28,BODY_L,BODY_W,36),box(-18,-10,38,8.2,20,2),box(30.3,-10,38,7.7,20,2),cyl(0,0,24,6,4))
for u in MOUNT_U:
 for v in MOUNT_V: body=cut(body,cyl(u,v,37,3.6,4))
horn=cut(cyl(0,0,22,36,2),cyl(0,0,21,3,4))
for angle in [0,90,180,270]:
 import math
 horn=cut(horn,cyl(14.5*math.cos(math.radians(angle)),14.5*math.sin(math.radians(angle)),21,2.4,4))
nut=hexhole(0,0,0.25,13,6.5).cut(cyl(0,0,-1,8.1,9))
jam=hexhole(0,0,-6.5,13,6.5).cut(cyl(0,0,-7,8.1,8))
for axis in ['Z','X','Y']:
 for name,shape in [('servo_enveloppe',body),('palonnier_reference',horn),('ecrou_adaptateur',nut),('contre_ecrou_adaptateur',jam)]: hardware.append((f'{name}_{axis}',tf(shape,axis)))
# Rediriger les références utilisées par le générateur de base.
g.parts=parts; g.instances=instances; g.hardware=hardware

def export():
 rows=[]
 for name,p in parts.items():
  s=p['shape']
  if p['rot']: s=s.rotate(*p['rot'])
  b=s.BoundingBox(); s=s.translate((-b.xmin,-b.ymin,-b.zmin)); b=s.BoundingBox()
  assert max(b.xlen,b.ylen,b.zlen)<=180
  cq.exporters.export(s,str(STL/(name+'.stl')),tolerance=0.08,angularTolerance=0.15)
  rows.append(dict(fichier=name+'.stl',quantite=p['qty'],X_mm=round(b.xlen,2),Y_mm=round(b.ylen,2),Z_mm=round(b.zlen,2),volume_cm3=round(s.Volume()/1000,2),note=p['note']))
 with (DOC/'nomenclature_impression.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter=';');w.writeheader();w.writerows(sorted(rows,key=lambda r:r['fichier']))
 a=cq.Assembly(name='Armoire_Parallax_V03')
 colors={'fixe':(0.68,0.75,0.8),'Z':(0.2,0.45,0.65),'XZ':(0.9,0.55,0.15),'XYZ':(0.85,0.25,0.2)}
 for i,(name,s,group) in enumerate(instances):a.add(s,name=f'{name}_{i}',color=cq.Color(*colors[group]))
 for i,(name,s) in enumerate(hardware):a.add(s,name=f'ACHAT_{name}_{i}',color=cq.Color(.3,.3,.3))
 target=ROOT/'CAO'/'assemblage_Fusion.step'; tmp=target.with_suffix('.tmp.step')
 if tmp.exists():tmp.unlink()
 assert exportAssembly(a,str(tmp)) and tmp.stat().st_size>100000
 tmp.replace(target)
 return rows

if __name__=='__main__':
 rows=export();print('EXPORT',len(rows),sum(r['quantite'] for r in rows),flush=True)
