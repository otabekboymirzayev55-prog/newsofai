"""Persistent public editorial backlog; later searches merge, never replace it."""
from datetime import date,timedelta
from pathlib import Path
import json,os,tempfile

def read(path):
 p=Path(path)
 return json.loads(p.read_text()) if p.exists() else {'schema_version':1,'candidates':[]}

def save(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.news-pool-',dir=p.parent)
 try:
  with os.fdopen(fd,'w') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def merge(path,incoming,checked_on):
 data=read(path);items={c['id']:c for c in data['candidates']}
 for item in incoming:
  for key in ['id','title','date','source']:
   if not isinstance(item.get(key),str) or not item[key]:raise ValueError('Incomplete public candidate')
  event=date.fromisoformat(item['date']);new=dict(item);new['valid_through']=(event+timedelta(days=14)).isoformat();new['checked_on']=checked_on
  old=items.get(new['id'])
  if old:
   publication={k:old[k] for k in ('publication_hold','publication_hold_reason','editorial_status') if k in old}
   history=old.get('history',[])
   if any(old.get(k)!=v for k,v in new.items() if k not in ('status','checked_on')):
    history=history+[{'checked_on':old.get('checked_on'),'title':old['title'],'source':old['source'],'importance':old.get('importance'),'date':old.get('date'),'note':old.get('note'),'limitation':old.get('limitation')}]
   current_status=old.get('status','reserve');old.update(new);old.update(publication);old['status']=current_status;old['history']=history
  else:
   new.setdefault('status','reserve');new['history']=[];items[new['id']]=new
 data['candidates']=list(items.values());data['updated_on']=checked_on;save(path,data);return data

def eligible(data,publication_date):
 today=date.fromisoformat(publication_date)
 return sorted([c for c in data['candidates'] if c.get('status') in ('reserve','video_ready','selected')
                and date.fromisoformat(c['date'])<=today<=date.fromisoformat(c['valid_through'])],
               key=lambda c:(-c.get('importance',0),c['valid_through'],c['id']))

def publishable_videos(data,publication_date):
 """An interesting held story stays eligible; its old export cannot be queued."""
 return [c for c in eligible(data,publication_date) if c.get('status')=='video_ready'
         and c.get('video') and c.get('sha256') and not c.get('publication_hold')]
