"""Contract tests use temporary synthetic responses, never the user's review form."""
import contextlib, copy, io, json, tempfile, unittest
from pathlib import Path
from pilot0_validate import check_return

class ReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.out=Path(__file__).resolve().parents[1]/'outputs/pilot0/local_v0_20260922'
        cases=json.loads((self.out/'review/review_cases.json').read_text(encoding='utf-8'))
        build=json.loads((self.out/'review/review_build_summary.json').read_text())
        self.payload={'task_id':'paris_local_v0_20260922','review_fingerprint':build['review_fingerprint'],'responses':[]}
        for c in cases:self.payload['responses'].append({'case_id':c['review_case_id'],'pair_id':c['pair_id'],'query_view_id':c['query_view_id'],'reference_view_id':c['reference_view_id'],'proposed_relation':c['relation'],'human_relation':c['relation'],'overlap':'clear' if c['relation']=='positive' else 'none','quality':'usable','reviewer':'SYNTHETIC_TEST_ONLY','evidence':'Synthetic contract fixture; not a visual annotation.','notes':''})
    def run_payload(self,payload):
        with tempfile.TemporaryDirectory(prefix='pilot0_gate_test_') as tmp:
            path=Path(tmp)/'synthetic.json';path.write_text(json.dumps(payload),encoding='utf-8')
            output=io.StringIO()
            with contextlib.redirect_stdout(output):code=check_return(self.out,path)
            return code,json.loads(output.getvalue())
    def test_complete_does_not_apply_or_unlock(self):
        code,r=self.run_payload(self.payload);self.assertEqual(code,0);self.assertFalse(r['baseline_ready']);self.assertFalse(r['labels_applied'])
    def test_blank_not_approval(self):
        self.payload['responses'][0]['human_relation']='';code,r=self.run_payload(self.payload);self.assertEqual(code,2);self.assertEqual(r['completed'],131)
    def test_positive_without_overlap_rejected(self):
        self.payload['responses'][0]['overlap']='none';self.assertEqual(self.run_payload(self.payload)[0],2)
    def test_duplicate_case_rejected(self):
        self.payload['responses'].append(copy.deepcopy(self.payload['responses'][0]));self.assertEqual(self.run_payload(self.payload)[0],2)
    def test_wrong_version_rejected(self):
        self.payload['review_fingerprint']='wrong';self.assertEqual(self.run_payload(self.payload)[0],2)
    def test_negative_dispute_requires_rule_review(self):
        row=next(r for r in self.payload['responses'] if r['proposed_relation']=='negative');row['human_relation']='ignore'
        code,r=self.run_payload(self.payload);self.assertEqual(code,0);self.assertEqual(len(r['rule_review_required']),1);self.assertFalse(r['baseline_ready'])
if __name__=='__main__':unittest.main()
