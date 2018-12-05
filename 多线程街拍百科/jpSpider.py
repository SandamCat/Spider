# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from lxml import etree
from queue import Queue
import threading
import time


class Seimages:

    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.UrlQueue = Queue()
        self.resQueue = Queue()
        self.imageQueue = Queue()
        # 111.7.163.2:80
        self.proxies = {'http': 'http://111.7.163.2:80'}

    def getUrl(self):
        for i in range(1, 301):
            url = 'http://www.jiepaibaike.net/index-%d.html' % i
            self.UrlQueue.put(url)

    def getPage(self):
        while True:
            url = self.UrlQueue.get()
            res = requests.get(url, proxies=self.proxies,headers=self.headers)
            res.encoding = 'utf-8'
            html = res.text
            self.resQueue.put(html)

            self.UrlQueue.task_done()

    def getParse(self):
        while True:
            html = self.resQueue.get()
            parseHtml = etree.HTML(html)
            img_list = parseHtml.xpath('//div[@class="content"]/p/img/@src')
            for i in img_list:
                self.imageQueue.put(i)

            self.resQueue.task_done()

    def getImage(self):
        while True:
            img = self.imageQueue.get()
            res = requests.get(img, headers=self.headers)
            res.encoding = 'utf-8'
            html = res.content
            filename = img[-8:]
            with open('./图片/'+filename, 'wb') as f:
                f.write(html)
                print('下载成功')

            self.imageQueue.task_done()

    def run(self):
        th_list = []
        self.getUrl()
        for i in range(10):
            thRes = threading.Thread(target=self.getPage)
            th_list.append(thRes)
        for i in range(10):
            thParse = threading.Thread(target=self.getParse)
            th_list.append(thParse)
        for i in range(10):
            thImage = threading.Thread(target=self.getImage)
            th_list.append(thImage)

        for th in th_list:
            th.setDaemon(True)
            th.start()

        self.UrlQueue.join()
        self.resQueue.join()
        self.imageQueue.join()

if __name__ == '__main__':
    spider = Seimages()
    spider.run()
