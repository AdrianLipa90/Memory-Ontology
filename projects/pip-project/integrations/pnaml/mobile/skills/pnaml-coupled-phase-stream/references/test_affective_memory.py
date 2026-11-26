"""Boundary tests. Fixture journal explicitly substitutes for existing source store."""
import sys, tempfile, types, unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
# The real operation_memory imports the original source journal in deployment.
# Isolated adapter tests inject a fixture at the journal boundary only if it is absent.
try:
    import operation_memory
except ModuleNotFoundError:
    m=types.ModuleType('operation_memory'); m.store_path=lambda:Path('/nonexistent/test-fixture'); m.MemoryStore=object
    sys.modules['operation_memory']=m
import affective_memory as am

class FixtureJournal:
    def __init__(self,path):self.path=path
    rows={}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def remember(self,event,threshold):
        assert threshold==.60
        k=event['event_id']; old=self.rows.get(k)
        if old and old['payload']!=event:raise ValueError('changed payload')
        self.rows[k]={'cid':'fixture-cid-'+k,'payload':deepcopy(event)}
        return {'status':'DUPLICATE' if old else 'COMMITTED','event_id':k,'cid':self.rows[k]['cid'],'persistent_write':not old}
    def get_event(self,k):return self.rows.get(k)
    def recall(self,q,limit):return [v for v in self.rows.values() if q in v['payload']['title']][:limit]

class Tests(unittest.TestCase):
    def setUp(self):
        FixtureJournal.rows.clear();self.t=tempfile.TemporaryDirectory();self.path=Path(self.t.name)/'fixture';self.p1=patch.object(am,'MemoryStore',FixtureJournal);self.p2=patch.object(am,'store_path',lambda:self.path);self.p1.start();self.p2.start();self.e={'event_id':'test','source_ref':'TEST_FIXTURE','session_id':'fixture','title':'title','summary':'bounded summary','subject':'MODEL_OUTPUT','confidence':.7,'intensity':.8,'distinct_lexical_cues':1,'labels':['positive-valence'],'affect':dict(zip(am.AKEYS,[.8,.3,0,0,.2,.7]))}
    def tearDown(self):self.p2.stop();self.p1.stop();self.t.cleanup()
    def test_selected_scalar_event_and_duplicate(self):
        self.assertEqual(am.remember(self.e)['status'],'COMMITTED');self.assertEqual(am.remember(self.e)['status'],'DUPLICATE');saved=FixtureJournal.rows['affective:test']['payload'];self.assertIn('"valence": 0.8',saved['summary']);self.assertNotIn('aux_link',saved);self.assertIn('M10',saved['tags'])
    def test_no_write_low_confidence(self):
        self.e['confidence']=.44;self.assertEqual(am.remember(self.e)['status'],'IGNORED_EPHEMERAL');self.assertFalse(FixtureJournal.rows)
    def test_reject_inconsistent_intensity_and_raw_fields(self):
        self.e['intensity']=.9
        with self.assertRaises(ValueError):am.remember(self.e)
        self.e['intensity']=.8;self.e['phase36']=[0]*36
        with self.assertRaises(ValueError):am.remember(self.e)
    def test_empty_read_no_create_and_recall(self):
        self.assertEqual(am.read_affective_memory()['status'],'EMPTY');self.assertFalse(self.path.exists());am.remember(self.e);self.path.touch();self.assertEqual(len(am.read_affective_memory()['events']),1)
    def test_readback_mismatch_raises(self):
        with patch.object(FixtureJournal,'get_event',return_value=None):
            with self.assertRaises(RuntimeError):am.remember(self.e)
if __name__=='__main__':unittest.main()
