"""Original story-specific explanatory 3D; no vendor footage or product replica."""
import argparse, math, sys, random, time
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--story',required=True);p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=4);p.add_argument('--size',type=int,default=432);p.add_argument('--fps',type=int,default=8);p.add_argument('--preview',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
random.seed(31);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=2;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.12;s.render.use_persistent_data=True
s.render.resolution_x=a.size;s.render.resolution_y=round(a.size*16/9);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.world.color=(.07,.08,.09);s.view_settings.view_transform='AgX'
def mat(name,c,metal=.5,rough=.28,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 return m
M={'dark':mat('Carbon',(.025,.04,.055),.7),'silver':mat('Titanium',(.5,.62,.68),.9),'gold':mat('Champagne',(.65,.39,.12),.85),'mint':mat('Signal',(.08,.85,.6),.4,emit=2),'blue':mat('Cold signal',(.05,.4,.8),.4,emit=1.5),'red':mat('Warm signal',(.95,.22,.08),.4,emit=1.5),'white':mat('Ceramic',(.75,.83,.88),.2)}
def finish(ob,ma):ob.data.materials.append(M[ma]);return ob
def box(name,loc,scale,ma='silver',bevel=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:mod=o.modifiers.new('Soft machined edge','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return finish(o,ma)
def ball(loc,r=.1,ma='mint'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=loc);o=bpy.context.object
 for q in o.data.polygons:q.use_smooth=True
 return finish(o,ma)
def line(name,pts,ma='mint',radius=.02):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for point,co in zip(sp.points,pts):point.co=(*co,1)
 o=bpy.data.objects.new(name,c);s.collection.objects.link(o);return finish(o,ma)
def torus(loc,r=.8,minor=.035,ma='gold'):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=minor,major_segments=48,minor_segments=8,location=loc);return finish(bpy.context.object,ma)
def group(name,objects):
 g=bpy.data.objects.new(name,None);s.collection.objects.link(g)
 for o in objects:o.parent=g
 return g
floor=box('Stage',(0,0,-.8),(200,200,.1),'dark',0)
for name,loc,power,color,size in [('Key',(1,-3,7),850,(1,.83,.63),5),('Cool',(-4,1,3),900,(.35,.8,1),3),('Rim',(3,4,5),1100,(1,.55,.2),3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,6));cam=bpy.context.object;cam.data.lens=54;s.camera=cam
actors=[];main=[];pulse=[]
if a.story=='world':
 main.append(box('Simulation platform',(0,0,-.28),(3.6,3.6,.35),'silver'))
 for x in range(4):
  for y in range(4):
   h=.18+random.random()*.9;o=box('Imaginary world building',((x-1.5)*.7,(y-1.5)*.7,.08+h/2),(.38,.38,h),'dark');main.append(o);actors.append((o,h))
 for i in range(4):main.append(line('World grid',[(-1.6,(i-1.5)*.8,-.08),(1.6,(i-1.5)*.8,-.08)],'mint',.012))
 pulse=[ball((-1.4,-1.4,.25),.13,'gold')]
elif a.story=='watch':
 main+=[box('Watch strap',(0,0,-.1),(1.15,4.1,.16),'dark'),box('Conceptual watch',(0,0,.1),(1.7,2.05,.38),'silver',.2),box('Abstract signal display',(0,0,.31),(1.42,1.74,.045),'dark',.16)]
 pts=[(-.64+i*.016,-.2+.22*math.sin(i*.21)*math.exp(-((i-39)/21)**2),.345) for i in range(81)];main.append(line('Illustrative PPG, not clinical data',pts,'mint',.018))
 for y in [-.58,.58]:main.append(line('Motion signal',[(-.55,y,.345),(.55,y,.345)],'blue',.012))
 pulse=[ball((0,0,.36),.05)]
elif a.story=='battery':
 for i in range(3):
  x=(i-1)*1.25;main += [box('Used EV pack',(x,.7,-.02),(.95,1.3,.45),'dark'),box('Independent converter',(x,-.45,.02),(.65,.48,.42),'gold')]
  main.append(line('Isolated pack to converter',[(x,.1,.18),(x,-.3,.18)],['mint','blue','red'][i],.027));main.append(line('Converter to common bus',[(x,-.7,.05),(x,-1.15,.05)],'mint',.025));pulse.append(ball((x,0,.18),.06))
 main.append(line('Shared DC bus',[(-1.65,-1.15,.05),(1.65,-1.15,.05)],'mint',.045));main.append(box('Storage power interface',(0,-1.6,.2),(1,.45,.8),'silver'))
elif a.story=='car':
 main.append(box('Generic vehicle chassis',(0,0,.0),(1.6,3.0,.35),'silver',.18));main.append(box('Abstract cabin',(0,.2,.35),(1.25,1.55,.5),'dark',.25));nose=box('Illustrative nose',(0,-1.25,.12),(1.4,.65,.28),'gold',.14);main.append(nose)
 for x in [-.85,.85]:
  for y in [-.9,.9]:
   o=torus((x,y,-.1),.28,.11,'dark');o.rotation_euler[1]=math.pi/2;main.append(o)
 for j in range(5):
  x=(j-2)*.55;pts=[(x*(1+.3*math.exp(-(y/.9)**2)),y,.4+.4*math.exp(-(y/.9)**2)) for y in [k*.12-2.4 for k in range(41)]];main.append(line('Conceptual airflow, not CFD',pts,'blue',.013));pulse.append(ball((x,-2.2,.4),.04,'mint'))
elif a.story=='quantum':
 for i in range(5):
  z=i*.38;main.append(torus((0,0,z),1.13-i*.13,.055,'gold'))
  for theta in [0,2.1,4.2]:main.append(line('Cryostat support',[(math.cos(theta)*.85,math.sin(theta)*.85,0),(math.cos(theta)*.85,math.sin(theta)*.85,1.6)],'silver',.025)) if i==0 else None
 main.append(box('Illustrative quantum lattice',(0,0,-.18),(1.5,1.5,.10),'dark'))
 for x in range(4):
  for y in range(4):pulse.append(ball(((x-1.5)*.34,(y-1.5)*.34,-.1),.055,'mint'))
elif a.story=='plane':
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(0,0,.5));f=finish(bpy.context.object,'silver');f.scale=(.3,2.0,.28);main.append(f)
 verts=[(-2,.65,.4),(0,-.7,.4),(2,.65,.4),(0,.4,.5),(-.85,1.6,.5),(0,1.05,.5),(.85,1.6,.5),(0,1.45,.6)]
 mesh=bpy.data.meshes.new('Generic swept wings');mesh.from_pydata(verts,[],[(0,1,3),(1,2,3),(4,5,7),(5,6,7)]);mesh.update();o=bpy.data.objects.new('Conceptual wings, not X70 geometry',mesh);s.collection.objects.link(o);finish(o,'dark');main.append(o)
 main.append(box('Experimental payload',(0,.1,.08),(.35,.65,.25),'gold'));main.append(line('Flight path',[(-1.5,-2.2,-.35),(-.6,-1,-.25),(.3,.3,-.3),(1.6,1.7,-.35)],'mint',.02))
 pulse=[ball((0,-2,.5),.05,'blue')]
elif a.story=='molecule':
 positions=[(math.cos(i*math.tau/8)*1.25,math.sin(i*math.tau/8)*1.25,.3+(.15 if i%2 else -.15)) for i in range(8)]
 for i,co in enumerate(positions):main.append(ball(co,.16,'silver' if i%3 else 'gold'));main.append(line('Illustrative bond',[co,positions[(i+1)%8]],'dark',.055))
 main.append(line('Conceptual added bond',[positions[1],positions[5]],'mint',.045));pulse=[ball((0,0,.5),.14,'blue')]
else:raise ValueError(a.story)
g=group('Story geometry',main)
for ob in pulse:ob.parent=g
centers=[o.location.copy() for o in pulse]
count=round(4.5*a.fps);start=time.time()
for shot in range(4):
 folder=out/f'shot{shot}';folder.mkdir(exist_ok=True)
 for f in ([count//2] if a.preview else range(count)):
  dest=folder/f'{f:04}.png'
  if dest.exists():continue
  u=f/(count-1);t=shot*4.5+u*4.5;g.rotation_euler[2]=-.35+shot*.16+u*.13
  cam.location=(5.4-shot*.22-u*.18,-7.2+shot*.1,6.0+(.25 if shot%2 else 0));cam.data.lens=53+shot*1.4;cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
  if a.story=='world':
   for i,(o,h) in enumerate(actors):o.scale.z=.8+.2*math.sin(t*.5+i*.4)
   pulse[0].location=(-1.4+2.8*(u if shot%2==0 else 1-u),-1.4,.3)
  elif a.story=='watch':pulse[0].location=(-.6+1.2*u,-.2+.12*math.sin(t*3),.36)
  elif a.story=='battery':
   for i,o in enumerate(pulse):o.location=((i-1)*1.25,.1-.8*((u+i*.2)%1),.18)
  elif a.story=='car':
   for i,o in enumerate(pulse):o.location=((i-2)*.55,-2.2+4.4*((u+i*.12)%1),.45+.4*math.exp(-((-2.2+4.4*u)/.9)**2))
  elif a.story=='quantum':
   for i,o in enumerate(pulse):o.scale=(1+ .35*math.sin(t*1.5+i),)*3
  elif a.story=='plane':g.rotation_euler[1]=.05*math.sin(t*.5);pulse[0].location=(.2*math.sin(t),-2+4*u,.45)
  elif a.story=='molecule':g.rotation_euler[0]=.08*math.sin(t);pulse[0].location=(.35*math.cos(t),.35*math.sin(t),.5)
  s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
  print(f'PROGRESS {a.story} shot={shot} frame={f}/{count} elapsed={time.time()-start:.1f}',flush=True)
