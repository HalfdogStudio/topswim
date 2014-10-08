#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬取topswim.net选定帖子指定层数
"""

from lxml import etree
from lxml.html import fromstring, tostring
import requests
import sys
import os
import datetime
from weasyprint import HTML, CSS


try:
    n_layer = int(sys.argv[2])
    tid = int(sys.argv[1])
    flag = int(sys.argv[3])
    if flag == 1:  # online
        FLAG_ONLINE = True
        FLAG_PDF = False
    elif flag == 2:  # pdf
        FLAG_ONLINE = False
        FLAG_PDF = True
    elif flag == 3:  # both html and pdf
        FLAG_ONLINE = True
        FLAG_PDF = True
    elif flag == 4:
        print "flag NOT IMPLEMENTED"
        FLAG_ONLINE = False
        FLAG_PDF = False
        sys.exit(0)

except:
    print "[Usage] python topswim tid n_layer flag"


def download(tid, n_layer):
    n_page = 1
    new_html = ''
    header = u"""
    <html>
    <head>
    <title>游泳日报——来自topswim的精选——%s</title>
    <link href="css/style_1.css" type="text/css" rel="stylesheet">
    <link rel="shortcut icon" href="favicon.ico" >
    </head>
    <body>
    <nav id='topbar'>
    <a href="index.html">
    <img id="navtop"
    title="游泳日报" alt="游泳日报" src="image/swimnews.png">
    </a>
    <a href="http://reverland.org">
    <img id="author"
    title="reverland" alt="reverland's blog" src="image/author.png">
    </a>
    </nav>
    """
    # footer
    footer = u"""
    <a id='origin' href='%s'>在topswim上查看原文讨论</a>
    <a id='pdfdownload' href='pdf/%s.pdf'>保存为pdf格式</a>
    </body>
    <footer>© Reverland 2014</footer>
    </html>
    """
    while 1:
        url = "http://www.topswim.net/viewthread.php?tid="\
            + str(tid) + "&page=" + str(n_page)
        print "[I]parsing ", url
        r = requests.get(url)
        assert(r.content.find("charset=gbk"))
        # print "pages got " + str(n_page)
        if n_page == 1:
            title = fromstring(r.content).xpath('//h1/text()')[0].strip()
            new_html = header % title
        else:
            pass
        posts = fromstring(r.content).xpath('//td[@class="postcontent"]')
        # assert(len(posts) == 30)
        # only odd elements matters
        posts = posts[0::2]
        # assert(len(posts) == 15)

        for post in posts:
            postmessages = post.xpath(
                './div[@class="postmessage defaultpost"]')
            assert(len(postmessages) == 1)

            # 尝试下载图片
            images = postmessages[0].xpath('.//img')
            images = download_img(images)
            new_html += tostring(postmessages[0], encoding='unicode')
            if post.xpath(
                './div[@class="postinfo"]/strong/text()'
            )[0] == str(n_layer):
                new_html += footer % (unicode(url.split('&')[-2]),
                                      title)
                new_html = remove_white(new_html)
                return title, new_html

        n_page += 1


def download_img(images):
    try:
        for img in images:
            # 奇葩的attachment.gif
            if img.get('src') == 'images/attachicons/image.gif':
                continue
            if img.get('src') == 'images/default/attachimg.gif':
                continue
            img_url = img.get('src')
            filename = img_url.split('/')[-1]
            img.set('src', "image/" + filename)
            if img_url.find("http://") == -1:
                img_url = 'http://www.topswim.net/' + img_url
            # print img_url
            if os.path.exists('html/image/' + filename):
                continue
            # download
            try:
                r = requests.get(img_url, stream=True)
                with open('html/image/' + filename, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
            except:
                continue
    except:
        pass
    return images


def remove_white(html):
    root = fromstring(html)
    whites = root.xpath('//font[@color="white"]')
    for white in whites:
        white.getparent().remove(white)
    return tostring(root, encoding='unicode')


def remove_swf(html):
    html = html.decode('utf-8')
    root = fromstring(html)
    whites = root.xpath('//object')
    for white in whites:
        link_url = white.xpath('./embed')[0].get('src')
        link = etree.Element('a', href=link_url)
        link.text = u"视频地址： " + link_url
        white.getparent().append(link)
        white.getparent().remove(white)
    # 所以说unicode与否搞死人啊
    # py3 大法好，退2保平安
    return tostring(root, encoding='unicode')


title, html = download(tid, n_layer)

print "[!] : ", title

html = html.encode('utf-8')

if FLAG_ONLINE:
    with open('html/' + title + '.html', 'wb') as f:
        f.write(html)

if FLAG_PDF:
    html = html.replace('style_1.css', 'style_pdf.css')
    html = remove_swf(html)
    HTML(string=html,
         base_url="./html/").\
        write_pdf('html/pdf/' + title + '.pdf',
                  stylesheets=[CSS(filename='html/css/style_pdf.css')])

with open("./rebuild.sh", 'a') as f:
    record = u"# " + title + '|'
    record += datetime.date.today().isoformat()
    record += '\n'
    record += "python topswim.py "
    record += str(tid) + " " + str(n_layer) + " " + str(flag)
    record += '\n'
    record = record.encode('utf-8')
    f.write(record)