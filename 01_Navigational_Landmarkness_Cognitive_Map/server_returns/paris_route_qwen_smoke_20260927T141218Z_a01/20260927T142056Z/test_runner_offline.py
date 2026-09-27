import json,tempfile,unittest
from pathlib import Path
from PIL import Image
import runner


class RunnerCoordinateIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner.SCHEMA=json.loads(runner.SCHEMA_PATH.read_text())

    def test_fenced_reply_converts_every_raw_value(self):
        fence=chr(96)*3
        raw=fence+'json\n{"candidates":[{"candidate_id":1,"bbox_xyxy_1000":[248,448,328,464],"type":"text","description":"ZARA HOME","hypothesized_role":"cue","visibility":"clear","uncertainty":0.2}]}\n'+fence
        value,kind,_=runner.parse_model_json(raw)
        candidates,status,pairs=runner.check_candidate(value,[640,640])
        self.assertEqual(kind,'full_json_fence')
        self.assertEqual(candidates[0]['bbox_xyxy_640'],[158.72,286.72,209.92,296.96])
        self.assertEqual(status,'ok')
        self.assertEqual(pairs,[])

    def test_converted_overlay_uses_pixel_box(self):
        row={'candidates':[{'candidate_id':1,'bbox_xyxy_1000':[776,480,800,504],'type':'text','description':'no entry','hypothesized_role':'cue','visibility':'clear','uncertainty':0.2}]}
        candidates,_,_=runner.check_candidate(row,[640,640])
        with tempfile.TemporaryDirectory() as tmp:
            image=Path(tmp)/'blank.png';output=Path(tmp)/'overlay.png'
            Image.new('RGB',(640,640),'white').save(image)
            runner.draw_box(image,candidates,output)
            with Image.open(output) as im:
                self.assertEqual(im.getpixel((497,307)),(255,0,0))
                self.assertEqual(im.getpixel((600,480)),(255,255,255))

    def test_old_reply_field_does_not_pass_new_schema(self):
        old=Path('/home/nas/wangyq/outputs/paris_route_qwen_smoke_20260927T123059Z_a01/stage0/candidate_raw/main_03_dec.attempt01.txt').read_text()
        value,kind,_=runner.parse_model_json(old)
        self.assertEqual(kind,'full_json_fence')
        with self.assertRaises(runner.FormatError):
            runner.check_candidate(value,[640,640])

    def test_route_json_still_uses_shared_fence_parser(self):
        fence=chr(96)*3
        raw=fence+'json\n{"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"limited image evidence","uncertain":true}\n'+fence
        value,kind,_=runner.parse_model_json(raw)
        decision=runner.check_decision(value,'synthetic_route','current_only')
        self.assertEqual(kind,'full_json_fence')
        self.assertEqual(decision['chosen_edge_id'],'A')


if __name__=='__main__':
    unittest.main()
