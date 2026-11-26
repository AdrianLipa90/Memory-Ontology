import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from operation_memory import record, read_experience

class ExperienceIntegration(unittest.TestCase):
    def test_original_pnaml_store_roundtrip(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{"PNAML_MAHAL_STORE":str(Path(d)/"continuity.sqlite3")}):
            self.assertEqual(read_experience()["status"],"EMPTY")
            run_id=str(uuid.uuid4())
            a=record({"operation":"pip","stage":"ATTEMPT","run_id":run_id})
            b=record({"operation":"pip","stage":"DONE","run_id":run_id,"lesson":"Synthetic test only"})
            self.assertEqual(a["readback"],"VERIFIED")
            self.assertEqual(b["readback"],"VERIFIED")
            events=read_experience("pip")["events"]
            self.assertEqual(len(events),2)
            self.assertEqual(events[0]["cid"],b["cid"])
            self.assertEqual(read_experience("gremlin")["events"],[])
            self.assertEqual(record({"operation":"pip","stage":"DONE","run_id":run_id,"lesson":"Synthetic test only"})["status"],"DUPLICATE")
if __name__=="__main__":unittest.main()
