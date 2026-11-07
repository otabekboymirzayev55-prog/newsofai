"""Blender 4.x CPU-rendered original AI literacy film. No external assets.

blender -b -t 3 --python studio_reel/scene.py -- --out .local/studio/raw --preview
Remove --preview to render all shots. Output is intended for finish.py.
"""
import argparse
import math
from pathlib import Path
import random
import sys
import time

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
parser.add_argument('--preview', action='store_true')
parser.add_argument('--samples', type=int, default=16)
parser.add_argument('--size', type=int, default=540)
parser.add_argument('--fps', type=int, default=12)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT = Path(args.out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
random.seed(27)
S = bpy.context.scene


def material(name, color, metal=0, rough=.3, emission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color,1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*color,1)
        bsdf.inputs['Emission Strength'].default_value = emission
    return mat


def cube(name, loc, dims, mat, bevel=.05, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Precision machined edge','BEVEL')
        mod.width, mod.segments = bevel, 3
        obj.modifiers.new('Surface normals','WEIGHTED_NORMAL')
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def line(name, points, mat, width=.012, parent=None):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth, curve.bevel_resolution = width, 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points,points):
        p.co = (*co,1)
    ob = bpy.data.objects.new(name,curve)
    S.collection.objects.link(ob)
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


def sphere(loc, radius, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius, location=loc)
    obj = bpy.context.object
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def text(body, loc, size, mat, parent=None):
    curve = bpy.data.curves.new(body, 'FONT')
    curve.body, curve.size, curve.align_x, curve.align_y = body, size, 'CENTER', 'CENTER'
    curve.extrude, curve.bevel_depth = .002,.001
    ob = bpy.data.objects.new(body,curve)
    S.collection.objects.link(ob)
    ob.location = loc
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


def root(name):
    ob = bpy.data.objects.new(name,None)
    S.collection.objects.link(ob)
    return ob


def aim(ob, at):
    ob.rotation_euler = (Vector(at)-ob.location).to_track_quat('-Z','Y').to_euler()


def light(name, loc, power, color, size, at=(0,0,0)):
    data = bpy.data.lights.new(name,'AREA')
    data.energy, data.color, data.shape, data.size = power, color, 'DISK', size
    ob = bpy.data.objects.new(name,data)
    S.collection.objects.link(ob)
    ob.location = loc
    aim(ob,at)


def setup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    S.render.engine = 'CYCLES'
    S.cycles.samples = args.samples
    S.cycles.use_denoising = False  # This build has no OIDN.
    S.cycles.max_bounces = 3
    S.cycles.diffuse_bounces = 2
    S.cycles.glossy_bounces = 2
    S.cycles.use_adaptive_sampling = True
    S.cycles.adaptive_threshold = .08
    S.render.use_persistent_data = True
    S.render.resolution_x, S.render.resolution_y = args.size, round(args.size*16/9)
    S.render.resolution_percentage = 100
    S.render.image_settings.file_format = 'PNG'
    S.render.image_settings.color_mode = 'RGB'
    S.render.fps = args.fps
    S.world.color = (.07,.07,.07)
    S.view_settings.view_transform = 'AgX'
    S.render.film_transparent = False
    # Large photographic softboxes create readable reflections on the metal.
    light('Warm key',(1,-3,7),850,(1,.82,.60),5)
    light('Cold strip',(-4,1,3),1000,(.36,.80,1),3)
    light('Gold rim',(3,4,4),1250,(1,.56,.18),3)
    light('Front fill',(0,-5,1),180,(.6,.72,1),4)
    bpy.ops.object.camera_add(location=(5,-7,6))
    camera = bpy.context.object
    camera.data.lens = 56
    S.camera = camera
    floor = material('Obsidian floor',(.012,.017,.022),.7,.26)
    cube('Infinite stage',(0,0,-1.05),(200,200,.2),floor,.02)
    return camera


def build_chip(M):
    group = root('Intelligence / conceptual core')
    board = cube('Carbon carrier',(0,0,-.20),(3.6,3.6,.22),M['dark'],.13,group)
    for side in [-1,1]:
        for j in range(13):
            x = (j-6)*.20
            cube('Gold contact',(x,side*1.24,.015),(.09,.48,.045),M['gold'],.012,group)
            cube('Gold contact',(side*1.24,x,.015),(.48,.09,.045),M['gold'],.012,group)
    for j in range(8):
        x = (j-3.5)*.37
        for side in [-1,1]:
            line('Etched conductor',[(x,side*1.45,-.075),(x,side*1.58,-.075),
                                    (x+side*.09,side*1.68,-.075)],M['trace'],.008,group)
    block = cube('Titanium package',(0,0,.09),(2.22,2.22,.34),M['silver'],.12,group)
    wafer = cube('Polished ceramic',(0,0,.305),(1.99,1.99,.1),M['dark'],.10,group)
    # A luminous inset frame is the common visual motif across the film.
    for axis in [0,1]:
        for side in [-1,1]:
            loc=[0,0,.365]
            dims=[1.68,.018,.012]
            loc[1-axis]=side*.84
            if axis:
                dims=[.018,1.68,.012]
            cube('Core light',loc,dims,M['mint'],.007,group)
    title = text('AI',(0,0,.372),.72,M['white'],group)
    text('M I R A B I L I S',(0,-.58,.373),.13,M['gold'],group)
    screws=[]
    for x,y in [(-1.5,-1.5),(1.5,-1.5),(1.5,1.5),(-1.5,1.5)]:
        screws.append(sphere((x,y,-.05),.06,M['silver'],group))
    return group, block, wafer, title


def build(shot):
    cam=setup()
    M={
      'dark':material('Graphite / satin',(.035,.044,.055),.78,.24),
      'silver':material('Brushed titanium',(.48,.55,.61),.92,.22),
      'gold':material('Champagne anodized metal',(.65,.37,.12),.85,.20),
      'mint':material('Liquid signal',(.15,.95,.72),.25,.22,3),
      'white':material('Ceramic lettering',(.82,.90,.93),.3,.22,.35),
      'trace':material('Etched trace',(.11,.19,.23),.8,.3),
      'amber':material('Uncertainty',(.95,.25,.035),.3,.23,2.5),
    }
    movers=[]
    if shot in (0,1):
        chip,block,wafer,title=build_chip(M)
        if shot==1:
            for i in range(12):
                a=i*math.tau/12
                tile=cube('Token tile',(math.cos(a)*2.3,math.sin(a)*2.3,1.2),
                          (.30,.30,.13),M['gold'] if i%3==0 else M['silver'],.04,chip)
                movers.append((tile,a))
        return cam,chip,block,wafer,title,movers
    if shot==2:
        network=root('Connections / visual metaphor')
        nodes=[]
        for row in range(4):
            for col in range(4):
                p=Vector(((col-1.5)*1.15,(row-1.5)*1.25,.2+random.uniform(-.65,.65)))
                nodes.append(p)
                sphere(p,.16 if (row+col)%3 else .24,M['silver'],network)
                sphere(p+Vector((0,-.02,.09)),.055,M['mint'],network)
        edges=[]
        for i,a in enumerate(nodes):
            for j,b in enumerate(nodes):
                if j>i and (a-b).length<1.9:
                    line('Network fibre',[a,b],M['trace'],.014,network)
                    edges.append((a,b))
        for i,(a,b) in enumerate(edges):
            bead=sphere(a,.045,M['mint'] if i%3 else M['amber'],network)
            movers.append((bead,a,b,i*.173))
        return cam,network,None,None,None,movers
    group=root('Answer / uncertainty')
    cube('Answer plate',(0,0,.1),(2.9,2.9,.20),M['silver'],.18,group)
    cube('Dark glass',(0,0,.23),(2.66,2.66,.08),M['dark'],.15,group)
    check=line('Check symbol',[(-.65,-.05,.30),(-.14,-.55,.30),(.75,.60,.30)],M['mint'],.07,group)
    check.rotation_euler[2]=math.radians(40)
    for i in range(26):
        a=i*math.tau/26
        piece=cube('Doubt fragment',(math.cos(a)*2.1,math.sin(a)*2.1,.4),
                   (.12,.12,.18),M['amber'] if i%5==0 else M['gold'],.025,group)
        movers.append((piece,a))
    return cam,group,None,None,None,movers


def animate(shot,u,objects):
    cam,group,block,wafer,title,movers=objects
    eased=u*u*(3-2*u)
    if shot==0:
        angle=-.48+u*.30
        group.rotation_euler[2]=angle
        cam.location=(4.8-u*.9,-6.1+u*.5,5.8-u*.5)
        cam.data.lens=57+u*4
        aim(cam,(0,0,.9))
    elif shot==1:
        group.rotation_euler[2]=.3-u*.35
        block.location.z=.09+eased*.5
        wafer.location.z=.305+eased*1.05
        title.location.z=.372+eased*1.05
        # Inset frame and logo lift with the upper layer.
        for ob in group.children:
            if ob.name.startswith('Core light'):
                ob.location.z=.365+eased*1.05
            elif ob.name.startswith('M I R A'):
                ob.location.z=.373+eased*1.05
        for tile,a in movers:
            tile.location=(math.cos(a+u*.35)*2.1, math.sin(a+u*.35)*2.1, .5+math.sin(a)*.2+eased*.6)
            tile.rotation_euler=(u*.15,0,a+u*.8)
        cam.location=(5.1-u*.45,-7.0+u*.5,4.6+u*.2)
        cam.data.lens=54
        aim(cam,(0,0,1.15))
    elif shot==2:
        for bead,a,b,phase in movers:
            progress=(u*1.3+phase)%1
            bead.location=a.lerp(b,progress)
        group.rotation_euler[2]=-.12+u*.18
        cam.location=(3.2-u*.9,-6.8+u*1.2,4.8-u*.7)
        cam.data.lens=50+u*5
        aim(cam,(0,0,.9))
    else:
        group.rotation_euler[2]=-.25+u*.4
        group.location.z=.15*math.sin(u*math.pi)
        for ob,a in movers:
            radius=1.9+.35*math.sin(u*math.pi)
            ob.location=(math.cos(a+u*.5)*radius,math.sin(a+u*.5)*radius,.3+u*.3+math.sin(a+u*2)*.2)
            ob.rotation_euler=(a+u,a*.5,u*2)
        cam.location=(4.5-u*.4,-6.3-u*.3,5.5+u*.4)
        cam.data.lens=57-u*3
        aim(cam,(0,0,1.05))


start=time.time()
count=round(4.5*args.fps)
for shot in range(4):
    objects=build(shot)
    shot_dir=OUT/f'shot{shot}'
    shot_dir.mkdir(exist_ok=True)
    indices=[count//2] if args.preview else range(count)
    for frame in indices:
        file=shot_dir/f'{frame:04}.png'
        if file.exists():
            continue
        animate(shot,frame/(count-1),objects)
        S.render.filepath=str(file)
        bpy.ops.render.render(write_still=True)
        print(f'PROGRESS shot={shot} frame={frame}/{count} elapsed={time.time()-start:.1f}',flush=True)
