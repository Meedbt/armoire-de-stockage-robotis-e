"""Avant-projet mécanique V0.2. CadQuery 2.7. Unités : mm.
Les STL sont normalisés sur le plateau ; les positions sont conservées dans le STEP.
Ce générateur est la source géométrique, pas un script Fusion.
"""
from pathlib import Path
import math, json, csv
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
STL=ROOT/'STL'; STL.mkdir(exist_ok=True)
DOC=ROOT/'Documentation'; DOC.mkdir(exist_ok=True)
V=cq.Vector
parts={}; instances=[]; hardware=[]; basefix=[]

def box(x,y,z,a,b,c): return cq.Solid.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,d,L,axis='z'):
    return cq.Solid.makeCylinder(d/2,L,V(x,y,z),V(*{'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[axis]))
def join(*ss):
    s=ss[0]
    for t in ss[1:]: s=s.fuse(t)
    return s.clean()
def cut(s,*ss):
    for t in ss: s=s.cut(t)
    return s.clean()
def holes(s,coords,d,L,axis='z'):
    return cut(s,*[cyl(*p,d,L,axis) for p in coords])
def hexhole(x,y,z,af,L,axis='z'):
    s=cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(L).val()
    if axis=='x': s=s.rotate((0,0,0),(0,1,0),90)
    if axis=='y': s=s.rotate((0,0,0),(1,0,0),-90)
    return s.translate((x,y,z))
def mirrorx(s,offset=270): return s.mirror('YZ').translate((offset,0,0))
def reg(name,s,note='',rot=None):
    assert s.isValid(),name+' invalide'
    assert len(s.Solids())==1,(name,len(s.Solids()))
    parts[name]={'shape':s,'note':note,'rot':rot,'qty':0}
    return s
def put(name,s=None,shift=(0,0,0),group='fixe'):
    p=parts[name]; p['qty']+=1
    instances.append((name,(s or p['shape']).translate(shift),group))
def item(name,s,note='',rot=None,group='fixe'):
    reg(name,s,note,rot); put(name,group=group); return s
def screw_pilots(s,coords,L=12,axis='z',d=2.6): return holes(s,coords,d,L,axis)

# 01 - CASES : même enveloppe que V0.1, trous latéraux et couvercle à languettes.
body=join(box(0,0,0,90,100,3),box(0,0,0,3,100,62),box(87,0,0,3,100,62),box(0,97,0,90,3,62),
          box(10,0,3,3,97,6),box(77,0,3,3,97,6),box(13,95,3,8,5,8),box(69,95,3,8,5,8))
body=cut(body,box(30,96,8.5,30,5,24))
body=holes(body,[(x,y,z) for x in [-1,86] for y in [20,80] for z in [15,50]],3.4,5,'x')
body=holes(body,[(x,40,35) for x in [-1,86]],3.4,5,'x')
reg('01_case',body,'Fond sur plateau. Trou arrière : pont de 30 mm à examiner au tranchage. 9 exemplaires.')
lid=join(box(0,0,62,90,100,3),box(3.3,30,58,2,40,4),box(84.7,30,58,2,40,4))
reg('02_couvercle',lid,'Imprimer face supérieure contre le plateau ; languettes vers le haut.',((0,0,0),(1,0,0),180))
for c in range(3):
 for r in range(3):
    put('01_case',shift=(90*c,0,180+65*r)); put('02_couvercle',shift=(90*c,0,180+65*r))

# Éclisses : leur grand axe est Z, vis suivant X.
link=holes(box(0,-6,-20,4,12,40),[(-1,0,-15),(-1,0,15)],3.4,6,'x')
reg('03_liaison_cases',link,'2 vis M3x12 + écrous par éclisse ; liaison entre rangées.',((0,0,0),(0,1,0),90))
for x in [-4,270]:
 for y in [20,80]:
  for z in [245,310]: put('03_liaison_cases',shift=(x,y,z))

# 02 - SOCLE ET PIEDS. Fixations M4 aux tuiles, écrous captifs dessous.
lower=join(box(-30,0,6,40,40,6),box(-20,10,12,20,20,84))
lower=holes(lower,[(x,y,5) for x in [-24,4] for y in [6,34]],4.5,8)
lower=holes(lower,[(-21,20,86)],2.6,22,'x')
upper=join(box(-20,10,96,20,20,84),box(-4,10,180,4,20,25))
upper=holes(upper,[(-21,20,106)],2.6,22,'x')
upper=holes(upper,[(-5,20,195)],3.4,6,'x')
reg('04_pied_bas_gauche',lower,'Deux exemplaires. Pied avec embase M4.')
reg('05_pied_haut_gauche',upper,'Deux exemplaires. Vis M3x12 entre oreille et case.')
reg('06_pied_bas_droit',mirrorx(lower),'Deux exemplaires.')
reg('07_pied_haut_droit',mirrorx(upper),'Deux exemplaires.')
for dy in [0,60]:
 for nm in ['04_pied_bas_gauche','05_pied_haut_gauche','06_pied_bas_droit','07_pied_haut_droit']: put(nm,shift=(0,dy,0))
 for x in [-24,4,266,294]:
  for y in [6+dy,34+dy]: basefix.append((x,y))
splice=holes(box(0,-10,-20,4,20,40),[(-1,0,-10),(-1,0,10)],3.4,6,'x')
reg('08_eclisse_structure',splice,'M3x10 dans avant-trous imprimés. Serrer modérément.',((0,0,0),(0,1,0),90))
for x in [-24,0,266,290]:
 for y in [20,80]: put('08_eclisse_structure',shift=(x,y,96))

# Colonnes creuses 30x40x140 ; six tronçons.
post=cut(box(-60,170,6,30,40,140),box(-54,176,5,18,28,142))
post=holes(post,[(-61,190,z) for z in [16,136]],2.6,32,'x')
# Trous pour les consoles inférieures et supérieures (répliqués aux trois niveaux).
post=holes(post,[(-45,169,z) for z in [130,134]],3.3,8,'y')
reg('09_colonne_140',post,'Trois segments par colonne. Tube vertical ; quatre périmètres minimum à tester.')
for xshift in [0,360]:
 for dz in [0,140,280]: put('09_colonne_140',shift=(xshift,0,dz))
 for zz in [146,286]:
  for xx in [-64+xshift,-30+xshift]: put('08_eclisse_structure',shift=(xx,190,zz))
# Équerres de fixation des colonnes au socle.
angle=join(box(0,0,0,30,30,5),box(0,25,0,30,5,30))
angle=holes(angle,[(7,10,-1),(23,10,-1)],4.5,7)
angle=holes(angle,[(7,24,20),(23,24,20)],3.4,7,'y')
reg('10_equerre_colonne',angle,'Deux équerres par colonne. M4 au socle ; M3 avec écrous aux tubes.')
for dx in [0,360]:
 put('10_equerre_colonne',shift=(-60+dx,140,6))
 back=angle.rotate((15,15,0),(15,15,1),180).translate((-60+dx,210,6))
 put('10_equerre_colonne',s=back)
 for x in [-53+dx,-37+dx]:
  for y in [150,230]: basefix.append((x,y))
# trous de fixation des équerres dans les tubes (le modèle commun porte les mêmes trous aux étages).
p=parts['09_colonne_140']['shape']
p=holes(p,[(x,169,26) for x in [-53,-37]],3.4,42,'y')
parts['09_colonne_140']['shape']=p
instances=[(n,p.translate((0 if s.BoundingBox().xmin<0 else 360,0,round((s.BoundingBox().zmin-6)/140)*140)) if n=='09_colonne_140' else s,g) for n,s,g in instances]

# Consoles des guides Z. Gauche : vis à X=-10,Y=205. Droite : guidage uniquement.
def anchor(top=False,left=True):
 z=426 if top else 142
 s=box(-65,130,z,95,115,8)
 if not top: s=cut(s,box(-65,169,z-1,40,42,10))
 s=join(s,box(-60,164,z-22,30,6,30))
 s=holes(s,[(-45,163,z-12)],4.5,8,'y')
 s=holes(s,[(-25,145,z-1)],8.3,10)
 # Vis de blocage du guide, avant-trou M3.
 s=holes(s,[(-25,129,z+4)],2.6,18,'y')
 if left:
  s=holes(s,[(-10,205,z-1)],13,10)
  s=cut(s,cyl(-10,205,z+1,22.3,8))
  s=holes(s,[(x,y,z-1) for x in [-21,1] for y in [194,216]],2.6,10)
 if top and left:
  s=holes(s,[(x,y,z-1) for x in [-35,15] for y in [180,230]],4.5,10)
 return s if left else mirrorx(s)
for top in [False,True]:
 for left in [True,False]:
  item(('11' if not top else '12')+'_console_Z_'+('gauche' if left else 'droite'),anchor(top,left),'Console à fixer au tube avec une vis M4x16 ; trou du tube à finir à Ø4,5 si nécessaire.')

def cap():
 s=box(-15,-15,0,30,30,3)
 return holes(s,[(0,0,-1)],13,5).cut(cq.Compound.makeCompound([cyl(x,y,-1,3.4,5) for x in [-11,11] for y in [-11,11]]))
reg('13_retenue_roulement',cap(),'Retient la bague extérieure du 608 ; ne pas bloquer la bague intérieure.')
for z in [150,434]: put('13_retenue_roulement',shift=(-10,205,z))

def motorplate_z(cx,cy,z,w=80,h=80):
 s=box(cx-w/2,cy-h/2,z,w,h,6)
 s=holes(s,[(cx,cy,z-1)],23,8)
 return holes(s,[(cx+i,cy+j,z-1) for i in [-15.5,15.5] for j in [-15.5,15.5]],3.4,8)
mp=motorplate_z(-10,205,470)
mp=holes(mp,[(x,y,469) for x in [-35,15] for y in [180,230]],4.5,8)
item('14_support_moteur_Z',mp,'NEMA17 : entraxe 31, centrage 23. Moteur posé au-dessus ; arbre dirigé vers le bas.')
sp=cut(cyl(0,0,0,12,36),cyl(0,0,-1,4.5,38))
reg('15_entretoise_36',sp,'Quatre entretoises pour le moteur Z ; boulons M4x55.')
for x in [-35,15]:
 for y in [180,230]: put('15_entretoise_36',shift=(x,y,434))

# 03 - PORTIQUE MOBILE. Coordonnées locales Z=hauteur du poussoir.
end=box(-45,130,-45,51,126,115)
end=cut(end,box(-66,168,-46,42,44,117))
end=holes(end,[(-25,145,-46)],8.5,117)
end=holes(end,[(-46,165,z) for z in [-30,30]],8.3,57,'x')
end=holes(end,[(-46,230,55)],13,57,'x')
end=cut(end,cyl(-46,230,55,26,26,'x'),cyl(-1,230,55,22.3,8,'x'))
end=holes(end,[(-4,y,z) for y in [219,241] for z in [44,66]],2.6,11,'x')
end=holes(end,[(-46,y,21) for y in [220,252]],3.3,17,'x')
end=holes(end,[(-10,205,-46)],8.8,117)
end=cut(end,hexhole(-10,205,62.8,13.4,8))
end=holes(end,[(x,y,59) for x in [-21,1] for y in [194,216]],2.6,12)
end=holes(end,[(-5,165,-46),(-5,165,30)],2.6,17)
reg('16_chariot_Z_gauche',end,'Alésage vertical Ø8,5 à calibrer ; écrou M8 en haut ; logements 608 côté intérieur.',((0,0,0),(1,0,0),90))
right=mirrorx(end)
# trou M8 vertical surnuméraire à droite sans fonction ; géométrie miroir pour fabrication homogène.
reg('17_chariot_Z_droit',right,'Même guidage ; logement M8 vertical laissé vide.',((0,0,0),(1,0,0),90))
put('16_chariot_Z_gauche',shift=(0,0,200.5),group='Z'); put('17_chariot_Z_droit',shift=(0,0,200.5),group='Z')
nutcap=holes(box(-15,-15,0,30,30,3),[(0,0,-1)],8.8,5)
nutcap=holes(nutcap,[(x,y,-1) for x in [-11,11] for y in [-11,11]],3.4,5)
reg('18_retenue_ecrou_M8',nutcap,'Écrou DIN934 13 sur plats, 6,5 épaisseur ; jeu prévu 0,4 sur plats.')
put('18_retenue_ecrou_M8',shift=(-10,205,270.5),group='Z')
for x,angle in [(6,90),(264,-90)]:
 s=parts['13_retenue_roulement']['shape'].rotate((0,0,0),(0,1,0),angle).translate((x,230,255.5))
 put('13_retenue_roulement',s=s,group='Z')
# Support moteur X, accouplement dégagé à gauche.
mx=join(box(-70,204,17,6,52,70),box(-64,216,17,19,8,8),box(-64,248,17,19,8,8))
mx=holes(mx,[(-71,230,55)],23,8,'x')
mx=holes(mx,[(-71,230+y,55+z) for y in [-15.5,15.5] for z in [-15.5,15.5]],3.4,8,'x')
mx=holes(mx,[(-71,y,21) for y in [220,252]],4.5,44,'x')
reg('19_support_moteur_X',mx,'Deux M4x40 fixent les bras au chariot gauche. Moteur sur face extérieure X=-70.',((0,0,0),(0,1,0),90))
put('19_support_moteur_X',shift=(0,0,200.5),group='Z')

# Chariot X, deux guides et bras supérieur pour la vis X.
xc=join(box(-28,150,-45,56,45,115),box(-28,195,42,56,50,28))
xc=cut(xc,box(-14,149,-12,28,48,24))
xc=holes(xc,[(-29,165,z) for z in [-30,30]],8.5,58,'x')
xc=holes(xc,[(-29,230,55)],8.8,58,'x')
xc=cut(xc,hexhole(-28,230,55,13.4,7.2,'x'))
xc=holes(xc,[(-29,y,z) for y in [219,241] for z in [44,66]],2.6,13,'x')
xc=holes(xc,[(x,184,-22) for x in [-15,15]],8.3,13,'y')
xc=holes(xc,[(0,180,25)],13,17,'y')
xc=cut(xc,cyl(0,188,25,22.3,8,'y'))
xc=holes(xc,[(x,182,z) for x in [-24,24] for z in [-10,38]],2.6,15,'y')
reg('20_chariot_X',xc,'Deux alésages X Ø8,5 ; écrou M8 latéral ; roulement 608 pour le poussoir.',((0,0,0),(0,1,0),90))
put('20_chariot_X',shift=(45,0,200.5),group='XZ')
s=nutcap.rotate((0,0,0),(0,1,0),-90).translate((17,230,255.5))
put('18_retenue_ecrou_M8',s=s,group='XZ')

# 04 - POUSSOIR Y, structure fixe portée par le chariot X.
front=cut(box(-34,195,-32,68,6,74),box(-14,194,-12,28,8,24))
front=holes(front,[(x,194,-22) for x in [-15,15]],8.3,8,'y')
front=holes(front,[(0,194,25)],13,8,'y')
front=holes(front,[(x,194,z) for x in [-24,24] for z in [-10,38]],3.4,8,'y')
front=holes(front,[(x,194,-24.5) for x in [-29,29]],3.4,8,'y')
reg('21_platine_poussoir_avant',front,'Retient le 608 avant. Quatre M3x16 au chariot X.',((0,0,0),(1,0,0),90))
put('21_platine_poussoir_avant',shift=(45,0,200.5),group='XZ')
for num,yy,ll in [(22,201,100),(23,301,99)]:
 rail=box(25,yy,-32,8,ll,15)
 rail=holes(rail,[(29,yy-1,-24.5)],2.6,15,'y')
 rail=holes(rail,[(29,yy+ll-14,-24.5)],2.6,15,'y')
 rail=holes(rail,[(24,291 if num==22 else 311,-24.5)],3.4,12,'x')
 reg(f'{num}_longeron_poussoir',rail,'Deux exemplaires, un de chaque côté ; jonction par éclisse.')
 put(f'{num}_longeron_poussoir',shift=(45,0,200.5),group='XZ')
 put(f'{num}_longeron_poussoir',s=rail.mirror('YZ').translate((45,0,200.5)),group='XZ')
railsplice=holes(box(33,281,-32,4,40,15),[(32,y,-24.5) for y in [291,311]],3.4,6,'x')
reg('24_eclisse_poussoir',railsplice,'Deux M3x20 et écrous par éclisse.',((0,0,0),(0,1,0),90))
put('24_eclisse_poussoir',shift=(45,0,200.5),group='XZ')
put('24_eclisse_poussoir',s=railsplice.mirror('YZ').translate((45,0,200.5)),group='XZ')
rear=join(box(-34,400,-32,68,6,82),box(-15,396,10,30,4,30))
rear=holes(rear,[(x,399,-22) for x in [-15,15]],8.3,8,'y')
rear=holes(rear,[(0,395,25)],13,12,'y')
rear=cut(rear,cyl(0,395,25,22.3,8,'y'))
rear=holes(rear,[(x,395,z) for x in [-11,11] for z in [14,36]],2.6,12,'y')
rear=holes(rear,[(x,399,-24.5) for x in [-29,29]],3.4,8,'y')
rear=holes(rear,[(x,399,z) for x in [-27,27] for z in [-25,43]],4.5,8,'y')
rear=holes(rear,[(x,403,-33) for x in [-15,15]],2.6,13)
reg('25_platine_poussoir_arriere',rear,'Roulement 608 ; tiges Ø8 ; quatre entretoises moteur.',((0,0,0),(1,0,0),90))
put('25_platine_poussoir_arriere',shift=(45,0,200.5),group='XZ')
s=parts['13_retenue_roulement']['shape'].rotate((0,0,0),(1,0,0),90).translate((45,396,225.5))
put('13_retenue_roulement',s=s,group='XZ')
my=box(-34,444,-32,68,6,82)
my=holes(my,[(0,443,25)],23,8,'y')
my=holes(my,[(x,443,25+z) for x in [-15.5,15.5] for z in [-15.5,15.5]],3.4,8,'y')
my=holes(my,[(x,443,z) for x in [-27,27] for z in [-25,43]],4.5,8,'y')
reg('26_support_moteur_Y',my,'Moteur à l’arrière, face à Y=450.',((0,0,0),(1,0,0),90))
put('26_support_moteur_Y',shift=(45,0,200.5),group='XZ')
sp38=cut(cyl(0,0,0,12,38),cyl(0,0,-1,4.5,40))
reg('27_entretoise_38',sp38,'Quatre M4x60 avec écrous.')
for x in [-27,27]:
 for z in [-25,43]: put('27_entretoise_38',s=sp38.rotate((0,0,0),(1,0,0),-90).translate((45+x,406,200.5+z)),group='XZ')

# Chariot mobile du poussoir, course -115 en Y.
yc=box(-23,340,-32,46,20,72)
yc=holes(yc,[(x,339,-22) for x in [-15,15]],8.5,22,'y')
yc=holes(yc,[(0,339,25)],8.8,22,'y')
yc=cut(yc,hexhole(0,352.8,25,13.4,8,'y'))
yc=holes(yc,[(x,347,z) for x in [-11,11] for z in [14,36]],2.6,14,'y')
yc=holes(yc,[(x,339,z) for x in [-13,13] for z in [-9,9]],2.6,14,'y')
reg('28_chariot_poussoir',yc,'Tester le glissement à la main avant de monter la vis.',((0,0,0),(1,0,0),90))
put('28_chariot_poussoir',shift=(45,0,200.5),group='XYZ')
s=nutcap.rotate((0,0,0),(1,0,0),-90).translate((45,360,225.5))
put('18_retenue_ecrou_M8',s=s,group='XYZ')

# Tige de poussée en deux parties ; recouvrement 30, boulons noyés.
pf=join(box(-6,110,-6,12,100,12),box(-6,210,0,12,30,6),box(-12,110,-9,24,4,18))
pr=join(box(-6,210,-6,12,30,6),box(-6,240,-6,12,100,12),box(-18,334,-15,36,6,30))
for yy in [218,232]:
 pf=cut(pf,cyl(0,yy,-1,3.4,8),cyl(0,yy,4,6.2,3))
 pr=cut(pr,cyl(0,yy,-7,3.4,8),hexhole(0,yy,-6,5.8,2.8))
pr=holes(pr,[(x,333,z) for x in [-13,13] for z in [-9,9]],3.4,8,'y')
reg('29_tige_poussoir_avant',pf,'Joint à mi-bois ; deux M3x10 à tête basse, écrous M3 noyés. Supports sous la languette.',((0,0,0),(0,1,0),90))
reg('30_tige_poussoir_arriere',pr,'Quatre M3x16 relient la bride au chariot Y.',((0,0,0),(0,1,0),90))
put('29_tige_poussoir_avant',shift=(45,0,200.5),group='XYZ'); put('30_tige_poussoir_arriere',shift=(45,0,200.5),group='XYZ')

# 05 - GOULOTTE. Trois rampes nervurées ; pente 45° ; sortie à Z=30.
def yzpoly(points,width): return cq.Workplane('YZ').polyline(points).close().extrude(width).val()
ramp=yzpoly([(-110,27),(0,137),(0,140),(-110,30)],90)
rib=yzpoly([(-110,6),(0,6),(0,137),(-110,27)],3)
rib=cut(rib,yzpoly([(-96,13),(-10,13),(-10,116),(-96,30)],3))
ramp=join(ramp,rib,rib.translate((87,0,0)),box(0,-110,6,90,110,4))
for x in [15,75]:
 for y in [-95,-15]:
  ramp=cut(ramp,cyl(x,y,5,4.5,8)); basefix.extend([(x+90*c,y) for c in range(3)])
ramp=holes(ramp,[(-1,y,z) for y,z in [(-80,35),(-20,125)]],3.4,92,'x')
reg('31_rampe_45deg',ramp,'Trois modules ; imprimer sur une face latérale pour limiter les supports.',((0,0,0),(0,1,0),90))
for c in range(3): put('31_rampe_45deg',shift=(90*c,0,0))
panel=box(0,-113,95,90,3,140)
panel=holes(panel,[(x,-114,z) for x in [10,45,80] for z in [105,225]],3.4,5,'y')
reg('32_panneau_avant',panel,'Six panneaux, deux rangées. Imprimer à plat.',((0,0,0),(1,0,0),90))
for c in range(3):
 for dz in [0,140]: put('32_panneau_avant',shift=(90*c,0,dz))
for k in range(3):
 z=30+115*k
 s=box(-3,-110,z,3,110,115)
 coords=[(-4,y,zz) for y in [-100,-10] for zz in [z+10,z+105]]
 for yy,zz in [(-80,35),(-20,125),(-10,215),(-10,345),(-100,105),(-100,225),(-100,245),(-100,365)]:
  if z+2<zz<z+113: coords.append((-4,yy,zz))
 s=holes(s,coords,3.4,5,'x')
 reg(f'33_panneau_lateral_{k+1}',s,'Un exemplaire par côté, assemblage en miroir.',((0,0,0),(0,1,0),90))
 put(f'33_panneau_lateral_{k+1}'); put(f'33_panneau_lateral_{k+1}',s=mirrorx(s))
# Éclisse plane 40x12 ; trous espacés de 20, à orienter au montage.
flatlink=holes(box(-20,-6,0,40,12,4),[(-10,0,-1),(10,0,-1)],3.4,6)
reg('34_eclisse_panneaux',flatlink,'M3x12 + écrous ; les têtes restent à l’extérieur de la descente.')
for x in [90,180]:
 for z in [105,225,245,365]: put('34_eclisse_panneaux',s=flatlink.rotate((0,0,0),(1,0,0),90).translate((x,-113,z)))
for x in [45,135,225]:
 put('34_eclisse_panneaux',s=flatlink.rotate((0,0,0),(0,1,0),90).rotate((0,0,0),(0,0,1),-90).translate((x,-113,235)))
for x in [-3,273]:
 for y in [-100,-10]:
  for z in [145,260]:
   s=flatlink.rotate((0,0,0),(0,1,0),90)
   if x==-3: s=s.rotate((0,0,0),(0,0,1),180)
   put('34_eclisse_panneaux',s=s.translate((x,y,z)))
corner=join(box(0,0,0,3,20,15),box(0,0,0,20,3,15))
corner=holes(corner,[(-1,10,7.5)],3.4,5,'x'); corner=holes(corner,[(10,-1,7.5)],3.4,5,'y')
reg('35_angle_goulotte',corner,'Huit angles intérieurs ; M3x12 + écrous.')
for z in [105,225,245,365]:
 put('35_angle_goulotte',shift=(0,-110,z-7.5))
 put('35_angle_goulotte',s=corner.mirror('YZ').translate((270,-110,z-7.5)))
tie=holes(box(-7,-16,-6,4,62,12),[(-8,y,0) for y in [-10,40]],3.4,6,'x')
reg('36_attache_goulotte',tie,'Deux attaches de chaque côté à Z=215 et 345.',((0,0,0),(0,1,0),90))
washer=cut(cyl(0,0,0,9,3),cyl(0,0,-1,3.4,5))
reg('37_cale_3mm',washer,'Compense le décalage entre paroi de goulotte et case.')
for z in [215,345]:
 put('36_attache_goulotte',shift=(0,0,z)); put('36_attache_goulotte',s=mirrorx(tie).translate((0,0,z)))
 put('37_cale_3mm',s=washer.rotate((0,0,0),(0,1,0),90).translate((-3,40,z)))
 put('37_cale_3mm',s=washer.rotate((0,0,0),(0,1,0),90).translate((270,40,z)))
# Bacs de récupération, ouverts vers la rampe.
tray=join(box(0,-210,27,90,100,3),box(0,-210,30,3,100,25),box(87,-210,30,3,100,25),box(0,-210,30,90,3,25))
for x in [10,80]:
 for y in [-200,-120]:
  tray=join(tray,box(x-7,y-7,6,14,14,21))
  tray=cut(tray,cyl(x,y,5,4.5,27),cyl(x,y,27,8.5,4))
  basefix.extend([(x+90*c,y) for c in range(3)])
reg('38_bac_reception',tray,'Trois bacs. Imprimer fond sur plateau après retournement/avec supports des pieds ; voir guide.',((0,0,0),(0,1,0),90))
for c in range(3): put('38_bac_reception',shift=(90*c,0,0))

# 06 - CAPTEURS, CÂBLES, ÉPROUVETTES. Réglage par lumières, perçage final selon capteur réel.
sensor=join(box(0,0,0,35,25,4),box(0,21,0,35,4,25))
sensor=holes(sensor,[(7,8,-1),(28,8,-1)],3.4,6)
for x in [8,24]:
 sensor=cut(sensor,box(x-1.7,20,8,3.4,6,10),cyl(x,20,8,3.4,6,'y'),cyl(x,20,18,3.4,6,'y'))
reg('39_support_capteur_reglable',sensor,'Trois supports de fins de course + un capteur de passage. Fixations au bâti à percer après réglage réel.')
for _ in range(4): parts['39_support_capteur_reglable']['qty']+=1
clip=cut(box(0,0,0,20,12,6),box(6,3,2,8,6,5))
clip=holes(clip,[(3,6,-1),(17,6,-1)],3.4,8)
reg('40_attache_cable',clip,'Six attaches pour colliers ; perçage pilote du support après cheminement des câbles.')
parts['40_attache_cable']['qty']=6
test=box(0,0,0,110,35,12)
for i,d in enumerate([8.2,8.3,8.4,8.5,8.6]): test=cut(test,cyl(12+21*i,12,-1,d,14))
for i,d in enumerate([3.2,3.4,4.3,4.5]): test=cut(test,cyl(15+23*i,27,-1,d,14))
reg('41_test_alesages',test,'Rangée Ø8,2 à 8,6 de gauche à droite ; rangée Ø3,2 / 3,4 / 4,3 / 4,5. Tester avant les chariots.')
parts['41_test_alesages']['qty']=1
test2=box(0,0,0,110,35,10)
for i,d in enumerate([22.1,22.2,22.3,22.4]): test2=cut(test2,cyl(15+26*i,17.5,2.8,d,8),cyl(15+26*i,17.5,-1,10,12))
reg('42_test_roulements',test2,'Quatre logements : Ø22,1 / 22,2 / 22,3 / 22,4, profondeur 7,2.')
parts['42_test_roulements']['qty']=1

# SOCLE modulaire 4x5 tuiles ajourées 100x140. Le code génère les perçages de fixation.
base_link=holes(box(-20,-10,0,40,20,5),[(-10,0,-1),(10,0,-1)],4.5,7)
for x in [-10,10]: base_link=cut(base_link,cq.Solid.makeCone(4.5,2.25,2.25,V(x,0,0),V(0,0,1)))
reg('43_liaison_socle',base_link,'M4x10 à tête fraisée, vissées par dessous dans les écrous captifs des tuiles.')
for i in range(1,4):
 for j in range(5): put('43_liaison_socle',shift=(-65+100*i,-210+140*j+70,-5))
for i in range(4):
 for j in range(1,5): put('43_liaison_socle',s=base_link.rotate((0,0,0),(0,0,1),90).translate((-65+100*i+50,-210+140*j,-5)))
for i in range(4):
 for j in range(5):
  x0=-65+100*i; y0=-210+140*j
  s=cut(box(x0,y0,0,100,140,6),box(x0+8,y0+8,-1,84,124,8))
  s=join(s,box(x0+47,y0,0,6,140,6),box(x0,y0+67,0,100,6,6))
  pts=[(x0+10,y0+70),(x0+90,y0+70),(x0+50,y0+10),(x0+50,y0+130)]
  pts += [(x,y) for x,y in basefix if x0+0.1<x<x0+99.9 and y0+0.1<y<y0+139.9]
  pts=list(dict.fromkeys(pts))
  for x,y in pts:
   s=join(s,box(x0,y-5,0,100,10,6),cyl(x,y,0,16,6))
  for x,y in pts: s=cut(s,cyl(x,y,-1,4.5,8),hexhole(x,y,-0.1,7.4,3.5))
  s=s.intersect(box(x0,y0,0,100,140,6)).clean()
  item(f'44_socle_C{i+1}_R{j+1}',s,f'Tuile colonne {i+1}, rangée {j+1}. Origine globale X={x0}, Y={y0}. Écrous M4 insérés dessous avant montage.')

# Géométrie de référence des composants achetés, uniquement dans le STEP.
def hw(name,s): hardware.append((name,s))
for x in [-25,295]: hw('guide_Z',cyl(x,145,142,8,300))
hw('vis_Z_M8',cyl(-10,205,135,8,315))
for z in [170.5,230.5]: hw('guide_X',cyl(-40,165,z,8,345,'x'))
hw('vis_X_M8',cyl(-44,230,255.5,8,365,'x'))
for x in [30,60]: hw('guide_Y',cyl(x,185,178.5,8,226,'y'))
hw('vis_Y_M8',cyl(45,180,225.5,8,244,'y'))
hw('moteur_Z_enveloppe',box(-31.15,183.85,476,42.3,42.3,38))
hw('moteur_X_enveloppe',box(-108,208.85,234.35,38,42.3,42.3))
hw('moteur_Y_enveloppe',box(23.85,450,204.35,42.3,38,42.3))

# Roulements et accouplements : enveloppes nominales, non imprimées.
for z in [143,427]: hw('608_Z',cut(cyl(-10,205,z,22,7),cyl(-10,205,z-1,8,9)))
for x in [-1,264]: hw('608_X',cut(cyl(x,230,255.5,22,7,'x'),cyl(x-1,230,255.5,8,9,'x')))
for y in [188,396]: hw('608_Y',cut(cyl(45,y,225.5,22,7,'y'),cyl(45,y-1,225.5,8,9,'y')))
hw('accouplement_Z',cut(cyl(-10,205,440,19,25),cyl(-10,205,439,8.2,27)))
hw('accouplement_X',cut(cyl(-60,230,255.5,19,25,'x'),cyl(-61,230,255.5,8.2,27,'x')))
hw('accouplement_Y',cut(cyl(45,414,225.5,19,25,'y'),cyl(45,413,225.5,8.2,27,'y')))

def export():
 rows=[]
 for name,p in parts.items():
  s=p['shape']
  if p['rot']: s=s.rotate(*p['rot'])
  b=s.BoundingBox(); s=s.translate((-b.xmin,-b.ymin,-b.zmin)); b=s.BoundingBox()
  assert max(b.xlen,b.ylen,b.zlen)<180,(name,b.xlen,b.ylen,b.zlen)
  cq.exporters.export(s,str(STL/(name+'.stl')),tolerance=0.08,angularTolerance=0.15)
  rows.append({'fichier':name+'.stl','quantite':p['qty'],'X_mm':round(b.xlen,2),'Y_mm':round(b.ylen,2),'Z_mm':round(b.zlen,2),'volume_cm3':round(s.Volume()/1000,2),'note':p['note']})
  print(name,p['qty'],flush=True)
 with (DOC/'nomenclature_impression.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter=';'); w.writeheader(); w.writerows(rows)
 a=cq.Assembly(name='Armoire_prototype_V02')
 colors={'fixe':(0.68,0.75,0.8),'Z':(0.2,0.45,0.65),'XZ':(0.9,0.55,0.15),'XYZ':(0.85,0.25,0.2)}
 for k,(name,s,g) in enumerate(instances): a.add(s,name=f'{name}_{k:03d}',color=cq.Color(*colors[g]))
 for k,(name,s) in enumerate(hardware): a.add(s,name=f'ACHAT_{name}_{k}',color=cq.Color(0.35,0.35,0.38))
 a.export(str(ROOT/'CAO'/'assemblage_Fusion.step'))
 (DOC/'positions_pieces.json').write_text(json.dumps([{'piece':n,'groupe':g,'centre':[s.Center().x,s.Center().y,s.Center().z]} for n,s,g in instances],indent=2),encoding='utf-8')
 return rows

if __name__=='__main__':
 raise SystemExit('Exécuter generer.py pour la version Parallax V0.3.')
