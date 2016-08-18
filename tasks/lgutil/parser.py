# -*- coding: utf-8 -*-

import os
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize.stanford_segmenter import StanfordSegmenter

os.environ['STANFORD_PARSER'] = 'stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'stanford-parser-3.6.0-models.jar'

model_en_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
model_de_path = "edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz"
model_cn_path = "edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz"
model_ch_lex_path = "edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz"

segmenter = StanfordSegmenter(path_to_jar="extools/stanford-segmenter.jar",
                              path_to_sihan_corpora_dict="stanford-segmenter-2015-12-09/data",
                              path_to_model="stanford-segmenter-2015-12-09/data/pku.gz",
                              path_to_dict="stanford-segmenter-2015-12-09/data/dict-chris6.ser.gz")

#parser_en = StanfordParser(model_path = model_en_path)
#parser_de = StanfordParser(model_path = model_de_path)
#parser_cn = StanfordParser(model_path = model_cn_path)
#parser_ch_lex = StanfordParser(model_path = model_ch_lex_path)

dep_parser_en = StanfordDependencyParser(model_path = model_en_path)
dep_parser_de = StanfordDependencyParser(model_path = model_de_path)
dep_parser_cn = StanfordDependencyParser(model_path = model_cn_path)


def get_dep_str(snt, lan='en'):
    """
    :param snt: a string of sentence
    :param lan: 'de','en','ch'
    :return: string in conll(10) format
    """
    if lan == 'ch':
        ch_seg_snt = segmenter.segment(snt)
        result = dep_parser_cn.raw_parse(ch_seg_snt)
        dep = next(result)
        return dep.to_conll(10)
    elif lan == 'en':
        result = dep_parser_en.raw_parse(en_snt)
        dep = next(result)
        return dep.to_conll(10)
    elif lan == 'de':
        result = dep_parser_de.raw_parse(de_snt)
        dep = next(result)
        return dep.to_conll(10)
    else:
        print('Usage: <sentence>, lan="en" or "de" or "ch"')


def test_parser():
    en_snt = "The quick brown fox jumps over the lazy dog."
    ch_snt = "今天是星期天"
    de_snt = "Heute ist Sonntag"

    ch_seg_snt = segmenter.segment(ch_snt)
    print(segmenter.segment(ch_snt))

    result = dep_parser_en.raw_parse(en_snt)
    dep = next(result)
    dep_en = dep.to_conll(10)
    print(dep_en)

    result = dep_parser_de.raw_parse(de_snt)
    dep = next(result)
    dep_de = dep.to_conll(10)
    print(type(dep_de))
    print(dep_de)

    result = dep_parser_cn.raw_parse(ch_seg_snt)
    dep = next(result)
    dep_ch = dep.to_conll(10)
    print(dep_ch)


if __name__ == "__main__":
    str_ch1 = '国务院总理今天出访美国'
    str_ch2 = '中国对赢了'
    dep_str = get_dep_str(str_ch1, lan='ch')
    print(dep_str)
    dep_str = get_dep_str(str_ch2, lan='ch')
    print(dep_str)


