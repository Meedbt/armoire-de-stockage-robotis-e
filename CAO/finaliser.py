"""Exporter la version V0.3 et contrôler les solides STEP."""
import json
import generer as g
import cadquery as cq
from pathlib import Path
CHANGED=['14_support_servo_Z','15_entretoise_44','19_support_servo_X','26_support_servo_Y','27_entretoise_40','45_adaptateur_palonnier_M8','46_coupon_fixation_servo']
rows=g.export()
step=cq.importers.importStep(str(g.ROOT/'CAO/assemblage_Fusion.step')).solids().vals()
assert len(step)==len(g.instances)+len(g.hardware),(len(step),len(g.instances)+len(g.hardware))
assert all(s.isValid() for s in step)
out=g.ROOT/'CAO/STEP_pieces_modifiees';out.mkdir(exist_ok=True)
for n in CHANGED:cq.exporters.export(g.parts[n]['shape'],str(out/(n+'.step')))
summary={'version':'0.3-Parallax','references_STL':len(rows),'exemplaires':sum(r['quantite'] for r in rows),'solides_STEP_valides':len(step),'interfaces_servo':'Enveloppes nominales hypothétiques ; coupon et mesure réelle requis','essais_physiques':False,'limites':['pas de calcul du couple ni de rigidité','palonnier réel à vérifier','visserie de fixation non représentée','capteurs non implantés','pas de simulation continue de mouvement']}
(g.DOC/'resume_validation.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(summary,flush=True)
# Vues produites directement depuis les solides.
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
colors={'fixe':'#acbec8','Z':'#2f7697','XZ':'#d9993c','XYZ':'#c74c40'}
objects=[]
for n,s,group in g.instances:
 if n.startswith(('32_','33_','34_','35_','36_','37_')):continue
 objects.append((n,s,'#00a892' if n in CHANGED else colors[group]))
for n,s in g.hardware:objects.append((n,s,'#252f3b' if n.startswith('servo') else '#767c84'))

def render(objects,path,title,limits,azim=125):
 fig=plt.figure(figsize=(12,9),facecolor='#f7f9fb'); ax=fig.add_subplot(111,projection='3d')
 for n,s,color in objects:
  vs,fs=s.tessellate(.6,.25);points=np.array([[v.x,v.y,v.z] for v in vs])
  ax.add_collection3d(Poly3DCollection(points[np.array(fs)],facecolors=color,linewidth=0,shade=False))
 ax.set_xlim(*limits[0]);ax.set_ylim(*limits[1]);ax.set_zlim(*limits[2]);ax.set_box_aspect([b-a for a,b in limits]);ax.view_init(elev=27,azim=azim)
 ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)');ax.set_title(title,pad=20)
 fig.text(.5,.03,'Vert : pièces modifiées • noir : enveloppes servo nominales • ajustement réel à vérifier',ha='center',fontsize=10)
 fig.savefig(path,dpi=140,bbox_inches='tight');plt.close(fig)
render(objects,g.DOC/'vue_ensemble_V03.png','V0.3 — adaptation Parallax 900-00008',[(-115,340),(-215,495),(-10,530)])
selected=[t for t in objects if t[0] in ['14_support_servo_Z','15_entretoise_44','12_console_Z_gauche','13_retenue_roulement','45_adaptateur_palonnier_M8','vis_Z_M8','servo_enveloppe_Z','palonnier_reference_Z','ecrou_adaptateur_Z','contre_ecrou_adaptateur_Z'] and t[1].BoundingBox().zmax>425]
render(selected,g.DOC/'detail_servo_Z.png','Axe Z — support, servo et adaptateur M8',[(-60,40),(155,250),(420,515)],-65)
print('APERÇUS EXPORTÉS',flush=True)
