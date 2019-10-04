'''
kuku漫画爬虫
为了下载《摇曳庄的幽奈小姐》100s下完
下载越大的漫画 速度越明显
协程 异步io lxml解析 保存图片时使用线程池
'''

from urllib import parse

import time

import os

import asyncio

import aiohttp

from lxml import etree

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

rootDir = ''

#these are url prefixs
rootUrl = 'http://comic.ikkdm.com'

searchUrl = 'http://so.kukudm.com/search.asp'

cmoicUrl = 'http://comic.ikkdm.com/comiclist'

downloadUrl = 'http://n9.1whour.com/'

#using in getContent
submit = parse.quote('确定',encoding='GBK')

contentTimeout = None

defaultTimeout = 3

#control concurrent for some super-long mangas
SLICE = 100

DONT_SLICE = 99999


async def getContent(session,name):
    name = parse.quote(name,encoding='GBK')
    #kuku use GBK encoding
    async with session.get('{}?kw={}&Submit={}'.format(searchUrl,name,submit,encoded=True)) as resp:
        data = etree.HTML(await resp.text())
        tmp = data.xpath('//*[@id="comicmain"]/dd/a[1]/@href')[0]
        #remove last '/'
        return cmoicUrl + tmp[tmp.rfind('/',0,-2):]


async def getChapters(session,url):
    async with session.get(url=url,timeout=contentTimeout) as resp:
        data = etree.HTML(await resp.text())
        return data.xpath('//*[@id="comiclistn"]/dd/a[1]/@href')


async def getPagesCount(session,url): 
    async with session.get(url) as resp:
        text = await resp.text(encoding='GBK')
        begin = text.find('共')
        end = text.find('页',begin)
        return int(text[begin + 1:end])


async def downloadMany(session,path,chapter):
    if not os.path.exists(path):
         os.mkdir(path)

    totalPage = await getPagesCount(session,chapter)

    chapter = chapter[:-5]

    tasks = []
    for i in range(1,totalPage + 1):
        name = '{}\{}.jpg'.format(path,i)
        if not os.path.exists(name):
            tasks.append(downloadOne(session,name,'{}{}.htm'.format(chapter,i)))

    await asyncio.gather(*tasks)


async def downloadOne(session,name,url):
    if os.path.exists(name):
        return

    image = await getImage(session,url)
    
    #use run_in_executor() to avoid obstruction
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None,saveImage,name,image)


async def getImage(session,url):
    while True:
        try:
            async with session.get(url) as resp:
                text = await resp.text(encoding='gbk')
        except:
            pass
        else:
            break

    #<IMG SRC='"+m201304d+"newkuku/2017/07/30/汤摇庄的幽奈同学_第72话/001909V.jpg'>
    begin = text.find('+"') + len('+"')
    end = text.find('.jpg',begin) + len('.jpg')
    imageUrl = downloadUrl + text[begin:end]
    

    while True:
        try:
            async with session.get(imageUrl) as resp:
                ans = await resp.read()
        except:
            pass
        else:
            return ans


def saveImage(name,image):
    with open(name, 'wb') as f:
        f.write(image)


async def crawler(dir):
    global SLICE

    rootDir = dir

    if not os.path.exists(rootDir):
        os.mkdir(rootDir)

    name = input('漫画名：')

    while True:
        try:
            _ = input('请输入开始话与结束话:').split()
            start,end = (int)(_[0]),(int)(_[1])
        except:
            print('非法输入')
        else:
            break

    c = input('输入y启用分段下载（适用超长篇漫画,默认关闭，默认下载失败时请启用），输入任意字符关闭:')
    
    SLICE_FLAG = c == 'y'

    conn = aiohttp.TCPConnector(limit=150,ssl = False)
    timeout = aiohttp.ClientTimeout(total=defaultTimeout)
    async with aiohttp.ClientSession(connector=conn,timeout=timeout,headers=headers) as session:
        url = await getContent(session,name)

        #construct manga dir
        path = rootDir + name
        if not os.path.exists(path):
            os.mkdir(path)
        path+='\\'

        tasks = []
        #only in [start,end]
        chapters = (await getChapters(session,url))[start - 1:end]
        end = min(end,len(chapters))

        if not SLICE_FLAG:
            SLICE = DONT_SLICE

        for i,chapter in enumerate(chapters):
            t = i + start
            tasks.append(downloadMany(session,path + str(t),rootUrl + chapter))
            if t % SLICE == 0:
                await asyncio.gather(*tasks)
                tasks.clear()
        if tasks:
            await asyncio.gather(*tasks)

    return name
