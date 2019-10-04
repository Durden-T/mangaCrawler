'''
将rootPath中文件夹中的图片合成为pdf
线程池
'''


import os

from concurrent import futures

from PIL import Image

#电脑跑不动....哭了
MAX_WORKERS = 2


#convert images in rootPath to pdf
def img2pdf(rootPath):
    paths = []
    for name in os.listdir(rootPath):
        curPath = os.path.join(rootPath,name)
        if os.path.isdir(curPath) and not os.path.exists(curPath + '.pdf'):
            paths.append(curPath)

    workers = min(MAX_WORKERS, len(paths))
    if workers:
        with futures.ThreadPoolExecutor(workers) as executor:
            executor.map(img2pdfHelper, paths)


def img2pdfHelper(path):
    dirs = os.listdir(path)
    dirs.sort(key=lambda s:int(s[:-4]))
    files = [os.path.join(path,name) for name in dirs]

    pdf = Image.open(files[0])
    files.pop(0)

    images = []
    for file in files:
        image = Image.open(file)
        if image.mode == "RGBA":
            image = image.convert('RGB')
        images.append(image)

    pdf.save(path + '.pdf',"PDF",save_all=True,append_images=images)


