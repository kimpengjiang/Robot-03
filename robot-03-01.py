import re
import requests
import redis
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup


class getPageSoure:
    def __init__(self):
        pass

    def getNowDate(self):
        now = datetime.now()
        datestr = now.strftime('%Y/%m/%d')
        # print(datestr)
        return datestr  # 返回当前日期2019/10/05

    def spliceURL(self,url,datastr):
        newURL = url + datastr
        # print(newURL)
        return newURL

    def judgeURL(self,url):
        '''
        检测拼接的URL是否可用，使用request库检测
        '''
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True,url
            else:
                return False,None
        except requests.exceptions.ConnectionError:
            return False,None

    def downloadPageSource(self,url):
        datastr = getPageSoure.getNowDate(self)
        newURL = getPageSoure.spliceURL(self,url,datastr)
        data,newurl = getPageSoure.judgeURL(self,newURL)
        if data == True:
            client = webdriver.Chrome()
            client.get(newurl)
            html = client.page_source
            client.close()
            return html
        else:
            print('error')
            exit(233)

    def downloadNextPageSource(self,url): # 我觉得这个模块可以再改改，合并
        data, newurl = getPageSoure.judgeURL(self, url)
        if data == True:
            client = webdriver.Chrome()
            client.get(newurl)
            html = client.page_source
            client.close()
            return html
        else:
            print('end')
            exit(233)


class getTorrent:
    def __init__(self):
        pass

    def re_html(self,html):
        torrent = re.compile('<a.*?title="Download .torrent" href="(.*?)"')
        torrentList = re.findall(torrent,html)
        titleList = []
        soup = BeautifulSoup(html,'lxml')
        for h5 in soup.select('h5'):
            h5 = h5.get_text()
            h5 = h5.replace("\n","")
            h5 = h5.replace("\xa0","")
            h5 = h5.split()
            data = str(h5[0])+'--'+str(h5[1]) # 这一串转换来转换去都是为了格式化输出
            titleList.append(data)
        return torrentList,titleList

    def spliceTorrent(self,html):
        newTorrentList = []
        torrentList,titleList = getTorrent.re_html(self,html)
        loadClass = getPageSoure() # 这里也要将getPageSource初始化一次，不然会调用失败
        for i in torrentList:
            a = loadClass.spliceURL(url,i)
            newTorrentList.append(a)
        # print(newTorrentList)
        # print(titleList)
        torrentDict = dict(zip(titleList,newTorrentList))
        return torrentDict

    def writeRedis(self,html):
        torrentDict = getTorrent.spliceTorrent(self,html)
        pool = redis.ConnectionPool(host='127.0.0.1',port=6379)
        r = redis.Redis(connection_pool=pool)
        loadclass = getPageSoure()
        datetimes = loadclass.getNowDate()
        for x,y in torrentDict.items():
            x = datetimes+":"+x # 添加日期，方便redis区分目录
            r.set(x,y)
        r.close()

def first_get(url):
    first_get_page = getPageSoure()
    html = first_get_page.downloadPageSource(url)
    first_get_torrent = getTorrent()
    first_get_torrent.writeRedis(html)

def next_get(url):
    test1 = getPageSoure()
    datestr = test1.getNowDate()
    url = test1.spliceURL(url,datestr)
    num = 2
    while True:
        newurl = url + '?page=' + str(num)
        test2 = getPageSoure()
        html = test2.downloadNextPageSource(newurl)
        next_get_torrent = getTorrent()
        next_get_torrent.writeRedis(html)
        num = num + 1



if __name__=='__main__':
    url = 'https://onejav.com/'
    first_get(url)
    next_get(url)