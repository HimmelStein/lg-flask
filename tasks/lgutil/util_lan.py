# -*- coding: utf-8 -*-
from collections import defaultdict
from nltk.parse import DependencyGraph


def is_link_verb_node(node):
    if not isinstance(node, dict):
        return False
    lan = node.get('lan', 'xlan')
    if lan == 'de':
        if node['lemma'] == 'sein' and node['tag'] == 'VAFIN':
            return True
    elif lan == 'ch':
        if node['word'] == '是' and 'SBV' in node['deps'].keys() and 'VOB' in node['deps'].keys():
            return True
    elif lan == 'en':
        return False
    else:
        return (node.get('lemma', False) == 'sein' and node.get('tag', False) == 'VAFIN') \
               or (node['word'] == '是' and 'SBV' in node['deps'].keys() and 'VOB' in node['deps'].keys())


def remove_link_verb(graph, node, node_address):
    """
    :param graph: <DependenctGraph> defaultdic(list)
    :param node:
    :param node_address:
    :return:
    """
    print("in remove_link_verb", graph, node, node_address)
    node['feature'] = defaultdict(list)
    node['feature']['root'] = [0]
    if node['lan'] == 'de':
        preds = node['deps'].get('pred', [])
        subjs = node['deps'].get('subj', [])
    elif node['lan'] == 'ch':
        preds = node['deps'].get('VOB', [])
        subjs = node['deps'].get('SBV', [])
        print('**', preds, subjs)

    if preds and subjs:
        new_root = graph[preds[0]] 
        new_root['feature'] = defaultdict(list)
        new_root['feature']['root'] = [1]
        if node['lan'] == 'de':
            graph[0]['deps']['root'] = preds
        elif node['lan'] == 'ch':
            graph[-1]['deps']['HED'] = preds
            new_label = str(node_address) + ":" + node['word']+":"+node['tag']
            new_root['deps'].update({new_label: subjs})
    return graph