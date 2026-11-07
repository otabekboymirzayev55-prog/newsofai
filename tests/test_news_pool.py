import tempfile,unittest
from pathlib import Path
import news_pool
class PoolTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)/'pool.json'
 def tearDown(self):self.tmp.cleanup()
 def item(self,id,score=8):return {'id':id,'title':'Important development','date':'2026-11-01','source':'https://example.com/'+id,'importance':score}
 def test_later_search_keeps_unseen_old_candidates(self):
  news_pool.merge(self.p,[self.item('old-important',10)],'2026-11-07')
  result=news_pool.merge(self.p,[self.item('new',8)],'2026-11-08')
  self.assertEqual([c['id'] for c in news_pool.eligible(result,'2026-11-09')],['old-important','new'])
 def test_published_state_survives_new_search_and_history_records_changes(self):
  first=self.item('event');first['status']='published';news_pool.merge(self.p,[first],'2026-11-07')
  newer=self.item('event',9);newer['title']='Updated finding';data=news_pool.merge(self.p,[newer],'2026-11-08')
  self.assertEqual(data['candidates'][0]['status'],'published')
  self.assertEqual(data['candidates'][0]['history'][0]['date'],'2026-11-01')
  self.assertEqual(news_pool.eligible(data,'2026-11-09'),[])
 def test_expired_story_remains_saved_but_not_eligible(self):
  data=news_pool.merge(self.p,[self.item('event')],'2026-11-07')
  self.assertEqual(len(news_pool.eligible(data,'2026-11-15')),1)
  self.assertEqual(news_pool.eligible(data,'2026-11-16'),[])
  self.assertEqual(len(news_pool.read(self.p)['candidates']),1)
 def test_format_hold_survives_search_without_losing_important_story(self):
  item=self.item('event');item.update(status='video_ready',video='draft.mp4',sha256='a'*64,publication_hold=True,editorial_status='needs_format_revision')
  news_pool.merge(self.p,[item],'2026-11-07')
  refresh=self.item('event');refresh['publication_hold']=False
  data=news_pool.merge(self.p,[refresh],'2026-11-08')
  self.assertEqual(len(news_pool.eligible(data,'2026-11-09')),1)
  self.assertTrue(data['candidates'][0]['publication_hold'])
  self.assertEqual(data['candidates'][0]['editorial_status'],'needs_format_revision')
  self.assertEqual(news_pool.publishable_videos(data,'2026-11-09'),[])
  data['candidates'][0]['publication_hold']=False
  self.assertEqual(len(news_pool.publishable_videos(data,'2026-11-09')),1)
if __name__=='__main__':unittest.main()
