"""Denoise, editorial typography, optical-flow finish and original sound design.

Optional local OIDN library is used only to clean the original Blender renders.
It is not a generative image/video service. No voiceover or external footage.
"""
import argparse
import ctypes as C
import math
from pathlib import Path
import subprocess
import time
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W,H,FPS=1080,1920,24
WHITE=(241,239,231)
GOLD=(221,183,113)
MUTED=(136,149,155)


class Denoiser:
    def __init__(self, library, width, height):
        self.lib=C.CDLL(str(Path(library).resolve()))
        api=self.lib
        ptr=C.c_void_p
        signatures={
          'oidnNewDevice':([C.c_int],ptr),
          'oidnSetDeviceInt':([ptr,C.c_char_p,C.c_int],None),
          'oidnCommitDevice':([ptr],None),
          'oidnNewFilter':([ptr,C.c_char_p],ptr),
          'oidnSetSharedFilterImage':([ptr,C.c_char_p,ptr,C.c_int,C.c_size_t,C.c_size_t,C.c_size_t,C.c_size_t,C.c_size_t],None),
          'oidnSetFilterBool':([ptr,C.c_char_p,C.c_bool],None),
          'oidnCommitFilter':([ptr],None),
          'oidnExecuteFilter':([ptr],None),
          'oidnGetDeviceError':([ptr,C.POINTER(C.c_char_p)],C.c_int),
        }
        for name,(inputs,result) in signatures.items():
            fn=getattr(api,name)
            fn.argtypes,fn.restype=inputs,result
        self.device=api.oidnNewDevice(1)
        api.oidnSetDeviceInt(self.device,b'numThreads',1)
        api.oidnCommitDevice(self.device)
        self.input=np.zeros((height,width,3),dtype=np.float32)
        self.output=np.zeros_like(self.input)
        self.filter=api.oidnNewFilter(self.device,b'RT')
        for name,array in [(b'color',self.input),(b'output',self.output)]:
            api.oidnSetSharedFilterImage(self.filter,name,array.ctypes.data,3,width,height,0,0,0)
        api.oidnSetFilterBool(self.filter,b'hdr',False)
        api.oidnSetFilterBool(self.filter,b'srgb',True)
        api.oidnCommitFilter(self.filter)
        self.check()

    def check(self):
        message=C.c_char_p()
        code=self.lib.oidnGetDeviceError(self.device,C.byref(message))
        if code:
            raise RuntimeError(message.value.decode() if message.value else 'Denoiser failed')

    def run(self,image):
        self.input[:]=np.asarray(image.convert('RGB'),dtype=np.float32)/255
        self.lib.oidnExecuteFilter(self.filter)
        self.check()
        return Image.fromarray(np.uint8(np.clip(self.output,0,1)*255))


def denoise_all(root, library, count=54, watch=False):
    engine=None
    for shot in range(4):
        target=root/'clean'/f'shot{shot}'
        target.mkdir(parents=True,exist_ok=True)
        for i in range(count):
            result=target/f'{i:04}.png'
            if result.exists():
                continue
            source=root/'frames'/f'shot{shot}'/f'{i:04}.png'
            deadline=time.monotonic()+300
            while True:
                try:
                    with Image.open(source) as opened:
                        image=opened.convert('RGB')
                    break
                except (OSError,ValueError):
                    if not watch or time.monotonic()>deadline:
                        raise RuntimeError(f'Missing/incomplete render: {source}')
                    time.sleep(1)
            if engine is None:
                engine=Denoiser(library,image.width,image.height)
            clean=engine.run(image)
            clean.save(result)
            print(f'CLEAN shot={shot} frame={i+1}/{count}',flush=True)


def music(path):
    rate=48000
    t=np.arange(18*rate,dtype=np.float64)/rate
    left=np.zeros_like(t)
    right=np.zeros_like(t)
    chords=[(146.83,174.61,220,329.63),(116.54,146.83,174.61,220),
            (98,116.54,146.83,220),(110,130.81,164.81,196)]
    rng=np.random.default_rng(19)
    beat=18/32
    for section,chord in enumerate(chords):
        start=section*4.5
        local=t-start
        gate=np.clip(local/.8,0,1)*np.clip((4.5-local)/.9,0,1)
        gate[(local<0)|(local>4.5)]=0
        for i,f in enumerate(chord):
            pan=i/3
            pad=(np.sin(math.tau*f*t)+.25*np.sin(math.tau*f*2.002*t))*.019*gate
            left+=pad*(1-.4*pan)
            right+=pad*(.6+.4*pan)
        for k in range(8):
            delay=local-k*beat
            envelope=np.where(delay>=0,np.exp(-np.maximum(delay,0)*11),0)
            f=chord[k%4]*2
            pluck=(np.sin(math.tau*f*delay)+.22*np.sin(math.tau*f*3*delay))*.055*envelope
            left+=pluck*(.8 if k%2 else .5)
            right+=pluck*(.5 if k%2 else .8)
            kick=np.sin(math.tau*(48*delay+3*(1-np.exp(-np.maximum(delay,0)*25))))
            kick*=np.where(delay>=0,np.exp(-np.maximum(delay,0)*17),0)*(.15 if k%2==0 else .055)
            left+=kick
            right+=kick
    # Broad, soft transition sweeps and small digital impacts, all synthesized here.
    noise=rng.normal(0,1,len(t))
    smooth=np.convolve(noise,np.ones(45)/45,mode='same')
    for cut in [4.5,9,13.5,15.4]:
        whoosh=np.exp(-((t-(cut-.09))/.20)**2)*smooth*.16
        left+=whoosh
        right+=np.roll(whoosh,320)
        dt=np.maximum(t-cut,0)
        hit=np.where(t>=cut,np.exp(-dt*8)*np.sin(math.tau*(66*dt+2*np.exp(-dt*15))),0)*.17
        left+=hit
        right+=hit
    fade=np.minimum(np.clip(t/.45,0,1),np.clip((18-t)/1.2,0,1))
    sound=np.column_stack([left,right])*fade[:,None]
    sound*=.84/max(np.max(np.abs(sound)),.001)
    with wave.open(str(path),'wb') as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(np.int16(sound*32767).tobytes())


class Typography:
    def __init__(self):
        base=Path('/usr/share/fonts/truetype/open-sans')
        self.bold=base/'OpenSans-CondBold.ttf'
        self.regular=base/'OpenSans-Regular.ttf'
        self.cache={}
        yy=np.arange(H)[:,None]
        top=np.clip((730-yy)/550,0,1)*.42
        bottom=np.clip((yy-1470)/350,0,1)*.7
        self.shade=Image.fromarray(np.uint8(np.broadcast_to(np.maximum(top,bottom)*255,(H,W))),'L')

    def font(self,size,bold=False):
        key=(size,bold)
        if key not in self.cache:
            self.cache[key]=ImageFont.truetype(str(self.bold if bold else self.regular),size)
        return self.cache[key]

    def compose(self,frame,shot,u):
        if shot==3 and 1.82<u<2.08:
            # Brief color separation on the geometry expresses uncertainty without a flash.
            pixels=np.asarray(frame.convert('RGB')).copy()
            pixels[850:1450,:,0]=np.roll(pixels[850:1450,:,0],7,axis=1)
            pixels[850:1450,:,2]=np.roll(pixels[850:1450,:,2],-5,axis=1)
            frame=Image.fromarray(pixels)
        frame=frame.convert('RGBA')
        shadow=Image.new('RGBA',(W,H),(3,6,8,0))
        shadow.putalpha(self.shade)
        frame=Image.alpha_composite(frame,shadow)
        layer=Image.new('RGBA',(W,H))
        d=ImageDraw.Draw(layer)
        # Consistent editorial masthead and precise safe margins.
        d.line((82,127,99,100),fill=GOLD,width=4)
        d.line((94,127,111,100),fill=GOLD,width=4)
        d.text((137,91),'SAFEGUARD ON',font=self.font(28,True),fill=WHITE)
        d.text((82,157),'AI SAVODXONLIGI  /  01',font=self.font(21),fill=MUTED)
        d.text((890,101),f'0{shot+1}',font=self.font(26),fill=GOLD)
        sequence=[
          ('SAVOL',['AI javobi','qanday tug‘iladi?'],'Javob ekranga chiqishidan oldin…'),
          ('TOKEN',['Matn avval','bo‘laklanadi.'],'Bu bo‘laklar «token» deyiladi.'),
          ('BASHORAT',['Keyingi bo‘lak','bashorat qilinadi.'],'Model o‘rgangan bog‘lanishlarga tayanadi.'),
          ('TEKSHIRUV',['Ishonchli ko‘rinish.','Xato bo‘lishi mumkin.'],'Ravon javob — aniqlik kafolati emas.'),
        ]
        kicker,lines,sub=sequence[shot]
        if shot==3 and u>2.6:
            kicker,lines,sub='ESLAB QOLING',['Manbani ham','tekshiring.'],'AI bilan ishlang. Tanqidiy fikrlang.'
        reveal=min(1,u/.45)
        ease=1-(1-reveal)**3
        y=275+int((1-ease)*26)
        d.text((82,y),kicker,font=self.font(23,True),fill=GOLD)
        for i,line in enumerate(lines):
            size=112
            while d.textbbox((0,0),line,font=self.font(size,True))[2]>920:
                size-=2
            d.text((78,y+58+i*140),line,font=self.font(size,True),fill=WHITE if i==0 else GOLD)
        d.line((82,y+375,82+round(100*ease),y+375),fill=GOLD,width=3)
        d.text((82,y+400),sub,font=self.font(27),fill=(194,200,197))
        d.text((82,1634),'@safeguard_on',font=self.font(29),fill=WHITE)
        d.text((82,1690),'Soddalashtirilgan konseptual 3D tasvir',font=self.font(21),fill=MUTED)
        d.text((82,1734),'SAVOL BERING.  MANBANI TEKSHIRING.',font=self.font(19,True),fill=GOLD)
        for i in range(4):
            x=82+i*232
            d.line((x,1795,x+209,1795),fill=(52,59,60),width=3)
            if i<shot:
                d.line((x,1795,x+209,1795),fill=GOLD,width=3)
            elif i==shot:
                d.line((x,1795,x+round(209*u/4.5),1795),fill=GOLD,width=3)
        # Staggered titles come in gently, while product geometry keeps moving.
        if reveal<1:
            alpha=layer.getchannel('A').point(lambda a:int(a*reveal))
            layer.putalpha(alpha)
        frame=Image.alpha_composite(frame,layer)
        return frame.convert('RGB')


def edit(root,output,poster=False,shots=4,wait_clean=False):
    output=Path(output).resolve()
    if output.exists():
        raise FileExistsError('Output exists')
    typography=Typography()
    if poster:
        raw=Image.open(root/'clean/shot0/0027.png').resize((W,H),Image.Resampling.LANCZOS)
        typography.compose(raw,0,2.25).save(output)
        return
    soundtrack=root/'soundtrack.wav'
    music(soundtrack)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(soundtrack),
         '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p',
         '-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-ar','48000','-b:a','192k',
         '-t',str(4.5*shots),'-movflags','+faststart',str(output)]
    encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for shot in range(shots):
            if wait_clean:
                deadline=time.monotonic()+480
                while True:
                    try:
                        with Image.open(root/'clean'/f'shot{shot}'/'0053.png') as last_file:
                            last_file.verify()
                        break
                    except OSError:
                        if time.monotonic()>deadline:
                            raise RuntimeError('Timed out waiting for the completed shot')
                        time.sleep(1)
            # Interpolate each shot independently so cuts never morph into each other.
            decode=['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-framerate','12',
                    '-i',str(root/'clean'/f'shot{shot}'/'%04d.png'),'-vf',
                    'tpad=stop_mode=clone:stop_duration=0.3,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1:search_param=16,scale=1080:1920:flags=lanczos',
                    '-t','4.5','-f','rawvideo','-pix_fmt','rgb24','-']
            decoder=subprocess.Popen(decode,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            last=None
            for i in range(108):
                data=decoder.stdout.read(W*H*3)
                if len(data)==W*H*3:
                    last=Image.frombytes('RGB',(W,H),data)
                elif last is None:
                    raise RuntimeError('Missing decoded frame')
                encoder.stdin.write(typography.compose(last,shot,i/FPS).tobytes())
            decoder.stdout.close()
            decoder.wait(timeout=60)
            print(f'EDIT shot {shot+1}/{shots}',flush=True)
    finally:
        encoder.stdin.close()
    error=encoder.stderr.read()
    if encoder.wait(timeout=120):
        raise RuntimeError(error.decode(errors='replace')[:400])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--oidn-lib')
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--denoise-only',action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--poster',action='store_true')
    parser.add_argument('--shots',type=int,choices=range(1,5),default=4,help='Render a shorter edit proof')
    parser.add_argument('--wait-clean',action='store_true',help='Wait for each completed shot before encoding')
    args=parser.parse_args()
    if args.oidn_lib:
        denoise_all(args.root,args.oidn_lib,watch=args.watch)
    if not args.denoise_only:
        edit(args.root,args.output,poster=args.poster,shots=args.shots,wait_clean=args.wait_clean)
