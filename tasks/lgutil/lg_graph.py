# -*- coding: utf-8 -*-

import psycopg2
import sys
import copy
from nltk.parse import DependencyGraph
from collections import defaultdict
from pprint import pprint


class LgGraph(DependencyGraph):
    """
    all graphs are in the sub-class of nltk.parse.DependencyGraph!
    """

    def __init__(self):
        DependencyGraph.__init__(self)
        self._snt = ''
        self._lan = ''
        self._ldg = ''
        self._ldg_json = {}
        self._ldg_nx = ''

    def get_snt(self):
        return self._snt

    def get_lan(self):
        return self._lan

    def get_ldg(self):
        return self._ldg 

    def set_conll(self, conllStr):
        DependencyGraph.__init__(self, conllStr)

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

    #
    # graph selector
    #
    def has_link_verb(self):
        """
        ch: '是'; 'de': 'sein'; 'en': 'be'
        :return:
        """
        for node in self.nodes.values():
            if self._lan == 'de':
                if node['lemma'] == 'sein' and node['tag']=='VAFIN' and node.get('feature',[])==[]:
                    return True
            elif self._lan == 'en':
                return False
        return False

    def get_link_verb_address(self):
        """
        ch: '是'; 'de': 'sein'; 'en': 'be'
        :return:
        """
        for node in self.nodes.values():
            if self._lan == 'de':
                if node['lemma'] == 'sein' and node['tag'] == 'VAFIN':
                    yield node['address']
        return

    def remove_link_verb(self):
        """
        :return: graph
        """
        if self.has_link_verb():
            new_graph = copy.deepcopy(self.nodes)
            if self._lan == 'de':
                link_verb_address_gen = self.get_link_verb_address()
                link_verb_address = next(link_verb_address_gen)
                print(link_verb_address)
                lk_node = new_graph[link_verb_address]
                lk_node['feature'] = defaultdict(list)
                lk_node['feature']['root'] = False
                preds = lk_node['deps'].get('pred', [])
                subjs = lk_node['deps'].get('subj', [])
                if preds and subjs:
                    new_root = new_graph[preds[0]]
                    new_root['deps'].update({link_verb_address: subjs})
                    new_root['feature'] = defaultdict(list)
                    new_root['feature']['root'] = True

                    new_graph[0]['deps']['root'] = preds
            return new_graph

    def recover_link_verb(self):

        pass


if __name__ == '__main__':

    LgGraphObj = LgGraph()
    LgGraphObj.set_sample_snt_ldg_from_db(lan='de', table='pons', num=0)
    pprint(LgGraphObj.remove_link_verb())
