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
                                          'ldg': 0,
                                          'gid': 1, #has the same value of the gid of nodes in ldg.
                                          'lemma': None,
                                          'head': None,
                                          'deps': defaultdict(int),
                                          'remaining_ops': defaultdict(list), #list(LgGraph.operator_dic.keys()),
                                          'ctag': None,
                                          'tag': None,
                                          'feats': None,
                                          })
        self.git_list = [1]
        self.nodes[0].update(
                        {'address': 0,
                         'head': -1,
                         'ldg': 'TOP',
                         'gid': 1, #has the same value of the gid of nodes in ldg.
                         'remaining_ops': defaultdict(list),
                         }
                    )
        if isinstance(ldg, LgGraph):
            self.nodes[0]['ldg'] = ldg

        if isinstance(ldg, GraphNet):
            self.nodes = ldg
            self.git_list = ldg.get_git_list()

    def get_next_gid(self):
        gid = random.randint(2,99)
        while gid in self.git_list:
            gid = random.randint(2, 99)
        self.git_list.append(gid)
        return gid

    def get_git_list(self):
        return list(self.nodes.keys())

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
                yield node

    def fork_ldg(self, ldg=None):
        """
        if ldg == None

        if ldg != None

        :param ldg:
        :return:
        """
        if isinstance(ldg, LgGraph):
            gid = ldg.get_gid()
            newGid = self.get_next_gid()
            cpLdg = copy.deepcopy(ldg)
            cpLdg.set_gid(newGid)
            self.nodes[newGid]['ldg'] = cpLdg
            self.nodes[newGid]['address']= newGid
            self.nodes[newGid]['head'] =  gid
            self.nodes[newGid]['gid'] = newGid  # has the same value of the gid of nodes in ldg.
            self.nodes[newGid]['remaining_ops'] = list(LgGraph.operator_dic.keys())
            self.nodes[gid]['deps'].update({'fork'+str(newGid): newGid})
        else:
            newGid = self.get_next_gid()
            self.nodes[newGid].update(
                {'address': newGid,
                 'head': 0,
                 'ldg': None,
                 'gid': newGid,  # has the same value of the gid of nodes in ldg.
                 'remaining_ops': []
                 }
            )
            self.nodes[0]['deps'].update({'fork'+str(newGid): newGid})
        return newGid

    def change_to_ER_graph(self):
        """
        change the ldg into an ER graph
        :return:
        """
        for node in self.nodes.values():
            lgGraph = node['ldg']
            if lgGraph:
                erGraph = lgGraph.get_ER_graph()
                node['ldg'] = erGraph

    def gen_ER_graph(self, ldg):
        fork_gid = self.fork_ldg(ldg = ldg)

        for graphNode in list(self.gen_ldg_in_net()):
            print('in gen_ER_graph')
            lgGraph = graphNode['ldg']
            erGraph = lgGraph.get_ER_graph()
            print('** ergraph')
            newGraphNet = GraphNet(ldg = erGraph)
            return newGraphNet
            #newGraphNet.to_json()
            #newGraphNet.remove_by_address(0)
            #newGid = self.get_next_gid()
            #newGraphNet.set_gid(newGid)
            #gid = int(lgGraph.get_gid())
            #newGraphNet.set_key_address_same_as_gid(1, newGid)
            #newGraphNet.set_head(gid, address=newGid)
            #self.nodes.update(newGraphNet.nodes)
            #applied = True
        #return applied


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
        def remove_operator_from_node(node, operator):
            if operator in node['remaining_ops']:
                index = node['remaining_ops'].index(operator)
                del node['remaining_ops'][index]
            return node

        applied = False
        for graphNode in list(self.gen_ldg_in_net()):
            lgGraph = graphNode['ldg']
            if operator in graphNode['remaining_ops'] and lgGraph.is_applicable(operator):
                graphNode = remove_operator_from_node(graphNode, operator)
                newGraph = lgGraph.apply_operator(operator)
                newGraphNet = GraphNet(ldg = newGraph)
                newGraphNet.remove_by_address(0)
                newGid = self.get_next_gid()
                newGraphNet.set_gid(newGid)
                gid = int(lgGraph.get_gid())
                newGraphNet.set_key_address_same_as_gid(1, newGid)
                newGraphNet.set_head(gid, address=newGid)
                self.nodes[gid]['deps'][operator].append(newGid)
                self.nodes.update(newGraphNet.nodes)
                applied = True
            else:
                graphNode = remove_operator_from_node(graphNode, operator)

        return applied

    def apply_all_graph_operators(self):
        """
        this function shall generate all possible graphs

        while True:
            applied = False
            for operator in LgGraph.operator_dic.keys():
                applied = applied or self.apply_graph_operation(operator)
            if not applied:
                break
        """
        self.gen_ER_graph()
        while True:
            applied = False
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


