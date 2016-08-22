# -*- coding: utf-8 -*-
import unittest

try:
    import sys
    sys.path.insert(0, '..')
    import lg_graph
except ImportError:
    lg_graph = None


class TestHITConnection(unittest.TestCase):
    def setUp(self):
        self.deSnt = 'Er ist ein Regisseur'

    def test_retrieve_de_snt_from_db(self):
        LgGraphObj = lg_graph.LgGraph()
        LgGraphObj.set_sample_snt_ldg_from_db(lan='de', table='pons', num=0)
        self.assertEqual(LgGraphObj.get_snt(), "Er ist ein Regisseur")


if __name__ == '__main__':
    unittest.main()