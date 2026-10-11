"""CPU-only checks for bbox conversion and deterministic matched regions."""
import unittest
import tempfile
from pathlib import Path
from PIL import Image
from phase0_intervention_geometry import qwen_1000_to_pixels, matched_controls, overlap, render_masks


class GeometryTest(unittest.TestCase):
    def test_bbox_contract(self):
        self.assertEqual(qwen_1000_to_pixels([100, 200, 200, 300]), (64, 128, 128, 192))
        for bad in ([0, 0, 1, 1], [600, 300, 200, 900], [0, 0, 1001, 50]):
            with self.assertRaises(ValueError):
                qwen_1000_to_pixels(bad)

    def test_controls(self):
        candidate = (185, 220, 250, 285)
        first = matched_controls(candidate, 'q17')
        self.assertEqual(first, matched_controls(candidate, 'q17'))
        self.assertEqual(len(first), 3)
        for i, box in enumerate(first):
            self.assertEqual((box[2]-box[0], box[3]-box[1]), (65, 65))
            self.assertFalse(overlap(candidate, box))
            self.assertLessEqual(abs((box[1]+box[3])/2 - 252.5), 128)
            self.assertTrue(all(not overlap(box, other) for other in first[:i]))

    def test_mask_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'query.jpg'
            Image.new('RGB', (640, 640), (41, 72, 130)).save(source, format='JPEG')
            candidate = (100, 120, 160, 180)
            controls = matched_controls(candidate, 'test-mask')
            report = render_masks(source, {'candidate': candidate, 'control1': controls[0]}, root / 'masked')
            self.assertEqual(len(report['variants']), 2)
            with Image.open(report['variants'][0]['masked_640_path']) as out:
                self.assertEqual(out.getpixel((101, 121)), (127, 127, 127))
                self.assertNotEqual(out.getpixel((0, 0)), (127, 127, 127))
            with Image.open(report['variants'][0]['model_448_path']) as out:
                self.assertEqual(out.size, (448, 448))


if __name__ == '__main__':
    unittest.main()
