import time

import asyncio

from img2pdf import img2pdf

from kukuCrawler import crawler


rootDir = '.\\output\\'


def main():
    startTime = time.time()
    try:
        name = asyncio.run(crawler(rootDir))
    except IndexError:
        print('kuku漫画找不到该资源')
        return

    print('下载完成，耗时{}s'.format(int(time.time() - startTime)),'转换为pdf中')
    img2pdf(rootDir + name)
    print('转换完成')
    

if __name__ == '__main__':
    main()

