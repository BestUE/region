# -*- coding: utf-8 -*-
# @Time    : 2021/9/7 2:54 下午
# @Author  : XY
# @FileName: to_mysql.py
# @Software: PyCharm
import json

import pymysql


def main():
    fo = open("region.txt", "r")
    res = json.loads(fo.read())
    sql_list = []
    for item in res:
        sql = "insert into region (region_id,name,level)values(%s,'%s',1)" % (item['code'], item['name'])
        sql_list.append(sql)
        city = item['child']
        for city_item in city:
            sql = "insert into region (region_id,pid,name,level)values(%s,%s,'%s',2)" % (
                city_item['code'], item['code'], city_item['name'])
            sql_list.append(sql)
            county = city_item['child']
            for county_item in county:
                sql = "insert into region (region_id,pid,name,level)values(%s,%s,'%s',3)" % (
                    county_item['code'], city_item['code'][0:6], county_item['name'])
                sql_list.append(sql)

    db = ConnectDb()
    db.execute(sql_list)
    fo.close()


class ConnectDb:
    def __new__(cls):
        if not hasattr(cls, 'conn'):
            cls.conn = pymysql.connect(host="127.0.0.1", user="ue", password="~Q1w2e3r4", db="copy1")
            cls.cursor = cls.conn.cursor()
        return super(ConnectDb, cls).__new__(cls)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def select(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def execute(self, sql_list):
        try:
            for item in sql_list:
                print(item)
                self.cursor.execute(item)
            self.conn.commit()
        except pymysql.err.MySQLError as e:
            self.conn.rollback()
            print(e)


if __name__ == "__main__":
    main()
