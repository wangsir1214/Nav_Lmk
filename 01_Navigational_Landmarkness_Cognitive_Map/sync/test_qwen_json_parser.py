"""Focused checks for the model-reply wrapper contract."""

import json
import unittest

from qwen_json_parser import parse_model_json


class ModelJsonParserTests(unittest.TestCase):
    def test_plain_json_is_unchanged(self):
        value, kind, normalized = parse_model_json('  {"candidates":[]}  ')
        self.assertEqual(value, {"candidates": []})
        self.assertEqual(kind, "none")
        self.assertEqual(normalized, '{"candidates":[]}')

    def test_full_json_fence(self):
        value, kind, normalized = parse_model_json('```json\n{"candidates":[]}\n```')
        self.assertEqual(value, {"candidates": []})
        self.assertEqual(kind, "full_json_fence")
        self.assertEqual(normalized, '{"candidates":[]}')

    def test_unlabeled_crlf_fence(self):
        value, kind, _ = parse_model_json('```\r\n{"candidates":[]}\r\n```')
        self.assertEqual(value, {"candidates": []})
        self.assertEqual(kind, "full_json_fence")

    def test_prose_or_partial_fence_is_rejected(self):
        for raw in (
            'Here is JSON:\n```json\n{"candidates":[]}\n```',
            '```json\n{"candidates":[]}\n```\nDone.',
            '```json\n{"candidates":[]}',
        ):
            with self.subTest(raw=raw), self.assertRaises((ValueError, json.JSONDecodeError)):
                parse_model_json(raw)

    def test_invalid_json_inside_fence_is_rejected(self):
        with self.assertRaises(json.JSONDecodeError):
            parse_model_json('```json\n{"candidates": [}\n```')


if __name__ == "__main__":
    unittest.main()
