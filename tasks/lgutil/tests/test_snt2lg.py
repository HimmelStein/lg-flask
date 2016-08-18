# -*- coding: utf-8 -*-
import unittest

try:
    import sys
    sys.path.insert(0, '..')
    import snt2lg
except ImportError:
    snt2lg = None


class TestHITConnection(unittest.TestCase):
    def setUp(self):
        self.chSnt = '这是美好的一天'

    def test_hit_cloud_response(self):
        result = snt2lg.get_chinese_language_dependency_graph(self.chSnt)
        self.assertGreater(len(result), 20)


if __name__ == '__main__':
    unittest.main()
