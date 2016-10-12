# -*- coding: utf-8 -*-

import sys
import codecs
import re
import csv


try:
    from . import config_wv
except:
    sys.path.append("/Users/tdong/git/lg-flask/tasks/lgutil/pre_processing_wvconfig_wv")
    import config_wv


def get_all_lines(fname, encoding='utf8'):
    with codecs.open(fname, "r", encoding) as fd:
        return fd.readlines()


def replace_markers(ln, rMarkers=[["（","("], ["）", ")"], ["\n", ""], ["“","\""],["‘", "'"], ["\r",""]]):
    for pair in rMarkers:
        ln = ln.replace(pair[0], pair[1])
    return ln


def get_all_notes(ln, encoding='utf8', markers=[["(",")"]]):
    noteLst = []
    for pair in markers:
        pattern = ".*?\("+pair[0]+".*?"+pair[1]+"\)"
        regex = re.compile(pattern)  # move something in () to the end
        noteLst = noteLst + re.findall(regex, ln)
    return noteLst


def to_bytes(lst):
    if type(lst) == str:
        return str.encode(lst)
    else:
        return [to_bytes(ele) for ele in lst]


def write_matrix_to_csv(csvfile, matrix):
    with open(csvfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(matrix)


def create_bible_csv(fname, csvfname, encoding='utf8', rawSep = config_wv.EnSntSeparators, markers=[["(",")"]]):
    pattern = '|'.join(rawSep)
    emptyMarkers = [m[0]+m[1] for m in markers]
    matrix=[]
    count = 0
    for ln in get_all_lines(fname, encoding=encoding):
        ln = replace_markers(ln)
        lst = ln.split(' ')
        if ":" in lst[1]:
            cnt = ' '.join(lst[2:])
            noteLst = get_all_notes(ln,  markers=markers)
            for note in noteLst:
                cnt = cnt.replace(note, "")
                for marker in emptyMarkers:
                    cnt = cnt.replace(marker, "")

            sntLst = re.split(pattern, cnt)
            print(sntLst)
            Lst = sntLst+noteLst
            for i in range(len(Lst)):
                if len(Lst[i]) > 0:
                    matrix.append([lst[0], lst[1], str(i), Lst[i]])
                    count += 1

        else:
            print("ill-formatted line ", ln)
    #print(matrix)
    write_matrix_to_csv(csvfname, matrix)
    print('total:', count)

def checking_csv(fname):
    pass

if __name__ == "__main__":
    #create_bible_csv(config_wv.ChBibleRaw, config_wv.ChBibleCsv, rawSep = config_wv.ChSntSeparators, encoding='gb2312')
    #create_bible_csv(config_wv.EnBibleRaw, config_wv.EnBibleCsv)
    create_bible_csv(config_wv.DeBibleRaw, config_wv.DeBibleCsv, encoding='ISO-8859-1')

