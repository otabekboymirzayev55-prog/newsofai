"""Native-resolution typography over original source-specific Blender animation."""
import argparse,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio_reel.finish import Typography, music, W,H,FPS,WHITE,GOLD,MUTED,denoise_all

def wrap(draw,text,font,width):
 lines=[];line=''
 for word in text.split():
  new=(line+' '+word).strip()
  if draw.textlength(new,font=font)>width and line:lines.append(line);line=word
  else:line=new
 if line:lines.append(line)
 return lines

class NewsType(Typography):
 def __init__(self,story):super().__init__();self.story=story
 def compose(self,frame,shot,u):
  frame=frame.convert('RGBA');shadow=Image.new('RGBA',(W,H),(3,6,8,0));shadow.putalpha(self.shade);frame=Image.alpha_composite(frame,shadow)
  layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
  d.line((82,127,99,100),fill=GOLD,width=4);d.line((94,127,111,100),fill=GOLD,width=4)
  d.text((137,91),'MIRABILIS ON',font=self.font(28,True),fill=WHITE)
  d.text((82,157),self.story['publisher'].upper()+'  /  '+self.story['date'],font=self.font(20),fill=MUTED)
  d.text((890,101),f'0{shot+1}',font=self.font(26),fill=GOLD)
  kicker,lines,sub=self.story['scenes'][shot]
  reveal=min(1,u/.35);ease=1-(1-reveal)**3;y=275+int((1-ease)*20)
  d.text((82,y),kicker,font=self.font(22,True),fill=GOLD)
  for i,line in enumerate(lines):
   size=105
   while d.textlength(line,font=self.font(size,True))>920:size-=2
   d.text((78,y+58+i*137),line,font=self.font(size,True),fill=WHITE if i==0 else GOLD)
  d.line((82,y+368,82+round(100*ease),y+368),fill=GOLD,width=3)
  for i,line in enumerate(wrap(d,sub,self.font(29),910)):
   d.text((82,y+395+i*42),line,font=self.font(29),fill=(199,208,207))
  d.text((82,1634),'@mirabilis_on',font=self.font(29),fill=WHITE)
  d.text((82,1688),'Original konseptual 3D • mahsulot demosimas',font=self.font(20),fill=MUTED)
  d.text((82,1732),'MANBA VA CHEKLOVLAR — POST MATNIDA',font=self.font(19,True),fill=GOLD)
  for i in range(4):
   x=82+i*232;d.line((x,1795,x+209,1795),fill=(52,59,60),width=3)
   if i<shot:d.line((x,1795,x+209,1795),fill=GOLD,width=3)
   elif i==shot:d.line((x,1795,x+round(209*u/4.5),1795),fill=GOLD,width=3)
  if reveal<1:layer.putalpha(layer.getchannel('A').point(lambda a:int(a*reveal)))
  return Image.alpha_composite(frame,layer).convert('RGB')

def export(root,story,out):
 t=NewsType(story);out.mkdir(parents=True,exist_ok=True)
 target=out/'video.mp4'
 if target.exists():raise FileExistsError(target)
 audio=root/'soundtrack.wav';music(audio)
 encoder=subprocess.Popen(['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-ar','48000','-b:a','192k','-t','18','-movflags','+faststart',str(target)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for shot in range(4):
   decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-framerate','8','-i',str(root/'clean'/f'shot{shot}'/'%04d.png'),'-vf','tpad=stop_mode=clone:stop_duration=0.4,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1:search_param=16,scale=1080:1920:flags=lanczos','-t','4.5','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   last=None
   for i in range(108):
    data=decoder.stdout.read(W*H*3)
    if len(data)==W*H*3:last=Image.frombytes('RGB',(W,H),data)
    elif last is None:raise RuntimeError('No decoded video frame')
    encoder.stdin.write(t.compose(last,shot,i/FPS).tobytes())
   decoder.stdout.close();decoder.wait(timeout=60)
   print('FINISH',story['id'],shot+1,flush=True)
 finally:encoder.stdin.close()
 err=encoder.stderr.read()
 if encoder.wait(timeout=120):raise RuntimeError(err.decode()[:500])
 raw=Image.open(root/'clean/shot0/0018.png').resize((W,H),Image.Resampling.LANCZOS);t.compose(raw,0,2.25).save(out/'cover.jpg')
 caption=story['caption']+'\n\nManba: '+story['source']+'\n\n#Texnologiya #Yangiliklar #Ozbekcha #MirabilisOn'
 (out/'caption.txt').write_text(caption)
 (out/'story.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n')
 def stamp(seconds):
  ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 srt=[]
 for i,(_,lines,sub) in enumerate(story['scenes']):srt.append(f'{i+1}\n{stamp(i*4.5)} --> {stamp((i+1)*4.5)}\n'+ ' '.join(lines)+'\n'+sub+'\n')
 (out/'screen-text.srt').write_text('\n'.join(srt))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--story',required=True);p.add_argument('--out',type=Path);p.add_argument('--denoise-only',action='store_true');p.add_argument('--oidn-lib');a=p.parse_args()
 stories=json.loads(Path(__file__).with_name('stories.json').read_text());story=next(s for s in stories if s['id']==a.story)
 if a.oidn_lib:denoise_all(a.root,a.oidn_lib,count=36,threads=3)
 if not a.denoise_only:export(a.root,story,a.out)
