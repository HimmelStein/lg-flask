# -*- coding: utf-8 -*-


from ..lgutil import database_utility as dbutil
from ..lgutil.lg_graph import LgGraph


def get_raw_ldg(chsntOrId, table='PONS'):
    if chsntOrId.isdigit():
        id = int(chsntOrId)
        raw_ldg_str = dbutil.get_raw_ldg_with_id(id, table=table)
        LgGraphObj = LgGraph()
        print(raw_ldg_str.replace('*', '\n').replace('_ _ _', '_ _'))
        LgGraphObj.set_conll(raw_ldg_str.replace('*', '\n').replace('_ _ _', '_ _'))
        return LgGraphObj.ldg2json()
    else:
        pass
