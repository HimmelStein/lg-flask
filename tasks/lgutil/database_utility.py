# -*- coding: utf-8 -*-

import psycopg2
import sys

table_kdic = [
    {"lan": "de",  "table": "pons",  "snt": "de_snt",  "ldg": "de_ldg"},
    {"lan": "ch", "table": "pons", "snt": "ch_snt", "ldg": "ch_ldg"},
    {"lan": "ch", "table": "ldc2002t01", "snt": "ch_snt", "ldg": "ch_ldg"},
    {"lan": "en",  "table": "ldc2002t01", "snt": "en_snt",  "ldg": "en_ldg"},
    {"lan": "de", "table": "debible", "snt": "snt", "ldg": "snt_lg"},
    {"lan": "ch", "table": "chbible", "snt": "snt", "ldg": "snt_lg"},
    {"lan": "en", "table": "enbible", "snt": "snt", "ldg": "snt_lg"},
    ]

db = 'language_graph'
dbuser = 'postgres'


def get_raw_ldg_with_id(id, table=''):
    global table_kdic
    try:
        con = psycopg2.connect(host='localhost', database=db, user=dbuser)
        print('connecting postgre')
        cur = con.cursor()
        sql_str = "SELECT ch_ldg FROM "+ table + " where id="+str(id)
        print(sql_str)
        cur.execute(sql_str)
        con.commit()
        rows = cur.fetchall()
        for row in rows:
            print('row', row[0])
            return row[0]
    except psycopg2.DatabaseError:
        if con:
            con.rollback()
        print('Error %s' % psycopg2.DatabaseError)
        sys.exit(1)
    finally:
        if con:
            con.close()