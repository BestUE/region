# -*- coding: utf-8 -*-
# @Time    : 2021/9/2 2:30 下午
# @Author  : XY
# @FileName: region.py
# @Software: PyCharm

import json
import re
import urllib.request
from bs4 import BeautifulSoup


def main():
    print("脚本开始")
    res_json = []
    # 统计局首页地址
    base_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/"
    # 获取省份信息
    province = Province.get_province(base_url)
    for province_info in province:
        print(province_info.text + "...")
        province_code = "%s0000" % (re.match("\d.", province_info.get("href")).group())
        province_json = {"name": province_info.text, "code": province_code}
        # 城市信息
        city_html = City.get_city(base_url, province_info.get("href"))
        province_json["child"] = []
        for city_item in city_html:
            city_line = city_item.find_all('a')
            city_name = province_info.text if city_line[1].text == "市辖区" else city_line[1].text
            # 获取区（县）信息
            county_html = County.get_county(base_url, city_line[1].get("href"))
            county_json = []
            for county_item in county_html:
                county_line = county_item.find_all('a')
                if not county_line:
                    continue
                # 区的名称 这里只爬到区域(县) 居委会什么的就算了
                county_json.append({"code": county_line[0].text[0:6], "name": county_line[1].text})
            # 将城市加入json
            province_json["child"].append({"code": city_line[0].text[0:6], "name": city_name, "child": county_json})
        res_json.append(province_json)
    print("爬取完成写入文件中")
    fo = open("region.txt", 'w')
    fo.write(json.dumps(res_json, ensure_ascii=False))
    fo.close()
    print("脚本结束")


# 获取省份名称以及城市页面地址
class Province:
    page = "index.html"

    @classmethod
    def get_province(cls, base_url):
        html = Request.get_html(base_url + cls.page)
        print(base_url + cls.page)
        return html.select('table[class="provincetable"]  a')


# 城市名称以及区域页面地址
class City:
    @classmethod
    def get_city(cls, base_url, href):
        html = Request.get_html(base_url + href)
        print(base_url + href)
        return html.find_all('tr', class_="citytr")


# 区名称(县)
class County:
    @classmethod
    def get_county(cls, base_url, href):
        html = Request.get_html(base_url + href)
        print(base_url + href)
        return html.find_all('tr', class_="countytr")


# 请求网址 返回网页内容
class Request:
    status = 0  # 爬取状态
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }

    @classmethod
    def get_html(cls, base_url):
        retry = 3  # 总尝试次数

        while retry > 0:
            res = cls.request(base_url)
            retry -= 1
            if cls.status:
                return res
            else:
                print('重试中..')
        print('爬取失败')

    @classmethod
    def request(cls, base_url):
        try:
            request = urllib.request.Request(base_url, headers=cls.headers)
            response = urllib.request.urlopen(request)
            response = response.read().decode('gbk')
            cls.status = 1
            return BeautifulSoup(response, "html.parser")
        except urllib.error.HTTPError as e:
            cls.status = 0
            print(e.reason)
            return


if __name__ == '__main__':
    main()
