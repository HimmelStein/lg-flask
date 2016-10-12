# -*- coding: utf-8 -*-

import sys
import time
import random
import os
import codecs
import re
import csv
from pprint import pprint
from nltk.parse.stanford import StanfordDependencyParser
from subprocess import Popen, PIPE

util_loc = "/Users/tdong/git/lg-flask/tasks/lgutil"
model_en_path = os.path.join(util_loc,"edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
dep_parser_en = StanfordDependencyParser(model_path = model_en_path)
parzu_loc = '/Users/tdong/components/ParZu/parzu'

try:
    from . import config_wv
    from . import pre_util
except:
    sys.path.append("/Users/tdong/git/lg-flask/tasks/lgutil/pre_processing_wv/config_wv")
    import config_wv
    import pre_util

sys.path.append('/usr/local/bin/')
pprint(sys.path)


def get_all_ldgs_of_sentences(csvfname, encoding='utf-8', parser='hit', format='conll'):
    picklefname =  csvfname[:-3]+'pickle'
    dic = pre_util.load_pickle(picklefname)
    existing_keys = list(dic.keys())
    for rowLst in pre_util.get_all_rows_from_csv(csvfname, encoding=encoding):
        key = rowLst[0]+"_"+"_"+rowLst[1]+"_"+rowLst[2]
        snt = rowLst[3]
        if len(snt.strip())==0:
            continue
        if key not in existing_keys:
            print("get ldg for ", key, snt)
            ldg = get_ldg(snt, parser=parser, format=format)

            if ldg == 'need_long_wait':
                print('beginning long waiting...')
                time.sleep(25)
                print('try again...')
                get_all_ldgs_of_sentences(csvfname, encoding=encoding, parser=parser, format=format)

            dic[key] = ldg
            pre_util.dump_pickle(picklefname, dic)


def get_ldg(snt, parser='none', format = 'conll'):
    if parser == 'hit':
        return get_ch_ldg(snt, ch_parser=parser, format=format)
    elif parser == 'stanford':
        return get_en_ldg(snt, format=format)
    elif parser == 'parzu':
        return get_de_ldg(snt, de_parser=parser, format=format)


def get_de_ldg(snt, de_parser='parzu', format='conll'):
    """
    :param snt:
    :param en_parser:
    :param format:
    :return:
    """
    if de_parser == 'parzu':
        echo_process = Popen(['echo', snt], stdout=PIPE)
        parzu_process = Popen([parzu_loc],
                             stdin=echo_process.stdout, stdout=PIPE)
        echo_process.stdout.close()
        out, err = parzu_process.communicate()
        pprint(out.decode("utf-8"))
        return out.decode("utf-8")
    else:
        print('de parser is not recognized')


def get_en_ldg(snt, en_parser='stanford', format='conll'):
    """
    :param snt:
    :param en_parser:
    :param format:
    :return:
    """
    result = dep_parser_en.raw_parse(snt)
    dep = next(result)
    if format == 'conll':
        print(dep.to_conll(10))
        return dep.to_conll(10)

def get_ch_ldg(snt, ch_parser='hit', format='conll'):
    """
    :param snt: one sentence
    :param ch_parser:
    :param format: output format
    :return:
    """
    if ch_parser == 'hit':
        time.sleep(2)
        import urllib.request
        import urllib.parse
        from urllib.parse import quote
        url_get_base = "http://api.ltp-cloud.com/analysis/?"
        api_key = random.choice(["74x4c7F3JiRepP6isevdShbXmhrLJE8RJWvnsZPy",
                                 "47b7P5F0pQvs8b3MUSXAtAqu6pCZsXYKndEXoise"])
        pattern = "dp"
        url = url_get_base + 'api_key=' + api_key + '&text=' + quote(
            snt) + '&format=' + format + '&pattern=' + pattern
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                content = ''
                for line in response:
                    line = line.decode('utf8')  # Decoding the binary data to text.
                    content = content + line
        except:
            return 'need_long_wait'
        return content


def create_ldg_from_text(fname, encoding = 'ISO-8859-1'):
    fullname, ext = os.path.splitext(fname)
    output = fullname + '.ldg'
    print(output)
    cmd = parzu_loc + "  -l -o conll <  " + fname + " > " + output
    os.system(cmd)


def create_ldg_pickle_from_ldg_text(fnamecsv, fnameldgtxt, encoding = 'ISO-8859-1'):
    """
    :param fnamecsv: csv file, each line is a snt
    :param fnameldgtxt: txt file,
    :param encoding:
    :return:
    """
    picklefname = fnamecsv[:-3] + 'pickle'
    dic = pre_util.load_pickle(picklefname)

    allRowLst = pre_util.get_all_rows_from_csv(fnamecsv, encoding=encoding)
    with open(fnameldgtxt, 'r') as fh:
        data = fh.read()
        ldgLst = data.split('\n\n')
    j = 0
    for i in range(len(allRowLst)):
        rowLst = allRowLst[i]
        key = rowLst[0] + "_" + "_" + rowLst[1] + "_" + rowLst[2]
        snt = rowLst[3]
        if len(snt.strip()) == 0:
            continue
        else:
            ldg = ldgLst[j]
            dic[key] = ldg
            j += 1
    pre_util.dump_pickle(picklefname, dic)
    print(len(dic.keys()))


if __name__ == '__main__':
    #get_all_ldgs_of_sentences(config_wv.EnBibleCsv, parser='stanford')
    #get_all_ldgs_of_sentences(config_wv.ChBibleCsv, parser='hit', encoding='gb2312')
    #get_all_ldgs_of_sentences(config_wv.DeBibleCsv, parser='parzu', encoding='ISO-8859-1')
    #dic = pre_util.load_pickle(config_wv.ChBiblePickle)
    #pprint(dic)
    #create_ldg_from_text(config_wv.DeBibleLst)
    create_ldg_pickle_from_ldg_text(config_wv.DeBibleCsv, config_wv.DeBibleLDG)