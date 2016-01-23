# coding: utf-8

__author__ = 'maria'

import MySQLdb
import traceback
import pypyodbc
from pymongo import MongoClient
from bson.objectid import ObjectId
import redis
from bson.objectid import ObjectId

__author__ = 'maria'

# Establish connection to DB
# conn = pypyodbc.connect('DRIVER={MySQL ODBC 5.1 Driver};SERVER=localhost;DATABASE=SentiFeed;UID=root;PWD=291119851$Mk', ansi=True)


class MySQLDatabaseConnector(object):
    def __init__(self):
        try:
            # use this if you use MySQLdb (usually in windows)
            self.conn = MySQLdb.connect(host="127.0.0.1",
                                        user="root",
                                        passwd="",
                                        db="SentiFeed")

            # use this if you use mysql.connector
            # self.conn = mysql.connector.connect(user='root',
            #                                     password='291119851$Mk',  # 291119851$Mk
            #                                     host='127.0.0.1',
            #                                     database='SentiFeed')

            self.query = ''
            self.cur = self.conn.cursor()
        except:
            traceback.print_exc()
            raise Exception("Could not connect to MySQL, check if server is running!")

    def lastrowid(self):
        return self.cur._lastrowid

    def execute_query(self, query):
        self.query = query
        self.cur.execute(query)
        self.conn.commit()
        rows = self.cur.fetchall()
        return rows

    def update(self, query):
        cur = self.conn.cursor()
        self.query = query
        cur.execute(self.query)
        self.conn.commit()
        last_row_id = self.cur.lastrowid
        cur.close()
        return last_row_id

    def close_conn(self):
        self.conn.close()