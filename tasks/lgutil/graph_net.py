# -*- coding: utf-8 -*-

from nltk.parse import DependencyGraph
from collections import defaultdict
import random
import sys
import copy
from json import dumps
from pprint import pprint
try:
    from .lg_graph import LgGraph
except:
    sys.path.append("/Users/tdong/git/lg-flask/tasks/lgutil")
    from .lg_graph import LgGraph


class GraphNet(DependencyGraph):
    """
    {'address': 1,
        'ctag': 'PRO',
        'deps': defaultdict(list, {'remove-link-verb':[..]}),
        'feats': '3|Sg|Masc|Nom',
        'head': 2,
        'lemma': 'er',  --> 'lemma' : <sentence of the ldg>
        'tag': 'PPER',
        'word': 'Er' --> 'ldg': <graph>
        }
        tag, ctag, and feats are not used!
    """
    def __init__(self, ldg=None):
        DependencyGraph.__init__(self)
        self.nodes = defaultdict(lambda: {'address': None,
                                          'ldg': None,
                                          'gid': 0, #has the same value of the gid of nodes in ldg.
                                          'lemma': None,
                                          'head': None,
                                          'deps': defaultdict(list),

                                          'ctag': None,
                                          'tag': None,
                                          'feats': None,
                                          })
        self.nodes[0].update(
                        {'address': 0,
                         'head': 0,
                            'ldg': 'TOP',
                            'gid': 0, #has the same value of the gid of nodes in ldg.
                        }
                    )
        self.git_list = [0, 1]

        if isinstance(ldg, LgGraph):
            ldg.set_gid(1)
            self.nodes[1]['address'] = 1
            self.nodes[1]['ldg'] =ldg
            self.nodes[1]['head'] = 0
            self.nodes[1]['gid'] = 1
            self.nodes[0]['deps']['NetRoot'] = [1]

    def get_next_gid(self):
        gid = random.randint(2,99999)
        while gid in self.git_list:
            gid = random.randint(2, 99999)
        self.git_list.append(gid)
        return gid

    def set_gid(self, gid):
        for node in self.nodes.values():
            node['gid'] = gid
            if isinstance(node['ldg'], LgGraph):
                node['ldg'].set_gid(gid)

    def set_head(self, gid, address=1):
        self.nodes[address]['head'] = gid

    def set_key_address_same_as_gid(self, address, newGid):
        if address in self.nodes.keys():
            self.nodes[newGid] = copy.deepcopy(self.nodes[address])
            self.nodes[newGid]['address'] = newGid
            del self.nodes[address]

    def to_json(self):
        dic = {}
        for nodeId in self.nodes.keys():
            dic[nodeId] = self.nodes[nodeId]
            if isinstance(dic[nodeId]['ldg'], LgGraph):
                dic[nodeId]['ldg'] = dic[nodeId]['ldg'].ldg2json()
        pprint(dic)
        return dic

    def _remove_node(self, address):
        del self.nodes[address]

    def gen_ldg_in_net(self):
        for node in self.nodes.values():
            if isinstance(node['ldg'], LgGraph):
                yield node['ldg']

    def apply_graph_operation(self, operator):
        """
        apply operator to all nodes with non-null 'ldg' key of self, except the TOP node
        for node in self.nodes.values():
            if node.applicatable(operator){
                newNode = node.apply(operator)
                newGid = self.get_next_gid()
                newNode.set_gid(newGid)
                gid = node.get_gid()
                newNodeInNet = GraphNet(ldg = new_node)
                newNodeInNet['head'] = gid
                self.nodes[gid]['deps'].append(newGid)
                self.nodes[newGid] = newNodeInNet
            }
        :param operator:
        :return:
        """
        applied = False
        for graph in list(self.gen_ldg_in_net()):
            if graph.is_applicable(operator):
                newGraph = graph.apply_operator(operator)
                newGraphNet = GraphNet(ldg = newGraph)
                print('newNodeInNet')
                newGraphNet.remove_by_address(0)
                newGid = self.get_next_gid()
                newGraphNet.set_gid(newGid)
                gid = int(graph.get_gid())
                newGraphNet.set_key_address_same_as_gid(1, newGid)
                newGraphNet.set_head(gid, address=newGid)
                self.nodes[gid]['deps'][operator].append(newGid)
                self.nodes.update(newGraphNet.nodes)
                applied = True
        return applied

    def apply_all_graph_operators(self):
        """
        this function shall generate all possible graphs
        applied = False
        while True:
            for operator in operator_dic:
                applied = applied or self.apply_graph_operation(operator)
            if not applied:
                break
        """
        applied = False
        while True:
            for operator in LgGraph.operator_dic.keys():
                applied = applied or self.apply_graph_operation(operator)
            if not applied:
                break


if __name__ == '__main__':
    LgGraph0 = LgGraph()
    LgGraph0.set_sample_snt_ldg_from_db(lan='de', table='pons', num=0)
    GraphNet0 = GraphNet(ldg = LgGraph0)
    GraphNet0.apply_graph_operation('remove-link-verb')

    pprint(GraphNet0.to_json())


