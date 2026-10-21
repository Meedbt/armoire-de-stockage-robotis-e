"""Contrôles ponctuels des solides CAO, pas une simulation mécanique."""
import json
import generer as g

def collisions(objects):
 out=[]
 bbs=[s.BoundingBox() for n,s,group in objects]
 for i,(n,a,ga) in enumerate(objects):
  ba=bbs[i]
  for j in range(i):
   m,b,gb=objects[j]; bb=bbs[j]
   if min(ba.xmax,bb.xmax)-max(ba.xmin,bb.xmin)<0.01 or min(ba.ymax,bb.ymax)-max(ba.ymin,bb.ymin)<0.01 or min(ba.zmax,bb.zmax)-max(ba.zmin,bb.zmin)<0.01: continue
   vol=a.intersect(b).Volume()
   if vol>0.1: out.append((m,n,round(vol,3)))
 return out

def hw_group(n):
 if n in ['guide_X','vis_X_M8','608_X'] or n.endswith('_X'):return 'Z'
 if n in ['guide_Y','vis_Y_M8','608_Y'] or n.endswith('_Y'):return 'XZ'
 return 'fixe'

def run():
 results=[]
 positions=[(45,200.5,0),(225,200.5,0),(45,330.5,0),(225,330.5,0),(45,200.5,-115),(225,200.5,-115),(45,330.5,-115),(225,330.5,-115),(135,265.5,-57.5),(43,200.5,0)]
 for x,z,dy in positions:
  objs=[]
  for n,s,group in g.instances+[(n,s,hw_group(n)) for n,s in g.hardware]:
   shift={'fixe':(0,0,0),'Z':(0,0,z-200.5),'XZ':(x-45,0,z-200.5),'XYZ':(x-45,dy,z-200.5)}[group]
   objs.append((n,s.translate(shift),group))
  c=collisions(objs)
  results.append(dict(X=x,Z=z,Y=dy,collisions=c))
  print(x,z,dy,c,flush=True)
 (g.DOC/'verification_mouvements.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 assert not any(r['collisions'] for r in results),'Interférences détectées'
 return results
if __name__=='__main__':run()
