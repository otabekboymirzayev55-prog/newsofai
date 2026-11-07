"""Verify finished films and release only this task's expendable render caches."""
import hashlib,io,json,shutil,subprocess,sys,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio_reel.verify import verify
ROOT=Path(__file__).resolve().parents[1];stories=json.loads((ROOT/'batch_news/stories.json').read_text())
finished=set()
while len(finished)<len(stories):
 log=(ROOT/'.local/news-batch/batch.log').read_text()
 for i,story in enumerate(stories):
  if story['id'] in finished or f"VIDEO DONE {i+1} {story['id']}" not in log:continue
  out=ROOT/'media/batches/2026-11-07'/story['id'];video=out/'video.mp4'
  previous=json.loads((out/'production.json').read_text()) if (out/'production.json').exists() else {}
  report=verify(video);report.update(native_3d_render='432x768, 8 fps, 4 Cycles samples; OIDN denoised and interpolated independently per shot to 24 fps',rights='Original procedural geometry, typography and locally synthesized music',visual_review='pending_human_or_assistant_frame_review',scheduled=False)
  if previous.get('sha256')==report['sha256'] and previous.get('visual_review','').startswith('assistant inspected'):
   report['visual_review']=previous['visual_review']
  (out/'production.json').write_text(json.dumps(report,indent=2)+'\n')
  canvas=Image.new('RGB',(1080,1920))
  for j,t in enumerate([2,6.5,11,17]):
   raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-f','image2pipe','-c:v','png','-'])
   frame=Image.open(io.BytesIO(raw));canvas.paste(frame.resize((540,960)),((j%2)*540,(j//2)*960))
  canvas.save(out/'contact.jpg')
  work=ROOT/'.local/news-batch-v1'/story['id']
  for folder in ['frames','clean']:
   p=work/folder
   if p.exists() and not p.is_symlink():shutil.rmtree(p)
  finished.add(story['id']);print('VERIFIED',story['id'],flush=True)
 time.sleep(3)
