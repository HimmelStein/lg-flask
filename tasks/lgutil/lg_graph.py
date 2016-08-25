# -*- coding: utf-8 -*-

import psycopg2
import sys
import copy
from nltk.parse import DependencyGraph
from collections import defaultdict
from pprint import pprint
try:
    from . import util_lan as ulan
except:
    sys.path.append("/Users/tdong/git/lg-flask/tasks/lgutil")
    import util_lan as ulan


class LgGraph(DependencyGraph):
    """
    all graphs are in the sub-class of nltk.parse.DependencyGraph!
     {'address': 1,
        'gid' : 0,
        'ctag': 'PRO',
        'deps': defaultdict(list, {}),
        'feats': '3|Sg|Masc|Nom',
        'head': 2,
        'lemma': 'er',
        'rel': 'subj',
        'tag': 'PPER',
        'word': 'Er'
        }
    """
    operator_dic = {'remove-link-verb': "_remove_link_verb"
                    }

    def __init__(self, lan=None):
        DependencyGraph.__init__(self)
        self.nodes.update({
            'gid':0,
            'lan':lan,
        })
        self._snt = ''
        self.gid = 0
        # all nodes of the graph have the same gid, nodes of different graphs have different gid values
        self._lan = lan
        self._ldg = ''
        self._ldg_json = {}
        self._ldg_nx = ''

    def get_snt(self):
        return self._snt

    def get_lan(self):
        return self._lan

    def set_lan(self, lan):
        self._lan = lan
        for node in self.nodes.values():
            node['lan'] = lan

    def set_nodes(self, newNodes):
        self.nodes = newNodes

    def get_ldg(self):
        return self._ldg 

    def set_conll(self, conllStr):
        DependencyGraph.__init__(self, conllStr)
        self.set_lan(self._lan)

    def set_sample_snt_ldg_from_db(self, lan='', table='', num=-1):
        """
        get sample sentence and its language dependency graph from db
        :param lan: user input the language of the snt
        :param table:
        :param num:
        :return:
        """
        assert lan in ['ch', 'de', 'en']
        assert table in ["pons", "ldc2002t01", "chbible", "dehbible", "enbible"]
        sql_str = ''
        if lan == 'ch' and table == 'pons':
            sql_str = "SELECT id, ch_snt, ch_ldg FROM "+ table + " where id =" + str(num)
        elif lan == 'de' and table == 'pons':
            sql_str= "SELECT id, de_snt, de_ldg FROM "+ table + " where id ="+str(num)
        elif lan == 'ch' and table == 'ldc2002t01':
            sql_str = "SELECT id, ch_snt, ch_ldg FROM " + table + " where id ="+str(num)
        elif lan == 'en' and table == 'ldc2002t01':
            sql_str = "SELECT id, en_snt, en_ldg FROM " + table + " where id ="+ str(num)
        elif table in ["chbible", "dehbible", "enbible"]:
            sql_str = "SELECT id, snt, ldg FROM " + table + " where id ="+ str(num)
        else:
            print("no table found in db\n")

        try:
            con = psycopg2.connect(database="language_graph", user="postgres")
            cur = con.cursor()
            cur.execute(sql_str)
            rows = cur.fetchall()
            for row in rows:
                self._lan = lan
                self._snt = row[1]
                self._ldg = row[2].replace('*', '\n')
                print(self._snt)
                print(self._ldg)
            if self._ldg and lan in ['de', 'en']:
                DependencyGraph.__init__(self, self._ldg) #
                self.set_lan(self._lan)
        except psycopg2.DatabaseError:
            if con:
                con.rollback()
            print('Error %s' % psycopg2.DatabaseError)
            sys.exit(1)
        finally:
            if con:
                con.close()

    def set_snt_from_user(self, snt='', lan=''):
        """
        get sentence from user
        :param snt:
        :param lan:
        :return:
        """

        self._lan = lan
        self._snt = snt

    def ldg2json(self, snt='', ldg=''):
        dic = {}
        for nodeId in self.nodes.keys():
            dic[nodeId] = self.nodes[nodeId]
        return dic

    def ldgjson2nx(self, snt='', ldg=''):
        pass

    def set_gid(self, gid):
        self.gid = gid
        for node in self.nodes.values():
            node['gid'] = gid

    def get_gid(self):
        return self.gid

    def is_applicable(self, operator):
        if operator not in LgGraph.operator_dic.keys():
            print(operator, ' not in operator list')
            return False
        if operator == 'remove-link-verb':
            return self._has_link_verb()
        return False

    def apply_operator(self, operator):
        """
        till a fix point appears
        :param operator:
        :return: a new graph
        """
        assert operator in LgGraph.operator_dic.keys()
        new_graph = self._remove_link_verb()

        return new_graph


    
    #
    # graph selector
    #
    def _has_link_verb(self):
        """
        ch: '是'; 'de': 'sein'; 'en': 'be'
        :return:
        """
        for node in self.nodes.values():
            if ulan.is_link_verb_node(node):
                return True
        return False

    def _get_link_verb_address(self):
        """
        ch: '是'; 'de': 'sein'; 'en': 'be'
        :return:
        """
        for node in self.nodes.values():
            print(node, type(node))
            if ulan.is_link_verb_node(node):
                yield node['address']

    def remove_node(self, address):
        self.nodes[address]['deps'] = defaultdict(list)
        del self.nodes[address]

    def _remove_link_verb(self):
        """
        :return: graph
        """

        print('in _remove_link_verb')
        new_graph = copy.deepcopy(self)
        for link_verb_address in list(self._get_link_verb_address()):
            print(link_verb_address)
            lk_node = new_graph.nodes[link_verb_address]
            new_nodes = ulan.remove_link_verb(new_graph.nodes, lk_node, link_verb_address)
            new_graph.remove_node(link_verb_address)
            new_graph.set_nodes(new_nodes)
        return new_graph

    def recover_link_verb(self):
        pass


if __name__ == '__main__':

    LgGraphObj = LgGraph(lan='de')
    LgGraphObj.set_sample_snt_ldg_from_db(lan='de', table='pons', num=0)
    ngraph = LgGraphObj.apply_operator('remove-link-verb')
    pprint(ngraph)
