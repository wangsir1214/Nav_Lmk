import json
import unittest
from pathlib import Path

from coordinate_contract import CoordinateContractError, convert_bbox_1000, validate_candidates

SCHEMA=json.loads((Path(__file__).parent/'QWEN_OUTPUT_SCHEMAS_COORD1000_20260927.json').read_text())


def candidate(candidate_id, box, description='visible sign'):
    return dict(candidate_id=candidate_id,bbox_xyxy_1000=box,type='text',
                description=description,hypothesized_role='possible navigation cue',
                visibility='clear',uncertainty=0.25)


class CoordinateContractTests(unittest.TestCase):
    def test_zara_home_values_below_640_are_still_scaled(self):
        rows,status,pairs=validate_candidates([candidate(1,[248,448,328,464])],(640,640),SCHEMA)
        self.assertEqual(rows[0]['bbox_xyxy_1000'],[248,448,328,464])
        self.assertEqual(rows[0]['bbox_xyxy_640'],[158.72,286.72,209.92,296.96])
        self.assertEqual(status,'ok')
        self.assertEqual(pairs,[])

    def test_no_entry_values_above_640(self):
        rows,_,_=validate_candidates([candidate(1,[776,480,800,504])],(640,640),SCHEMA)
        self.assertEqual(rows[0]['bbox_xyxy_640'],[496.64,307.2,512.0,322.56])

    def test_zero_and_thousand_boundaries(self):
        self.assertEqual(convert_bbox_1000([0,0,1000,1000],640,640),[0.0,0.0,640.0,640.0])
        self.assertEqual(convert_bbox_1000([250,250,750,750],800,600),[200.0,150.0,600.0,450.0])

    def test_degenerate_out_of_range_nonfinite_and_boolean_rejected(self):
        for box in ([100,100,100,200],[100,100,200,100],[-1,0,100,100],
                    [0,0,1001,100],[0,0,float('nan'),100],[True,0,100,100]):
            with self.subTest(box=box),self.assertRaises(CoordinateContractError):
                convert_bbox_1000(box,640,640)

    def test_exact_duplicate_box_is_flagged_not_merged(self):
        rows,status,pairs=validate_candidates([candidate(1,[360,440,380,460],'street sign'),
                                                 candidate(2,[360,440,380,460],'street sign')],(640,640),SCHEMA)
        self.assertEqual(len(rows),2)
        self.assertEqual(status,'ok')
        self.assertEqual(len(pairs),1)
        self.assertIn('identical_raw_bbox',pairs[0]['reasons'])
        self.assertTrue(rows[0]['duplicate_review_flags'])
        self.assertTrue(rows[1]['duplicate_review_flags'])

    def test_same_storefront_text_at_two_boxes_is_flagged_for_review(self):
        rows,_,pairs=validate_candidates([candidate(1,[248,448,328,464],'ZARA HOME'),
                                           candidate(2,[400,464,504,484],'ZARA HOME')],(640,640),SCHEMA)
        self.assertEqual(len(rows),2)
        self.assertIn('same_description_possible_same_landmark',pairs[0]['reasons'])

    def test_old_misnamed_field_and_extra_key_rejected(self):
        row=candidate(1,[248,448,328,464])
        row['bbox_xyxy_640']=row.pop('bbox_xyxy_1000')
        with self.assertRaises(CoordinateContractError):
            validate_candidates([row],(640,640),SCHEMA)
        row=candidate(1,[248,448,328,464]);row['view_index']=0
        with self.assertRaises(CoordinateContractError):
            validate_candidates([row],(640,640),SCHEMA)

    def test_empty_candidate_response_is_allowed(self):
        self.assertEqual(validate_candidates([],(640,640),SCHEMA),([], 'no_clear_candidate', []))


if __name__=='__main__':
    unittest.main()
