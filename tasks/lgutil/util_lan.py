# -*- coding: utf-8 -*-
from collections import defaultdict
from nltk.parse import DependencyGraph

chContentTagList = ['v','n','r','a','m','ns', 'nt', 'nz']

def is_functional_node(node):
    tag = node.get('tag', 'x')
    lan = node.get('lan', 'xlan')
    if lan == 'ch':
        return tag not in chContentTagList
    return False


def is_content_node(node):
    tag = node.get('tag', 'x')
    lan = node.get('lan', 'xlan')
    if node['address'] == None:
        return True
    if lan == 'ch':
        return tag in chContentTagList
    return True


def is_link_verb_node(node):
    """

    :param node:
    :return:
    """
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


def value_match(value0, value1):
    if type(value0) == type(value1):
        if value0 == value1:
            return True
    elif isinstance(value1, list):
        index = value1.index(value0)
        if index > -1:
            return True
    return False


def is_ch_quantitative_word(node, patt={}, context = None):
    """
    {'ch' : {'tag': 'q'}
     'de' : 'no such word',
     'en' : 'no such word'}
    :param node: a node of type dict
    :param patt:  {'ch' : {'tag': 'q'}}
    :param context: None
    :return:
    """
    if not isinstance(node, dict):
        return False
    if 'ch' not in patt.keys():
        print('patt error!')
        return False
    lan = node.get('lan', 'xlan')
    patDic = patt[lan]
    matched = True
    for key in patDic.keys():
        if not (key in node.keys() and value_match(node[key], patDic[key])):
            matched = False
    return matched
    #if lan == 'ch':
    #    if node['tag'] == 'q':
    #        return True
    return False


def is_leaf_with_pos_u(node, patt={}, context = None):
    """

    :param node:
    :param patt: {'ch': {'word': '的', 'tag':'u', 'deps': [], 'rel': 'RAD'}}
    :param context: {'g': graph, 'parent': {'tag': ['a','n']}}
    :return:
    """
    if not isinstance(node, dict):
        return False
    lan = node.get('lan', 'xlan')
    if lan == 'ch':
        if node['word'] == '的' and node['tag'] == 'u' and len(node['deps']) == 0 and node['rel'] == 'RAD':
            return True
    return False


def node_has_pattern_in_context(node, patt = {}, context = None):
    """
    :param node: a node of type dict
    :param patt: {'ch': {}, 'en':{}, 'de':{}}
    :param context: {'g':graph of node,
                     'parentPat':{<node patt>},
                     'parentPat':{<node patt>},
                     'childPat':{<edge patt>:<node patt>},
                     'grandChildPat': {<edge patt>:<node patt>},
                     'siblingPat':{<edge patt>:<node patt>}}
    :return:
    do unit test!
    node_has_pattern_in_context( node,
                                patt = {'ch': {'word': '的', 'tag':'u', 'deps': [], 'rel': 'RAD'}},
                                 context = {'g': <graph>,
                                            'parentPat': {'tag':'n'},
                                            'childPat' : {'x': {'tag':'n'},
                                                          'VOB': {'tag':'n'}}
                                            })
    """
    if not isinstance(node, dict):
        return False
    lan = node.get('lan', 'xlan')
    if lan not in patt.keys():
        print('patt error!')
        return False
    patDic = patt[lan]
    matched = True
    contextMatched = True
    for key in patDic.keys():
        if not (key in node.keys() and value_match(node[key], patDic[key])):
            matched = False
    if matched and context != None:
        thisGraph = context['g']
        parentPat = context.get('parentPat', False)
        if parentPat:
            parentAddress = node['head']
            parentNode = thisGraph.nodes[parentAddress]
            contextMatched = node_has_pattern_in_context(parentNode, parentPat)
        childPat = context.get('childPat', False)
        if childPat:
            for childRel in childPat.keys():
                if childRel == 'x': #matching any edge
                    for aRel in node['deps'].keys():
                        for address in node['deps'][aRel]:
                            childNode = thisGraph[address]
                            thisChildPat = childPat.get(childRel, False)
                            if thisChildPat:
                                contextMatched = node_has_pattern_in_context(childNode, thisChildPat)
                else:
                    for address in node['deps'].get(childRel,[]):
                        childNode = thisGraph[address]
                        thisChildPat = childPat.get(childRel, False)
                        if thisChildPat:
                            contextMatched = node_has_pattern_in_context(childNode, thisChildPat)
    return matched and contextMatched


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


def remove_ch_quantitative_word(graph, node, node_address):
    head_address = node['head']
    deps_address = node['deps'].get('ATT', [])
    assert len(deps_address) == 1
    if head_address and deps_address:
        dep_address = deps_address[0]
        graph[dep_address]['head'] = head_address

        if len(graph[head_address]['deps']['ATT']) == 1:
            del graph[head_address]['deps']['ATT']
        else:
            index = graph[head_address]['deps']['ATT'].index(node_address)
            del graph[head_address]['deps']['ATT'][index]

        new_label = str(node_address) + ":" + node['word']+":"+node['tag']
        graph[head_address]['deps'].update({new_label: deps_address})
    return graph


def remove_leaf_with_pos_u(graph, node, node_address):
    headAddress = node['head']
    headOfHeadAddress = graph[headAddress]['head']
    if headAddress and headOfHeadAddress:
        if len(graph[headOfHeadAddress]['deps']['ATT']) == 1:
            del graph[headOfHeadAddress]['deps']['ATT']
        else:
            index = graph[headOfHeadAddress]['deps']['ATT'].index(headAddress)
            if index > -1:
                del graph[headOfHeadAddress]['deps']['ATT'][index]
        new_label = str(node_address) + ":" + node['word'] + ":" + node['tag']
        graph[headOfHeadAddress]['deps'].update({new_label: [headAddress]})
    return graph
