# -*- coding: utf-8 -*-

import os
import time
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
from subprocess import Popen, PIPE

os.environ['STANFORD_PARSER'] = 'stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'stanford-parser-3.6.0-models.jar'
util_loc = "/Users/tdong/git/lg-flask/tasks/lgutil"

model_en_path = os.path.join(util_loc,"edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
model_de_path = os.path.join(util_loc,"edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz")
model_cn_path = os.path.join(util_loc,"edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz")
model_ch_lex_path =os.path.join(util_loc, "edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz")

segmenter = StanfordSegmenter(path_to_jar=os.path.join(util_loc,"extools/stanford-segmenter.jar"),
                              path_to_sihan_corpora_dict=os.path.join(util_loc,"stanford-segmenter-2015-12-09/data"),
                              path_to_model=os.path.join(util_loc,"stanford-segmenter-2015-12-09/data/pku.gz"),
                              path_to_dict=os.path.join(util_loc,"stanford-segmenter-2015-12-09/data/dict-chris6.ser.gz"))

#parser_en = StanfordParser(model_path = model_en_path)
#parser_de = StanfordParser(model_path = model_de_path)
#parser_cn = StanfordParser(model_path = model_cn_path)
#parser_ch_lex = StanfordParser(model_path = model_ch_lex_path)

dep_parser_en = StanfordDependencyParser(model_path = model_en_path)
dep_parser_de = StanfordDependencyParser(model_path = model_de_path)
dep_parser_cn = StanfordDependencyParser(model_path = model_cn_path)


def get_dep_str(snt, lan='en', ch_parser = 'hit', de_parser='parzu'):
    """
    for german sentence, we use parzu, which is much better than stanford parser
    for chinese sentence, we use hit.
    :param snt: a string of sentence
    :param lan: 'de','en','ch'
    :return: string in conll(10) format
    """
    if lan == 'ch':
        if ch_parser == 'hit':
            time.sleep(5)
            import urllib.request
            import urllib.parse
            from urllib.request import urlopen
            from urllib.parse import quote
            url_get_base = "http://api.ltp-cloud.com/analysis/?"
            api_key = "74x4c7F3JiRepP6isevdShbXmhrLJE8RJWvnsZPy"
            #api_key = "47b7P5F0pQvs8b3MUSXAtAqu6pCZsXYKndEXoise"
            format = "conll"
            pattern = "dp"
            url = url_get_base + 'api_key=' + api_key + '&text=' + quote(
                snt) + '&format=' + format + '&pattern=' + pattern
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                content = ''
                for line in response:
                    line = line.decode('utf8')  # Decoding the binary data to text.
                    content = content + line
            return content
        else:
            snt = str(snt)
            ch_seg_snt = segmenter.segment(snt).strip('\n').strip('。')
            print(type(ch_seg_snt), '+'+ch_seg_snt+'+')
            #ch_seg_snt = ch_seg_snt.encode(encoding='UTF-8')
            result = dep_parser_cn.raw_parse(ch_seg_snt)
            dep = next(result)
            return dep.to_conll(10)
    elif lan == 'en':
        result = dep_parser_en.raw_parse(snt)
        dep = next(result)
        return dep.to_conll(10)
    elif lan == 'de':
        if de_parser == 'parzu':
            echo_process = Popen(['echo', snt], stdout=PIPE)
            parzu_process = Popen(['/Users/tdong/components/ParZu/parzu'],
                                  stdin=echo_process.stdout, stdout=PIPE)
            echo_process.stdout.close()
            out, err = parzu_process.communicate()
            return out.decode("utf-8")
        else:
            result = dep_parser_de.raw_parse(snt)
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
    str_ch2 = '他借了几本书。'
    str_de1 = 'Jenes Mädchen ist sehr hübsch.'
    str_en1 = 'In other words, counterfactual thinking influences how satisfied each athlete feels.'
    dep_str = get_dep_str(str_ch1, lan='ch', ch_parser='hit')
    print(dep_str)
    #dep_str = get_dep_str(str_en1, lan='en')
    #print(dep_str)
    #dep_str = get_dep_str(str_de1, lan='de')
    #print(dep_str)


