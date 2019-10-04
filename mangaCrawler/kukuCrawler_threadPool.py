'''
废弃demo,有一些小问题，没有处理异常，所以不稳定
'''
'''
kuku漫画爬虫
为了下载《摇曳庄的幽奈小姐》
线程池初步实现 lxml解析
'''
import os

import requests

from concurrent import futures

from lxml import etree

from tqdm import tqdm


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

rootDir = '.\\'

rootUrl = 'http://comic.ikkdm.com'

searchUrl = 'http://so.kukudm.com/search.asp'

comicUrl = 'http://comic.ikkdm.com/comiclist'

downloadUrl = 'http://n9.1whour.com/'

MAX_WORKERS = 32


def getContent(name):
    params = {'kw':name.encode('GBK'),'Submit':'确定'.encode('GBK')}
    response = requests.get('http://so.kukudm.com/search.asp',params=params,headers=headers)
    data = etree.HTML(response.text)
    tmp = data.xpath('//*[@id="comicmain"]/dd/a[1]/@href')[0]
    return comicUrl + tmp[tmp.rfind('/',0,-2):]


def getChapters(url):
    response = requests.get(url, headers)
    data = etree.HTML(response.text)
    return data.xpath('//*[@id="comiclistn"]/dd/a[1]/@href')


def getPagesCount(url):
    response = requests.get(url,headers)
    response.encoding = 'GBK'
    text = response.text
    begin = text.find('共')
    end = text.find('页',begin)
    return int(text[begin + 1:end])


def downloadOne(info):
    name,url = info
    image = getImage(url)
    saveImage(name,image)


def getImage(url):
    response = requests.get(url,headers)
    response.encoding = 'GBK'
    text = response.text
    #<IMG SRC='"+m201304d+"newkuku/2017/07/30/汤摇庄的幽奈同学_第72话/001909V.jpg'>
    begin = text.find('+"') + len('+"')
    end = text.find('.jpg',begin) + len('.jpg')
    imageUrl = downloadUrl + text[begin:end]
    return requests.get(imageUrl,headers).content


def saveImage(name,image):
     with open(name,'wb') as f:
        f.write(image)


def main():
    name = input('漫画名：')

    try:
        url = getContent(name)
    except IndexError:
        print('kuku漫画找不到该资源')
        return

    _ = input('请输入开始话与结束话:').split()
    start,end = (int)(_[0]),(int)(_[1])

    path = rootDir + name
    if not os.path.exists(path):
        os.mkdir(path)
    path+='\\'

    chapters = getChapters(url)
    index = 0
    for chapter in tqdm(chapters[start - 1:end],ncols = 80):
        cur = path + str(start + index)
        index += 1
        os.mkdir(cur)
        
        chapter = rootUrl + chapter
        totalPage = getPagesCount(chapter)
        chapter = chapter[:-5]

        pages = []
        for i in range(1,totalPage + 1):
            pages.append(['{}\{}.jpg'.format(cur,i),'{}{}.htm'.format(chapter,i)])
        
        workers = min(MAX_WORKERS, totalPage)
        with futures.ThreadPoolExecutor(workers) as executor:
            executor.map(downloadOne, pages)
        
    print('下载完成')


if __name__ == '__main__':
    main()