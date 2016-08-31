# -*- coding: utf-8 -*-

import psycopg2
import sys
import copy
import json
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
        {'address': None,
                  'ctag': None,
                  'deps': defaultdict(<class 'list'>, {'HED': [1]}),
                  'feats': None,
                  'head': None,
                  'lan': 'ch',
                  'lemma': None,
                  'rel': None,
                  'tag': None,
                  'word': None}
    """

    content_word_list = ['v','n','r','a']
    operator_dic = {'remove-link-verb': {"checker":"_has_link_verb",
                                         "executor":"_remove_link_verb"},
                    'remove-ch-quantitative-word': {"checker":"_has_ch_quantitative_word",
                                                     "executor":"_remove_ch_quantitative_word"},
                    'remove-leaf-with-pos-u':{"checker":"_has_leaf_with_pos_u",
                                             "executor":"_remove_leaf_with_pos_u"}
                    }

    def __init__(self, lan=None):
        DependencyGraph.__init__(self)
        self.nodes.update({
            'gid':0,
            'lan':lan,
            'address': -1,
            'lemma':'',
            'word': ''
        })
        self._snt = ''
        self.gid = 0
        # all nodes of the graph have the same gid, nodes of different graphs have different gid values
        self._lan = lan
        self._ldg = ''
        self._ldg_json = {}
        self._ldg_nx = ''

    def __repr__(self):
        dict={}
        dict['node'] = self.ldg2json()
        dict['snt'] = self._snt
        dict['gid'] = self.gid
        dict['_lan'] = self._lan
        return json.dumps(dict)

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
                #print(self._snt)
                #print(self._ldg)
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
            if node:
                node['gid'] = gid

    def get_gid(self):
        return self.gid

    def is_root(self, node):
        if node['address'] is None:
            return True
        else:
            return False

    def is_frame_node(self, node):
        if node:
            if node['address'] is None:
                return False
            #lan = node.get('lan', 'xlan')
            #if lan == 'ch':
            return node.get('head', -100) == -1
        return False

    def get_all_functional_node_address(self):
        result = []
        for node in self.nodes.values():
            if ulan.is_functional_node(node):
                result.append(node['address'])
        return result

    def get_parent_content_node_address(self, node):
        """
        :param node:
        :return:
        """
        if self.is_frame_node(node):
            print('get_parent_content_node_address', node)
            return None
        upperNodeAddress = node['head']
        while True:
            if ulan.is_functional_node(self.nodes[upperNodeAddress]):
                upperNodeAddress = self.nodes[upperNodeAddress]['head']
            elif ulan.is_content_node(self.nodes[upperNodeAddress]):
                return upperNodeAddress
        return None

    def establish_ER_relation_between(self, parentContentNodeAddress, address):
        """
        :param parentContentNodeAddress:
        :param address:
        :return:
        """
        print(self.nodes.keys(), address)
        self.nodes[address]['head'] = parentContentNodeAddress
        if 'ER' in self.nodes[parentContentNodeAddress]['deps'].keys() and not self.is_root(self.nodes[parentContentNodeAddress]):
            self.nodes[parentContentNodeAddress]['deps']['ER'].append(address)
        else:
            self.nodes[parentContentNodeAddress]['deps']['ER'] = [address]

    def remove_nodes(self, nodeAddress):
        for node in list(self.nodes.values()):
            for key in list(node['deps']):
                if key != 'ER':
                    del node['deps'][key]

        for address in nodeAddress:
            if address in list(self.nodes.keys()):
                del self.nodes[address]

    def get_ER_graph(self):
        """
        :return:
        """
        ERGraph = copy.deepcopy(self)
        print('starting ERGraph', ERGraph)
        #functionalNodeAddress = ERGraph.get_all_functional_node_address()
        #print('all func', functionalNodeAddress)
        for node in list(ERGraph.nodes.values()):
            if self.is_root(node):
                continue
            if ulan.is_content_node(node):
                node['ER'] = 1
                parentContentNodeAddress = ERGraph.get_parent_content_node_address(node)
                if parentContentNodeAddress is not None:
                    print('parent content', node['address'], parentContentNodeAddress)
                    ERGraph.establish_ER_relation_between(parentContentNodeAddress, node['address'])
            else:
                node['ER'] = 0
                print('non content node', node)
        #self.remove_nodes(functionalNodeAddress)
        if None in ERGraph.nodes.keys():
            del ERGraph.nodes[None]

        print('ending ERGraph', ERGraph)
        return ERGraph

    def is_applicable(self, operator):
        if operator not in LgGraph.operator_dic.keys():
            print(operator, ' not in operator list')
            return False
        checker = LgGraph.operator_dic[operator]['checker']
        return getattr(self, checker)()

    def apply_operator(self, operator):
        """
        till a fix point appears
        :param operator:
        :return: a new graph
        """
        assert operator in LgGraph.operator_dic.keys()
        executor = LgGraph.operator_dic[operator]['executor']
        return getattr(self, executor)()


    
    #
    # graph selector
    # remove_link_verb
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
        newGraph = copy.deepcopy(self)
        for link_verb_address in list(self._get_link_verb_address()):
            print(link_verb_address)
            lk_node = newGraph.nodes[link_verb_address]
            new_nodes = ulan.remove_link_verb(newGraph.nodes, lk_node, link_verb_address)
            newGraph.remove_node(link_verb_address)
            newGraph.set_nodes(new_nodes)
        return newGraph

    def recover_link_verb(self):
        pass

    #
    # remove_ch_quantitative_word
    #

    def _has_ch_quantitative_word(self):
        for node in self.nodes.values():
            if ulan.is_ch_quantitative_word(node, patt = {'ch' : {'tag': 'q'}}):
                return True
        return False

    def _get_ch_quantitative_word_address(self):
        for node in self.nodes.values():
            if ulan.is_ch_quantitative_word(node, patt = {'ch' : {'tag': 'q'}}):
                yield node['address']

    def _remove_ch_quantitative_word(self):
        print('in _remove_ch_quantitative_word')
        newGraph = copy.deepcopy(self)
        for qword_address in list(self._get_ch_quantitative_word_address()):
            qword_node = newGraph.nodes[qword_address]
            new_nodes = ulan.remove_ch_quantitative_word(newGraph.nodes, qword_node, qword_address)
            newGraph.remove_node(qword_address)
            newGraph.set_nodes(new_nodes)
        return newGraph

    #
    # remove_leaf_with_pos_u
    #
    def _has_leaf_with_pos_u(self):
        for node in self.nodes.values():
            if ulan.is_leaf_with_pos_u(node):
                return True
        return False

    def _get_leaf_with_pos_u_address(self):
        for node in self.nodes.values():
            if ulan.is_leaf_with_pos_u(node):
                yield node['address']

    def _remove_leaf_with_pos_u(self):
        print('in _remove_leaf_with_pos_u')
        newGraph = copy.deepcopy(self)
        for qword_address in list(self._get_leaf_with_pos_u_address()):
            qword_node = newGraph.nodes[qword_address]
            new_nodes = ulan.remove_leaf_with_pos_u(newGraph.nodes, qword_node, qword_address)
            newGraph.remove_node(qword_address)
            newGraph.set_nodes(new_nodes)
        return newGraph

if __name__ == '__main__':

    LgGraphObj = LgGraph(lan='ch')
    LgGraphObj.set_sample_snt_ldg_from_db(lan='ch', table='pons', num=1)
    #ngraph = LgGraphObj.apply_operator('remove-link-verb')
    print(LgGraphObj)
    ergraph = LgGraphObj.get_ER_graph()
    print(ergraph)
