# -*- coding: utf-8 -*-

from nltk.parse import DependencyGraph
from collections import defaultdict
import random
from pprint import pprint
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


    def to_json(self):
        dic = {}
        for nodeId in self.nodes.keys():
            dic[nodeId] = self.nodes[nodeId]
            if isinstance(dic[nodeId]['ldg'], LgGraph):
                dic[nodeId]['ldg'] = dic[nodeId]['ldg'].ldg2json()
        return dic

    def apply_graph_operation(self, operator):
        """
        apply operator to all nodes of self, except the TOP node
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
        for node in self.nodes.values():
            if node.is_applicable(operator):
                newNode = node.apply_operator(operator)
                newGid = self.get_next_gid()
                newNode.set_gid(newGid)
                gid = node.get_gid()
                newNodeInNet = GraphNet(ldg = newNode)
                newNodeInNet['head'] = gid
                self.nodes[gid]['deps'][operator].append(newGid)
                self.nodes[newGid] = newNodeInNet


if __name__ == '__main__':
    LgGraph0 = LgGraph()
    LgGraph0.set_sample_snt_ldg_from_db(lan='de', table='pons', num=0)
    GraphNet0 = GraphNet(ldg = LgGraph0)
    LgGraph1 = LgGraph0.remove_link_verb()


