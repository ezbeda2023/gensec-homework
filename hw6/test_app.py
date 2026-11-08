import json
from pathlib import Path
import tempfile
import unittest
import app


class SecurityTests(unittest.TestCase):
    def load(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.jsonl'
            path.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            return app.load_events(path)

    def row(self, second=0, **changes):
        return dict(timestamp=f'2026-11-08T12:00:{second:02d}Z', ip='192.0.2.1', user='alice', result='failure', **changes)

    def test_demo(self):
        report = app.analyze(app.load_events(Path(__file__).parent / 'samples/auth.jsonl'))
        self.assertEqual([f['type'] for f in report['findings']], ['repeated_failures', 'success_after_failures'])

    def test_sort_window_and_user_correlation(self):
        rows = [self.row(0), self.row(10), {**self.row(11), 'user': 'bob', 'result': 'success'}]
        result = app.analyze(self.load(list(reversed(rows))), threshold=2, window=10)
        self.assertEqual(len(result['findings']), 1)
        self.assertEqual(app.analyze(self.load(rows), 2, 9)['findings'], [])

    def test_adversarial_inputs(self):
        for changes in ({'ip': 'bad'}, {'user': '\x1b[31m'}, {'timestamp': '2026-11-08'},
                        {'result': 'execute'}, {'extra': 'ignored?'}, {'user': ['alice']},
                        {'timestamp': '0001-01-01T00:00:00+23:00'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.load([{**self.row(), **changes}])

    def test_line_limit(self):
        with self.assertRaises(ValueError):
            self.load([{**self.row(), 'user': 'x' * 5000}])

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'report.json'
            target.write_text('keep', encoding='utf-8')
            self.assertEqual(app.main([str(Path(__file__).parent / 'samples/auth.jsonl'), '--output', str(target)]), 2)
            self.assertEqual(target.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
