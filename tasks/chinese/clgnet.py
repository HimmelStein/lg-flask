# -*- coding: utf-8 -*-

from json import dumps
from ..lgutil import database_utility as dbutil
from ..lgutil.lg_graph import LgGraph
from ..lgutil.graph_net import GraphNet


def get_raw_ldg(chsntOrId, table='PONS'):
    if chsntOrId.isdigit():
        id = int(chsntOrId)
        raw_ldg_str = dbutil.get_raw_ldg_with_id(id, table=table)
        LgGraphObj = LgGraph(lan='ch')
        print(raw_ldg_str.replace('*', '\n').replace('_ _ _', '_ _'))
        LgGraphObj.set_conll(raw_ldg_str.replace('*', '\n').replace('_ _ _', '_ _'))
        return LgGraphObj.ldg2json()
    else:
        pass


def get_graph_net(chsntOrId, table='PONS'):
    if chsntOrId.isdigit():
        id = int(chsntOrId)
        raw_ldg_str = dbutil.get_raw_ldg_with_id(id, table=table)
        LgGraphObj = LgGraph(lan='ch')
        LgGraphObj.set_conll(raw_ldg_str.replace('*', '\n').replace('_ _ _', '_ _'))
        GraphNetObj = GraphNet(ldg = LgGraphObj)
        GraphNetObj.apply_graph_operation('remove-link-verb')

        return GraphNetObj.to_json()
    else:
        pass
