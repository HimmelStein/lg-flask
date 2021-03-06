# -*- coding: utf-8 -*-
import os
import sys
import codecs
import re
from bs4 import BeautifulSoup
import psycopg2

try:
    from . import snt2ldg
except:
    sys.path.append("/Users/tdong/git/lg-flask/tasks/lgutil")
    import snt2ldg

#
# following are raw bible files
#
project_loc = '/Users/tdong/git/lg-flask/data'
chinese_train_file = 'hgb.txt'
english_train_file = 'bbe.txt'
german_train_file = 'Martin_Luther_Uebersetzung_1912.txt'

#
# following are LDC2002T01 en-ch training files
# chinese txt encoded in gb2312
#
LDC2002T01_loc = '/Users/tdong/git/lg-flask/data/mt_chinese_v1'
ch_loc = 'source'
en_loc = 'translation'
en_sub_loc = 't[a|b][0-9]'
en_sub = 'ta0'


con = None


#
# load all LDC2002T01 paired ch-en sentences into Database
#
def load_ldc_into_database(ldc = LDC2002T01_loc, ch_loc = ch_loc, en_loc = en_loc, en_sub = en_sub):
    """
    table ldc2002t01: id | fname | en_sub | seg_id  | ch_snt | en_snt | ch_ldg | ch_sdg | en_ldg | en_sdg
    :param ldc:
    :param ch_loc:
    :param en_loc:
    :param en_sub:
    :return:
    """
    ch_path = os.path.join(LDC2002T01_loc, ch_loc)
    en_path = os.path.join(LDC2002T01_loc, en_loc, en_sub)
    ch_files = [f for f in os.listdir(ch_path) if re.match(r'.*\.sgm', f)]
    en_files = [f for f in os.listdir(en_path) if re.match(r'.*\.sgm', f)]
    if len(ch_files) != len(en_files):
        print('paired directories contain different number of files')
        return
    else:
        n = 0
        for fname in ch_files:
            ch_fname = os.path.join(ch_path, fname)
            en_fname = os.path.join(en_path, fname)
            try:
                ch_seg_lst = get_ldc_in_soup(ch_fname, lan = 'ch').find_all('seg')
                en_seg_lst = get_ldc_in_soup(en_fname, lan = 'en').find_all('seg')
                for i in range(len(ch_seg_lst)):
                    n += 1
                    ch_txt = ch_seg_lst[i].get_text().strip()
                    en_txt = en_seg_lst[i].get_text().strip()
                    print(fname, en_sub, i, ch_txt, en_txt, '\n')
                    insert_2snt_into_db_table(db='language_graph', dbuser='postgres', table='ldc2002t01',
                                              id=n, fname=fname, en_sub=en_sub, seg_id = i, ch_snt=ch_txt, en_snt=en_txt)
            except OSError as err:
                print("OS error: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])


#
# read LDC2002T01 chinese file
#
def get_ldc_in_soup(fname, lan='ch'):
    """
    :param fname: must be the full file name wit path
    :param lan: 'ch' or 'en'
    :return: soup object
    """
    if lan == 'ch':
        fhd = codecs.open(fname, 'rb', encoding='gb2312')
        ch_txt = fhd.read()
        soup = BeautifulSoup(ch_txt, 'html.parser')
        return soup
    elif lan == 'en':
        fhd = open(fname, 'rb')
        en_txt = fhd.read()
        soup = BeautifulSoup(en_txt, 'html.parser')
        return soup
    else:
        print('Usage: lan="ch" or "en"')
        return


def read_train_file(fname, encode='utf-8'):
    """

    :param fname:
    :param encode:
    :return:
    """
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


def insert_2snt_into_db_table(db='language_graph', dbuser='postgres', table='ldc2002t01',
                              id = 0, fname='', en_sub='', seg_id=0, ch_snt='', en_snt=''):
    """
        table ldc2002t01: id | fname | en_sub |  seg_id  |ch_snt | en_snt | ch_ldg | ch_sdg | en_ldg | en_sdg
    """
    try:
        con = psycopg2.connect(host='localhost', database=db, user=dbuser)
        print('connecting postgre')
        cur = con.cursor()

        ch_snt = ch_snt.replace("'", "\'")
        en_snt = en_snt.replace("'", "''")
        sql_str = "INSERT INTO " + table + "(id, fname, en_sub,  seg_id, ch_snt, en_snt) VALUES({0}, '{1}', '{2}', {3}, '{4}', '{5}')".format(id, fname, en_sub, seg_id, ch_snt, en_snt)
        print(sql_str)
        cur.execute(sql_str)
        con.commit()
    except psycopg2.DatabaseError:
        if con:
            con.rollback()
        print('Error %s' % psycopg2.DatabaseError)
        sys.exit(1)
    finally:
        if con:
            con.close()


def insert_snt_into_db_table(fname, encode='utf-8', db='language_graph', dbuser='postgres', table=''):
    """
    table ldc2002t01: id | fname | en_sub | ch_snt | en_snt | ch_ldg | ch_sdg | en_ldg | en_sdg
    table chbible: id | bbid | snt | snt_lg | snt_sdg
    table debible: id | bbid | snt | snt_lg | snt_sdg
    table enbible: id | bbid | snt | snt_lg | snt_sdg

    :param fname:
    :param encode:
    :param db:
    :param dbuser:
    :param table:
    :return:
    """
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


def insert_lg_into_table(fname, lan='', encode='utf-8', db='language_graph', dbuser='postgres', table=''):
    """
    ldg is the conll 10 format
    :param fname:
    :param lan:
    :param encode:
    :param db:
    :param dbuser:
    :param table:
    :return:
    """
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
            lg = snt2ldg.get_dep_str(snt, lan=lan)
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


def copy_sqlite_table_into_postgres():
    """
    load snt table into postgres
    :return:
    """
    try:
        con = psycopg2.connect(host='localhost', database="language_graph", user="postgres")
        print('connecting postgre')
        cur = con.cursor()
        import sqlite3
        conn_sqlite = sqlite3.connect(os.path.join(project_loc, 'PONS.db'))
        c_sqlite = conn_sqlite.cursor()
        for row in c_sqlite.execute("SELECT * FROM snt"):
            print(row)
            id = row[0]
            ch_snt = row[2]
            de_snt = row[1]
            sql_str = "INSERT INTO pons (id, ch_snt, de_snt) VALUES({0}, '{1}', '{2}')".format(id,  ch_snt, de_snt)
            print(sql_str)
            cur.execute(sql_str)
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
# load LDG to three tables
#
def load_ldg_into_table(lan=''):
    """
    table 1: chbible: id | bbid | snt | snt_lg | snt_sdg
    table 2: debible: id | bbid | snt | snt_lg | snt_sdg
    table 3: enbible: id | bbid | snt | snt_lg | snt_sdg
    table 4: pons:    id | ch_snt | de_snt | ch_ldg | ch_sdg | de_ldg | de_sdg
    table 5: ldc2002t01: id | fname | en_sub | ch_snt | en_snt | seg_id | ch_ldg | ch_sdg | en_ldg | en_sdg
    :param lan:
    :return:
    """
    batch_lst =[
        #{"lan": "de",  "table": "pons",  "snt": "de_snt",  "ldg": "de_ldg"},
        {"lan": "ch", "table": "pons", "snt": "ch_snt", "ldg": "ch_ldg"},
        {"lan": "ch",  "table": "ldc2002t01",  "snt": "ch_snt",  "ldg": "ch_ldg"},
        #{"lan": "en",  "table": "ldc2002t01", "snt": "en_snt",  "ldg": "en_ldg"},
        #{"lan": "de", "table": "debible", "snt": "snt", "ldg": "snt_lg"},
        #{"lan": "ch", "table": "chbible", "snt": "snt", "ldg": "snt_lg"},
        #{"lan": "en", "table": "enbible", "snt": "snt", "ldg": "snt_lg"},
        ]
    try:
        con = psycopg2.connect(host='localhost', database="language_graph", user="postgres")
        print('connecting postgre')
        cur = con.cursor()
        for dic in batch_lst:
            lan = dic['lan']
            table = dic['table']
            snt = dic['snt']
            ldg_col = dic['ldg']
            cur.execute("SELECT id," + snt +", "+ldg_col+ " FROM "+ table )
            rows = cur.fetchall()
            for row in rows:
                print(type(row[2]))
                if row[2] is None or row[2] == '':
                    id = row[0]
                    print(row[1])
                    ldg = snt2ldg.get_dep_str(row[1],lan=lan).replace('\t', ' ').replace('\n', ' * ').replace("'", "''")
                    print(dic, row)
                    print(ldg)
                    sql_str = """update {0} set {1} = '{2}' where id = {3}""".format(table, ldg_col, ldg, id)
                    print(sql_str)
                    cur.execute(sql_str)
                    con.commit()
    except psycopg2.DatabaseError:
        if con:
            con.rollback()
        print('Error %s' % psycopg2.DatabaseError)
        sys.exit(1)
    finally:
        if con:
            con.close()


def load_bible_ldg_into_table():
        """
        table 1: chbible: id | bbid | snt | snt_lg | snt_sdg
        table 2: debible: id | bbid | snt | snt_lg | snt_sdg
        table 3: enbible: id | bbid | snt | snt_lg | snt_sdg
        do in parallel
        :param lan:
        :return:
        """
        batch_lst = [
            {"lan": "ch", "table": "chbible", "snt": "snt", "ldg": "snt_lg"},
            {"lan": "de", "table": "debible", "snt": "snt", "ldg": "snt_lg"},
            {"lan": "en", "table": "enbible", "snt": "snt", "ldg": "snt_lg"}
        ]
        try:
            con = psycopg2.connect(host='localhost', database="language_graph", user="postgres")
            print('connecting postgre')
            cur_ch = con.cursor()
            cur_en = con.cursor()
            cur_de = con.cursor()

            ch_lan = batch_lst[0]['lan']
            de_lan = batch_lst[1]['lan']
            en_lan = batch_lst[2]['lan']
            ch_table = batch_lst[0]['table']
            de_table = batch_lst[1]['table']
            en_table = batch_lst[2]['table']
            snt = batch_lst[0]['snt']
            ldg_col = batch_lst[0]['ldg']

            cur_ch.execute("SELECT id," + snt + ", " + ldg_col+ " FROM " + ch_table )
            ch_rows = cur_ch.fetchall()
            cur_de.execute("SELECT id," + snt + ", " + ldg_col+ " FROM " + de_table)
            de_rows = cur_de.fetchall()
            cur_en.execute("SELECT id," + snt + ", " + ldg_col+ " FROM " + en_table)
            en_rows = cur_en.fetchall()

            for i in range(len(ch_rows)):
                print(i,ch_rows[i])
                id = ch_rows[i][0]
                if ch_rows[i][2] is None:
                    ldg_ch = snt2ldg.get_dep_str(ch_rows[i][1], lan=ch_lan, ch_parser='stanford').replace('\t', ' ').replace("'", "''")
                    sql_str = """UPDATE {0} SET {1} = '{2}' WHERE id = {3}""".format(ch_table, ldg_col, ldg_ch, id)
                    print(sql_str)
                    cur_ch.execute(sql_str)

                id = de_rows[i][0]
                print(i, de_rows[i][0])
                if de_rows[i][2] is None:
                    ldg_de = snt2ldg.get_dep_str(de_rows[i][1], lan=de_lan).replace('\t', ' ').replace('\n', ' * ').replace("'", "''")
                    sql_str = """UPDATE {0} SET {1} = '{2}' WHERE id = {3}""".format(de_table, ldg_col, ldg_de, id)
                    print(sql_str)
                    cur_de.execute(sql_str)

                id = en_rows[i][0]
                print(i, en_rows[i][0])
                if en_rows[i][2] is None:
                    ldg_en = snt2ldg.get_dep_str(en_rows[i][1], lan=en_lan).replace('\t', ' ').replace('\n', ' * ').replace("'", "''")
                    sql_str = """UPDATE {0} SET {1} = '{2}' WHERE id = {3}""".format(en_table, ldg_col, ldg_en, id)
                    print(sql_str)
                    cur_en.execute(sql_str)

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
    #load_ldc_into_database(ldc=LDC2002T01_loc, ch_loc=ch_loc, en_loc=en_loc, en_sub=en_sub)
    #copy_sqlite_table_into_postgres()
    load_ldg_into_table()
    #load_bible_ldg_into_table()
