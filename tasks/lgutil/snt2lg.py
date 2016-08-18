# -*- coding: utf-8 -*-
import os
import sys
import codecs
import re
import psycopg2

project_loc = '/Users/tdong/git/lg-flask/data'
chinese_train_file = 'hgb.txt'
english_train_file = 'bbe.txt'
german_train_file = 'Martin_Luther_Uebersetzung_1912.txt'

con = None


def read_train_file(fname, encode='utf-8'):
    fhandle = codecs.open(os.path.join(project_loc, fname), "r", encode)
    for line in fhandle.readlines():
        line = line.strip('\n')
        bbid = ''
        snt = ''
        lst = line.split(' ')
        if len(lst) < 3:
            bbid = lst[0]+' '+lst[1]
        elif ':' in lst[1]:
            bbid = lst[0]+' '+lst[1]
            snt = ' '.join(lst[2:])
        else:
            print('**', lst)
        print(bbid, snt)


def test_reading_train_files():
    read_train_file(chinese_train_file, encode="gb2312")
    read_train_file(german_train_file, encode='ISO-8859-1')
    read_train_file(english_train_file)


def insert_snt_into_db_table(fname, encode='utf-8', db='language_graph', dbuser='postgres', table=''):
    try:
        con = psycopg2.connect(database=db, user=dbuser)
        cur = con.cursor()
        fhandle = codecs.open(os.path.join(project_loc, fname), "r", encode)
        i = 0
        for line in fhandle.readlines():
            line = line.strip('\n').strip('\r')
            bbid = ''
            snt = ''
            lst = line.split(' ')
            if len(lst) < 3:
                bbid = lst[0] + ' ' + lst[1]
            elif ':' in lst[1]:
                bbid = lst[0] + ' ' + lst[1]
                snt = ' '.join(lst[2:])
            else:
                print('**', lst)
            print(bbid, snt)
            cur.execute("INSERT INTO "+table+"(id, bbid, snt) VALUES(%s, %s, %s)",(i, bbid, snt))
            i += 1

        con.commit()
    except psycopg2.DatabaseError:
        if con:
            con.rollback()
        print('Error %s' % psycopg2.DatabaseError)
        sys.exit(1)
    finally:
        if con:
            con.close()


def get_chinese_language_dependency_graph(snt):
    import urllib.request
    import urllib.parse
    from urllib.request import urlopen
    from urllib.parse import quote
    url_get_base = "http://api.ltp-cloud.com/analysis/?"
    api_key = "74x4c7F3JiRepP6isevdShbXmhrLJE8RJWvnsZPy"
    format = "conll"
    pattern = "dp"
    url = url_get_base+'api_key='+api_key+'&text='+quote(snt)+'&format='+format+'&pattern='+pattern
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        content = ''
        for line in response:
            line = line.decode('utf8')  # Decoding the binary data to text.
            content = content + line
    print(content)
    return content


def get_language_dependency_graph(snt, lan=''):
    if lan == 'ch':
        return get_chinese_language_dependency_graph(snt)
    elif lan == 'en':
        return get_english_language_dependency_graph(snt)
    elif lan == 'de':
        return get_german_language_dependency_graph(snt)


def insert_lg_into_table(fname, lan='', encode='utf-8', db='language_graph', dbuser='postgres', table=''):
    try:
        con = psycopg2.connect(database=db, user=dbuser)
        cur = con.cursor()

        fhandle = codecs.open(os.path.join(project_loc, fname), "r", encode)
        for line in fhandle.readlines():
            line = line.strip('\n').strip('\r')
            bbid = ''
            snt = ''
            lst = line.split(' ')
            if len(lst) < 3:
                bbid = lst[0] + ' ' + lst[1]
            elif ':' in lst[1]:
                bbid = lst[0] + ' ' + lst[1]
                snt = ' '.join(lst[2:])
            else:
                print('**', lst)
            print(bbid, snt)
            lg = get_language_dependency_graph(snt, lan=lan)
            cur.execute("INSERT INTO " + table + "(snt_lg) VALUES(%s) where bbid=%s", (lg, bbid))

        con.commit()
    except psycopg2.DatabaseError:
        if con:
            con.rollback()
        print('Error %s' % psycopg2.DatabaseError)
        sys.exit(1)
    finally:
        if con:
            con.close()

#
# Postgres SQL
# SELECT table_schema,table_name FROM information_schema.tables where table_schema='public'
# ORDER BY table_schema,table_name;
#

if __name__ == "__main__":
    #read_train_file(chinese_train_file, encode="gb2312")
    #read_train_file(german_train_file, encode='ISO-8859-1')
    #read_train_file(english_train_file)
    #insert_snt_into_db_table(chinese_train_file, encode='gb2312',  table='chbible')
    #insert_snt_into_db_table(english_train_file,   table='enbible')
    #insert_snt_into_db_table(german_train_file, encode='ISO-8859-1', table='debible')
    pass
