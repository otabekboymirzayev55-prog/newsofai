"""Resume the commissioned batch without redoing valid completed videos.

No model/API requests: after editorial work this is Blender + FFmpeg CPU work.
A scheduler may invoke it again; flock prevents concurrent duplicate renders.
"""
import fcntl,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ROOT_WORK=ROOT/'.local/news-batch-v1'
ROOT_WORK.mkdir(parents=True,exist_ok=True)

def checkpoint(phase,story=None,error=None):
 data={'phase':phase,'story':story,'pid':os.getpid(),'updated_at':datetime.now(timezone.utc).isoformat(),'error':error}
 tmp=ROOT_WORK/'state.tmp';tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,ROOT_WORK/'state.json')

def valid_video(path):
 if not path.exists():return False
 try:
  d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],stderr=subprocess.DEVNULL))
  v=next(s for s in d['streams'] if s['codec_type']=='video');a=next(s for s in d['streams'] if s['codec_type']=='audio')
  return v['codec_name']=='h264' and v['width']==1080 and v['height']==1920 and int(v['nb_frames'])==432 and a['codec_name']=='aac' and abs(float(d['format']['duration'])-18)<.05
 except (subprocess.CalledProcessError,ValueError,KeyError,StopIteration):return False

def quarantine(path):
 if path.exists():path.rename(path.with_name(path.name+f'.interrupted-{time.time_ns()}'))

def run():
 stories=json.loads((ROOT/'batch_news/stories.json').read_text())
 oidn=ROOT/'.local/tools/oidn-2.5.1.x86_64.linux/lib/libOpenImageDenoise.so'
 if not oidn.is_file():raise RuntimeError('Required local OIDN library unavailable')
 for i,story in enumerate(stories):
  work=ROOT_WORK/story['id'];work.mkdir(exist_ok=True);dest=ROOT/'media/batches/2026-11-07'/story['id']
  if valid_video(dest/'video.mp4') and (dest/'story.json').exists() and json.loads((dest/'story.json').read_text())==story:
   print('VIDEO DONE',i+1,story['id'],'(verified existing export)',flush=True);continue
  quarantine(dest/'video.mp4')
  for part in ('frames','clean'):
   for path in (work/part).glob('shot*/*.png'):
    try:
     with Image.open(path) as image:image.verify()
    except (OSError,ValueError):quarantine(path)
  checkpoint('rendering',story['id']);print('RENDER START',i+1,story['id'],flush=True)
  with (work/'render.log').open('a') as log:
   subprocess.run(['blender','-b','-t','3','--python',str(ROOT/'batch_news/scene.py'),'--','--story',story['topic'],'--out',str(work/'frames'),'--fps','8','--samples','4'],stdout=log,stderr=subprocess.STDOUT,check=True)
  checkpoint('finishing',story['id'])
  with (work/'finish.log').open('a') as log:
   subprocess.run([sys.executable,str(ROOT/'batch_news/finish.py'),'--root',str(work),'--story',story['id'],'--oidn-lib',str(oidn),'--out',str(dest)],stdout=log,stderr=subprocess.STDOUT,check=True)
  if not valid_video(dest/'video.mp4'):raise RuntimeError('Final export failed technical preflight')
  print('VIDEO DONE',i+1,story['id'],flush=True)
 checkpoint('rendering_completed_review_required')

if __name__=='__main__':
 with (ROOT_WORK/'batch.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print('Batch renderer already running.');sys.exit(0)
  try:run()
  except Exception as exc:
   checkpoint('failed',error=type(exc).__name__);raise
